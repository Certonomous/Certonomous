# DRAFT REGISTER ROW — VMFL046-R9-REGRADE

**DRAFT, NOT COMMITTED, NOT IN THE REGISTER.** Written by an `ansys-lane-opus`
2026-09-10. The supervisor commits it after reading the measurement-script diff
personally (`SUPERVISION_CHARTER` §3 check-1).

**⚠ THE ROW NUMBER BELOW IS PROVISIONAL AND MUST BE RE-DERIVED AT COMMIT, IN THE SAME
SHELL INVOCATION, FROM THE MAXIMUM EXISTING NUMBER — NEVER A COUNT (rule 11).** At
drafting time the maximum existing `## Row #` in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` is **74**, so the draft
reads **#75**. The `.tsv` is a derived view and lags; it is never the source of the
next number.

---

## Row #75 — VMFL046-R9-REGRADE — Supersonic Flow with a Normal Shock in a Converging-Diverging Nozzle (VM2026R1 p. 155) — **`NOT A RESULT`**

Graded **2026-09-10T15:46:15Z → 15:46:39Z** by an `ansys-verification` lane against the
**frozen** pre-registration `cases/ansys_verification/VMFL046-R9-REGRADE/PREREGISTRATION.md`
(freeze commit **`faf4ccfd`**, prereg blob `2634c72e2d1af373320e64b8c642b7b49ca82be9`).

Comparator **`grade_vmfl046_r8_repaired.py`**, grading-path blob
**`660464f94a2afcbf73c5787e992887233b2b3419`** — the post-fold blob the registration
pins. `git hash-object` on disk **==** the pinned blob **==** the blob committed at
`faf4ccfd`, **re-verified in the same shell invocation that launched the grade** (rule 2:
the frozen file *is* the file that ran). The repair's provenance blob
`c7c00bbf1fa627ef4cbdda9c81724b0cd62008e5` (pre-fold, committed at `e6ad3459`) is a
**different object** and is recorded as such (`§2d.4.3`).

`grade_rc = 1` with a **printed limb verdict and no traceback**, so this is **not** the
pre-registered INSTRUMENT FAULT class. Per the pre-registered outcome map, rc 1 resolves
to **`NOT A RESULT`** because the triple is not `CONVERGING` and no level plateaued.

### ONE RUN, TWO READINGS — ROW #71 IS UNCHANGED

> **Row #71 stays `NOT A RESULT`. It is not amended, not relabelled, not superseded, not
> struck, and not one byte of it is rewritten.** Row #71 is a true record of what the
> **frozen** instrument did to this data: it refused, at its own `:1103`, because three
> `^`-anchored regexes could not read a legal brace-inline `constant/fvOptions`. That
> remains true. This row is a **second, differently-instrumented reading of the SAME
> solve.**
>
> **The 590.7413 core-min of the underlying VMFL046-R8 solve is NOT re-charged here and
> must never be counted twice. This pair is NOT two independent confirmations.**

This side-by-side publication is the `§2d.4` before/after discharge of the R9
registration §1(3), landed as a **register fact** rather than a claim:

| reading | instrument | blob | rc | outcome |
|---|---|---|---|---|
| **BEFORE** (Row #71) | frozen `grade_vmfl046_r8.py` | `f89114bb…` | **2** (REFUSED at L1, LIMB (a)) | `NOT A RESULT` — zero gate quantities computed |
| **AFTER** (this row) | repaired `grade_vmfl046_r8_repaired.py` | `660464f9…` | **1** (gate reached and resolved) | `NOT A RESULT` — plateau failure + `OSCILLATORY` triple |

### THE STRICT COMPLETION RULE — VERIFIED INDEPENDENTLY, AND IT HOLDS AT ALL THREE LEVELS

Checked by the lane **before** the comparator ran, with its own reader, not by relaying
the comparator's word. `adjustTimeStep yes`, `deltaT 1e-08`, `maxDeltaT 1e-04`, so rule 4
clause 5 takes its **adaptive-`deltaT`** form (`n_exec == steps written`, Sanaa 2026-09-09)
— `round(endTime/deltaT)` = 8 000 000 is not the applicable arithmetic here, and the
comparator's declared N2 departure implements the stronger four-limb replacement.

| level | rc | `End` | `FOAM FATAL` | last `Time` | `endTime` | n(`Time =`) | n(`ExecutionTime`) | equal | strictly increasing | last time dir | fields at `0.08` | age guard vs own `0/T` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 (3 200 cells) | **0** | yes | absent | **0.08** | 0.08 | 30 885 | 30 885 | **yes** | **yes** | `0.08` | `T U p phi rho uniform` | **OK** — `0/T` 18:31:31Z, fields 18:38:55Z |
| L2 (12 800 cells) | **0** | yes | absent | **0.08** | 0.08 | 64 105 | 64 105 | **yes** | **yes** | `0.08` | `T U p phi rho uniform` | **OK** — `0/T` 18:38:55Z, fields 19:34:43Z |
| L3 (51 200 cells) | **0** | yes | absent | **0.08** | 0.08 | 125 473 | 125 473 | **yes** | **yes** | `0.08` | `T U p phi rho uniform` | **OK** — `0/T` 19:34:43Z, fields 2026-09-10T04:24:43Z |

`n_min = floor(endTime/maxDeltaT) = 800` at every level, far below the step counts, so the
"cannot have got there in fewer steps" limb holds. **The solve is not what failed, at any
level.** Row #71 said so of L1 alone; this row says so of all three, because L2's and L3's
`check_completion` had never run before this grade.

### THE PLANTED-ZERO CONTROL (rule 3) — ALL FIVE FIRED AGAINST REAL DATA, FOR THE FIRST TIME

Every control plants a known perturbation into a **scratch copy**, reads it back **from
disk**, and **refuses (exit 2)** if the reader cannot see it. Plants:
`PLANT_DX = 1.000e-02 m`, `PLANT_DX_SMALL = 6.250e-04 m` (= `DELTA_X`, the
quantum-discrimination plant), `PLANT_K_T = 1.0e-3` relative into `T`.

| control | what it protects | L1 | L2 | L3 | tolerance |
|---|---|---|---|---|---|
| **A** | the `x_shock` reader recovers a known displacement | err 6.924e-05 | err 2.415e-04 | err 6.601e-05 | 2.500e-03 m |
| **B** | the plateau **reducer** sees a plant into the window's **maximum** | ptp 1.0094e-01 → 1.1094e-01 | 4.1806e-02 → 5.1791e-02 | 6.0972e-01 → 6.1967e-01 | recovers +1.000e-02 m |
| **C1** | translation invariance: inert arm must not move, live arm must | inert 0.000e+00, live +1.000000e-02 | same | same | — |
| **C2** | per-sample independent read-back | worst 7.390e-04 | worst 2.415e-04 | worst 2.133e-04 | 2.500e-03 m |
| **D** | the `T`-field reader | err 4.989e-08 | err 4.989e-08 | err 4.999e-08 | 1e-6 relative |

**The refusal path is exercised, not merely present.** The comparator's `--selftest`, run
by the lane at the pinned blob, reports **90 ok / 0 FAILED, rc 0**, and among the green
arms are `A refuses a dead reader`, `A refuses the node-snapping reader at plant = DELTA_X`,
`B refuses a dead reader`, `C1 refuses a DEAD reducer (constant)`,
`C1 refuses a NON-TRANSLATION-INVARIANT reducer`, `C2 refuses a dead reader (constant)`,
`C2 refuses a half-scale (biased) reader`,
`C2 refuses R1's node-snapping reader at plant = DELTA_X`, and
`D refuses a T internalField that is not a nonuniform scalar list` — each reported
`-> REFUSES(2)`. **A reader shown able to see a non-zero, and shown to refuse when it
cannot.**

**The W1 read audit also passed at all three levels:** exactly **33 distinct** centreline
samples opened inside each level's run root, all inside the registered window
`t ∈ (0.064, 0.080]`, which holds 33 of the 160 written samples. The 19 excluded paths per
level are the plants' own `/tmp` scratch copies, excluded under `§2aw(c)` as **not run
data** and enumerated by name in the log rather than filtered silently.

### THE GATE, AND WHY THE VALUE DOES NOT DECIDE IT

Gate quantity **`x_shock`**; reference **1.250 m** (F. M. White, quasi-1D inviscid); band
**±5 %** = **[1.1875, 1.3125] m**; reader = interpolating last downward Mach = 1 crossing;
plateau `DELTA_X = 6.250e-04 m`. **Every one of these is carried byte-identical from R8.
This registration moved no gate object: 0 gates, 0 bands, 0 thresholds, 0 caps, 0 labels.**

| level | `x_shock` (window-A mean, THE LEVEL VALUE) | deviation vs 1.250 m | inside band? | `x_shock` final sample | plateau P1 / P2 / P3 | plateau state |
|---|---|---|---|---|---|---|
| **L1** | **1.260863658 m** | **+0.8691 %** | *would be inside* | 1.303061746 m | 1.0094e-01 / 1.2522e-01 / 2.0919e-02 | **NOT PLATEAUED** — worst **200.3×** `DELTA_X` |
| **L2** | **1.181161685 m** | **−5.5071 %** | outside | 1.156016742 m | 4.1806e-02 / 4.2993e-02 / 1.6613e-02 | **NOT PLATEAUED** — worst **68.8×** `DELTA_X` |
| **L3** | **1.369600526 m** | **+9.5680 %** | outside | 1.414690237 m | 6.0972e-01 / 3.0216e-01 / 9.2269e-02 | **NOT PLATEAUED** — worst **975.5×** `DELTA_X` |

### ROACHE TRIPLE GATING (rule 5) — `OSCILLATORY`, SO `NOT A RESULT` WHATEVER THE VALUE

```
triple on x_shock: L1=1.260864  L2=1.181162  L3=1.369601   state=OSCILLATORY  R=-2.364  p=n/a  GCI=n/a
```

r = 2 triple, L1 (3 200) → L2 (12 800) → L3 (51 200) cells.
**R = (f₃−f₂)/(f₂−f₁) = (+0.188439)/(−0.079702) = −2.364.** R < 0 is oscillatory, and
|R| > 1 means the oscillation **grows** under refinement — the sequence does not merely
wobble, it wobbles wider.

- **Observed order p: `n/a`.** Not computable on a non-monotone triple, and not fabricated.
- **GCI: `n/a`, DELIBERATELY NOT QUOTED.** Rule 5's own sentence: *never quote a GCI when
  the three values are not monotone.* `Fs = 1.25` is the registered factor and is **not
  applied** here. **A GCI printed on this triple would be a number with no referent.**

**Two independent, sufficient grounds for `NOT A RESULT`, in rule 5's own order:**

1. **Step 1 — no level plateaued.** All three fail the pre-registered plateau at
   `endTime = 0.080 s`. This alone is `NOT A RESULT` *before any band comparison is
   permitted*.
2. **Step 2 — the triple is `OSCILLATORY`.** `NOT A RESULT` whatever the value, with the
   value, both triples and the orders printed beside it (above, and in the log).

**⚠ THE VALUE THAT LOOKS LIKE SUCCESS IS THE ONE LEAST ENTITLED TO IT.** L1 at **+0.87 %**
sits comfortably inside the ±5 % band and is the **coarsest** level of the three. This is
`ANSYS_VERIFICATION_CHARTER` §24.6's lesson landing on this case a second time — *"an
agreement obtained at the coarsest level is the least trustworthy number in the set, and it
is the one that looks most like success."* **L1's +0.87 % is not a partial pass, not a
GATE REACHED at L1, and not evidence of anything. Rule 5 forbids reading it as any of
those, and the gate can only turn a would-be verdict INTO `NOT A RESULT`, never the
reverse.**

### THE OFF-GATE LIMBS PASSED, AND THAT IS WORTH RECORDING

Neither had ever touched this run's data before — the frozen reader refused at LIMB (a),
upstream of both.

- **LIMB (b) — the `fvOptions limitTemperature [150, 2000] K` clamp is NON-BINDING.** `T`
  over the graded window spans **[229.5, 634.39] K** (L1), **[227.74, 641.64] K** (L2),
  **[223.57, 666.53] K** (L3) — interior of the clamp at every level, with no approach to
  either bound. **The clamp the frozen reader could not parse turns out never to have
  bitten.**
- **LIMB (c) — washout / shock-stand guard.** `x_shock` stands in **[1.1812, 1.3176]**,
  **[1.1544, 1.1974]**, **[1.0855, 1.6953]** m, interior of exit 1.998 m at every level. No
  washout.
- **Independent corroboration of §1's Instrument A, re-measured by the lane rather than
  relayed:** across the three solver logs there are **1 322 778** `limitTemperature=limitT`
  report lines (L1 185 310 + L2 384 630 + L3 752 838), of which **0** carry bounds other
  than `Tmin=150` / `Tmax=2000` and **0** carry `LimitedCells ≠ 0`. The clamp was present,
  active, at exactly the frozen bounds, and never limited a single cell — so the frozen
  reader's refusal was the reader's fault and not the case's, established by an instrument
  inside the solver that grades nothing.

### `PASS` IS UNREACHABLE AND THIS ROW DOES NOT APPROACH IT

Registered pre-run on two independent grounds, and neither is affected by the outcome:
(1) the comparator contains **no code path that prints `PASS`**; (2)
`ANSYS_VERIFICATION_CHARTER` §24.4 re-caps VMFL046 at **`GATE REACHED`** — §23.3's
enumerated-channel model-form bound (`dx_shock/x ≤ 0.63 %`) is **UNVALIDATED** and was
**refuted by the run by 20.5×**, and the reference is **inviscid quasi-1D analytical**
against a **viscous 2-D Navier-Stokes** solve, so model-sameness is DIFFERENT and the cap
stands. **No `PASS` may be recorded for VMFL046 under any outcome, and this row records
none.**

### THE `§2d.1` DISCLOSURE — ONE CONDITION, NOT FOUR

Carried forward from the frozen registration §1 verbatim in substance, because a row that
drops it is a row that overclaims:

- **(1) demonstrable error** — HOLDS, machine-provable in a minute: `:1097`'s
  `type\s+limitTemperature` is unanchored and matches; `:1099`/`:1100`'s `^\s*min` /
  `^\s*max` under `re.M` cannot match a key preceded by `selectionMode all; ` on the same
  physical line. Carries no discretion.
- **(2) independent, grades-nothing instrument** — HOLDS. **This is the protection.**
  Instrument A (the solver's own `limitTemperature` reporting, 1 322 778 lines,
  re-measured above) and Instrument B (`§2d.5`, the frozen R8 registration's own text)
  discharge **ONE** condition between them, not two.
- **(3) disclosure and quantification** — DISCHARGED, and what it quantifies is **a regex
  returning `None` instead of `150`**, not a value that moved. `§2d.3.3`'s absence shortcut
  is **expressly declined**: R8's solves completed, so under `§2d.4` conditions (3) and (4)
  bite in full.
- **(4) pre-repair values beside the published ones** — **SATISFIED VACUOUSLY AND WORTH
  NOTHING.** There were no published values: `GRADING_VMFL046_R8.log` is 15 lines carrying
  the gate's *definition* and not one measured value.

> **THIS REPAIR IS PROTECTED BY ONE CONDITION PLUS THE FREEZE-BEFORE-RUN ORDERING, NOT BY
> FOUR CONDITIONS.** Standing where condition (4) normally stands is the ordering alone:
> the repaired comparator was committed at `e6ad3459` before it was ever run; the
> registration was frozen at `faf4ccfd` before its first run; **the first invocation of the
> repaired reader against the real run root is the one this row reports**, at
> 2026-09-10T15:46:15Z, and `GRADING_VMFL046_R9.{log,json}` were verified **absent**
> immediately before it. **Do not read this row as four-condition support.**

### COST (rule 12)

- **Solver compute for this act: 0 core-min. $0.00.** No mesh, no solver, no field
  written. Nothing in the run root was modified before the grade — verified by `find
  -newermt`, zero files touched since the 04:25:31Z R8 grade.
- **Grading act: 0.4000 core-min MEASURED** (24 s wall × 1 rank ÷ 60), against a
  pre-registered point estimate of **~3 core-min** and a **cap of 30 core-min**. **No
  overrun.** Dollars **DERIVED, NOT MEASURED**: **$0.000342** at c7a.4xlarge
  $0.0513/core-h, owner-stated / reported-by-owner — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER` §5).
- **The underlying solve's 590.7413 core-min is recorded at Row #71 and is NOT re-charged
  here.** Calibration for both the solve and this grading act is filed in
  `docs/COST_CALIBRATION.md`.

### WHAT THIS ROW REFUSES TO CLAIM

| | |
|---|---|
| that the run is now graded as sound physics | **NO.** The physics limbs ran and the run **failed** them: no level plateaued and the triple oscillates. The repair fixed a *reader*, and the reader then delivered a negative verdict. |
| that L1's +0.87 % is a partial pass | **NO.** Rule 5 forbids it, and §24.6 names it as the least trustworthy number in the set. |
| that the repair recovered the 590.74 core-min | **NO.** It recovered a **reading**, not an answer. Row #71's waste figure stands unerased. |
| that this and Row #71 are two confirmations | **NO. One run, two readings.** |
| a GCI or an observed order | **NEITHER EXISTS.** The triple is non-monotone; both are printed `n/a` and neither is estimated. |
| four-condition `§2d.1` support | **NO — one condition plus the freeze-before-run ordering.** |
| a `PASS` | **UNREACHABLE for this case on two independent grounds (§24.4).** |
| that the underlying solve was mis-run | **NO.** rc 0, `End`, `endTime` and the age guard hold at all three levels, independently verified. **The run is clean and the answer is still negative** — which is what a documented failure looks like (`VERIFICATION_CHARTER` §8). |

### THE FINDING THIS ROW CARRIES

**The instrument defect of Row #71 cost the lab a reading, not an answer.** The same
590.7413 core-min would have graded **`NOT A RESULT`** even had the frozen reader parsed
its own case file — on the plateau limb at L1, before the triple was ever assembled. That
is worth saying plainly in both directions: it does **not** excuse the defect (a frozen
comparator that cannot parse its own frozen case is the `§38.1` class and the fix was
owed), and it does **not** mean the re-grade was wasted (the lab now knows *why* the run is
not gradeable — an unsettled shock at `endTime = 0.080 s` at every level — which is a
physics finding the refusal was hiding).

**The actionable consequence for a successor rung: `endTime = 0.080 s` is too short.** The
plateau misses by 68.8×–975.5× of `DELTA_X`, and the shock at L3 is still moving downstream
at the final sample (window-A mean 1.3696 m, final sample 1.4147 m). This is a
**registration-design finding**, not a gate that may be widened here — and it is a matter
for a new pre-registration, not an addendum to this one.

### Provenance — every number above cites an artifact still on disk

| object | path / value |
|---|---|
| frozen pre-registration | `cases/ansys_verification/VMFL046-R9-REGRADE/PREREGISTRATION.md`, blob `2634c72e2d1af373320e64b8c642b7b49ca82be9`, freeze commit **`faf4ccfd`** |
| grading path (the file that ran) | `cases/ansys_verification/VMFL046-R9-REGRADE/grade_vmfl046_r8_repaired.py`, blob **`660464f94a2afcbf73c5787e992887233b2b3419`**, disk == pin == committed, re-verified in the launching shell |
| repair provenance (a DIFFERENT object) | same path, pre-fold blob `c7c00bbf1fa627ef4cbdda9c81724b0cd62008e5`, committed `e6ad3459` |
| frozen R8 comparator, UNTOUCHED (rule 6) | `cases/ansys_verification/VMFL046-R8/grade_vmfl046_r8.py`, blob `f89114bb6ff81f683c6c6718460040cab305a8ce` — re-hashed, unchanged |
| case input the frozen reader could not parse | `cases/ansys_verification/VMFL046-R8/case/constant/fvOptions`, blob `cc81891fd7445e2777a245e16baf0c9b829ec299` |
| **AFTER** grading log (all limb prints, 108 lines) | `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R9.log` |
| **AFTER** grading json | `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R9.json` |
| **BEFORE** grading log/json (Row #71, not overwritten) | `.../VMFL046-R8/GRADING_VMFL046_R8.log` (15 lines), `.../GRADING_VMFL046_R8.json` (`grade_rc 2`) |
| per-level solver logs, rc, fields | `.../VMFL046-R8/{L1,L2,L3}/log.rhoPimpleFoam`, `.../RUN_RC`, `.../0.08/{T,U,p,phi,rho}` |
| per-level clocks | `.../{L1,L2,L3}/system/controlDict` (`endTime 0.08`, `deltaT 1e-08`, `maxDeltaT 1e-04`, `adjustTimeStep yes`) |
| cell counts | `.../{L1,L2,L3}/log.blockMesh` (`nCells: 3200 / 12800 / 51200`) |
| autograder record of the BEFORE reading | `.../VMFL046-R8/AUTOGRADE_WATCH_STATE.txt` |
| manual | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf` p. 155, title-page verified under rule 15 at the R1 registration and carried forward |
