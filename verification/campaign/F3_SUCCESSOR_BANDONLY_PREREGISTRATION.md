# F3 SUCCESSOR (band-only) — PRE-REGISTRATION

## STATUS: **DRAFT. NOT FROZEN. NOT FIRED. ZERO COMPUTE.**

**Drafted 2026-08-26 by a cfd lab-lane under cfd-supervisor.** No solver was started, no
mesher was run, no case directory was created, and no file under this rung's run root was
touched. **This document is not frozen and confers no authority to launch.** It becomes the
frozen registration only when cfd-supervisor has (a) read the grading path as a diff, (b)
ruled the one open item in **Annex D**, and (c) committed it. **Until then, firing anything
under it is unregistered compute.**

Written in the **template-speed prereg form** authorised by Sanaa's EXECUTION REBALANCE for
standard verification cases. F3 is an exact-theory supersonic suite; the ten numbered lines
below are the registration, and the annexes are the derivations a grader needs to attack it.

---

## THE TEN LINES

1. **Case.** Two single-rank OpenFOAM `rhoCentralFoam` runs, fine level only, built by F3's
   byte-unchanged generators: `wedge/M2.5_th10/fine` (M=2.5, θ=10°, 28,800 cells) and
   `diamond/M2.5_eps5/fine` (M=2.5, ε=5.0°, 32,000 cells). Run root
   `verification/runs/F3_runs/successor_bandonly_2026-08-25/runs/`. **Both target directories
   are ABSENT at drafting** (verified 2026-08-26; the run root itself does not exist).

2. **Reference.** **Exact analytic** — oblique-shock relations and diamond wave drag, computed
   by `exact_theory.py` (sha256 `1e1879a3…`) and pinned in `grade_f3.py`'s frozen `EXACT`
   table. The reference contributes **zero** uncertainty; the whole error budget is numerical.

3. **Quantities.** Three gate rows, and no others:
   | row | quantity | write path (named, per the both-direction requirement) |
   |---|---|---|
   | G-F3-1 / M2.5_th10 | wedge wall pressure ratio `p2/p1` | `<case>/postProcessing/surfaceSampleDict/<t>/*p*.raw` |
   | G-F3-2 / M2.5_th10 | wedge shock angle β (deg) | `<case>/result.json:shock_pts` → frozen 5-station least-squares fit |
   | G-F3-5 / M2.5_eps5 | diamond wave drag `cd` | `<case>/postProcessing/forces1/<t>/force.dat` |

4. **Bands.** **±0.5 % (p2/p1), ±2.0 % (β), ±1.0 % (cd) — CARRIED OVER FROM F3 UNCHANGED.**
   **No band is chosen by this rung, so no band of this rung can have been chosen to fit an
   answer.** Derivations reproduced in **Annex A** so a reader can check that no measured
   deviation entered them. This discharges the band-contamination hazard by *elimination*
   rather than by argument, and it is condition 2 of `BAND_ONLY_RULING_2026-08-25.md`.

5. **Ladder.** **None. Fine level only — these are BAND-ONLY rows.** No grid triple, no
   observed order, no GCI. Every row therefore carries on its own face, emitted by the grader:
   **"band only — no grid triple — no discretization-error estimate — NOT a credential."**
   Standing rule 5 clause 2 is a test performed *on* a triple; an absent triple has nothing to
   turn. **Rule 5 clause 1 is the open item — see Annex D.**

6. **Decomposition seed.** **`none` — recorded, not omitted.** `nRanks = 1` per run
   (`rerun_f3.py:135` writes `ranks=1`), `decomposePar` is not invoked, the partition is the
   identity, and there is no stochastic element to seed. At most 2 runs live at once → 2 of
   16 cores.

7. **Criteria.** A row is `PASS` inside its band, `GATE FAIL` outside it, `NOT A RESULT` if it
   fails the completion rule (Annex C) or the Annex D convergence element, `PENDING` if its run
   is absent. **No row of this rung is a credential** — `BAND_ONLY_RULING_2026-08-25.md`
   ruling (a), inherited deliberately and not by carry-over: a band-only row carries no
   discretization-error estimate and cannot distinguish a converged answer from one whose
   discretization error exceeds the band.

8. **Cap.** **HARD CAP 7.630 core-min = 457.8 core-s**, governing **wall-seconds × ranks ÷ 60
   as measured by the LAUNCHER in its own invocation** (Annex B). Checked **incrementally,
   before and after each of the two runs**, plus an unconditional polled watchdog. Expected
   spend **6.358 core-min**; **$0.00544 expected / $0.00652 at cap, DERIVED at $0.0513/core-h,
   NOT MEASURED** — this box cannot read its own billing.

9. **Grading path.** `verification/runs/F3_runs/successor_bandonly_2026-08-25/grade_successor.py`,
   frozen at this document's commit. It **does not grade**: it invokes F3's comparator
   `conversion_2026-08-24/grade_f3.py` **byte-unchanged as a subprocess** with its own freeze
   check live, and adds only the mandatory per-row limitation annotation. **It has one
   confirmed defect that must be repaired before freeze — Annex F.**

10. **What this rung does NOT do.** **It cannot change F3's tally and must never be cited as
    doing so.** F3 is CLOSED at **5 PASS, 1 GATE FAIL, 1 NOT A RESULT, 3 PENDING**. Its three
    `PENDING` cells stay `PENDING` in `F3_CONVERSION_GRADED.json` and `RESULTS.md`, and stay
    `BLOCKED` as a launch request per `PENDING_ROWS_DISPOSITION.md`. This rung produces **its
    own three rows under its own registration**. No frozen F3 file is edited, no F3 cap is
    raised, re-partitioned or reinterpreted, and F3's 39.5 core-min cap is untouched and spent.

---

## ANNEX A — the bands, and the principle each came from

Reproduced from `F3_CONVERSION_PREREGISTRATION.md` §4.1–§4.3, so a reader
can check the derivations here rather than being told they exist elsewhere. **This rung
re-derives nothing; these are shown, not chosen.**

**Blob citation, corrected.** That document's blob at HEAD is `e5f48c68`, **not** the
`774dad46` recorded in `PENDING_ROWS_DISPOSITION.md` §1 — ADDENDUM 3 has landed since, under
rule 6 as a dated post-compute addendum. **§4.1–§4.3 are unmoved by it**; ADDENDUM 3 records the
post-repair sha256 of `grade_f3.py` and alters no gate, threshold, cap or label. The band text
reproduced here is therefore identical in both blobs. Cited so the next reader who hashes the
file does not read a stale citation as a freeze breach.

- **±0.5 % on `p2/p1`** — *principle: the reference class plus the second-order requirement.*
  The reference is exact analytic (zero uncertainty), and `p2/p1` is read from patch face
  centres with `interpolate false` — no interpolation, no detector, no fit — so the only error
  term is discretization. `rhoCentralFoam` is nominally second-order and each level halves `h`
  exactly, so a medium-level error of order 1 % must fall ≈4× at fine. **±0.5 % is that
  requirement stated as a band.** It is a real bar: a first-order-behaving solve lands near
  0.5–1 % and fails it.

- **±2.0 % on β** — *principle: the detector's own quantization floor, from mesh geometry only.*
  β is detected then fitted, so its floor is quantization, not physics. For **the in-scope
  pair, wedge M2.5 θ10**: domain height H = 0.9940, fine Δy = H/80 = 0.01242, σ = Δy/√12
  propagated through the frozen 5-station least-squares slope and through β = atan(m) gives
  **1σ = 0.969 %, 2σ = 1.937 %**. **The band is the rounded-up 2σ floor: 2.0 %.** No CFD value
  enters this arithmetic; it is reproducible from `grade_f3.py::beta_quantization_pct`. A
  tighter band would gate the detector's discrete arithmetic rather than the solver.

- **±1.0 % on `cd`** — *principle: composition of the §4.1 budget over the panels that carry it.*
  `cd` is an integrated pressure force from OpenFOAM's own `forces` object — no detector, no
  fit — carrying two panels' worth of the surface-pressure budget (one compression, one
  expansion) plus corner smearing the wedge gate does not see. **±1.0 % = 2 × the ±0.5 % band,
  one band per panel.**

**Disclosure, made rather than concealed.** In drafting, this lane read on-disk values for the
**out-of-scope** pair `diamond/M2.0_eps7p125` (Annex D). **No in-scope measured value was read**
— the two in-scope run directories do not exist. And because every band above is carried over
verbatim from a document frozen before F3's first compute, **no band here could have been moved
by anything this lane read.**

---

## ANNEX B — the cap: which quantity, and checked when

**Which quantity.** `wall_s × ranks ÷ 60`, **measured by the launcher across the full run
envelope** — process spawn to exit, including case build, `blockMesh`, `checkMesh`, the solve
and the `postProcess` sampling. **`ExecutionTime` is NOT this quantity and does not govern**;
it excludes startup, meshing and sampling, and it is not wall time.

**This is not a hypothetical distinction, and it is registered because F3 measured the gap.**
For the same ten runs F3 has two figures on disk: `F3_CONVERSION_RUN_LEDGER.json`
(launcher-measured envelope) totals **2,005.06 core-s**, while `F3_CONVERSION_GRADED.json`
(runner-measured `wall_s` from `result.json`) totals **1,972.95 core-s** and reports
`actual_core_minutes: 32.8825`. **A gap of 32.11 core-s — 1.6 % — and two available numbers.**
F3's cap check used the launcher figure; **this rung names that figure and only that figure**,
so no one can pick the one that passes.

**Costing.** Predictions are F3's frozen `rerun_f3.py::PRED` values: **wedge 148.1**, **diamond
189.8 core-s** (total 337.9). Calibrated by F3's **measured** ratio **1.1290** — derived on the
launcher basis (2,005.06 measured ÷ 1,775.90 predicted over the ten launched runs), the same
basis this cap governs, per `BAND_ONLY_RULING_2026-08-25.md` condition 4:

| run | predicted | × 1.1290 calibrated | per-run cap (× 1.20 headroom) |
|---|---|---|---|
| `wedge/M2.5_th10/fine` | 148.1 | 167.20 core-s | **200.65 core-s** |
| `diamond/M2.5_eps5/fine` | 189.8 | 214.28 core-s | **257.14 core-s** |
| **total** | **337.9** | **381.49 core-s = 6.358 core-min** | **457.79 → HARD CAP 457.8 core-s = 7.630 core-min** |

**When it is checked — INCREMENTALLY, and the launcher HALTS AND REPORTS on a crossing.**
Three enforcement points, all live:
1. **Before each run**: `spent + calibrated_pred(run) × 1.20 > CAP` → **do not launch; halt and
   report**. Registered outcome: the unlaunched row is `PENDING`, never a killed row.
2. **After each run**: `spent > CAP` → **halt; launch nothing further; report**.
3. **During**: an unconditional polled watchdog on `spent + live` → terminate and mark `KILLED`.
   A `KILLED` run's rows grade `NOT A RESULT`, never a value.

**This cap is NOT totalled only at the end.** That failure mode has a name in this team — F4's
cap was evaluable exactly once, after every core-minute was spent: a post-hoc audit wearing a
guard's name. With two runs, points 1 and 2 give **four** cap evaluations, two of them before
any compute at all. An overrun stops the run; it does not get a new budget.

---

## ANNEX C — the completion rule (standing rule 4)

Inherited from `grade_f3.py::completion_check`, byte-unchanged, with its **declared adaptation
for a transient adjustable-timestep solver** (F3 §5): `rhoCentralFoam` is explicit and
density-based, so the steady-iteration clause `ExecutionTime count == endTime` **does not
apply** and is declared inapplicable rather than silently dropped. Live clauses: `rc = 0`; an
`End` line; **fields present**; the **age guard** (every field at the last time newer than the
case's own `0/`); and the completion limb.

**The completion limb is `latest + dt_final > endTime`, NOT `latest >= endTime`.** With
`adjustTimeStep yes` the final step lands on either side of `endTime` — `wedge/M3.0_th15/fine`
ends at `2.5999683` against `endTime 2.600000`, short by 3.17e-5 — and the naive form refuses a
genuinely complete run. `grade_f3.py:191` implements this as `|last − endTime| ≤ maxDeltaT`
with `maxDeltaT = 1e-3` read from the case's own `controlDict`, which is the same one-step
allowance expressed against a value the case declares. **It is not a two-sided tolerance band
chosen after seeing which runs it admits** — `maxDeltaT` is an input, frozen in the case at
build time, and no epsilon is fitted here.

**Pre-existing-directory guard, before any case is built.** The launcher refuses (exit 2) if
either target directory exists, or contains a `0/` or any time directory, **before it invokes a
generator** — because the age guard dates a run from `0/T`, and a pre-existing tree defeats it.
Verified at drafting: **the run root and both target directories are absent.** *(F3's 2026-07-28
run trees do exist at `F3_runs/wedge/M2.5_th10/fine` and `F3_runs/diamond/M2.5_eps5/fine`, one
directory level up. This rung's root is disjoint from them and the guard covers the difference;
the old trees are never read and never written.)*

---

## ANNEX D — convergence: **THE OPEN ITEM, AND IT IS A SUPERVISOR'S RULING, NOT A LANE'S**

Standing rule 5 clause 1 — *any level not iteratively converged or not plateaued → NOT A RESULT*
— applies **per level**, so it binds a band-only row exactly as it binds a triple.

**What the artifacts can actually carry, measured on disk, not assumed:**

- **A residual-based convergence gate is IMPOSSIBLE on this solver, and would be a gate quantity
  that could never be non-zero.** `rhoCentralFoam` solves ρ, ρU, ρE with the `diagonal` solver —
  a direct solve. Every one of the **8,071** `Time =` blocks in
  `conversion_2026-08-24/runs/wedge/M3.0_th15/fine/log.rhoCentralFoam` reports
  `Initial residual = 0, Final residual = 0, No Iterations 0` for **all four fields**. The
  residual is **structurally, identically zero**. **Registering it would be the exact defect two
  teams have already been caught by. It is not registered.**
- **The wedge has NO time series at all — exactly ONE reading.** `run_wedge_case.py:87-88`
  invokes `postProcess -func sampleDict -latestTime` **after** the solve, so
  `postProcessing/surfaceSampleDict/` holds **one** time directory (confirmed: `2.5999683`,
  one entry). **One reading is not evidence of convergence.**
- **The diamond has a series of THREE points.** `forces1` uses `writeControl writeTime` against
  `writeInterval = endTime/3`, so `force.dat` holds **3 data rows** (out-of-scope pair
  `M2.0_eps7p125`: t = 2.00, 4.00, 6.00).

**Therefore a Class C convergence gate — sustained window floor, trend fit rejecting a growing
series, explicit stationarity test able to report NOT stationary, and refusal below a minimum
sample count — CANNOT BE FED by these artifacts.** Element 4 is decisive and is precisely the
element that gets quietly dropped because dropping it always makes a run gradeable. **It is not
dropped here.** A Class C gate registered against 1 sample (wedge) and 3 samples (diamond) would
**refuse**, and a gate registered knowing it will refuse is theatre.

**F3's own registered reading, stated so the successor does not silently differ.** F3 §4.4
clause 1 reads *"any level failing the completion rule (§5) → NOT A RESULT"* — F3 substituted
the **completion rule** for rule 5's *"iteratively converged or plateaued"*, on the reading that
an explicit transient marched to a fixed endTime set as N flow-throughs has no iteration to
converge, and that temporal steadiness is delivered **by design** through the flow-through
count. **That reading is a design argument, not a measurement**, and F3's two executed
band-only `PASS` rows were graded under it.

**The choice, put to cfd-supervisor. This lane does not take it, because each limb moves a
label or a threshold, and one of them retro-impugns F3's closed rows.**

- **Form 1 — MEASURE steadiness.** Re-author the runners in this rung's own path so a genuine
  time series exists (sample the wedge surface on a cadence during the solve; raise the diamond
  `forces1` cadence), then register a full four-element Class C gate. **Cost:** the byte-unchanged
  reuse of `run_wedge_case.py` / `run_diamond_case.py` is lost — the bands are unaffected, since
  they live in `grade_f3.py` which stays frozen, but the "identical inputs" defence weakens, the
  runners' `sorted(glob(...))[-1]` time-directory resolution is **lexicographic, not numeric**
  (`run_wedge_case.py:94`, `:131`) and becomes wrong the moment there is more than one sample
  time, and the cost uplift must be re-costed. **This is the only limb that produces measured
  convergence evidence.**
- **Form 2 — INHERIT F3's reading, and say so on every row.** Fire as F3 would have. Every row
  carries, in addition to the band-only limitation, **"temporal steadiness ASSUMED from the
  flow-through count, NOT MEASURED"**. Adds one gating, downgrade-only check available at zero
  extra cost on the diamond: if the last-to-previous relative change in `force.dat` exceeds
  **0.1 % = one tenth of the ±1.0 % band** — *derived from the band, an order-of-magnitude
  separation between a tolerance and the drift permitted beneath it, fixed before any in-scope
  value is read* — the row is **NOT A RESULT**. **The wedge gets no steadiness check of any
  kind, and its rows must say so.** Consistent with rule 5's asymmetry: this can only downgrade.
- **Form 3 — do not fire.** The rung is worth 6.358 core-min only if its rows say something the
  existing record does not. If Form 2's answer is knowable from F3's own runs, that is an
  argument for Form 3, and it is a fair one.

**No limb is selected here. The document cannot be frozen until one is.**

---

## ANNEX E — planted-zero controls, and the both-direction proof

**Planted zeros (standing rule 3), inherited live and byte-unchanged from `grade_f3.py`,
each refusing (exit 2) if the reader cannot see its plant:** PZ-1 surface pressure
(`PLANT_P = 1.234e-03` additive into the pressure column), PZ-3 β re-derived independently from
the stored shock locus with `PLANT_SLOPE = 1.000e-02`, PZ-4 `cd` re-derived independently from
`force.dat` with `PLANT_FX = 1.234e-05` and required to move by exactly the amount the
definition demands. Plus **PZ-A**, this rung's own: the limitation annotator is planted in
**both** directions (a band-only row that must be annotated, a triple row that must not), and
the search that checks the wording against the supervisor's ruling on disk is itself planted
with a phrase known present and a phrase known absent — because a searcher returning True for
everything, or False for everything, would make the wording check meaningless. The wording is
checked against the **ruling file**, never against this grader's own constant: a check comparing
a constant with itself cannot fail.

**Each gate quantity CAN take both a failing and a passing value on this solver's real on-disk
output — demonstrated from F3's executed rows, not asserted:**

| quantity | a PASS on disk | a non-PASS on disk |
|---|---|---|
| wedge `p2/p1` (G-F3-1) | M3.0_th15 `PASS`, dev **+0.00733 %** | M2.0_th15 **`NOT A RESULT`**, dev +0.0722 %, triple `OSCILLATORY` (R = −0.0875) |
| wedge β (G-F3-2) | M2.0_th15 `PASS`, dev **−1.4353 %**; M3.0_th15 `PASS`, dev −0.9593 % | cone β (G-F3-4) **`GATE FAIL`** on the same detector and the same ±2.0 % band |
| diamond `cd` (G-F3-5) | M2.0_eps7p125 `PASS`, dev **−0.2579 %** | — see below |

All values from `F3_CONVERSION_GRADED.json`. **Stated honestly: G-F3-5 has no executed
`GATE FAIL` or `NOT A RESULT` on this suite.** What is shown for it is that the reader produces
a real non-zero `cd` from `force.dat` and that PZ-4 moves it by a planted increment — i.e. the
quantity is not structurally pinned — **not** that a diamond row has ever failed. That gap is
recorded rather than papered over.

---

## ANNEX F — instrument discipline, and **a CONFIRMED DEFECT that must be repaired before freeze**

**Flag-proof refusals.** No `assert` carries a refusal, guard, control or gate anywhere in this
rung's path — `python3 -O` deletes every `assert`, so all refusals are `sys.exit(2)` via
`refuse()`. **Measured by AST, not by grep: `grade_successor.py` has 0 `Assert` nodes;
`grade_f3.py` has 0.** Both were driven under `python3 -O`; the frozen-bytes assertion and the
PZ-A controls executed and held.

**DEFECT — an unconditional success print, confirmed by mutation.** `grade_successor.py`'s
`--selftest` path runs `controls = selftest_annotator()` and then prints `SELFTEST GREEN`
**without inspecting `controls`**. A mutation replacing that call with `controls = []` — the
entire planted-zero control removed — **still printed `SELFTEST GREEN` and still exited rc = 0**
under `python3 -O`. *(Mutation performed on a scratch copy; the file on disk was not modified.)*
This is the pattern already measured on a cfd instrument printing "PLANTED CONTROL PASSED" on an
estimator returning zeros. **Required repair before freeze:** the success claim moves **inside**
the passing branch and is coupled to the controls — the expected control count and every
`passed` flag are checked, and the check refuses otherwise — **so that removing the check removes
the claim.** The same rule binds the launcher: no `LAUNCH OK`, `CAP RESPECTED` or `COMPLETE`
print may sit outside the branch that established it.

**Build guards.** Guards produce **inputs**; a build guard that fails silently produces a wrong
input, and the remedy for a wrong input is a **re-registration, not a patch to a fired file**.
Every guard in this rung's launcher — the pre-existing-directory guard, the frozen-bytes
assertion, `checkMesh` acceptance and the cap checks — is written flag-proof in the **new** path,
is **driven under `python3 -O` and REQUIRED TO REFUSE** on a deliberately broken input before any
launch, and an AST check requiring **zero `Assert` nodes** runs over every file in this rung's
path as a launch precondition. `set -e` does not gate in this harness; every shell assertion is
written `|| { echo ABORT; exit 1; }`.

**Cost basis measured at launch by the launcher.** The launcher records HEAD, UTC and the machine
load **in its own invocation**, to `LAUNCH_HEAD.txt` / `LAUNCH_LOAD.txt` under this rung's root.
**A load figure relayed from a supervisor's brief is not a measurement and is not accepted** —
that error is on this team's board.

---

## ANNEX G — what this lane could NOT derive from a principle, stated plainly

1. **The convergence element (Annex D).** No Class C gate can be fed by the frozen artifacts.
   Every route out moves a label, a threshold or the inputs. **Left out rather than invented,
   and referred.** Per the brief's own instruction: where a gate cannot be derived from a
   principle, it is omitted, not fabricated.
2. **Whether `cd` has ever produced a non-PASS on this suite.** It has not (Annex E). The
   both-direction proof for G-F3-5 rests on reader sensitivity, not on an executed failing row.
3. **Whether either in-scope run will PASS.** Nothing was run; no in-scope gate quantity was
   observed. No prediction is offered and none should be read into any number in this document.
4. **Whether any other campaign leans on band-only rows as credentials.** Not swept — escalated
   as cross-family in `BAND_ONLY_RULING_2026-08-25.md` §7 and still open.

---

## COST CALIBRATION (standing rule 12)

**Compute incurred drafting this document: 0.0000 core-minutes, $0.00.** No row is added to
`docs/COST_CALIBRATION.md` — no process consuming compute completed, and a calibration row for
zero compute would put a fictitious measurement in the ledger. F3's own calibration stands at
rows **C-66 / C-68**, ratio **1.1290** over launched runs only, and is not restated as new.
**On this rung's completion, an estimate-versus-actual row is owed**: actual launcher-measured
core-minutes against the 6.358 core-min expectation and the 7.630 core-min cap, with the ratio,
the attribution, and dollars marked **derived, not measured**.

---

## STANDING RULES THIS DOCUMENT IS BOUND BY

Rule 1 (verdict vocabulary, six words, no synonyms) · Rule 2 (frozen before compute; **F3's cap
is NOT altered, re-partitioned or reinterpreted by this document**) · Rule 3 (planted zeros,
Annex E) · Rule 4 (strict completion, Annex C) · Rule 5 (triple gating; clause 2 not evaluated
for a band-only row, clause 1 open at Annex D) · Rule 6 (no frozen file edited) · Rule 7
(**submissions parked** — nothing here is sent, filed or registered outside this box) · Rule 10
(private-index git protocol) · Rule 12 (core-minutes, Annex B) · L-332 (no `assert` carries a
refusal, Annex F).
