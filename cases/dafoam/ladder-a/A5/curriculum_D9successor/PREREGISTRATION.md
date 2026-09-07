# DRAFT — NOT FROZEN — awaiting supervisor check-1 read and freeze

**`D9successor` — U-BEND PRESSURE-LOSS MINIMISATION WITH A MESH-QUALITY CONSTRAINT. Successor to `D9`.**

Drafted 2026-09-06 by a `lab-lane` on the dafoam-supervisor's brief, under Sanaa's directive `4ae4b33`
(the D9 fix must be tried and recorded). **The freeze and the enqueue belong to the dafoam-supervisor
and are not taken here.** No gate, threshold, cap or label in this file is registered until that
supervisor freezes it by sha. **This lane ran NO compute** — the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D9SUCCESSOR-a5-ubend-opt/` **does not exist at this draft**,
and neither does any `d9succ_out.json` anywhere on this box.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed or uploaded anywhere
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**THE OBJECTIVE, DESIGN VARIABLE, OPTIMISER, IMAGE AND `np` DO NOT MOVE IN THIS ITEM.** They are
carried forward byte-identical from `D9` (`cases/dafoam/ladder-a/A5/curriculum_D9/PREREGISTRATION.md`):
`OBJ.val = TP1 − TP2`; `shapexUpper` only, 27 components, bounds ±0.04, scaler 25.0; SLSQP; `np = 1`;
patched image `dafoam-idwarp-rot:v1` (`sha256:2927768a…e30f6d35`). **This item changes exactly one
thing about the optimisation: it adds a mesh-quality inequality constraint** so the optimiser cannot
drive the mesh past DAFoam's non-orthogonality limit. Everything else is `D9` re-cited, not re-derived.

---

## 0. WHY A SUCCESSOR, AND WHAT THIS ITEM ACTUALLY CHANGES

`D9` (frozen before its run root existed, graded 2026-08-25, **`NOT A RESULT`**, **46.77 core-min of a
110.0 core-min cap**) returned `NOT A RESULT` for a **mesh-quality** reason, not a solver-capability
reason. Two independent negatives, both measured
(`cases/dafoam/ladder-a/A5/curriculum_D9/RESULTS.md`):

1. **G9-3 `GATE FAIL`** — the SLSQP driver reported failure (`driver_failed=True`,
   `driver_iter_count=47` against `maxit=20`). Objective did move,
   `52.34521691559307 → 50.27935096533333` (2.06587, 3.947 %), but the gate maps *driver failed* to
   `GATE FAIL` irrespective of magnitude (`RESULTS.md` §1, G9-3 row).
2. **G9-4 `NOT A RESULT`** — only **1 of 4** registered endpoint FD steps produced a table. A plateau
   needs ≥ 3 consecutive usable steps and one survived (`RESULTS.md` §1, §2).

**The measured cause of the missing FD tables is the design point itself, not the harness**
(`RESULTS.md` §2, read in full):

> *"The optimised endpoint is already outside the case's own declared mesh-quality envelope. The
> unperturbed endpoint geometry measures `maxNonOrth = 80.930` against the case's own
> `checkMeshThreshold { maxNonOrth 70; }`. SLSQP drove the design there and DAFoam did not stop it,
> because that metric errors only on face-pyramid inversion, not on exceeding 70."*

Three of the four FD stages then exited `rc=1` with `AnalysisError: "Mesh quality error!"`
(`dafoam/mphys/mphys_dafoam.py:330`), `OOMKilled=false`, because a central-difference perturbation of a
large-negative design variable inverts cells in the already-warped mesh (`RESULTS.md` §2 table):

| step | `rc` | peak `maxNonOrth` reached by the perturbation |
|---|---|---|
| h = 1e-5 | **0** (survived) | 81.73 |
| h = 1e-4 | 1 | 89.46 |
| h = 1e-3 | 1 | 137.76 |
| h = 1e-2 | 1 | 116.01 |

`D9/RESULTS.md` §10 option 2 states the successor plainly, and this item **is** that option:
*"The optimisation ran without a mesh-quality constraint and terminated at `maxNonOrth = 80.93`
against the case's own threshold of 70. A follow-on that constrains the optimiser to the declared
quality envelope would produce an endpoint at which an FD sweep is performable."*

**This item registers that follow-on — with one honesty this draft insists on and §2 quantifies:
the constraint moves the ENDPOINT into the envelope; it does not by itself guarantee that every
registered FD step is performable at that endpoint, because the two largest D9 steps invert cells by a
margin the ~11° of headroom cannot close.** The item is therefore built around a headline gate the
constraint *can* deliver (`G-MESH`) and a second gate it is *tested against* (`G-FDPERF`), with the
honest `NOT A RESULT` outcome registered before compute.

---

## 1. THE MECHANISM — DAFoam's `meshQualityKS` FUNCTION AS A pyOptSparse INEQUALITY CONSTRAINT

### 1.1 The mechanism, and it is a real DAFoam capability, not a tutorial invention

DAFoam expresses a mesh non-orthogonality limit as a **function of type `meshQualityKS`** — a
Kreisselmeier–Steinhauser (KS) smooth aggregation of a per-face mesh-quality metric, computed as a
differentiable DAFoam function (`addToAdjoint: True`, so it carries an adjoint gradient) and then
registered to the optimiser as an inequality constraint through the driver's `addConstraint` /
`add_constraint` API.

**On-disk source citation — the authoritative one (the C++ function itself, in the patched image this
item buys):**

- `/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DAFunction/DAFunctionMeshQualityKS.C`
  and `.H` (inside image `dafoam-idwarp-rot:v1`, `sha256:2927768a…e30f6d35`).
  Header: *"Child class for mesh quality with KS function"*; `TypeName("meshQualityKS")`
  (`.H`, class declaration); it is registered into the DAFoam function run-time selection table
  (`.C:16`, `addToRunTimeSelectionTable(DAFunction, DAFunctionMeshQualityKS, dictionary)`), i.e. it is
  a first-class DAFoam function, selectable by the string `"meshQualityKS"`.
- `calcFunction()` (`.C:70`) reads two dictionary keys — `coeffKS` (`.C:33`) and `metric` (`.C:35`) —
  and computes, per the source, `functionValue = (1/coeffKS) · log( Σ_faces exp(coeffKS · m_face) )`
  (`.C:143`, `:186` `reduce(...sumOp)`, `:188` `log(functionValue)/coeffKS`). `metric` accepts exactly
  **`faceOrthogonality`, `nonOrthoAngle`, or `faceSkewness`** — any other string is a fatal error
  (`.C:180-181`). For `metric == "nonOrthoAngle"` (`.C:106-135`) each face's non-orthogonality is
  converted to **degrees** (`nonOrthoAngle[faceI] = angleDeg`, `.C:135`) before aggregation, so the
  function value is in the same units (degrees) as the case's `checkMeshThreshold { maxNonOrth 70; }`.

**On-disk usage citations — how it is wired to the optimiser, both API generations:**

- **Older `optFuncs`/`PYDAFOAM` API** — `/home/ubuntu/dafoam-tutorials/UBend_Channel/runScript_meshQualityConstraint_v2.py`
  (this is the **same U-bend case D9 is built on**). `daOptions["objFunc"]["nonOrtho"]["part1"]` is
  `type: meshQualityKS`, `metric: nonOrthoAngle`, `coeffKS: 1.0`, `source: boxToCell` over the whole
  domain, `addToAdjoint: True` (`:79-90`); it is then registered to pyOptSparse at `:207`
  (`DVCon.addConstraintsPyOpt(optProb)` for geometric cons) and `:213`
  `optProb.addCon("nonOrtho", lower=0, upper=70.0, scale=1)` — **the non-orthogonality angle capped at
  70°, the identical envelope D9's endpoint violated.**
- **Newer mphys / OpenMDAO API — the one `D9` itself uses** —
  `/home/ubuntu/dafoam-tutorials/UAV_Propeller/runScriptAero.py`. Same `meshQualityKS` function
  definitions (`:103-122`, `skewness` metric `faceSkewness`, `nonOrtho` metric `nonOrthoAngle`,
  `coeffKS 1.0`), exposed by `aero_post.mphys_add_funcs()` and registered to the driver as an
  OpenMDAO constraint: `self.add_constraint("hover.aero_post.nonOrtho", upper=80.0, scaler=0.1)`
  (`:292`; the companion `skewness` cap is `:291`). **This is the exact API surface `d9_run_script.py`
  uses** (`add_objective`/`add_constraint` on an OpenMDAO `Top`, `pyOptSparseDriver`,
  `scenario.aero_post` funcs) — so the mechanism transfers to D9's instrument with a one-function
  addition to the `"function"` block and one `self.add_constraint(...)` line.

### 1.2 The one caveat that reaches a gate — KS is a smooth OVER-BOUND of the true max, not the max

From the source (`.C`), the KS aggregate satisfies the standard KS bound:
`max_face(m) ≤ KS ≤ max_face(m) + log(N_faces)/coeffKS`. With `coeffKS = 1.0` and this mesh's face
count `N ~ O(10⁴)`, the upper slack `log(N)/coeffKS ≈ 9–10°`. **Consequences, both registered here:**

1. **Constraining `KS(nonOrthoAngle) ≤ 70` is CONSERVATIVE for the true max**: because `KS ≥ true max`,
   `KS ≤ 70 ⟹ true max ≤ 70`. The constraint cannot leave the true maximum above 70 — it can only
   drive it *below* 70 (possibly well below, by up to the slack). **The gate `G-MESH` (§3.1) is
   therefore evaluated against the RAW `checkMesh` `maxNonOrth` read from the endpoint mesh, never
   against the KS value the optimiser saw** — the raw number is what D9's failure was measured in
   (80.93), and it is what a plateau's feasibility depends on.
2. **`coeffKS` is a freeze-time tuning knob with a hard failure mode named in the source**: too large
   and `exp(coeffKS · angle)` overflows — `.C:148-149` aborts with *"KS function summation term too
   large! Reduce coeffKS!"*. The tutorials use `coeffKS = 1.0` for `nonOrthoAngle`; at angles ~80° that
   is `exp(80) ≈ 5.5e34`, far under double-precision overflow, so `1.0` is safe and is the value this
   draft proposes to carry. **The value is registered in §8; it is not chosen after seeing a run.**

---

## 2. THE HARD, HONEST PART — WHY THE CONSTRAINT MOVES THE ENDPOINT BUT MAY NOT, BY ITSELF, MAKE ALL FOUR D9 STEPS PERFORMABLE

This section is the reason this draft does **not** promise what D9's §10 option 2 phrased optimistically.
It is built entirely from D9's **measured** numbers.

### 2.1 The FD-feasible step window is squeezed from BOTH sides, and the measurements bound it

**From above — the mesh-inversion ceiling** (`D9/RESULTS.md` §2). At the D9 endpoint (base
`maxNonOrth = 80.93`) the perturbations reached: `h=1e-5 → 81.73` (survived), `h=1e-4 → 89.46`,
`h=1e-3 → 137.76`, `h=1e-2 → 116.01`. Cell inversion trips at `maxNonOrth ≈ 89`
(`***Error in face pyramids`, `RESULTS.md` §2 point 2). Lowering the **base** from 80.93 to ≤ 70 buys
roughly **11° of headroom**. Applying that shift to the measured peaks: `h=1e-4 → ~78` (**now below the
~89 ceiling — predicted performable**); `h=1e-3 → ~127` and `h=1e-2 → ~105` (**both still far above
~89 — predicted to STILL invert**, because their peaks are step-driven and 11° does not close a
38–57° excess).

**From below — the truncation/noise floor** (`D9/RESULTS.md` §4). The one D9 step that survived,
`h=1e-5`, showed a **near-constant additive `J_an − J_fd` offset** (mean `+6.379e-02`, stdev/mean
3.26 %), the classical signature of a step **too small** — the difference quotient dominated by the
primal's iterative-convergence noise (`≈ 2.5e-8` relative to `OBJ`), not by truncation. So `h=1e-5`
(and anything smaller) is **below the plateau** and does not qualify as a usable step.

**The window that remains is therefore roughly `[1e-4, ~2e-4]`** — larger than the noise floor,
smaller than the inversion ceiling at a 70° base (`8.5°` per `1e-4` × step ≤ ~19° headroom ⟹ step
≲ 2.2e-4). **A window that narrow may not contain the three distinct usable steps a plateau needs.**

### 2.2 What this means for the gate design, stated before compute

- The mesh-quality constraint **reliably delivers `G-MESH`** (endpoint in the envelope). That is the
  fix Sanaa's directive `4ae4b33` requires be tried and recorded, and it is the headline.
- The mesh-quality constraint **does NOT reliably deliver a demonstrated plateau**, because the FD
  step rule collides with a squeezed feasible window. **This is registered as a predicted risk, with
  its `NOT A RESULT` outcome written in advance (§3.3).** A successor that also **tightens the primal**
  (the D6RF4 mechanism — lower the noise floor to widen the window from below) may be required; **this
  draft does NOT make that change** (it is a second variable, and mixing two changes forfeits the
  attribution the ladder exists to protect) and flags it as a supervisor decision in §8.
- Because the two largest D9 steps are predicted to invert regardless of the constraint, this item
  **re-registers the FD step set** — a legitimate move only in a **new** pre-registration
  (`D9/RESULTS.md` §10 point 1: *"A new item with its own frozen sweep is the only legitimate
  route"*). The new set is chosen **a priori from the measured sensitivity and ceiling of §2.1, NOT
  from which D9 steps crashed** (§2.3).

### 2.3 The re-registered FD step set — derived a priori, frozen here, never chosen after seeing crashes

Registered steps: **`h ∈ {5e-5, 1e-4, 2e-4}`**, plus **one probe step `h = 1e-3` registered as a
falsifier expected to invert the mesh** (§6, `F-CEIL`). Derivation, entirely from §2.1's measured
quantities and fixed before any run:

- Lower bound `5e-5`: above the noise floor (D9's `1e-5` was below it; `5e-5` is 5× the noise-dominated
  step, the smallest that has a truncation-dominated signal by D9's own §4 arithmetic).
- Upper bound `2e-4`: the largest step whose predicted perturbation peak
  (`70 + 8.5°·(2e-4/1e-4) = ~87°`) stays under the `~89°` inversion ceiling **with margin** at a
  constrained endpoint.
- The three usable steps are **the frozen set itself**, and the reference step is fixed by the D9 rule
  carried verbatim: **longest qualifying plateau window, ties → lowest start index, middle step, per
  component** (`D9/PREREGISTRATION.md` §5). `PLATEAU_MIN_STEPS` stays **3**; the frozen set has exactly
  three usable members, so **all three must produce a table AND lie in a common plateau** for a
  gradeable component — a strictly harder bar than a set of four, disclosed as such.
- `1e-3` is a probe, not a usable step: it is predicted to `AnalysisError` and its purpose is to show
  the ceiling is real at the constrained endpoint, exactly as D9 measured it at the unconstrained one.

---

## 3. GATES — REGISTERED BEFORE COMPUTE, EVERY ONE POST-HOC

### 3.1 ⚠ `G-MESH` — **THE HEADLINE. The fix works: the constrained optimum is inside the case's own envelope**

> **`G-MESH`. The constrained-optimum endpoint mesh, measured by `checkMesh` on the unperturbed
> optimised geometry, must report `maxNonOrth ≤ 70.0` — the case's own
> `checkMeshThreshold { maxNonOrth 70; }` (`D9/RESULTS.md` §2, point 1).**
>
> **The number graded is the RAW `checkMesh` `Mesh non-orthogonality Max`, read back from the endpoint
> mesh's `checkMesh` log, NOT the KS aggregate the optimiser optimised against** (§1.2). Reported
> beside the verdict, always: the raw `maxNonOrth`, the KS constraint value the driver reported, and
> the gap between them (a measurement of the KS slack of §1.2).
>
> `PASS` if raw `maxNonOrth ≤ 70.0`. `GATE FAIL` if raw `maxNonOrth > 70.0` (the constraint did not
> hold at convergence — a reportable finding that the mechanism as configured does not bind).
> `NOT A RESULT` if the endpoint mesh or its `checkMesh` log is absent, or the value is non-finite.

**Registered prediction, before compute, so it can be wrong on the record:** because `KS ≥ true max`
(§1.2), a converged constraint `KS ≤ 70` forces raw `maxNonOrth ≤ 70`, and the KS slack (~9–10°) means
the raw max likely lands **below** 70 (≈ 60–70). D9's unconstrained endpoint was **80.93**; the
constraint is predicted to move it below 70. **PASS predicted with margin.** If the driver terminates
infeasible (constraint violated at the last major), that is `GATE FAIL` and is the finding.

### 3.2 ⚠ `G-FDPERF` — **the tested claim: the constrained endpoint admits an FD verification**

> **`G-FDPERF`. At the constrained optimised design point, at least `3` of the `3` registered usable FD
> steps `{5e-5, 1e-4, 2e-4}` (§2.3) must each produce a complete `check_totals` table (`rc=0`, 55 of
> 55 primals, 27 `J_an` and 27 `J_fd` entries).**
>
> `PASS`-eligible (feeds `G-GRAD`) if all 3 tables exist. `NOT A RESULT` if fewer than 3 tables exist —
> the plateau cannot be demonstrated from < 3 steps, exactly as D9's G9-4 (`D9/RESULTS.md` §1).
> `REFUSE (exit 2)` if a table is at a design point that is not the optimised endpoint (the D9 physical
> plant, §5).

**Registered prediction, and it is deliberately guarded:** §2.1 predicts `1e-4` and `2e-4` performable
at a ≤ 70° base and `5e-5` performable (above inversion risk). **All three are predicted to survive —
but the margin at `2e-4` is thin (~87° vs ~89° ceiling), and the plateau's *existence* across them is
NOT predicted** (that is `G-GRAD`). **The honest registered outcome (§3.3) is that this gate, or the
plateau inside it, may still read `NOT A RESULT`, and that is a good result** — it would measure that
the mesh-quality constraint alone is necessary but not sufficient for an FD-verifiable endpoint, which
is precisely the finding that motivates the primal-tightening successor named in §8.

### 3.3 ⚠ `G-GRAD` — **the endpoint gradient verification, D9's G9-6 carried verbatim over the new steps**

> **`G-GRAD`. Over the GRADEABLE components (those with a demonstrated plateau across the 3 usable
> steps), aggregate `Σ|J_an − J_fd(h*)| / Σ|J_fd(h*)| ≤ 5.0e-2` with `0` sign flips.**
>
> `PASS` if in band and no flips. `GATE FAIL` if out of band or ≥ 1 flip. `NOT A RESULT` if the
> gradeable fraction `N/27 < 0.70` (< 19 of 27) — the D9 N-of-M floor carried unchanged
> (`D9/PREREGISTRATION.md` §4, `MIN_GRADED_FRACTION = 0.70`). **Zero gradeable components → REFUSE**,
> never an aggregate over an empty set (D9's L-302 lesson, `D9/PREREGISTRATION.md` §5b).

**No aggregate is ever quoted over components whose FD was not shown to lie in a plateau** — the D9
grader's `--selftest` units B, C, F, G, Q enforce this and are carried (`D9/RESULTS.md` §3, the
"NO AGGREGATE IS QUOTED" clause). The idx16-class named in advance in D9 (idx 8, 16, 17;
`D9/PREREGISTRATION.md` §5c) is **carried and re-named here**, with the same consequence: a component
FD-ungradeable by construction is excluded with the count printed, split into named-in-advance and
not-named-in-advance.

### 3.4 CARRIED FROM `D9` UNCHANGED

`G9-0` (stage completeness / count == 27), `G9-1` (`delta_repeat` measured before any FD step is
sized), `G9-2` (calibration major first; buy-timeout by the frozen rule
`T_opt = min(3600, ceil(t_cal·(1+MAXIT_OPT)))`), `G9-7` (`sched_affinity` read back per stage, mismatch
hits the cost-attribution row only, never the derivative verdict). Bands, thresholds and labels are
`D9`'s, re-cited and not re-derived. **Probe verdict = worst of the gates in the order
`PASS/GATE REACHED < GATE FAIL < NOT A RESULT < BLOCKED`.**

**REGISTERED HONEST OUTCOMES, written before the run:**
- If the constraint holds (`G-MESH PASS`) but the endpoint still does not admit ≥ 3 FD tables, or the
  three admit no common plateau, the item is **`NOT A RESULT`** and that is a **good** result: it
  measures the constraint as necessary-not-sufficient and motivates the primal-tightening successor.
- The objective **magnitude is REPORTED, never gated** — carried verbatim from `D9/PREREGISTRATION.md`
  line 2. A constrained optimum will generally be **worse** (higher `OBJ`) than the unconstrained
  `D9` optimum, because the feasible set is smaller; **that is expected and is not a failure.** The
  registered question is whether the constrained endpoint is FD-verifiable, not whether it is a lower
  objective than D9's infeasible one.

---

## 4. THE PLANT (rule 3), STRICT COMPLETION (rule 4), AGE GUARD — ALL CARRIED FROM `D9`

- **Reader plant** — `PLANT = 1.234e-03` written into `J_an[0]` of a copy of the endpoint record, read
  **back from disk**, difference compared to the planted value; the grader **REFUSES (exit 2)** if the
  reader cannot see it (`D9/PREREGISTRATION.md` §5a.1). Carried verbatim.
- **Physical plant** — the optimiser must have MOVED the design point; a bit-identical-to-baseline
  `shapexUpper` at the endpoint → REFUSE (`D9/PREREGISTRATION.md` §5a.2). Carried, and now doubly
  relevant: a constrained optimum that never moved would defeat both the objective and the constraint.
- **Strict completion (rule 4)** — the `check_totals`-stage equivalent used by D9 is carried: completed
  primal count == registered `1 + 2×27 = 55`, cross-checked three ways (`End` lines, DAFoam pseudo-time
  dirs, `checkMesh` blocks) (`D9/RESULTS.md` §6). `rc`, `docker inspect` exit code, `OOMKilled`,
  artifact presence and finite values are exercised per stage.
- **Age guard (rule 4)** — `NOT EXERCISED, disclosed BEFORE compute`, same reason as D9: DAFoam gzips
  `0/U → 0/U.gz` mid-solve, so the field the guard dates against ceases to exist during the run
  (`D9/PREREGISTRATION.md` §5d). The stronger PRE-LAUNCH substitute `COLDSTART_PROVED` is carried: each
  arm directory destroyed, re-copied from the anchor, and answer file / time dir / `0/U.gz` asserted
  ABSENT before the container runs. Disclosed as a `VERIFICATION_CHARTER.md` §2d.1 matter, four
  conditions enumerated as in `D9/PREREGISTRATION.md` §5d; **no gate, threshold, cap or label moves.**

---

## 5. COST — RE-PRICED AGAINST D9's MEASURED ACTUALS, PLUS THE CONSTRAINT'S OVERHEAD

**`cost_basis`: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED, not measured.** Unit:
core-minutes = wall_s × ranks ÷ 60. `np = 1` throughout, so ranks = 1.

**Measured anchors, all from `D9/RESULTS.md` §8a** (D9's own actuals, not a curriculum figure):
`cal` 1.4333; `rep1+rep2` 0.4666; `opt` (SLSQP, 47 evals) 7.0500; **one complete `check_totals` FD
stage 7.5667.**

| stage | count | basis | core-min |
|---|---|---|---|
| `cal` — `run_driver -maxit=1` | 1 | D9 actual | 1.4 |
| `rep1`, `rep2` — `run_model` | 2 | D9 actual | 0.5 |
| `opt` — `run_driver -maxit=20`, **now with the constraint** | 1 | D9 `opt` 7.05 × ~1.5 (one extra adjoint per major for the constraint gradient + the `meshQualityKS` function eval per primal) | 10.6 |
| `fd_*` — `check_totals` × **3 usable steps** `{5e-5, 1e-4, 2e-4}` | 3 | D9's measured complete-stage 7.5667 | 22.7 |
| `fd_probe` — `check_totals` at `1e-3` (falsifier `F-CEIL`, **expected to invert ~33–55 % in**) | 1 | D9's crashed-stage partial ≈ 3.8 | 3.8 |
| `mesh` — `checkMesh` on the endpoint geometry (`G-MESH`) | 1 | seconds, not separately metered | < 0.2 |
| | | **PREDICTED TOTAL** | **≈ 39** |

- **REGISTERED CAP: 120.0 core-min** — by the family's ADOPTED cap form
  `max(3.0 × estimate, 1.25 × (4/3) × estimate) = max(3.0×39, 1.6667×39) = max(117.0, 65.0) = 117.0`,
  rounded up to **120.0**. The margin is for **contention, not slack** (rule 12); an overrun STOPS the
  run and does not get a new budget. The launcher ASSERTS the enforced cap equals this literal, with no
  environment override (the D9 pattern, `D9/PREREGISTRATION.md` §6).
- Per-stage timeouts carried from D9: `cal` 900 s, `rep*` 600 s, `fd_*` 1200 s, `opt` by the frozen
  rule in `G9-2`.
- **$0.0334 predicted / $0.1026 at the cap — DERIVED, NOT MEASURED.** (39 core-min = 0.650 core-h ×
  $0.0513; 120 core-min = 2.000 core-h × $0.0513.) Both far under the $25 pre-authorisation.
- **Estimate-versus-actual is OWED AT COMPLETION** (rule 12): compare the pre-registered estimate
  against the ledger actual in core-minutes, state the ratio, attribute the gap (contention / waste /
  misprediction, waste named separately per `COMPUTE_BUDGET_CHARTER.md` §6), and land a row in
  `docs/COST_CALIBRATION.md`. **The specific quantity this item calibrates, named in advance: the
  `×1.5` constraint overhead multiplier on `opt`** — measurable as
  `ExecutionTime(opt, constrained) / 7.05` against the registered `1.5`.
- Lineage cost carried, not written off: `D9` total **46.77 core-min** + this item's estimate 39 →
  lineage-to-date ≈ **85.8 core-min, $0.073 derived.**

---

## 6. FALSIFIERS — each names the gate it is predicted to fail, with the arithmetic

> ### `F-CEIL` — the inversion ceiling is real at the constrained endpoint too
> **Probe:** the `1e-3` `check_totals` stage (§2.3), at the constrained endpoint.
> **Named gate: `G-FDPERF`.** **Predicted value:** perturbation peak `~127°` (§2.1) **> ~89° ceiling**,
> so the stage `AnalysisError`s partway. **The inequality `127 > 89` predicts a crash at the wrong
> step by a wide margin**, showing the ceiling is intrinsic to the step size, not to the base — and
> that the constraint (which lowers the base ~11°) could never have rescued `1e-3`. If `1e-3`
> **completes**, §2.1's mechanism is wrong, and no claim about step feasibility may be made from this
> item.

> ### `F-PLANT` — the reader/physical plants (§4). If either fails to fire in its planted direction,
> the item is `NOT A RESULT` for want of a working guard, never a silent pass. Carried from D9.

> ### `F-MESH-NULL` — `G-MESH`'s own trivial baseline.
> **Probe:** `checkMesh` on the **unconstrained D9 endpoint** (already on disk,
> `/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt/`, `maxNonOrth = 80.93`).
> **Named gate: `G-MESH`.** **Predicted value: 80.93 > 70.0 — `G-MESH` FAILS on the unconstrained
> geometry, by 15.6 %.** This is a **measured** value, not an estimate (`D9/RESULTS.md` §2). It proves
> `G-MESH` measures the constraint and not something that would pass regardless. If the unconstrained
> endpoint **passes** `G-MESH`, the gate is not measuring non-orthogonality and its verdict is
> withdrawn.

---

## 7. WHAT THIS ITEM MAY NOT CONCLUDE

1. **Nothing about whether an FD-verifiable endpoint is reachable in general.** A `G-FDPERF`/`G-GRAD`
   `PASS` here says this case, at this constraint and these steps, admits a verification; a
   `NOT A RESULT` says the constraint alone is insufficient and names the primal-tightening successor
   as the next test. Neither generalises beyond this case and image.
2. **Nothing about the other five DV groups.** Carried from `D9/PREREGISTRATION.md` §10: only
   `shapexUpper` is FD-verified; a single-DV-group constrained optimum is not the case's optimum.
3. **Nothing at `np > 1`.** The np=4 FD path carries D9's measured idx16 anomaly and is not used.
4. **Nothing about the stock image.** The shipped row stays NOT BOUGHT for D9's reason
   (`D9/PREREGISTRATION.md` §9): A5's `OBJ.val wrt shapexUpper` is `GATE FAIL` on stock with two sign
   flips; an optimiser on the stock gradient descends on a derivative wrong in sign. **D9successor
   CANNOT claim a toolchain-independent result** and does not.
5. **Nothing about the acceptance/convergence rule.** `primalMinResTol`/`primalMinResTolDiff` are
   carried byte-identical from D9 and are NOT touched. Whether the primal must ALSO be tightened
   (D6RF4-style) to widen the FD window from below is a **separate change escalated to the supervisor
   in §8** and is not pre-empted here.
6. **Nothing about the KS aggregate as a mesh-quality truth.** `G-MESH` grades the RAW `checkMesh` max;
   the KS value is reported as the constraint the optimiser saw, with its slack measured, not as the
   mesh's true maximum.

---

## 8. STATE OF THIS DRAFT — WHAT A FREEZE STILL OWES

**Done here:** the D9 failure re-measured and attributed to mesh quality (§0); the mesh-quality
mechanism identified at C++ source level and at both API generations, with on-disk citations (§1); the
KS over-bound caveat and its consequence for `G-MESH` (§1.2); the squeezed-FD-window analysis from D9's
measured numbers and the a-priori-derived new step set (§2); the three new gates with predictions
written out (§3.1–§3.3); the plants / completion / age-guard carried (§4); the cost re-priced from D9's
actuals with the constraint overhead named for calibration (§5); the falsifiers, each with its named
gate and arithmetic including a measured trivial baseline (§6).

**Owed before any freeze, and NOT done here — a lane drafts, it does not freeze:**

1. **`d9succ_run_script.py`** derived from `d9_run_script.py` (md5 `af5f07bc…`), adding exactly: (a) a
   `nonOrtho` entry in the `"function"` block (`type meshQualityKS`, `metric nonOrthoAngle`,
   `coeffKS 1.0`, `source boxToCell` spanning the domain, `addToAdjoint True`); (b) one
   `self.add_constraint("scenario.aero_post.nonOrtho", upper=70.0, scaler=<TBD>)` line; (c) confirming
   the newer `"function"`-block API exposes `meshQualityKS` through `aero_post` under D9's exact mphys
   wiring — **this is the one API-version detail this draft could not fully verify on disk and it must
   be checked in the image before freeze** (the UAV example uses the `objFunc` block; D9 uses the newer
   `"function"` block, and the exposure name for the constraint output must be confirmed empirically).
   Every departure enumerated as `D9SUCC-1…n` in the script's docstring, with a
   `*_DELTAS_from_d9.diff` beside it.
2. **`d9succ_grade.py`** derived from `d9_grade.py`/`d9_grade_SUPPLEMENT.py` (md5 `7704513424…`), adding
   `G-MESH` (raw `checkMesh` reader + its planted-zero control) and `G-FDPERF` over the 3-step set;
   `--selftest` shown to REFUSE on an empty/short gradeable set, and the new `checkMesh` reader shown
   able to see a non-zero before its zero is trusted (rule 3). Read **as a diff** by the supervisor.
3. **The instrument table with md5s** (`DAFOAM_CHARTER.md` §18.3), existence asserted before any hash;
   anchor tree, FFD, controlDict, fvSolution, fvSchemes carried from D9 §11.
4. **The `coeffKS` and constraint `scaler` values pinned in the frozen script**, and a pre-launch check
   that `coeffKS` does not overflow the KS sum on this mesh (§1.2, `.C:148`).
5. **THE SUPERVISOR'S FOUR PERSONAL §3 CHECKS, none of which a lane may discharge:** the
   measurement-script diffs read **as diffs**; the crash triage (D9's `AnalysisError` is a finding
   this successor is built around — its recurrence at `1e-3` is expected, its absence at `1e-4`/`2e-4`
   is the hypothesis); the big-claim verification — **§2's squeezed-window prediction is a big claim,
   corroborated from D9's measurements, NOT independently measured**; and this file **committed before
   any compute**.
6. **THE SUPERVISOR DECISION §2.2/§7.5 raises:** whether the mesh-quality constraint is registered
   ALONE (this draft), or whether a combined constraint-plus-tightened-primal item is registered
   instead to widen the FD window from both sides. **This lane takes no position on it and does not
   pre-empt it** — it is a scoping call reserved above the lane.
7. **The freeze itself, by sha, by the dafoam-supervisor.** Not taken here.

**SUBMISSIONS PARKED. DRAFT — NOT FROZEN — awaiting supervisor check-1 read and freeze.**

---

## 9. SUPERVISOR RULING ON THE §8-ITEM-6 SCOPING CALL — dafoam-supervisor, 2026-09-07T~0345Z (draft still NOT FROZEN)

§8 item 6 hands upward the one scoping decision reserved above the lane: register the mesh-quality
constraint **ALONE** (this draft), or register a combined **constraint-plus-tightened-primal** item
instead. **I rule: the constraint ALONE — this draft's scope stands.** Grounds:

1. **Single-variable attribution is the ladder's core discipline** (`VERIFICATION_CHARTER.md` §2;
   this charter's ladder principle). Mixing two changes forfeits the attribution the ladder exists to
   protect — §2.2 says so and it is right. One change, one measured effect.
2. **The honest `NOT A RESULT` is registered in advance (§3.3), and it is a real result either way.**
   `G-MESH PASS` proves the named D9 §10-option-2 fix works (the headline Sanaa's `4ae4b33` requires
   tried-and-recorded); a `G-FDPERF`/`G-GRAD` `NOT A RESULT` **measures** that the constraint is
   necessary-but-not-sufficient for an FD-verifiable endpoint — which is a clean scientific increment,
   not a failure to run.
3. **The primal-tightening successor is the D6RF5-class mechanism, and it is not yet proven.** Bundling
   D9successor behind an A5 primal-tightening change would gate it on an unproven fix and couple two
   ladders. The disciplined order is: run the constraint alone, MEASURE the squeezed window, and only
   THEN — if `NOT A RESULT` — register the combined item with the D6RF5 lesson (whichever way A2's
   D6RF5 lands) in hand. **This ruling directs no compute and alters no gate, threshold, cap or label.**

### 9.1 What still owes a freeze after this ruling
Unchanged from §8 except item 6 (now ruled): the instruments (§8 items 1–2, **none written**), the
**image-API verification** §8 item 1 flags (does the newer `"function"`-block API expose
`meshQualityKS` through `aero_post` under D9's exact mphys wiring, and what is the constraint-output
exposure name — an empirical check in image `dafoam-idwarp-rot:v1` before freeze), the `coeffKS`/
`scaler` pinning (§8 item 4), the instrument-md5 table (§8 item 3), and **my check-1 read of the
authored measurement-script diffs** (§8 item 5, not the draft prose — the scripts themselves). **An
authoring lane is queued behind the 3-lane cap; the freeze by sha is taken only after I read those
diffs.** Costed core-min stands at **estimate ≈ 39, cap 120.0** (§5), brought to the chief before
compute.
