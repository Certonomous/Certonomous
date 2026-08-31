# RESULTS — VMFL033-R2: Viscous Heating in an Annulus

**Case.** Ansys Fluid Dynamics Verification Manual VM2026R1, **p. 119**. Tangential annular flow with
viscous dissipation; the reference is the **closed form** of Bird, Stewart & Lightfoot (1960), the
manual's own cited source, evaluated here rather than digitised — so the reference error is zero by
construction and the tier is **PASS-capable** (`ANSYS_VERIFICATION_CHARTER` §11.1).

**R2 is a NEW registration succeeding R1**, not an edit of it. R1 landed `NOT A RESULT` as register
row **#21** and **R1's frozen files are untouched and its row stands**. R2's **one** substantive
change is `endTime` 20 000 → 100 000 (R1 died of too few iterations). Freeze commit **`7c5158df`**.

**Solver.** OpenFOAM v2606 `buoyantSimpleFoam`, `laminar`, serial (`ranks = 1`, so core-min = wall-min
on every figure in this record). Radial refinement family `r = 2`, **θ held FIXED at 8 cells**:
`L1_nr32` 256 cells, `L2_nr64` 512, `L3_nr128` 1024. Fixed-iteration mode (`residualControl {}` empty);
every level runs the full 100 000 iterations.

---

## VERDICT: PASS

**The gate is the TEMPERATURE channel, and only the temperature channel.** `PREREGISTRATION.md` §6 —
frozen before compute — declares velocity **REPORTED but NOT A DISCRIMINATOR**, because the velocity
field of this problem is independent of every material property and so cannot discriminate between a
correct and an incorrect thermal solve. The velocity number below is printed either way and is not
allowed to become the verdict.

| channel | quantity | value | frozen band | result |
|---|---|---|---|---|
| **GATE — temperature** | `max_cells\|T − T_ex\| / (T_peak,ex − T1)` at L3 | **1.962465e-03** | **0.01** (`GATE_T_TOL`) | **INSIDE, by a factor of 5.10** |
| Roache triple (T volume-average) | state | **`CONVERGING`** | must be CONVERGING | met |
| Roache order | `p_obs` | **2.2090** | floor `P_MIN` 0.05; formal 2.0; suspicious-above `P_SUSPICIOUS` 2.5 | above floor, **below** the suspicion flag |
| Roache uncertainty | `GCI_fine` at `Fs` 1.25 | **0.000298 %** | ceiling `GCI_MAX` 10 % | met, four orders under |
| velocity — REPORTED, NOT THE GATE | `max\|v − v_ex\| / (Ω2·R2)` at L3 | 3.468273e-04 | report band 0.01 | within — **and not the verdict** |

**Verdict sentence, from the frozen comparator:** *"the TEMPERATURE band is met at the finest level on
a CONVERGING triple (GCI within ceiling, order above floor); a converging triple bounds the
discretisation error, so PASS is available per charter Sec.11.1"*.

`PASS` is the fixed vocabulary of `CLAUDE.md` rule 1. The rule-5 order was applied as written: no
level failed the plateau clause (step 1), the triple is `CONVERGING` rather than `DIVERGENT` /
`STAGNANT` / `OSCILLATORY` / `EXACT` (step 2), so step 3 grades against the pre-registered band.

---

## THE THREE THINGS THIS `PASS` DOES **NOT** SAY

A `PASS` is a statement about a pre-registered gate, not a certificate of general correctness. Three
measured facts sit beside it and are recorded here so the row cannot be read as more than it is.

### 1. The case MISSED its own registered expectation `E_T`, by 1.96×
`PREREGISTRATION.md` froze a **registered expectation** `EXPECT_T_TOL = 0.001` alongside the
`GATE_T_TOL = 0.01` gate — reported either way, never the gate. The measured 1.962465e-03 is
**`NOT MET`** against it, missing by a factor of **1.962**. The velocity expectation `E_v` (0.001) **is**
met at 3.468e-04. So the lab predicted, before compute, a temperature accuracy it did not achieve,
and passed on the looser band it had also frozen. **That is exactly what a registered expectation is
for, and burying it would make the freeze worthless.** The gate is the gate; the missed expectation is
a calibration signal about this lab's a-priori error prediction, and it is reported as one.

### 2. Grid refinement converges to a limit ~5.9 GCI-widths AWAY from the exact closed form
On the Roache functional (volume-average `T`):

| | value (K) |
|---|---|
| `f_coarse` L1 | 284.153139038 |
| `f_med` L2 | 284.141801258 |
| `f_fine` L3 | 284.139349004 |
| Richardson limit `f_ex` | 284.138672223 |
| **EXACT closed form** | **284.133655141** |

`GCI_fine` = 0.000298 % = **8.467e-04 K**. But `\|f_ex − exact\|` = **5.017e-03 K** — the grid-converged
limit sits **5.93 × GCI_fine** from the exact answer, and Richardson extrapolation closes only **11.9 %**
of the finest level's 5.694e-03 K gap. **Refinement is not closing this gap**, so roughly six GCI-widths
of the residual deviation is a setup/modelling signature, not discretisation error.

This does **not** overturn the `PASS`: the gate quantity is the *pointwise* normalised max error at the
finest level, which is measured at 1.962e-03 against a frozen 0.01 band, and that band was frozen
before any field existed. But it is the same shape as the VMFL005 finding recorded as `N-AV7` (there,
Richardson moved the answer *further* from the analytic value), and it is the honest reading of a
triple whose uncertainty estimate is much smaller than its distance from truth. **The mechanism is
NOT diagnosed here and is not claimed.** It would need a new registration, graded as its own row
citing this one; the frozen case was not re-run.

### 3. The finest level — the one the gate is read at — is a TIGHT pass on the convergence refusal
The plateau clause (`PREREGISTRATION.md` §7) refuses an unconverged level rather than grading it:
`ptp` over a fixed 500-sample window, normalised by the 17.3318 K viscous-heating rise, must be
`≤ PLATEAU_PTP_REL = 1.0e-06`.

| level | `ptp/scale` | threshold | margin |
|---|---|---|---|
| L1_nr32 | 0.000e+00 | 1.0e-06 | full |
| L2_nr64 | 0.000e+00 | 1.0e-06 | full |
| **L3_nr128** | **9.675e-07** | 1.0e-06 | **96.75 % of the way to refusal — 3.25 % margin** |

L3 passed the refusal clause with 3.25 % to spare, and L3 is the level the gate is read at. Had the
box been marginally noisier the comparator would have **refused** rather than graded, which is the
clause working as designed — but a reader of this row is entitled to know the pass was that close.
Worst final residuals were 9.97e-13 / 1.00e-12 / 7.32e-12, so this is a plateau-flatness margin, not
an iterative-convergence problem.

---

## (A) VERIFICATION OF THE VERDICT — done by this lane, not accepted

### A1. Freeze integrity (`CLAUDE.md` rule 2) — re-hashed independently
All **four** frozen files hash byte-identical on disk, at the freeze commit `7c5158df`, **and** at HEAD.
A freeze check is the one thing never taken on trust, so this was re-derived here rather than relayed:

| file | blob (disk == @7c5158df == @HEAD) |
|---|---|
| `PREREGISTRATION.md` | `215d726716f9a7cea4d82c13ec1c239a84726316` |
| `grade_vmfl033_r2.py` | `8ad8047c5ec830f5a84ef6046d422307a7da3915` |
| `make_blockmeshdict.py` | `7c3d312413279ea894b3e2c7371361b5dad3f44a` |
| `run_vmfl033_r2.sh` | `14b1fe15f5831cfd54bd96bc1744a38778706ac0` |

The launcher recorded `prereg_blob = 215d7267` and `comparator_blob = 8ad8047c` in **all three**
`RUN_RC.txt` and in `launcher.queue.out`'s `FREEZE VERIFIED` line, so the bytes the launcher hashed
are the bytes that are here. Launch HEAD `9f7056d7`, 2026-08-31T16:31:57Z.

### A2. The instrument is not a one-answer instrument
`--selftest` was run under **both** `python3` and `python3 -O`, with `__pycache__` cleared between the
two so the `-O` run could not read the non-`-O` bytecode (the stale-bytecode inversion). Both exit
**rc 0** and print `SELFTEST GREEN`, and the two outputs are **byte-identical**. The selftest prints
**16 named check lines**; the comparator does not emit an "N checks / M failures" counter, so no such
count is quoted here.

Reachability, which is the point of the arm: `PASS`, `GATE FAIL` **and every NOT-A-RESULT cause
(plateau, triple, `GCI_MAX`, `P_MIN`) are all REACHABLE from `decide_verdict`** — verified by the
selftest's own end-to-end arm, so a comparator that can only say `PASS` is excluded.

Also proven in the same arm: the AST guard **fires** on a file containing an `assert`; the plateau
clause **refuses** below the 500-sample floor, **refuses** a null range and **rejects a growing series**
(driven at `ptp/scale = 2.879e-02`); numeric time-dir selection picks `100000` where lexicographic
would misread `9`, and **two names for one time REFUSE**; a UNIFORM field, a count/header mismatch and
a headerless vector are each **REFUSED**; an empty level dir and a level recording `rc = 1` are each
**REFUSED**. Two independent derivation controls also pass: a BVP control showing the temperature
error falling **4.00× per doubling** (2nd order, derivation confirmed) and an **energy balance**
closing to `rel 0.00e+00` (total dissipation 1256.63706 W == net wall outflow 1256.63706 W).

### A3. The four declared design requirements (`PREREGISTRATION.md` §7) — each behaved
1. **`GCI_MAX` ceiling beside the `P_MIN` floor** — both applied in `decide_verdict`. `p_obs` 2.2090
   ≥ 0.05; `GCI_fine` 0.000298 % ≤ 10 %. The §7 a-priori DERIVED estimate was `GCI ~ 5e-4 %`; the
   measured 2.98e-4 % lands within a factor of 1.7 of it, so that prediction was good.
2. **The plant fires at EVERY level** — see A4. Fired at all three, not the finest alone (R1's
   disclosed weakness, and rows #44/#46 fired at L1 only).
3. **NUMERIC time-directory selection with a cardinality refusal** (L-339) — `lexicographic_would_
   have_misread = False` at all three levels, and the refusal itself is driven in the selftest on
   `{100000, 100000.0}`. Time directories are exactly `{0, 100000}` per level, cardinality 2, which
   is what the frozen comparator expects.
4. **No `assert` in the comparator, AST guard proven to fire** — 0 `ast.Assert` nodes, and the guard
   is driven to refusal on injected bytes. The guard runs at **every** invocation, first line of
   `main()`, before `--selftest` is even dispatched.

### A4. Planted-zero control (`CLAUDE.md` rule 3) — FIRED AND PASSED AT ALL THREE LEVELS
`PREREGISTRATION.md` §7 requirement 2 declared level-wide planting as a **design requirement before
compute**, so a single-level plant would have been a departure. Two independent channels per level —
a field plant and a geometry plant — read back through the **production** reader:

| level | field plant | reader saw | geometry ×2: radius | → | required |
|---|---|---|---|---|---|
| L1_nr32 | 1.234e-03 | 0.00123400000001 | 1.01546342 | 2.03092684 | 2.03092684 |
| L2_nr64 | 1.234e-03 | 0.00123400000001 | 1.00759285 | 2.0151857 | 2.0151857 |
| L3_nr128 | 1.234e-03 | 0.00123400000001 | 1.00367241 | 2.00734483 | 2.00734483 |

The comparator plants into **`tempfile.mkdtemp` copies** of each level's real `T` and `C`
(`grade_vmfl033_r2.py:525-556`), never the run's own files, and refuses (`P0`) if the *unplanted* copy
does not read back as itself before any plant is applied. **The run tree was not mutated by grading.**

### A5. Strict completion (`CLAUDE.md` rule 4) — every clause, checked here from the artifacts
R2 is **fixed-iteration**, so rule 4's `last time == endTime` applies unmodified (no
`residualControl`-termination inversion; `PREREGISTRATION.md` §7 states that choice before compute).

| level | `rc` | `^Time =` | `^ExecutionTime` | `^End` | last time | `endTime` | time dirs |
|---|---|---|---|---|---|---|---|
| L1_nr32 | 0 | 100000 | 100000 | 1 | 100000 | 100000 | `{0, 100000}` |
| L2_nr64 | 0 | 100000 | 100000 | 1 | 100000 | 100000 | `{0, 100000}` |
| L3_nr128 | 0 | 100000 | 100000 | 1 | 100000 | 100000 | `{0, 100000}` |

Counts are from **line-anchored** patterns; a bare `Time = ` also matches inside every
`ExecutionTime = ` line and would double the count. Fields present for the `laminar` closure at every
level: `T U p p_rgh C` (recorded by the launcher).

**Age guard**, the clause that dates the run allowed to produce the answer — every field at `endTime`
newer than that level's own `0/T`:

| level | `0/T` | `100000/T` | margin |
|---|---|---|---|
| L1_nr32 | 16:31:57Z | 16:33:33Z | **+96 s** |
| L2_nr64 | 16:33:33Z | 16:35:58Z | **+145 s** |
| L3_nr128 | 16:35:58Z | 16:39:52Z | **+234 s** |

Each margin equals that level's wall time exactly, which is the signature of a clean sequential
launch — `0/T` touched at level start, fields written at level end, nothing reused from an earlier run.

### A6. No stall
`ExecutionTime/ClockTime` = 93.88/96 = **0.9779**, 140.18/145 = **0.9668**, 226.49/234 = **0.9679** —
so 3–4 % of wall went outside the solver's own accounting, consistent with I/O and startup, not
contention. The `COMPUTE_BUDGET_CHARTER` §2 stall rule (a row over 3600 wall s) matches **no** level;
the longest is L3 at 234 s, **15.4× under** the threshold. Gross and cleaned are therefore identical.

---

## (B) TWO DEFECTS FOUND WHILE GRADING, BOTH DISCLOSED RATHER THAN QUIETLY HANDLED

### B1. The frozen comparator has NO JSON mode — the verdict here is cited to the frozen STDOUT
The grading brief for this item required the verdict to be read out of a machine-readable JSON
grading record and never out of stdout. **That is not possible on this frozen comparator, and the
requirement was not met.** Measured, not assumed: `grade_vmfl033_r2.py` contains **zero** occurrences
of `json`, imports only `ast, math, os, re, shutil, sys, tempfile` (`:44`), has **no** `argparse`, **no**
`--out` and **no** `--run-root`; `main()` (`:902-1003`) prints and returns 0. `RUN_ROOT` is hardcoded.

Adding a JSON mode would mean **editing a frozen file after first compute**, which `CLAUDE.md` rule 6
forbids and which rule 2 makes worse — the grading path is fixed at the pre-registration commit.
Fabricating a JSON from a *separate* reader would create an unfrozen second grading path, which is
the thing the freeze exists to prevent.

**Therefore the artifact this record and the register row cite is the one that actually exists:**
`GRADING_STDOUT_2026-08-31T1715Z.txt` in this run root — the complete, unedited output of the frozen
comparator, `rc = 0`. A row must not cite an artifact that is not on disk, so the claim is stated at
the strength the evidence supports and no higher. **The requirement is not waived, it is deferred to
where it can be honoured: the NEXT registration's comparator should emit a machine-readable record,
frozen with it before compute.** Bolting one on after the run is not available.

*(Contrast VMFL038, graded the same day: its comparator DID carry a `--out` JSON mode, so there the
missing artifact could be produced from the frozen path. Here it cannot.)*

### B2. `PREREGISTRATION.md:121` states a FALSE fact about cap enforcement — corrected by addendum, file NOT edited
The frozen text reads: *"Sanaa's runner-side cap enforcement is now ENFORCE (2026-08-31)"*. **It is
not, and it was not.** Two artifacts on disk say the opposite:

- `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3` — **"Status: ADVISORY. INERT. OFF. Not switched
  on, and no agent may switch it on."**
- `scripts/queue_runner.py:14-16` — *"It never kills anything: a cap is a runaway guard that REPORTS
  … and never terminates."*

The claim entered the freeze from the supervisor's own brief, was not independently checked before
the file was frozen, and is now inside a frozen document. **The frozen file is NOT edited** (rule 6):
line 121 still reads `ENFORCE`, struck rather than rewritten, because a frozen document that can be
silently corrected has no evidentiary value. The correction lands as **ADDENDUM 1, 2026-08-31,
v1.0 → v1.1**, appended at the foot, altering **no** gate, threshold, cap or label, and is also carried
on the register row.

The rule-6 assertion **`lines whose number changed above this section: 0` is proven by measurement,
not asserted**: SHA-256 of lines 1–327 is `51c2d3a72d8fd1a9138997fe20958c41863290ab61d10cca259398e
69dd42491` **before** the append, **after** it, **and** in the blob at the freeze commit `7c5158df` —
three readings, one value. The diff is **87 insertions, 0 deletions**.

**Blob-change note, so nobody is surprised later:** appending the addendum moves the file's blob from
the frozen `215d726716f9a7cea4d82c13ec1c239a84726316` to `a18e544917486e1e766a917814d5af4cef449908`.
**`215d7267` remains the blob that RAN** — it is what all three `RUN_RC.txt` and `launcher.queue.out`
recorded, and it is the blob every provenance claim in this record cites. A future re-launch of
`run_vmfl033_r2.sh` would now fail its own freeze check against the recorded blob, which is the
correct behaviour and not a defect: this case is graded and closed, and a re-run would be a new
registration, not a repeat of this one.

**NOTHING WAS EVER UNPROTECTED, and this is measured rather than asserted.** The operative guard is
not the queue runner at all — it is the **launcher's own per-level `timeout`**:
`run_vmfl033_r2.sh:130` computes `TIMEOUT_S = CAP*60/RANKS` and `:133` wraps the solver as
`timeout ${TIMEOUT_S}s buoyantSimpleFoam`. Confirmed **live in this run**: `launcher.queue.out` records
`cap=8 core-min timeout=480s` for L1 — and 8 core-min × 60 ÷ 1 rank **is** 480 s — with 720 s at L2's
12 core-min cap and 1200 s at L3's 20. So the cap was enforced in the executable path throughout, by
a mechanism that is real, per-level, and independent of the inert runner clause. The consequence of
the false sentence is confined to its stated *rationale for cap sizing*; the caps themselves, and the
guard that enforced them, are unaffected.

---

## (C) COST CALIBRATION (`CLAUDE.md` rule 12)

| | core-min |
|---|---|
| **EXTRAPOLATED** (`PREREGISTRATION.md` §2 line 12) | **~10.3** — 2.08 / 3.17 / 5.08 |
| **MEASURED** | **7.9167** — L1 **1.6000** (96 wall s) / L2 **2.4167** (145 s) / L3 **3.9000** (234 s) |
| **ratio actual/predicted** | **0.769** |

MEASURED figures are the launcher's own `core_min` fields in the three `RUN_RC.txt`, corroborated
line-for-line by `launcher.queue.out`. `ranks = 1`, so core-min = wall-min. Gross == cleaned (A6).
**Caps: per-level, not a shared drawdown** — 8 / 12 / 20 core-min, used **20.0 % / 20.1 % / 19.5 %**.
No cap was crossed, so `CAP CROSSED` was never printed and the rule-12 stop never armed.

**$0.006769 DERIVED, NOT MEASURED** — 7.9167 core-min = 0.131945 core-h × **$0.0513/core-h**
(c7a.4xlarge, owner-stated 2026-08-21/22, **REPORTED-BY-OWNER**; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). CPU only, under the $25 pre-authorisation.

**GAP ATTRIBUTION — a clean, mechanistic over-prediction, and the mechanism is reusable.** The §2
line-12 estimate took R1's MEASURED per-level times at 20 000 iterations and multiplied the **whole**
level time by 5. But a level's time is `F + k·iterations`, where `F` is fixed setup — `blockMesh`,
`checkMesh`, `writeCellCentres`, the field write — which does **not** scale with `endTime`. Solving
the two-point model from R1 and R2:

| level | R1 @20 000 | R2 @100 000 | fitted `k` (s/iter) | fitted fixed `F` | `F` as % of R1 level time |
|---|---|---|---|---|---|
| L1 | 25 s | 96 s | 8.875e-04 | 7.25 s | **29.0 %** |
| L2 | 38 s | 145 s | 1.3375e-03 | 11.25 s | **29.6 %** |
| L3 | 61 s | 234 s | 2.1625e-03 | 17.75 s | **29.1 %** |

The fixed fraction is **~29 % at every level**, and that single number explains the whole miss: the
correct multiplier is `0.29 + 5×0.71 = 3.84`, not 5.0, and `3.84/5.0 = 0.768` — which **is** the measured
0.769 ratio, to three figures, at all three levels independently (0.7692 / 0.7624 / 0.7677). The
extrapolation was not noisy; it was systematically wrong by exactly the fixed-overhead fraction.

**ACTIONABLE FOR THE NEXT ESTIMATE: when extrapolating a measured run to a longer `endTime`, split
the baseline into fixed setup and iteration-proportional parts and scale ONLY the latter.** Scaling
the whole level time over-predicts by the fixed fraction, ~29 % on this family. This is the mirror
image of VMFL038's miss the same day, which under-predicted by scaling with **cells** a run that
terminated on a fixed residual floor — both are the same error: extrapolating along the wrong variable.

**CONTENTION: named separately, negligible** — `ExecutionTime/ClockTime` 0.9779 / 0.9668 / 0.9679 (A6).
**WASTE: ZERO, named separately and NEVER absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER` §6).
Three levels launched, three completed `rc = 0`; no restart, no re-mesh, no abandoned or repeated
level, no smoke run in the graded path, no cap crossing. Every core-minute bought a level that appears
in the graded triple. **Note that R1's spend is NOT counted here** — R1 is its own closed row (#21);
this row is R2's cost against R2's own registered estimate.

---

## ARTIFACTS — committed vs on disk only

This team's standing ruling (Sanaa 2026-08-27 §1): solver logs and time directories stay OUT of git,
cited by path with sizes and mtimes; the small evidence set is committed by explicit path, no glob.

**COMMITTED (explicit paths):** `RESULTS.md` (this file), `GRADING_STDOUT_2026-08-31T1715Z.txt`,
`LAUNCH_RECORD.txt`, `STATUS.VMFL033-R2`, `launcher.queue.out`,
`L{1_nr32,2_nr64,3_nr128}/RUN_RC.txt`, `L{1_nr32,2_nr64,3_nr128}/MESH_BIRTH_CERTIFICATE.txt`.

**ON DISK ONLY, deliberately not in git:** `L*/log.buoyantSimpleFoam`, `L*/log.blockMesh`,
`L*/log.checkMesh`, `L*/log.writeCellCentres*`, the time directories `L*/0` and `L*/100000`, and
`L*/postProcessing/`.

Every number in this record cites an artifact still on disk. The comparator mutated nothing — it
plants into `tempfile` copies of the solver bytes, never the run's own files.

## Freeze / grading provenance
- Freeze commit **`7c5158df`**; prereg blob `215d726716f9a7cea4d82c13ec1c239a84726316`; comparator blob
  `8ad8047c5ec830f5a84ef6046d422307a7da3915`; `make_blockmeshdict.py` `7c3d3124…`; launcher
  `run_vmfl033_r2.sh` `14b1fe15…`. All four byte-identical on disk, @`7c5158df` and @HEAD.
- Launch HEAD `9f7056d71c8c8afeb0262e44e2a1e9d24332d9f3`, 2026-08-31T16:31:57Z; all levels finished
  by 16:39:52Z; graded 2026-08-31T17:15Z.
- Selftest `SELFTEST GREEN`, rc 0, byte-identical under `python3` and `python3 -O`.
- Verdict cited to `GRADING_STDOUT_2026-08-31T1715Z.txt` — see §B1 for why no JSON exists.
