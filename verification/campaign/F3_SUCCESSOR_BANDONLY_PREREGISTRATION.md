# F3 SUCCESSOR — PRE-REGISTRATION

## STATUS: **DRAFT v2. NOT FROZEN. NOT FIRED. ZERO COMPUTE.**

**Drafted 2026-08-26 by a cfd lab-lane under cfd-supervisor.** No solver was started, no
mesher was run, no case directory was created, and no file under this rung's run root was
touched. **This document is not frozen and confers no authority to launch.**

Written in the **template-speed prereg form** authorised by Sanaa's EXECUTION REBALANCE. The
ten numbered lines are the registration; the annexes are the derivations a grader needs to
attack it.

---

## REVISION RECORD — v1 → v2, both PRE-COMPUTE, both legal under rule 2

Rule 2 permits amendment before first compute **provided the condition is stated and the check
named**. **Condition: no run directory under this rung's root exists.** Checked 2026-08-26 —
`verification/runs/F3_runs/successor_triple_2026-08-26/runs` does not exist and neither does
`successor_bandonly_2026-08-25/runs`. **No compute has occurred under either version.**

| | v1 (2026-08-26, earlier) | **v2 (this document)** |
|---|---|---|
| scope | 2 runs, fine level only, band-only rows | **8 runs: two full grid triples + two control runs** |
| convergence | open item, three limbs referred | **Class C, MEASURED, all four elements live** |
| grading | delegate to `grade_f3.py` byte-unchanged | **must call `grade_ladder`** — see Annex H |
| cap | 7.630 core-min | **17.6541 core-min** |

**Two things forced the change, and only the first was foreseen.** cfd-supervisor ruled limb
(a) — re-author the runners so steadiness is measured. Then **Annex H**: `grade_ladder`
**hard-refuses below three levels**, so a single-level rung cannot call it at all, and the
supervisor's own binding ruling at `887ddfaf` requires every new cfd grading path to call it.
**Limb (a) at one level per pair would not have satisfied the ruling either.** The rung must
run full triples or it cannot produce a row.

---

## THE TEN LINES

1. **Case.** Eight single-rank OpenFOAM `rhoCentralFoam` runs. Two **full grid triples** —
   `wedge/M2.5_th10` and `diamond/M2.5_eps5` at coarse/medium/fine — plus **two control runs**
   (Annex I). Run root `verification/runs/F3_runs/successor_triple_2026-08-26/runs/`, which
   **does not exist** at drafting.

2. **Reference.** **Exact analytic** — oblique-shock relations and shock-expansion wave drag,
   from `exact_theory.py` (sha256 `1e1879a3…`), pinned in `grade_f3.py`'s frozen `EXACT` table.
   Zero reference uncertainty; the whole error budget is numerical.

3. **Quantities.** Three gate rows, and no others:
   | row | quantity | write path |
   |---|---|---|
   | G-F3S-1 wedge surface pressure | `p_wall_mean` (`p2/p1`) | `postProcessing/surfaceSampleDict/<t>/*p*.raw` |
   | G-F3S-2 wedge shock angle | β (deg), 5-station least-squares fit | `postProcessing/sampleDict/<t>/x*_*.xy` |
   | G-F3S-5 diamond wave drag | `cd` | `postProcessing/forces1/<t>/force.dat` |

4. **Bands.** **±0.5 % (`p2/p1`), ±2.0 % (β), ±1.0 % (`cd`) — CARRIED OVER FROM F3 UNCHANGED.**
   **No band is chosen by this rung, so no band of this rung can have been chosen to fit an
   answer.** Derivations reproduced in **Annex A**. This is `BAND_ONLY_RULING_2026-08-25.md`
   condition 2, and it discharges band contamination by *elimination*, not by argument.

5. **Ladder.** **Full grid triples, coarse → medium → fine, r = 2 exactly by construction** —
   every generator doubles both mesh directions (`RES` tables: wedge 1,800 / 7,200 / 28,800;
   diamond 2,000 / 8,000 / 32,000), so the refinement ratio is not inferred from a cell count.
   Observed order reported at **dim = 2** (single-cell-thick 2-D slabs) and at dim = 3.
   **Graded through `scripts/roache_triple.py::grade_ladder`**, supplied with
   `iterative_states` **and** `plateau_states` — Annex D — per the ruling at `887ddfaf`.

6. **Decomposition seed.** **`none` — recorded, not omitted.** `nRanks = 1` per run, no
   `decomposePar`, identity partition, no stochastic element to seed. At most 2 runs live → 2
   of 16 cores.

7. **Criteria.** Rule 5 in its order, enforced by `grade_ladder` and nowhere else: (a) any level
   not `CONVERGED` and `PLATEAUED` → **NOT A RESULT**; (b) finest triple `DIVERGENT`,
   `STAGNANT`, `OSCILLATORY` or `EXACT` → **NOT A RESULT** with every triple and order printed
   and **no GCI quoted**; (c) `CONVERGING` → **PASS** inside the band else **GATE FAIL**, GCI at
   Fs = 1.25. **`PENDING`** if a run is absent. **No row of this rung is a credential** —
   registered restrictively because a label may not be widened after compute (rule 2). If the
   supervisor wishes a CONVERGING-triple PASS here to carry credential status, that must be
   ruled **into this document before it is frozen**; it cannot be added later.

8. **Cap.** **HARD CAP 17.6541 core-min = 1,059.24 core-s**, governing **wall-seconds × ranks ÷
   60 as measured by the LAUNCHER in its own invocation** (Annex B). Checked **incrementally,
   before and after every one of the eight runs**, plus an unconditional polled watchdog.
   Expected **14.7117 core-min**; **$0.012579 expected / $0.015094 at cap, DERIVED at
   $0.0513/core-h, NOT MEASURED** — this box cannot read its own billing.

9. **Grading path.** Frozen at this document's commit:
   `verification/runs/F3_runs/successor_triple_2026-08-26/instrument.py` (the instrumented
   runner and the Class C gate) plus the ladder grader that calls `grade_ladder`. **It must not
   reimplement the triple** — that is the `ABSENT` defect `887ddfaf` forbids repeating, and
   `grade_f3.py:377-395` is the instance being avoided. Band values and exact references are
   **imported from `grade_f3.py`'s frozen constants**, so nothing is re-derived.

10. **What this rung does NOT do.** **It cannot change F3's tally and must never be cited as
    doing so.** F3 is CLOSED at **5 PASS, 1 GATE FAIL, 1 NOT A RESULT, 3 PENDING**. Its three
    `PENDING` cells stay `PENDING`, and stay `BLOCKED` as a launch request. This rung produces
    **its own rows under its own registration**. No frozen F3 file is edited; F3's 39.5 core-min
    cap is untouched and spent.

---

## ANNEX A — the bands, and the principle each came from

Reproduced from `F3_CONVERSION_PREREGISTRATION.md` §4.1–§4.3 so a reader can check the
derivations here rather than being told they exist elsewhere. **This rung re-derives nothing.**

**Blob citation.** That document's blob at HEAD is `e5f48c68`, **not** the `774dad46` recorded
in `PENDING_ROWS_DISPOSITION.md` §1 — ADDENDUM 3 landed since (commit `3574cdcb`), under rule 6
as a dated post-compute addendum. **Verified, not assumed: §4.1–§4.3 are byte-identical between
the two blobs** (49 lines each, empty diff; the diff was itself planted with a one-line change
and seen to catch it). ADDENDUM 3 alters no gate, threshold, cap or label.

- **±0.5 % on `p2/p1`** — *principle: the reference class plus the second-order requirement.*
  Exact analytic reference contributes zero uncertainty; `p2/p1` is read from patch face centres
  with `interpolate false` — no interpolation, no detector, no fit — so the only error term is
  discretization. `rhoCentralFoam` is nominally second-order and each level halves `h` exactly,
  so a medium-level error of order 1 % must fall ≈4× at fine. **±0.5 % is that requirement
  stated as a band.** A first-order-behaving solve lands near 0.5–1 % and fails it.

- **±2.0 % on β** — *principle: the detector's own quantization floor, from mesh geometry only.*
  β is detected then fitted, so its floor is quantization, not physics. For the in-scope pair
  **wedge M2.5 θ10**: H = 0.9940, fine Δy = H/80 = 0.01242, σ = Δy/√12 propagated through the
  frozen 5-station least-squares slope and through β = atan(m) gives **1σ = 0.969 %,
  2σ = 1.937 %**. **The band is the rounded-up 2σ floor: 2.0 %.** No CFD value enters this
  arithmetic. A tighter band would gate the detector's discrete arithmetic, not the solver.

- **±1.0 % on `cd`** — *principle: composition of the ±0.5 % budget over the panels carrying it.*
  `cd` is an integrated pressure force from OpenFOAM's own `forces` object — no detector, no fit
  — carrying two panels' worth of the surface-pressure budget (one compression, one expansion)
  plus corner smearing the wedge gate does not see. **±1.0 % = 2 × ±0.5 %, one band per panel.**

**Disclosure, made rather than concealed.** In drafting, this lane read on-disk values for the
**out-of-scope** pair `diamond/M2.0_eps7p125`, and read the 2026-07-28 record's tables, which
carry old values for the in-scope pairs. **Every band above is carried over verbatim from a
document frozen before F3's first compute, so no band here could have been moved by anything
this lane read.** The Class C drift tolerances in Annex D are derived from those bands, one
order of magnitude beneath them — not from any measured deviation.

---

## ANNEX B — the cap: which quantity, and checked when

**Which quantity.** `wall_s × ranks ÷ 60`, **measured by the launcher across the full run
envelope** — spawn to exit, including case build, `blockMesh`, `checkMesh`, the solve, the
in-solve series output and the post-process sampling. **`ExecutionTime` is NOT this quantity and
does not govern**; it excludes startup, meshing and sampling, and it is not wall time.

**Not a hypothetical distinction — F3 measured the gap.** For the same ten runs F3 carries two
figures: `F3_CONVERSION_RUN_LEDGER.json` (launcher envelope) totals **2,005.06 core-s**;
`F3_CONVERSION_GRADED.json` (runner-measured `wall_s`) totals **1,972.95 core-s** and reports
`actual_core_minutes: 32.8825`. **A gap of 32.11 core-s — 1.6 % — and two available numbers.**
F3's cap check used the launcher figure; **this rung names that figure and only that figure.**

**Costing.** Predictions are the 2026-07-28 record's measured per-run core-seconds, calibrated
by F3's **measured** ratio **1.1290** — independently re-derived as 2,005.06 ÷ 1,775.90 over the
ten launched runs, on the launcher basis this cap governs — times a registered **1.15
instrumentation uplift** on instrumented runs (extra sampling I/O; it changes wall time, not the
trajectory — Annex I proves the latter).

| run | predicted | basis of the prediction | per-run cap |
|---|---|---|---|
| `wedge/M2.5_th10/coarse` | 6.1 | **TRANSFERRED from wedge M2.0 coarse (identical 1,800 cells) — NOT measured for this pair** | 9.50 core-s |
| `wedge/M2.5_th10/medium` | 18.9 | measured 2026-07-28 | 29.45 core-s |
| `wedge/M2.5_th10/fine` | 148.1 | measured 2026-07-28 | 230.74 core-s |
| `diamond/M2.5_eps5/coarse` | 9.1 | measured 2026-07-28 | 14.18 core-s |
| `diamond/M2.5_eps5/medium` | 29.3 | measured 2026-07-28 | 45.65 core-s |
| `diamond/M2.5_eps5/fine` | 189.8 | measured 2026-07-28 | 295.71 core-s |
| control arm A — `wedge/M3.0_th15/fine` **uninstrumented** | 149.0 | measured 2026-07-28 | 201.87 core-s |
| control arm B — `wedge/M3.0_th15/fine` **instrumented** | 149.0 | measured 2026-07-28 | 232.14 core-s |
| **total** | **699.3** | | **EXPECTED 882.70 core-s = 14.7117 core-min; HARD CAP 1,059.24 core-s = 17.6541 core-min** |

**One prediction is a transfer, not a measurement, and is labelled so** — the 2026-07-28 record
ran only medium and fine for wedge M2.5, so its coarse cost is taken from the M2.0 coarse run at
identical cell count. A cost is never called measured unless a record backs it.

**When it is checked — INCREMENTALLY, and the launcher HALTS AND REPORTS on a crossing.**
1. **Before each run**: `spent + calibrated_pred × 1.20 > CAP` → **do not launch; halt; report.**
   The unlaunched row is `PENDING`, never a killed row.
2. **After each run**: `spent > CAP` → **halt; launch nothing further; report.**
3. **During**: an unconditional polled watchdog on `spent + live` → terminate, mark `KILLED`;
   a `KILLED` run's rows grade `NOT A RESULT`, never a value.

**This cap is NOT totalled only at the end.** F4's cap was evaluable exactly once, after every
core-minute was spent — a post-hoc audit wearing a guard's name. With eight runs, points 1 and 2
give **sixteen** cap evaluations, one of them before any compute at all.

---

## ANNEX C — the completion rule (standing rule 4)

Live clauses: `rc = 0`; an `End` line; **fields present**; the **age guard** (every field at the
last time newer than the case's own `0/`); and the completion limb.

**Declared adaptation.** `rhoCentralFoam` is explicit and density-based, so the steady-iteration
clause `ExecutionTime count == endTime` **does not apply** and is declared inapplicable rather
than silently dropped.

**The completion limb is `latest + dt_final > endTime`, NOT `latest >= endTime`.** With
`adjustTimeStep yes` the final step lands either side of `endTime` — `wedge/M3.0_th15/fine` ends
at `2.5999683` against `endTime 2.600000`, short by 3.17e-5 — and the naive form refuses a
genuinely complete run. Implemented as `|last − endTime| ≤ maxDeltaT` with `maxDeltaT = 1e-3`
read from **the case's own `controlDict`**. **This is not a two-sided tolerance band chosen after
seeing which runs it admits** — `maxDeltaT` is an input, frozen in the case at build time; no
epsilon is fitted.

**Pre-existing-directory guard, before any case is built.** `instrument.py::guard_fresh_case_dir`
refuses (exit 2) if the target directory exists non-empty or already holds `0/`, `constant/` or
`system/`, **before any generator runs** — because the age guard dates a run from `0/T`.
*(F3's 2026-07-28 trees exist one directory level up at `F3_runs/wedge/M2.5_th10/…`. This rung's
root is disjoint; those trees are never read and never written.)*

---

## ANNEX D — convergence: RULED, and MEASURED

**cfd-supervisor ruled limb (a) on 2026-08-26: re-author the runners so steadiness is measured.**
Lawful because this is a new pre-registration before its first compute; F3's
`postProcess -latestTime` is F3's and does not bind the successor.

### D.1 The sentence that governs, and the finding behind it

> **STEADINESS FOR A DENSITY-BASED EXPLICIT TIME-MARCHER IS DRIFT IN THE GRADED QUANTITY OVER A
> SUSTAINED WINDOW, NEVER A RESIDUAL.**

**Measured, not argued.** `rhoCentralFoam` runs the `diagonal` solver, which solves each step
exactly. All **8,071** `Time =` blocks in
`conversion_2026-08-24/runs/wedge/M3.0_th15/fine/log.rhoCentralFoam` report
`Initial residual = 0, Final residual = 0, No Iterations 0` for rho, rhoUx, rhoUy and rhoE.
**A residual gate here is a gate quantity that can never be non-zero** — the class that has now
bitten VMFL059 and F12's `P4`. **No residual gate is registered.**

### D.2 `iterative_states` — a real check that CAN fail

`diagonal` is a **direct** solver: per-step linear convergence holds by construction and the
residual is identically zero **by construction, not by tolerance**. That is the basis for
`CONVERGED`. **It is still a real check**: `instrument.py::iterative_state_from_log` parses every
solver line and only returns `CONVERGED` on that basis if **every** line reads `diagonal` with
final residual 0 and 0 iterations. If `fvSolution` is ever changed to an iterative solver, it
falls through to a genuine tolerance test that can return `NOT_CONVERGED`. It refuses outright if
no solver lines parse — an unestablished state is not a converged one.

### D.3 `plateau_states` — Class C, all four elements, **element 4 live and not waived**

Registered numbers, fixed before any run of this rung exists:

| element | registered value | derivation |
|---|---|---|
| 1 — sustained window floor | final **25 %** of `endTime` | a window, not an endpoint |
| 2 — trend fit rejecting growth | \|slope × span\| / value ≤ **tol** | least-squares over the window |
| 3 — stationarity, able to report NOT stationary | \|mean(2nd half) − mean(1st half)\| / value ≤ **tol** | two-half separation |
| 4 — **refusal below a minimum sample count** | **30 window samples** | **REFUSES; does not degrade** |

**tol = band ÷ 10** — 0.05 % for `p_wall_mean`, 0.20 % for β, 0.10 % for `cd`. *Principle: a
value cannot be claimed inside a ±X % band while still moving by more than X/10 % across the
window it is claimed on.* Fixed before any in-scope value was read; **not derived from any
measured deviation.**

**The output cadence is chosen from MEASURED step counts, not guessed.** Counting `Time =`
blocks across every F3 conversion log gives a **worst level of 3,919 steps** (wedge coarse), so
the final-25 % window holds ~979 steps at the least-resolved level this rung runs. At a cadence
of **every 20 steps** that is **~49 window samples against the floor of 30 — a 1.6× margin at
the binding level**, not at the comfortable one. Fine levels give ~100 (wedge 8,056 steps;
diamond 9,129). The window boundary is compared **strictly**, with no epsilon: adding a tolerance
to a gate boundary is a fitted threshold, and at a 1.6× margin a one-sample floating-point
boundary effect cannot move a verdict.

**Element 4 is live and was driven against reality.** On F3's actual artifacts the gate
**refuses**: the wedge has **1** sample, the diamond **3** rows. Driven under `python3 -O`, both
exit 2. It also refuses at 29 window samples and passes only above the floor. **A window that
cannot be filled is a refusal, never a band-only PASS, and never the last reading borrowed as a
plateau.**

**The plateau test carries its own planted control.** `plateau_plant_control` re-runs the same
series with a ramp **100× the registered tolerance** added and **requires the test to reject
it**. If the test cannot see the ramp, its `PLATEAUED` verdicts are not evidence and it refuses.
Driven: flat → `PLATEAUED`; ramp → `NOT_PLATEAUED`; mid-window step → `NOT_PLATEAUED`.

---

## ANNEX E — planted-zero controls, and the both-direction proof

**Inherited live and byte-unchanged from `grade_f3.py`**, each refusing (exit 2) if the reader
cannot see its plant: **PZ-1** surface pressure (`PLANT_P = 1.234e-03` additive into the pressure
column); **PZ-3** β re-derived independently from the stored shock locus (`PLANT_SLOPE =
1.000e-02`); **PZ-4** `cd` re-derived independently from `force.dat` (`PLANT_FX = 1.234e-05`),
required to move by exactly the amount the definition demands. **New in this rung:
PZ-PLATEAU** (Annex D.3) and `grade_ladder`'s own `planted_zero_control`, which
`assert_plant_control` requires — missing or failed plant control is a refusal, not a softer
number.

**Each gate quantity CAN take both a failing and a passing value on this solver's real on-disk
output — from F3's executed rows, not asserted:**

| quantity | a PASS on disk | a non-PASS on disk |
|---|---|---|
| wedge `p2/p1` | M3.0_th15 `PASS`, dev **+0.00733 %** | M2.0_th15 **`NOT A RESULT`**, dev +0.0722 %, triple `OSCILLATORY` (R = −0.0875) |
| wedge β | M2.0_th15 `PASS`, dev **−1.4353 %** | cone β **`GATE FAIL`**, same detector, same ±2.0 % band |
| diamond `cd` | M2.0_eps7p125 `PASS`, dev **−0.2579 %** | none — see below |

**Stated honestly: `cd` has no executed `GATE FAIL` or `NOT A RESULT` on this suite.** What is
shown is that the reader produces a real non-zero `cd` and that PZ-4 moves it by a planted
increment — the quantity is not structurally pinned — **not** that a diamond row has ever failed.

**A registered expectation about the diamond triple, recorded before compute so it cannot be
claimed afterwards as foresight.** The 2026-07-28 diamond M2.5 three-level set is **non-monotone**
(0.013428 → 0.013395 → 0.013406). If this rung's triple reproduces that shape it will grade
`OSCILLATORY` and therefore **NOT A RESULT** under rule 5 clause (b) — a real and likely outcome,
registered now, and **it is not a reason to alter the gate.**

---

## ANNEX F — instrument discipline, and the DEFECT, NOW REPAIRED AND MUTATION-TESTED

**Flag-proof refusals.** No `assert` carries a refusal, guard, control or gate in this rung's
path — `python3 -O` deletes every `assert`, so all refusals are `raise` / `sys.exit(2)`.
**Measured by AST, not grep: `instrument.py` 0 `Assert` nodes; `grade_successor.py` 0;
`grade_f3.py` 0.** `ast_no_asserts()` runs this census as a **launch precondition**.

**DEFECT FOUND AND REPAIRED — the manufactured-certification shape.** `grade_successor.py`'s
`--selftest` previously ran `controls = selftest_annotator()` and then printed `SELFTEST GREEN`
**without inspecting `controls`**. A mutation replacing that call with `controls = []` — the
whole planted-zero control deleted — **still printed `SELFTEST GREEN` and still exited rc = 0
under `python3 -O`**: a certificate issued by a run in which nothing was checked.

**Repaired by fixing the class, not the instance**: a `controls_all_passed()` predicate is
evaluated and the claim is printed **inside the passing branch**, so removing the check removes
the claim. **Re-mutated to prove it:**

| variant | rc | `SELFTEST GREEN` printed |
|---|---|---|
| control (unmutated) | 0 | **yes** |
| controls deleted (`controls = []`) | **2** | **no** |
| controls present but `passed=False` | **2** | **no** |
| frozen-bytes assertion deleted | **2** | **no** |

**Build guards.** The frozen generators carry build guards **as `assert`** —
`make_wedge_case.py:47` (`assert ny == ny2`) and `make_diamond_case.py:58` — which `python3 -O`
deletes, producing a **wrong mesh silently**. A build guard produces an **input**, and a wrong
input is cured by **re-registration, not by patching a fired file**.
`instrument.py::check_generator_guards()` drives the generator under `-O` with a deliberately
inconsistent `RES` entry and **records whether the guard fires**; every guard this rung owns is
written flag-proof in the **new** path and is required to refuse under `-O` before any launch.

**Never an unconditional success print.** No `LAUNCH OK`, `CAP RESPECTED`, `COMPLETE` or
`SELFTEST GREEN` may sit outside the branch that established it. `set -e` does not gate in this
harness; every shell assertion is written `|| { echo ABORT; exit 1; }`.

**Cost basis measured at launch, by the launcher, in its own invocation** — HEAD, UTC and machine
load written to `LAUNCH_HEAD.txt` / `LAUNCH_LOAD.txt` under this rung's root. **A load figure
relayed from a supervisor's brief is not a measurement and is not accepted.**

**Launcher paths resolved against the disk in the same invocation that writes them.** Commit
`a1fbe127` (the MOVE_MAP reorg) left roughly 140 tracked scripts citing the dead
`demo-output/website/...` tree, F6d's launcher `ROOT` among them. **This rung's launcher resolves
every path it registers and refuses on a miss** rather than trusting a literal.

---

## ANNEX H — **THE COLLISION THAT FORCED FULL TRIPLES**, measured by driving the instrument

The supervisor's ruling at `887ddfaf` binds forward: *every cfd grading path calls `grade_ladder`
and supplies `iterative_states` and `plateau_states`, or refuses.*

**`scripts/roache_triple.py::grade_ladder` HARD-REFUSES BELOW THREE LEVELS** — `if len(levels)
< 3: refuse("a Roache triple needs at least three levels")`. **Driven, with a working control:**

| levels supplied | result |
|---|---|
| 3 (control — proves the harness can see a success) | **PASS** |
| 2 | **REFUSED** — "a Roache triple needs at least three levels" |
| **1 — what a band-only rung has** | **REFUSED** |

**Therefore a single-level rung cannot call `grade_ladder` at all, and cannot satisfy the
ruling.** Limb (a) at one level per pair would not have cured this either: measuring steadiness
supplies the *states*, but not the three *levels*. **The rung runs full triples, or it produces
no row.** That is the reason for v2's scope, and it is a finding, not a preference.

**One consequence must be named rather than left to be discovered.** `grade_ladder` reaches its
gate through **four `assert` statements** — `roache_triple.py:195, 632, 634, 637` — which carry
`require_dim` and the `_seal` invariants (verdict in the fixed vocabulary; verdict one-way
against the band verdict; no GCI quoted on a non-monotone triple). **`python3 -O` deletes all
four**, so rule 1 and rule 5's own asymmetry stop being enforced in the shared instrument. This
is already on the board. **This rung's grading path must therefore never run under `-O`, and
must re-check those three invariants itself with `raise`** before emitting a row. Registered here
so the exposure is inherited knowingly. **Repairing the shared instrument is not this rung's to
do** and is not done here.

---

## ANNEX I — **INSTRUMENTATION IS AN OBSERVATION, NOT AN INTERVENTION** — and the proof, in three parts

The supervisor's condition: adding output must not perturb the trajectory, and the document must
**prove** it rather than assert it.

**1. ADDITIVE ONLY.** Not one key the frozen generator wrote is modified — no `writeInterval`,
no `purgeWrite`, no `writeControl`, no `deltaT`, no `maxCo`, no `endTime`. The series comes from
function objects **appended** in a new `functions` block.
`instrument.py::assert_controldict_additive()` compares the written `controlDict` line by line
against the generator's own output and **refuses unless it is a prefix-preserving extension
carrying the instrumentation marker**, naming the first modified line if not.

**2. `timeStep`-BASED OUTPUT, NEVER `adjustableRunTime`.** The written `controlDict` is read and
its keys quoted, never assumed. `adjustTimeStep` is **`yes`** on these cases, so the step adapts
and an `adjustableRunTime` output control **would clip steps onto write times and change the
trajectory**. Every appended function object uses `writeControl timeStep`, which cannot touch
`deltaT`, and `refuse_clipping_output()` refuses if the string `adjustableRunTime` appears
anywhere in the written `controlDict` or in the appended block.

**Measured from F3's own disk that the existing controls do NOT clip**, so the baseline this rung
compares against is itself unclipped: the wedge requested writes at `endTime/3 = 0.866667` with
`endTime 2.600000` and **wrote at 1.733263 and 2.5999683** — off the requested values by 7.1e-5
and 3.17e-5. A clipping control lands on them exactly. The diamond likewise wrote forces at
1.999939 / 4.0002418 / 5.99989277 against an interval of 2.0. **Non-clipping, from disk, not
from doctrine.**

**3. BIT-IDENTITY, TWO-ARMED — and one arm would not have been enough.** `wedge/M3.0_th15/fine`
already ran under F3 and its graded values are on record: `p_wall_mean = 2.821769172727273`,
β = `31.931111435642887`. The rung re-runs it **twice**:

- **arm A — uninstrumented re-run.** Establishes that this case is **bit-reproducible at all** on
  this box and this build.
- **arm B — instrumented re-run.** Same case with the appended function objects.

| outcome | reading | action |
|---|---|---|
| A ≠ F3's record | the solve is not bit-reproducible across re-runs | **the control cannot attribute anything — the rung STOPS** with that diagnosis |
| A = F3's record, B ≠ A | **the instrumentation changed the experiment** | **the rung STOPS** |
| A = F3's record, B = A | instrumentation is an observation | **proceed** |

**A single instrumented arm compared against a value recorded on 2026-08-24 would confound
"instrumentation perturbs the solve" with "the solver is not bit-reproducible across re-runs."**
That is `887ddfaf`'s own instruction — *state what two things you are comparing, and prove they
are comparable, before you read the difference* — applied here. Arm A costs **149.0 predicted
core-s** and is carried in the cap table; it is not left unpriced.

**The graded path is not touched.** `p_wall_mean`, β and `cd` are produced by the same code, at
the same final time, from the same artifacts. If the series machinery were deleted the graded
numbers would be unchanged. The series is a **second, additive read**.

**One inherited defect is repaired in the new path rather than carried.** F3's runners resolve
the latest time with `sorted(glob.glob(...))[-1]` — a **lexicographic** sort
(`run_wedge_case.py:94`, `:131`). With one sampled time that was harmless and was never wrong for
F3. **This rung creates many sampled times, and lexicographically "9.0" sorts after "10.0".**
`instrument.py::numeric_time_dirs()` sorts numerically. Re-authored, not inherited.

---

## ANNEX G — what this lane could NOT derive or verify, stated plainly

1. **Whether `cd` has ever produced a non-PASS on this suite.** It has not (Annex E). The
   both-direction proof for the diamond rests on reader sensitivity, not an executed failing row.
2. **Whether any run of this rung will PASS.** Nothing was run; no in-scope gate quantity was
   observed. The Annex E note about the old diamond triple's non-monotonicity is a **registered
   expectation about the old record**, not a prediction of this rung's values.
3. **Whether the instrumentation is in fact non-perturbing.** Argued from three independent
   grounds and made **falsifiable** by Annex I's two-arm control — but **not yet measured**, and
   it cannot be until compute is authorised. If arm B differs from arm A, the rung stops.
4. **The wedge M2.5 coarse cost is a TRANSFER, not a measurement** (Annex B).
5. **Whether the four `assert`-carried gates in the shared `roache_triple.py` will be repaired.**
   Not this rung's to fix; the exposure is registered in Annex H and inherited knowingly.
6. **Whether any other campaign leans on band-only rows as credentials.** Not swept — escalated
   as cross-family in `BAND_ONLY_RULING_2026-08-25.md` §7 and still open.

---

## COST CALIBRATION (standing rule 12)

**Compute incurred drafting this document: 0.0000 core-minutes, $0.00.** No row is added to
`docs/COST_CALIBRATION.md` — no process consuming compute completed, and a calibration row for
zero compute would put a fictitious measurement in the ledger. F3's own calibration stands at
rows **C-66 / C-68**, ratio **1.1290**, and is not restated as new.

**On this rung's completion an estimate-versus-actual row is owed**: launcher-measured
core-minutes against the **14.7117** expectation and the **17.6541** cap, the ratio, the
attribution (contention, waste and misprediction named separately, waste never absorbed into the
ratio), and dollars marked **derived, not measured**. **The 1.15 instrumentation uplift is a
registered guess and its calibration is the most interesting number this rung will produce** —
it is the first time this team will have measured what instrumentation costs.

---

## STANDING RULES THIS DOCUMENT IS BOUND BY

Rule 1 (verdict vocabulary, six words) · Rule 2 (frozen before compute; **F3's cap is NOT
altered, re-partitioned or reinterpreted**; v1→v2 amended pre-compute with the condition stated
and checked) · Rule 3 (planted zeros, Annex E and D.3) · Rule 4 (strict completion, Annex C) ·
Rule 5 (enforced **only** through `grade_ladder`, Annex D and H) · Rule 6 (no frozen file
edited) · Rule 7 (**submissions parked**) · Rule 10 (private-index git protocol) · Rule 12
(core-minutes, Annex B) · L-332 (no `assert` carries a refusal, Annex F and H).
