# Certonomous Innovation Standard

Version 1.0, dated 2026-07-25. Produced by the overnight reading program (R1).
Codifies, descriptively, how a new method enters this lab. The path below is
not aspirational: it is written from what the lab actually did to admit the
quasi-steady (multi-point cycle decomposition) valve method, traced through
`sdk/workflows/valve_study.py`, the `womersley` section of
`docs/physics_rules.yaml`, the Chief Researcher's closure-approval protocol
(`sdk/chief_engineer/chief_researcher.py`), and the mission lessons the valve
runs recorded.

## The path

### Stage 1. Proposal with a literature basis

A method arrives as a written proposal naming what it approximates and on
whose authority. For the valve: the Womersley number compares transient
inertia to viscous diffusion over a cycle; below alpha near 1 the profile
follows the instantaneous pressure gradient and each instant is a steady
problem (the textbook quasi-steady limit). The proposal also named what it is
not: at aortic alpha near 17 the flow is inertially unsteady, so a multi-point
decomposition could only ever be a screening approximation. Proposals now
arrive as JSONs in the agenda inbox with citations as display titles and
`source_kind` saying where the idea came from.

### Stage 2. Offline evidence on a benchmark

Before touching a surface, the method runs offline where its output can be
judged. For the valve: the decomposition screened eleven opening angles with
three steady phase points each, cycle-weighted; the ranking came out monotone
toward the widest admissible orifice, exactly what orifice physics predicts,
and the minimum-area floor still marked the tight openings infeasible. A
Monte-Carlo envelope over the flow and discharge-coefficient spreads priced
the input uncertainty. The evidence standard is behavioral: the method must
reproduce what is already known before it is trusted to say anything new.

### Stage 3. Gate criteria through the governed file

Admissibility becomes numbers in `docs/physics_rules.yaml`, never constants in
workflow code, so a ruling on camera can point to a stated criterion. For the
valve, two deliberately separated thresholds: `strict_quasi_steady_max: 1.0`
(the textbook limit where each instant is a steady problem) and
`multipoint_screening_max: 25.0` (the ceiling above which the transient jet
structure reorganizes within a cycle and a steady-per-phase picture stops
being even a useful screen). Every threshold carries its reasoning in the file
beside the number.

### Stage 4. Adoption with admissibility conditions

The method ships wearing its conditions:

- A fidelity ceiling: the valve screen is graded RESEARCH MODEL and its
  results are a ranking, never a validated pressure magnitude.
- Named model-form limitations: the analytic orifice model, dropped
  phase-interaction (history and added-mass terms), fixed leaflets, Newtonian
  blood; each is carried as a listed limitation, not absorbed into an error
  bar.
- A marked upgrade point: `_phase_pressure_loss` is the single place a real
  steady internal-flow solve plugs in, so the promotion path is executable,
  not rhetorical.
- Rulings at run time: the workflow reads the yaml thresholds and the ruling
  names the criterion; outside an envelope the Chief Researcher's answer is
  no, with orders to run coarse and state the uncertainty loudly.

### Stage 5. Lessons close the loop

Every mission using the method records what held and what stayed open through
the lessons machinery (`record_learned`), and the debriefs repeat the same
verdict the gates enforce: the angle ranking is trustworthy, the pressure
magnitude is not, and the next steps (full internal-flow plug-in,
harmonic-balance cycle solve, unsteady FSI) are named in the record.

## The rule, stated once

A new method is admitted when and only when it has: a literature basis on the
record, offline evidence on a benchmark the lab already understands, its
admissibility written as cited thresholds in the governed physics file, a
fidelity ceiling and named dropped physics at adoption, and a marked path to
the higher-fidelity version. Any method that cannot state what it drops does
not enter.

## Methods in the pipeline (status ledger)

### Sobol sensitivity indices -- STATUS: adopted on a surface (2026-07-31)

Proposal `r1-sobol-sensitivity-mission` (basis: Dakota theory manual;
Saltelli 2010 main estimator, Jansen 1999 total estimator). Primitive:
`sdk/chief_engineer/sensitivity.py` -- pick-and-freeze main and total indices
over a callable model and stated input distributions, cost n_base x (M+2)
evaluations, bootstrap CIs, deterministic given seed. Evidence run:
`sdk/scripts/run_sobol_evidence.py`, all evaluations reduced-order
(milliseconds), no solver.

Measured (recorded in the proposal JSON): on the valve screen's stated
spreads the discharge coefficient owns the loss variance (main 0.61 [0.58,
0.64]) over the flow amplitude (main 0.39 [0.37, 0.41]); on the airliner
sizing chain the non-wing drag buildup owns it (main 0.64 [0.60, 0.67]) over
the payload mass (main 0.35 [0.33, 0.38]). The estimator recovers the
Ishigami closed-form indices to 0.023 absolute at n_base 4096.

Gate criteria for adoption on a surface:
- A ranking is admissible only when every Sobol identity holds within
  bootstrap CI (indices in [0, 1], main <= total per input, mains sum <= 1);
  a run failing an identity is reported as sampling noise, never as physics.
- Indices are reported WITH their CIs; two inputs whose CIs overlap are
  stated as unresolved, not force-ranked.
- The indices inherit the model's fidelity ceiling: a ranking computed
  through a RESEARCH MODEL screen targets uncertainty-reduction effort for
  that screen and claims nothing about the solved flow.
- The input distributions must be the act's own stated spreads (the valve's
  bounded-uniform convention, the airliner's Gaussian convention) -- never
  spreads invented for the decomposition.

Named limitations: pick-and-freeze assumes independent inputs; correlated
spreads need a different estimator before any such case is admitted.

Stage 3 closed 2026-07-31: the gate criteria above are now numbers in
`docs/physics_rules.yaml` under `sobol` rather than constants in workflow
code. `identity_slack: 0.05` is how far a point estimate may break an
identity before the run counts as noise-dominated; it is set from the
run-to-run movement measured on the two lab models between base samples of
800 and 12800 (first-order shares summing to 1.014, 1.003, 0.991 on the valve
screen and 0.999, 1.015 on the airliner chain). `min_base_samples: 200` is
the design the proposal priced and `max_base_samples: 3200` is where a
mission stops escalating and reports the ranking unresolved.

Stage 4 closed 2026-07-31: the method ships as a routed mission,
`sdk/workflows/sobol_sensitivity.py`, reached from the control room by the
vocabulary of the decomposition (`sobol-sensitivity` in the router). It wears
its conditions on camera: the fidelity ceiling is RESEARCH MODEL because both
paths it decomposes are reduced-order screens; the identity check and the
overlapping-interval rule are read from the yaml and stated with the numbers
they enforce; the marked upgrade point is the third agenda entry, the same
decomposition carried through a meshed and solved case.

What the mission measured on its first run (base sample 800 on both cases,
11,200 evaluations, 0.44 s):

| Case | Leading input | Main effect | Runner up | Main effect |
|---|---|---|---|---|
| Valve screen, cycle-weighted pressure loss | discharge coefficient | 0.584 [0.527, 0.648] | flow amplitude | 0.430 [0.370, 0.488] |
| Airliner sizing chain, cruise lift to drag | non-wing drag | 0.664 [0.587, 0.741] | payload mass | 0.314 [0.258, 0.376] |

The first finding is about the budget, not the physics: at the approved base
sample of 200 NEITHER case cleared the gate. The valve's two intervals
overlapped; the airliner's first-order shares summed to 1.202 of the whole
variance with the leading input's main effect above its own total. Both
cleared at 800. A pick-and-freeze design priced at N of 200 for a two-input
model is under-sampled for these models, and the mission now says so on the
record rather than ranking through it.

### Multifidelity Monte Carlo (MFMC) -- STATUS: offline evidence measured (2026-07-25)

Proposal `r1-multifidelity-propagation` (basis: Peherstorfer, Willcox and
Gunzburger, SIAM Review 2018). Primitive:
`sdk/chief_engineer/multifidelity.py` -- control-variate fusion of a cheap
model against sparse high-fidelity anchors: measured correlation sets the
coefficient, measured cost ratio sets the allocation, both decide honestly
whether fusion pays. Evidence run: `sdk/scripts/run_mfmc_evidence.py` on the
race act's recorded paired evaluations (no new solve).

Measured (recorded in the proposal JSON): over the race's 88 matched
design evaluations the surrogate-solver correlation is 0.9967, the measured
cost ratio ~1e7 (5.10 s per solve vs ~5e-7 s per surrogate call, both
wall-clocked on this machine), the optimal allocation at the lane's own
449 s budget is 87 solves + ~3.4M surrogate evaluations, and the analytic
variance reduction at equal budget
is 150x (empirical replay over the real records: 61x). Honest split verdict:
for the race's actual estimand -- peak L/D under the Reynolds spread at fixed
alpha -- the recorded alpha-only surrogate is constant across the ensemble,
correlation is undefined, and MFMC would NOT have beaten the race's approach
at any budget.

Gate criteria for adoption on a surface:
- Fusion is admissible only when the cheap model demonstrably varies with
  the uncertain input of the estimand (a measured, defined rho on the paired
  records); a degenerate lane is refused, never zero-filled.
- The survey's pay condition must hold on measured numbers:
  cost_lo/cost_hi < rho^2/(1 - rho^2); otherwise the act runs single-fidelity
  and says fusion does not pay.
- At least one high-fidelity solve stays in every fused estimate (the
  accuracy anchor); a plan with zero solves is surrogate extrapolation and
  is refused by the allocation function itself.
- The fused envelope is labelled as fused, with rho, the allocation, and
  both lane costs on the record.

Named limitations: the recorded evidence pairs one surrogate with one
solver on one wing; the estimator is unbiased by construction, but the
variance-reduction claim transfers only after the target act's own rho and
costs are measured.

Neither method is wired to a router intent or a GUI act yet -- that is a
camera-surface change, deliberately deferred to a round with the owner
present. The primitives, their evidence scripts, the measured numbers in the
proposal JSONs, and the recorded lessons are the current extent of adoption.

## Sources

- Valve workflow and its module docstring, `sdk/workflows/valve_study.py`.
- Governed thresholds, `docs/physics_rules.yaml`, section `womersley`.
- Closure approval protocol, `sdk/chief_engineer/chief_researcher.py`.
- Mission lessons recording the valve admissions,
  `sdk/chief-engineer-runs/mission-state/lessons`.
- Verification and Validation in Computational Fluid Dynamics, Oberkampf and
  Trucano, Sandia report SAND2002-0529, for the benchmark-first evidence
  discipline the path mirrors.

## Amendment record: **[SANAA-DIRECT] REMOVE THE POSSIBILITY, NOT THE INSTANCE — `VERIFICATION_CHARTER` §2l IS ELEVATED HERE** (2026-08-31)

Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`,
proved by a byte-prefix check against HEAD in the commit that lands this section — the first
**11335** bytes are byte-identical, **206** lines before. This is the first amendment section in
this file; the `## Sources` list above is unchanged.

**Sanaa's words, verbatim, 2026-08-31** (captured at
`etc/sessions/2026-08-31T1505Z_sanaa_rulings_six.md`, commit `1405c265`; that session file is not
edited):

> (2) Both charter elevations approved (provenance tags → REPORTING_CHARTER; §2l →
> INNOVATION_STANDARD).

**WHY IT LANDS HERE.** §2l is a principle about **how this lab builds things**, which is this
standard's subject. It was drafted in `VERIFICATION_CHARTER` §2l (`95db2a82`, v1.24) because that
is the file its author owns, and proposed rather than taken. **`VERIFICATION_CHARTER` §2l is NOT
rewritten and remains the origin text** (rule 6).

### The rule

> **When a defect recurs, ask what would have to be true for it to be IMPOSSIBLE — and build
> that, rather than fixing the instance in front of you.**

It came from noticing that **three repairs landed by three teams against three unrelated defects
on one night were the same move**, and that **none of the obvious fixes would have removed the
defect** — only the instance.

### The three forms it takes

1. **DERIVE, DON'T MAINTAIN.** A value computed from its source cannot drift from it. The
   numerics FAMILY INDEX is generated from the tail because **a hand-maintained derived value
   does not drift less when watched more.**
2. **MOVE THE SAFETY INTO THE PATH.** `append_block.py` reads a block body from a **file, as
   bytes, so no shell ever sees it** — removing the whole class of quoting and expansion faults
   rather than escaping this one body correctly.
3. **MAKE THE BAD STATE UNREPRESENTABLE.** The queue runner keys on a **team NAME** rather than
   an integer cursor, so the starvation bug has no state to live in.

### The test — one question, and it is answerable

> **After this repair, what would it take to reintroduce the defect?**

- *"An edit a careful person could plausibly make"* → **the possibility is still there; only the
  instance was removed.**
- *"You would have to reinstate the mechanism itself"* → **it is gone.**

**In none of the three was the ordinary fix WRONG** — each would have worked that day on that
instance — **and in two of the three the defect had already returned before anyone acted.**

### WHEN TO REACH FOR IT, because "always" is wrong and would be expensive

Two triggers, and **a first occurrence with no asymmetry gets the ordinary fix**:

- **RECURRENCE.** Three careful teams hitting one defect in one afternoon **is not three lapses;
  it is evidence the safe path was harder** (the `L-405` form).
- **EFFORT ASYMMETRY** — the safe path costing more than the unsafe one. Where that holds,
  **discipline is not load-bearing, because discipline is the thing being taxed.**

### THE HONEST LIMIT, AND IT SHIPS ITS OWN COUNTER-EXAMPLE

From the same night: `T16`/`C_ORDER`. A guard hunting a **−1.0** signal carried a **1e-06**
tolerance and fired on real physics. **There is no way to make "a tolerance mis-sized for the
defect it hunts" unrepresentable.** The remedy was to split the clause and size each tolerance to
its own signal — **a judgement no construction can take over.** **§2l does not reach it, and
citing §2l to avoid making that judgement is a misreading of it.**

The principle's own failure mode is named too: **claiming a state is *unrepresentable* when it has
merely become inconvenient to reach.** That claim is checkable — by the test above — and must be
made, not assumed.

### Scope

Advisory on **method**, and it creates **no gate and no threshold**. It never licenses a
post-compute change to a frozen artifact: rule 2 and `VERIFICATION_CHARTER` §2d/§2d.1 govern that
and are untouched here. Where §2l and a freeze conflict, **the freeze wins** and the redesign
waits for the successor registration.
