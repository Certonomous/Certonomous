# F25-DUCT3D — fully developed laminar flow in a SQUARE DUCT, a GENUINE 3-D ladder (`simpleFoam`/SIMPLEC, streamwise cyclic, fixed body force, 4 ranks, r = 2 in x, y AND z) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F25_DUCT3D_PREREGISTRATION.md`
frozen at **`12def6b59d624816fd25f8cef68ff96a4982e8a8`** (v1.2). Two amendments,
**both pre-first-compute and both stating the condition and how it was checked**
(§ AMENDMENT 1, 2026-08-26T22:56:52Z, run root `test -e` **ABSENT**; § AMENDMENT 2,
2026-08-27T17:00:07Z, run root **ABSENT**, zero core-minutes, no `LAUNCHED` line).
Amendment 1 moved the **cost estimate and the cap only**; Amendment 2 moved the
**pre-spend projector only** and left the cap at 2,000. Neither moved a gate, a
band, a label, the ladder, the iterative floor or any case dictionary.
**Instrument-check** (`CASE_SELECTION_CHARTER.md` §3, labelled at registration):
counts toward no challenge column. Capability-grid cell **068c2bf0 — 3D · steady ·
incompressible**, the cell whose recorded gap was *"never produced a CONVERGING 3D
triple"*.

Levels launched by the queue runner and completed 2026-08-28T04:53:53Z →
07:00:07Z with no agent attached. Graded at **zero new compute** by the frozen
comparator, run exactly as the launcher printed it, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F25_DUCT3D/grade_f25.py --prereg-commit=12def6b59d624816fd25f8cef68ff96a4982e8a8`
Record: `verification/runs/F25_DUCT3D_runs/F25_GRADED.json` (the grader's default
output path; **this grader writes no `.out` file and none exists** — stated rather
than implied). Gated by `scripts/roache_triple.py::grade_ladder`, **one call node**
(AST census in the JSON: call node at line 894, text matcher driven both ways at
lines 530 and 894; 0 `assert` nodes across 4 files, planted assert seen).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F25-1 `E2_normalised_profile` | **7.421509523151607e−04** | [2.473836488844787e−04, 2.226452839960308e−03] | **CONVERGING** (dim 3, r21 = r32 = 2.000, monotone) | **1.9528825654732214** | 129.3280 % = **9.598087474857314e−04 absolute** | **PASS** |
| G-F25-2 `f_Re` | **56.85473707295265** | [56.74759613155525, 57.069018946693966], exact series 56.90830753912461 | **CONVERGING** (dim 3, r21 = r32 = 2.000, monotone) | **1.9697674377136016** | **0.12039783335840937 %** = 6.845187159745533e−02 absolute | **PASS** |

Level values (from `<level>/processor{0,1,2,3}/4000/U`, read by the frozen reader
— **decomposed, NEVER reconstructed**):

| level | cells | h | E2n | f·Re |
|---|---|---|---|---|
| coarse (128 × 16 × 16) | 32,768 | 0.0625 | 1.1483027320511749e−02 | 56.069277669592566 |
| medium (256 × 32 × 32) | 262,144 | 0.03125 | 2.9470028437881992e−03 | 56.69499506311901 |
| fine (512 × 64 × 64) | 2,097,152 | 0.015625 | 7.421509523151607e−04 | 56.85473707295265 |

**The strongest single line in this record: `f·Re` Richardson-extrapolates to
56.90949857023062 against the exact series 56.90830753912461 — agreement to
1.19e−03 absolute, 2.09e−05 relative.** The three grid levels, extrapolated by the
frozen classifier at the observed order 1.9698, recover the closed-form series
value of the duct's friction-factor product to five significant figures. That is
the ladder doing the thing a ladder is for.

**Read the E2n GCI as the ABSOLUTE figure, not the percentage.** 129.3280 % is the
**relative** form on an error norm whose exact limit is zero: the grader forms
GCI_pct as GCI_abs ÷ the fine value, and the fine value *is* the discretisation
error, so the percentage divides a bound on the error-of-the-error by the error
itself. The row's registered reference is **0.0** and its Richardson extrapolant is
**−2.5696045673424535e−05** — essentially zero, and negative. **The figure that
carries meaning is GCI_abs = 9.598087474857314e−04**, which sits comfortably inside
the registered band. Both are printed exactly as the grader printed them. The same
reading was recorded for the same reason at F17 (`F17_KV40_RESULTS.md` §1).

**Registered prediction (prereg §4/§5) — MET on both rows.** The registration's own
L-345 control fixed, at registration and through the grader's own classifier, that
the model's triples read **CONVERGING at orders 1.953 (E2n) and 1.970 (f·Re)** and
refused any other state; the run's measured triples read **CONVERGING at 1.9529 and
1.9698** — the model's orders to four decimal places on E2n and to four on f·Re.
Both fine values fall inside their bands.

**A note on band precision, stated rather than glossed.** The pre-registration
prints the bands in rounded form (`:161` `[2.473836489e−04, 2.226452840e−03]`;
`:166` `56.908307539 ± 3 × 5.357047e−02 = [56.747596130, 57.069018948]`); the
grader recomputes the same formula from the full-precision reference and predicted
error. The two agree to **2e−14** on G-F25-1 and to **2e−09** on G-F25-2 — orders
below any margin either verdict turns on. `BAND_FACTOR = 3`, one declared parameter
(`:124`), declared at registration and not revisable.

## 2. RULE 5, LIMB BY LIMB — AND THE ONE PLACE THE GATE DOES NOT READ ALL CHANNELS THE SAME WAY

### 2.1 Iterative convergence — Ux is gated; Uy, Uz and p are PRINTED AND EXCLUDED

`iterative_convergence` reads **CONVERGED at all three levels on both rows**, and
the basis must be stated plainly because it is not symmetric across the four
channels:

- **Gated:** the initial residual of **Ux**, the driven component, censused over
  **every iteration of the 1,200-iteration window**. `n_Ux_above_tol` = **0** at
  every level, against `UX_RES_TOL = 1e-08` **derived from the predicted fine-level
  error under L-346** (control `PZ-F25-L346`: budget 7.421509466534362e−05 =
  0.1 × the predicted fine E2n; ratio used 0.1617). Worst Ux initial residual:
  **2.43954605726e−15 / 3.23739042104e−14 / 6.86361903374e−13** (coarse / medium /
  fine) — four to seven orders under the floor.
- **PRINTED AND EXCLUDED by the freeze (N-AV8, vanishing channels):** the initial
  residuals of **Uy, Uz and p**, which read **O(1)** at every level — worst Uy
  0.670771491006 / 0.596701317409 / 0.571019668974, Uz 0.670020950598 /
  0.598400958977 / 0.570526724228, p 0.219769141807 / 0.145437342603 /
  0.160073582518. These are not evidence of anything failing: the exact solution
  has v = w = 0 and ∂/∂x = 0, so OpenFOAM's normalisation for those equations
  divides by a vanishing scale and the printed number is meaningless. The
  registration declared them out of the gate **before compute**, and the JSON
  carries them in `levels_detail.iterative_detail.ungated_printed` beside a
  `ungated_channels_note` saying so.
- **In their place the transverse components are checked in the FIELD at endTime**,
  against `transverse_field_floor = 2.0959500008590678e-10` (= u_max × 1e−10, u_max
  = 2.0959500008590677 from the exact series). Measured: **max|Uy| 2.11297173791e−15
  / 1.79809539121e−14 / 9.1437650888e−13** and **max|Uz| 2.07224698017e−15 /
  1.79603011482e−14 / 9.14368060836e−13**. All six sit two to five orders below the
  floor: the solver held the flow exactly axial to machine precision.

**A reader is entitled to know this, so it is said once and without hedging: the
iterative limb of this gate reads one residual channel and one field channel, not
four residual channels.** That asymmetry is registered, it is justified by the
physics of the case, and it is the honest reading of a case whose transverse
equations have no scale to normalise against. The x-uniformity diagnostic
(`x_nonuniformity` = **0.0** at every level) is likewise printed and not gated.

### 2.2 Plateau — PLATEAUED on all six counts

Class C on the graded quantity itself: 40 checkpoints 100 iterations apart, window
12 = 1,200 iterations, span 1,100, trend tolerance 2e−04 relative drift,
variance-ratio band [0.2, 5.0].

| level | E2n drift over window | E2n state | f·Re drift over window | f·Re state | variance ratio (E2n / f·Re) |
|---|---|---|---|---|---|
| coarse | 9.201380853101333e−17 | PLATEAUED | 6.796281251179688e−17 | PLATEAUED | 1.0 / 1.0 |
| medium | 4.322093450581086e−11 | PLATEAUED | 1.3233543824313921e−12 | PLATEAUED | 1.0000000000000617 / 0.9999999843807068 |
| fine | 6.225474923664013e−09 | PLATEAUED | 4.234964388558985e−11 | PLATEAUED | 0.9999999999673149 / 0.9999910062073444 |

Margins of **four to seven orders under the 2e−04 tolerance** on every one of the
six counts. Both graded quantities had stopped moving long before iteration 4,000.
Contrast F17b, where the same instrument on the same case family refused two rows
because the fine level's E2 was still drifting 13.5 % of itself over the window
(`F17b_KV40_EXT_RESULTS.md` §1) — the instrument is the same and it says yes here.

### 2.3 Triples, then bands

Both triples **CONVERGING**, `monotone` true, dim 3, `r21 = r32 = 2.0` exactly,
`ratio_gap` 0.0, form `equal`. Limb (3) is therefore reached, both fine values are
inside their registered bands, and both rows are **PASS**.

## 3. CONTROLS — 12 in the graded path, plus one on-disk plant per gate; ALL PASSED

**Planted-zero (rule 3), into the REAL decomposed artefacts through the REAL
reader.** The plant drives copies of
`fine/processor{0,1,2,3}/4000/U` made in a tempdir (`grade_f25.py:248-258`,
`_planted_copies`), so **nothing under the run root is written**:

- **G-F25-1** — planted **7.257759428297964e−04** into `e2n_from_files`; read back
  **7.257759428297964e−04**; reader delta identical to 17 significant digits.
- **G-F25-2** — planted **−7.001660376824503e−02** into `fre_from_files`; read back
  **−7.001660376824503e−02**; identical to 17 digits.

Both **PASS**. A zero from these readers is now a zero a reader was shown able to
see a non-zero through.

The 12 graded-path controls, each passed: symbolic substitution into the duct
Poisson equation (parabola and harmonic residuals identically `0`, wall Fourier
coefficients 1/3/5) with the **1.1× plant non-zero** (residual `−569/20000`); the
series converged, symmetric and reproducing the literature (400 terms, max
|N vs 2N| 2.64e−16, max asymmetry 4.93e−15, `f·Re` 56.90830753912461 against the
literature's 56.908, and a planted 3-term truncation differing by 1.53e−02);
constant-ratio refinement in **all three** directions (side and x ratios 2.0, cell
ratios 8.0); the model solved and second order (orders 1.962/1.989 on E2n,
1.976/1.993 on f·Re); **`PZ-F25-L345`** — the model's own triples through the
grader's own classifier reading CONVERGING at 1.9529 and 1.9698 with a planted
**DEGENERATE** positive control at order −0.0267; **`PZ-F25-CLASSC`** — the four
Class C limbs each shown able to refuse (flat PLATEAUED, ramp and step
NOT_PLATEAUED_TREND, short series `exit 2`); the single `grade_ladder` call site
driven both ways; solver dictionaries agreeing with the registration (ν 0.01,
G 0.2845, 4 ranks, endTime 4000, writeInterval 100, `residualControl` **absent**,
`simple n (1 2 2)`, SIMPLEC, relaxation U 0.95 / p 1.0, `Gauss linearUpwind
grad(U)`); the reader parsing **real solver-written `U` on this box** (a foreign
artefact, `verification/runs/ansys_verification/VMFL019/L1_30/5/U`, 120 cells, with
a mismatched count refused and a uniform-volume file expanded); **`PZ-F25-L342`**
infrastructure-vs-physics driven both ways (deleting infrastructure leaves the
verdict channel unchanged and refuses the cost claim; corrupting physics flips the
verdict to NOT A RESULT through the Ux residual, the transverse field floor and a
missing rank); and **`PZ-F25-L346`** the iterative floor derived from the predicted
fine error, both ways.

**Gate demonstration — both gates driven inside AND outside their bands** by
`demonstrate()`, re-executed by the grader at grading time:

| gate | construction | value | inside? | intended |
|---|---|---|---|---|
| G-F25-1 | exact + **1×** model error field, u × 1 | 7.421509466534361e−04 | yes | inside |
| G-F25-2 | exact + **1×** model error field, u × 1 | 56.85473706993482 | yes | inside |
| G-F25-1 | exact + **40×** model error field, u × 1 | 1.9910106264463958e−02 | no | outside |
| G-F25-2 | exact + 1× model error field, **u × 1.01** | 56.291818881123596 | no | outside |

G-F25-2's outside construction is a **1 % bulk-velocity perturbation**, not a 40×
error field, because `f·Re` reads the bulk velocity: 1 % on `Ubar_h` moves `f·Re`
by 0.563, which is 3.5× the band half-width. Each gate is shown able to say both
words.

## 4. FROZEN FILES — disk == blob at the pre-registration commit, checked by THIS LANE

**The F25 grader records the pre-registration sha but does not itself hash the
frozen files against it** (it requires `--prereg-commit` and refuses without one,
`grade_f25.py:957`, but performs no blob comparison — unlike F26D's `verify_freeze`).
That check was therefore done by this lane, `git hash-object <disk>` against
`git rev-parse 12def6b5:<path>`, over **every path the commit carries for this case
plus the gating script** — **18 of 18 SAME**:

| path | blob |
|---|---|
| `cases/F25_DUCT3D/grade_f25.py` | `ad5f28ff` |
| `cases/F25_DUCT3D/exact_f25.py` | `e552e4af` |
| `cases/F25_DUCT3D/foam_io_f25.py` | `591d112d` |
| `cases/F25_DUCT3D/build_f25.py` | `4863d97b` |
| `cases/F25_DUCT3D/proj_f25.py` | `9e5b8e60` |
| `cases/F25_DUCT3D/run_f25.sh` | `70ed1751` |
| `case/0/U.template`, `case/0/p` | `6d5a8658`, `291aff53` |
| `case/constant/fvOptions`, `transportProperties`, `turbulenceProperties` | `67edbb0f`, `ba88034b`, `ba5bb3d1` |
| `case/system/blockMeshDict.template`, `controlDict`, `decomposeParDict`, `fvSchemes`, `fvSolution` | `2eda56b1`, `56d90d34`, `2946fc98`, `a04e1c3b`, `f1e15207` |
| `scripts/roache_triple.py` | `78e56a3b` |
| `verification/campaign/F25_DUCT3D_PREREGISTRATION.md` | `e24d2404` |

**One file differs and it is named rather than omitted:**
`cases/F25_DUCT3D/queue_entry_F25_DUCT3D.json`. Its blob at the pre-registration
commit still carries the *superseded* sha `bbbcdf71`; the copy on disk carries
`12def6b5` and is byte-identical to HEAD. This is structural, not a defect: the
queue entry is re-issued **against** each new freeze, so it cannot be inside the
commit it names. It is an **INFRASTRUCTURE** record by the grader's own
`field_classes`, no verdict reads it, and the ladder's actual `grade_cmd` sha was
checked directly against the JSON instead.

## 5. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines | `ExecutionTime` lines | last time == endTime | fields at `4000/` | age guard (`0/U` → `processor0/4000/U`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 4000 | 4000 | 4000 == 4000 | U p in all 4 processor dirs | 04:53:55.469 → 04:55:22.220 Z | 86 s / 85.59 s |
| medium | 0 | 1 | 4000 | 4000 | 4000 == 4000 | U p in all 4 processor dirs | 04:55:29.003 → 05:08:48.341 Z | 796 s / 795.54 s |
| fine | 0 | 1 | 4000 | 4000 | 4000 == 4000 | U p in all 4 processor dirs | 05:09:35.184 → 07:00:06.195 Z | 6605 s / 6603.39 s |

Every clause holds at every level and the grader's own `completion()` agrees
(`n_times` 4000, `latest` 4000.0, `dt` 1.0, rc `0`, `done` true at all three, with
the stated `why`: *"rc 0; End present; latest + dt > endTime; 4000 `Time` lines ==
endTime; U and p at endTime in all 4 processor directories and newer than 0/U"*).

**Decomposed, never reconstructed.** 4 ranks at every level, `simple n (1 2 2)`,
2 × 2 cross-section quadrants, **x never cut**; decomposition seed `none`
(deterministic geometric, no RNG). Every artifact path a verdict cites is
`<level>/processor{0,1,2,3}/4000/U` — `reconstructPar` was never invoked and no
reconstructed time directory exists in the run root. This is the first lab ladder
graded end-to-end out of processor directories.

**Mesh admissibility** from each level's `MESH_LINE.txt` (source `log.checkMesh`):
max non-orthogonality **0°**, max skewness **0**, max aspect ratio **1** at all
three levels, against gates 70° / 4 — cubic cells, exactly as registered.

**One log-tail observation, disclosed.** `fine/log.simpleFoam` carries OpenMPI
`vader_segment` shared-memory `unlink(2)` warnings **after** the `End` line, at
finalisation. They are teardown messages emitted once the run had finished writing;
`RC.txt` is 0, the `End` line and all 4,000 `Time`/`ExecutionTime` lines precede
them, and every field at `4000/` is present and newer than `0/U`. They touch no
clause of rule 4 and are recorded so that a later reader who greps the log tail is
not surprised by them.

## 6. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted | **1,342.8 core-min** (coarse 4.1, medium 72.1, fine 1,266.6), the **AMENDED** figure at prereg `:470`. **§7's original 706.0 core-min is STRUCK by Amendment 1 and is NOT the comparison basis** — the amendment says so in its own words: *"is superseded by this row"*. Registered cap **2,000** (prereg `:471`) |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` (4 ranks) | coarse 86 s → **5.7333**; medium 796 s → **53.0667**; fine 6,605 s → **440.3333**; **499.1333 core-min gross** |
| corroboration | the launcher's own tally (`cases/F25_DUCT3D/launcher.queue.out`, *"Cumulative spend: 499.1333333333333 core-min of 2000"*) and the grader's `cost_claim.core_min_claim` / `partial_sum_core_min` in `F25_GRADED.json` (`defects: []`) — **all three agree to every digit** |
| ExecutionTime basis, stated beside it | (85.59 + 795.54 + 6,603.39) × 4 ÷ 60 = **498.9680 core-min** |
| **the 3,600-second row, addressed rather than passed over** | the fine level ran **6,605 wall s**, above the charter §2 stall heuristic. It is **not a stall**, and the artefacts say so independently of the wall figure: 4,000 `Time =` lines, 4,000 `ExecutionTime` lines, 40 written checkpoints, 8.389 × 10⁹ cell-iterations, and **ExecutionTime / ClockTime = 6,603.39 / 6,605 = 0.99976** — the ranks delivered CPU for 99.98 % of that wall. A stall is a wall with no work behind it. **There is nothing to clean.** |
| actual cleaned | **499.1333 — cleaned == gross**, for the reason in the row above |
| waste, named separately | **0.000 core-min** (`COMPUTE_BUDGET_CHARTER.md` §6) — no stall, no kill, no re-run, no cap movement; the ladder ran once, completed, and was graded once. Not folded into the ratio below |
| quantisation | `ClockTime` is integer-second: ± 0.0333 core-min per level at 4 ranks |
| share of cap | **25.0 %** (499.1333 / 2,000); no overrun, cap never raised |
| dollars | 499.1333 / 60 = 8.3189 core-h × $0.0513/core-h = **$0.4268 — DERIVED, NOT MEASURED** (c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). Registered: $1.15 at the estimate, $1.71 at the cap |
| **ratio actual/predicted** | **0.372** |

**Gap attribution — MISPREDICTION of the growth model, not contention and not
waste.** The amended estimate took a **measured** anchor — 2.44 core-µs per
cell-iteration, read from this case's own 65,536-cell instrument arm — and scaled
it by **+30 % per doubling of the cell count**, which the amendment itself labelled
`MODELLED, not measured` and flagged as *"derived beyond the anchor"* with the fine
level **five doublings above** it. Each ladder step multiplies cells by 8, i.e.
three doublings, so the model applied 1.3³ = **2.197× per level**. Measured:

| level | cells | registered rate (core-µs/cell-iteration) | **measured rate** | measured/registered |
|---|---|---|---|---|
| coarse | 32,768 | 1.877 | **2.6245** | **1.398** |
| medium | 262,144 | 4.124 | **3.0365** | **0.736** |
| fine | 2,097,152 | 9.060 | **3.1495** | **0.348** |

**The rate is very nearly FLAT across a 64× range of problem size.** Measured
per-level growth: **1.157×** coarse→medium and **1.037×** medium→fine, against the
modelled 2.197× at each step — i.e. **+5.0 % and +1.2 % per doubling measured,
against +30 % per doubling modelled.** The model over-predicted the ladder by
**2.69×** overall. Note the direction is not uniform: at the coarse level the model
*under*-predicted by 40 % (the anchor was extrapolated one halving **downward**,
where fixed startup costs do not amortise), and the over-prediction is entirely in
the two upper levels, which carry 98.8 % of the spend.

**Contention: present in the box load, absent from the wall-versus-CPU reading.**
`box_before.txt` / `box_after.txt` record load1 **10.75 → 13.22 → 14.00 → 14.02 of
16 cores**, free cores falling 5.25 → 2.78 → 2.00 → 1.98, MemAvailable steady at
27.8–28.3 GB. Yet ExecutionTime/ClockTime is **0.9953 / 0.9994 / 0.9998**: the four
ranks were never descheduled. The measured rates already carry the load they ran
under, and no separable contention figure can be extracted from them — so none is
invented.

**Carry forward, and it is the substantive lesson of this row.** A **+30 %
per-doubling growth term is wrong for 3-D `simpleFoam`/SIMPLEC on cubic cells with
a linear solver that scales well**: this ladder measured +1 % to +5 % per doubling.
The failure mode is the standing one the lab has now priced four times (F21, F22,
F18b, and F17c's counterfactual in `docs/COST_CALIBRATION.md` C-194) — the **base
rate measured right, the growth exponent imported and wrong**. Here the exponent
was wrong in the *safe* direction and cost nothing but headroom; the same
methodology that over-predicts by 2.7× can under-predict by the same factor and
trip a cap. **Amendment 2's replacement projector, which re-bases from this case's
own completed levels, is what actually tracked the run:** its live projections read
4.1 → 100.8 → 491.2 core-min against actuals 5.7 → 53.1 → 440.3, and the fine
projection — the one that decides whether the expensive level runs — was **1.115×**
the actual, against the frozen model's 2.876×.

**Estimate-versus-actual calibration lands as a row in `docs/COST_CALIBRATION.md`,
appended at the file's foot at commit time under its own append rules and the
rule-10 private-index protocol.**

## 7. WHAT THIS LADDER SETTLED

The capability-grid cell **3D · steady · incompressible** recorded *"never produced
a CONVERGING 3D triple"*. **It now has two**, both PASS, both at `dim = 3` with
`r = 2.000` in **all three** directions, both graded from processor directories on
4 ranks against a closed-form reference, with observed orders 1.953 and 1.970
against a registered model prediction of 1.953 and 1.970. Whether the supervisor
records the cell as closed is the supervisor's call and is not taken here.

What is **not** claimed: nothing about turbulence, nothing about developing duct
flow, nothing about any Reynolds number other than the Re_Dh ≈ 100 registered here,
and no order claim beyond the two the grader printed.

## 8. BOOKKEEPING — L-342 infrastructure fields; none touches a verdict

- `cases/F25_DUCT3D/STATUS.F25_DUCT3D` reads `launcher_rc=0
  end=2026-08-28T07:00:07Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`
  and was written by the queue runner. **The solver rc per level is `RC.txt` = 0 at
  all three**, cited in §5. `launcher.queue.out` under the case directory is the
  runner's record; not committed by this lane.
- The grader's `cost_claim` carries **`defects: []`**; the cost claim in §6 is not
  refused.
- **No foreign grade artefact** is present in the run root: `F25_GRADED.json` is the
  only non-level entry, written 2026-08-28T16:15Z by the invocation named at the
  head of this record.
- `cases/F25_DUCT3D/` also holds
  `queue_entry_F25_DUCT3D.WITHHELD_2026-08-27T162849Z.json` and
  `WORKTREE_NOTICE_lane_R_2026-08-27T1654Z.md`, both pre-launch records of other
  lanes' work. Neither is read by the grader and neither is touched by this record.
- The frozen grader was run with plain `python3`, never `-O`.

## 9. NOT REGISTERED, NOT SENT

No re-grade of any row; no amendment to the frozen pre-registration (this case is
**post-compute** and its gates, thresholds, cap and labels are **closed**); no
turbulence claim; `p` is not graded. **Nothing is sent, filed, uploaded, registered,
posted or submitted** (rule 7). Field data stays on disk under
`verification/runs/F25_DUCT3D_runs/` and is not committed.
