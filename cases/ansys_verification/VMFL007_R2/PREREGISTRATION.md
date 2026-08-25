# VMFL007-R2 — the LINEAR-SOLVER / PRECONDITIONER SLATE — PRE-REGISTRATION

**Version 1.0. Frozen 2026-08-25.** Drafted by `ansys-lane-opus` on the
`ansys-verification-supervisor`'s brief, for the supervisor to freeze.
Subordinate to `CLAUDE.md` (all sixteen standing rules bind without restatement)
and to `docs/charters/ANSYS_VERIFICATION_CHARTER.md` v1.4. Written on the team's
template form (`docs/ansys_verification/PREREG_TEMPLATE.md`) at Sanaa's directed
template speed. **Short is not weaker: every standing clause binds, and where one
will not fit in a line it is cited by name, never omitted.**

**NO GRADED COMPUTE HAS RUN FOR VMFL007-R2 AND NONE EXISTS TO RUN AGAINST.**
`verification/runs/ansys_verification/VMFL007_R2/` **does not exist** — checked
2026-08-25T17:29:11Z and re-checked at 2026-08-25T17:41:49Z immediately before
this freeze, and the launcher's age guard refuses any arm directory that
does. The only compute spent so far is the pre-flight of §12, in scratch under
`/tmp/claude-1000/`, outside the runs tree.

---

## 0. WHY THIS RUNG EXISTS — Sanaa's rule 2, and the case that landed on it

Her standing rule, byte-exact, spelling hers and not corrected:

> "When a grid doesnt converge, try different pre conditioners, see if that's a
> raised issue online/in the litterature, check for bugs, if unsteady check cfl,
> pick different meshing"

**VMFL007 run 1 landed precisely on that rule, so this rung executes it as
written.** Run 1's verdict is `NOT A RESULT`, tier `NOT HELD`
(`cases/ansys_verification/VMFL007/RESULTS.md`), and **run 1's tree, its
pre-registration and its comparator are PRESERVED — not edited, not cleared, not
re-labelled.** This is a new rung in a new directory citing the old one.

**R2 registers the LINEAR SOLVER / PRECONDITIONER as the single variable under
test.** The other three limbs of her rule are discharged as follows: the
literature limb in §11 (on this box only — **submissions are PARKED**, `CLAUDE.md`
rule 7: this lane files nothing, posts nothing and asks nothing upstream, ever);
the bug limb in §10, which found something; the CFL limb is `N/A` — the solver is
steady `simpleFoam` and prints no Courant number, asserted from the artifact by
comparator clause C7, never assumed; and the meshing limb is **named and
deliberately NOT taken here**, because changing the mesh would confound the
registered variable (§8).

---

## 1. THE STANDARD FORM (template lines 1–13)

```
1.  CASE            : VMFL007-R2 -- Non-Newtonian Flow in a Pipe -- manual p.29.
                      Solver = OpenFOAM v2606 simpleFoam, steady, laminar,
                      viscosityModels::powerLaw, axisymmetric 1 deg wedge.
                      NOT YET RUN; verification/runs/ansys_verification/VMFL007_R2/
                      ABSENT at 2026-08-25T17:29:11Z.
                      THIS IS A CONVERGENCE INVESTIGATION, NOT A GRADED CASE.
2.  REFERENCE       : 60.52 kPa pressure drop; W.F. Hughes & J.A. Brighton,
                      Schaum's Outline of Theory and Problems of Fluid Dynamics,
                      McGraw-Hill 1991 (manual p.29 Table .07.1). Closed form
                      re-derived in run 1 section 4 to 60521.96938383448 Pa.
                      Ansys Fluent 60.41 kPa / Ansys CFX 61.52 kPa -- CONTEXT ONLY.
3.  REFERENCE KIND  : CLOSED-FORM / EXACT -- category 1. BUYS V, NEVER P.
4.  TIER CEILING    : `GATE REACHED` for the CASE (P unavailable on a closed-form
                      reference). BUT SEE LINE 8: R2 IS SINGLE-GRID, SO R2'S OWN
                      CASE-LEVEL VERDICT CEILING IS `NOT A RESULT`. R2 seeks no
                      credential and cannot produce one.
5.  QUANTITIES      : PRIMARY -- the CONVERGENCE BEHAVIOUR of each arm, measured on
                      areaAverage(p) at the inlet and outlet patches [m2/s2], on
                      volume min/max of nu [m2/s], and on the final initial
                      residuals of Ux and p. SECONDARY/DIAGNOSTIC ONLY --
                      dp = rho*(p_in - p_out) [Pa], rho = 1000.
6.  BANDS (THE GATE): |dp_lab - 60520 Pa| / 60520 Pa <= 0.005, band
                      [60217.40, 60822.60] Pa. CARRIED UNCHANGED FROM RUN 1'S
                      FREEZE 48f7a9bf AND NOT APPLIED AS A VERDICT HERE -- it is
                      carried so R3 can register a triple against a gate this
                      rung never touched. THE COMPARATOR CANNOT EMIT A PASSING
                      GATE ROW (section 4).
7.  LADDER          : simpleFoam; powerLaw k=0.01 (kinematic) n=0.4 nuMin=1e-8
                      nuMax=1.0; laminar { model Stokes; }; ONE mesh, 25x25 = 625
                      cells, 1 deg wedge. BIRTH-CERTIFIED: mesh/birth_certificate_L1.json
                      (MESH_STANDARD section 6) -- verdict `flagged`, see section 10.2.
8.  DECOMPOSITION   : SINGLE GRID, DELIBERATELY. L1_25x25 only. THERE IS NO ROACHE
    SEED              TRIPLE, so under CLAUDE.md rule 5 THE CASE-LEVEL VERDICT IS
                      `NOT A RESULT`, stated here in advance. Serial, 1 rank, no
                      domain decomposition, no RNG. Reason in section 4.
9.  PRINCIPAL RISK  : THE FALSIFICATION ARM IS THE PREDICTED OUTCOME -- all six
                      configurations diverge alike and the linear solver is
                      exonerated. Predicted BEFORE any arm runs, with grounds, in
                      section 9. If an arm converges, that prediction is FALSIFIED
                      and the linear solver IS implicated.
10. EXPECTED ORDER  : N/A -- single grid, no observed order, no GCI, and none will
                      be quoted. Run 1's declared band p in [1.0, 2.5] stands
                      unused and is carried forward to R3.
11. WEDGE/GEOM BIAS : Axisymmetric. dp biased HIGH by sec(t/2)-1 =
                      +0.003807838573699485 % at t = 1 deg (N-AV9; charter v1.4
                      Clause A). The AREA deficit sin(t)/t = 0.005076879670529166 %
                      is the WRONG term for a dp gate and is not it. IRRELEVANT TO
                      R2'S PRODUCT -- a 0.0038 % bias cannot be seen beside a
                      divergence of 143 decades -- but carried because the clause
                      binds the DISCLOSURE, not the tolerance, and silence is what
                      it forbids.
12. COST + CAP      : point estimate 30 core-min; PER-ARM CAP 20 core-min
                      (timeout 1200 s); SLATE CAP 90 core-min (5400 s). Derived
                      $0.077 at the slate cap. Basis in section 7. AN OVERRUN
                      STOPS THE ARM AND THE SLATE; neither gets a new budget.
13. CONTROLS        : planted-zero (rule 3) fires per arm on that arm's own gate
                      series and REFUSES if the reader cannot see the plant;
                      strict completion C1-C7 incl. the AGE GUARD (rule 4);
                      Roache gating (rule 5) DECIDES THE CASE VERDICT AND IT IS
                      `NOT A RESULT` -- single grid. Comparator
                      grade_vmfl007_r2.py --selftest: 43 checks, 0 failures, with
                      21 MUTATION controls. Plus the determinism control (section 6)
                      and the confound assert (section 8).
```

---

## 2. THE SLATE — DECLARED IN FULL, IN A FIXED ORDER, BEFORE ANY ARM RUNS

**This is the binding guard and it is the whole discipline of this rung.**

| # | arm | `p` entry (the ONLY thing that varies) | what it isolates |
|---|---|---|---|
| **A1** | `A1_GAMG_GaussSeidel` | `solver GAMG; smoother GaussSeidel;` | **THE CONTROL — byte-identical to run 1's frozen `fvSolution`, blob `70953b4ea8d71a0b4744b1df695ceac9e24fa820`.** Without it no difference can be attributed to the swap |
| **A2** | `A2_GAMG_DICGaussSeidel` | `solver GAMG; smoother DICGaussSeidel;` | the **smoother**, agglomeration held |
| **A3** | `A3_PCG_DIC` | `solver PCG; preconditioner DIC;` | **NO agglomeration at all** — the sharpest test of the agglomeration hypothesis |
| **A4** | `A4_PCG_GAMGprecon` | `solver PCG; preconditioner { preconditioner GAMG; smoother GaussSeidel; }` | GAMG **demoted to preconditioner** under a Krylov outer loop |
| **A5** | `A5_PBiCGStab_DIC` | `solver PBiCGStab; preconditioner DIC;` | a **different Krylov**, preconditioner held with A3 |
| **A6** | `A6_smoothSolver_symGaussSeidel` | `solver smoothSolver; smoother symGaussSeidel; nSweeps 2;` | **no Krylov, no multigrid** — the crudest and most robust. If even this diverges the linear solver is definitively exonerated |

`tolerance 1e-12` and `relTol 0.01` are **held at run 1's values in every arm.**

> ### **ALL SIX ARMS ARE RUN AND REPORTED, IN THIS ORDER, WHATEVER ANY EARLIER ARM RETURNS.**
> **A slate truncated after seeing a number is answer-directed selection.** The
> launcher has **no `--arm` flag** and no early exit on a result: an arm that
> diverges, stalls or dies is **recorded and the slate continues**. The comparator
> prints every registered arm; an arm that did not run prints as **`MISSING`**, never
> silently dropped. The only things that stop the slate are a **setup** failure and
> the **cost cap**.

**The order was fixed before any arm ran** — it is written into
`grade_vmfl007_r2.py`'s `SLATE` and `run_vmfl007_r2.sh`'s `SLATE_NAMES`, both
committed in the machinery commit that precedes this document. §12 records a
pre-flight observation about per-arm solver-iteration counts; **that observation
came after the order was fixed and changes neither the order nor the criterion.**

---

## 3. THE FROZEN CONVERGENCE CRITERION — the selection rule, numerical, and frozen now

> ### **A CONVERGENCE FIX IS NEVER SELECTED BY WHICH ONE MAKES THE GATE PASS.**
> **The selection criterion is CONVERGENCE BEHAVIOUR — the solution ceasing to
> move — and it is frozen here, before any arm runs.** §4 makes this structural
> rather than merely promised: **on a single grid the comparator cannot emit a
> passing gate row at all**, so there is no gate outcome to select on.

Each arm is classified on **four primary legs and one declared-blind secondary**.

### 3.1 `C-BOUNDED` (primary, binary)

**`max over iterations 1..10000 of |areaAverage(p)|_inlet <= 1.0e4 m²/s²`.**

The physical value is **60.52196938383448 m²/s²** (Δp/ρ), so the bound is **165×
permissive** — chosen so it cannot be confused with the gate and trips only on a
genuine divergence. Run 1's L1 reached **9.449536950130e+144**, 140 decades over.
**Tripped → `DIVERGENT`.**

### 3.2 `C-DESCENT` (primary, quantitative) — `MONITOR_STANDARD` S13 v1.12

**Adopted UNCHANGED from run 1's frozen §8.2, deliberately, so the criterion
cannot be accused of having been tuned for this slate:**

| | value |
|---|---|
| window | **FIXED: the last 1000 iterations**, sampled every 100 → **10 samples** (S13 floor is 9) |
| normaliser | **the range the series spanned over the whole run** |
| threshold | **≤ 2.0e−4 (0.02 %)** of that range |
| null clause | whole-run range **< 1.0 m²/s²** → **REFUSED**, never passed. *A flat line is not a plateau; it is an absence of signal.* |

A **fixed** window, not a fraction of the run, because *"a fraction-of-run window
silently loosens as a run is extended, so the same case passes by being run
longer"* (charter v1.4 disclosure 1). **Failed → `STALLED`.**

### 3.3 `C-VISCOSITY` (primary — and it is the sharpest leg)

**Neither clip may EVER be reached, on any iteration:** `nuMaxAll < 1.0` and
`nuMinAll > 1e−8 × (1 + 1e−9)`.

**Why this is a convergence criterion and not a diagnostic.** The `nuMin` floor
of **1e−8** is **4298× below the physical wall viscosity 4.298435325556426e−05**.
Reaching it requires a shear rate of **1e10 s⁻¹** against the physical wall value
of **8800 s⁻¹** — a factor of **1.14e6**. **A run sitting on that floor has no
viscous damping left and has left the physical problem**, whatever its residual
says. Run 1 measured the floor pinned **from iteration 904 (L1) and 715 (L2)**,
and pinned for every remaining iteration. **Tripped → `DIVERGENT`.**

### 3.4 `C-COMPLETION` (primary) — `CLAUDE.md` rule 4, clauses C1–C7

`rc = 0` read from `RUN_RC.txt` on disk and never inferred · an anchored `End`
line · last time `== endTime == 10000` · `ExecutionTime` count `== 10000` ·
fields `U p phi nu` present at `10000` · **the AGE GUARD**, every field at
`endTime` newer than the case's own `0/U` marker · **zero `Courant Number` lines**,
so the `MONITOR_STANDARD` S8 exemption is read off the artifact rather than
asserted. The comparator **refuses (exit 2) rather than degrading**, and the
launcher's guard refuses an arm directory that already exists.

### 3.5 `C-RESIDUAL` (SECONDARY BACKSTOP — **DECLARED BLIND IN ADVANCE**)

Final initial residual **`Ux ≤ 1e−5`, `p ≤ 1e−4`**, carried unchanged from run 1.

> **THIS LEG IS DECLARED, BEFORE ANY ARM RUNS, TO BE NON-DISCRIMINATING ON THIS
> CASE, AND THE REASON IS MEASURED.** OpenFOAM normalises the initial residual by
> a factor built from the field's own magnitude, so **the ratio is
> SCALE-INVARIANT**: a solution growing without bound holds a bounded normalised
> residual. Run 1 measured exactly that — **p oscillating in ≈[0.15, 0.46] and Ux
> in ≈[0.042, 0.072] for all 10 000 iterations while `areaAverage(p)|inlet` grew
> from 3.022e+04 to 9.450e+144.** The residual channel was never going to show
> this and it did not.
>
> **It may only turn a `CONVERGED` into a `STALLED`, never the reverse.**

### 3.6 The classification lattice — exhaustive, frozen

| class | condition |
|---|---|
| **`CONVERGED`** | `C-BOUNDED` ∧ `C-DESCENT` ∧ `C-VISCOSITY` ∧ `C-COMPLETION` ∧ `C-RESIDUAL` |
| **`STALLED`** | bounded and viscosity-clean, but the plateau (or the residual backstop) fails |
| **`DIVERGENT`** | `C-BOUNDED` fails, **or** `C-VISCOSITY` fails, **or** the solver died (`rc ≠ 0`) |
| **`CAP-STOPPED`** | `rc = 124` — the arm hit its 20 core-min cap. Recorded; **not re-run** |
| **`INCOMPLETE`** | the arm's identity or completion could not be established |
| **`MISSING`** | the arm has not been run. **Reported, never dropped** |

---

## 4. WHAT R2 CAN AND CANNOT PRODUCE — the structural guarantee

> ### **R2 IS SINGLE-GRID BY DESIGN. ITS CASE-LEVEL VERDICT IS `NOT A RESULT`, AND THAT IS DECLARED HERE, BEFORE COMPUTE, NOT DISCOVERED AFTER.**

`CLAUDE.md` rule 5: a row without a `CONVERGING` triple is `NOT A RESULT`
whatever its value. R2 has no triple at all. **The comparator prints this at the
top of every run and refuses to apply the gate as a verdict.**

**This is not a limitation — it is the structural defence of §3's guard.** A
registration that *could* produce a credential creates an incentive to prefer the
arm that produces one. **R2 literally cannot.** Its product is the arm
classification table of §3.6 and nothing else.

**Why single-grid is the honest design and not a shortcut:**

1. The question is *"does the linear solver change the divergence"*, and that is
   answered per level. **L1 is where run 1 gives an exact control** — a completed
   10 000-iteration run of the identical configuration.
2. Run 1 measured L1 and L2 behaving **identically** in kind (floor pinned at 904
   and 715; monotone divergence on both), so the second level adds little.
3. **A six-arm × three-level design would be 18 runs at ≈490 core-min — and a
   slate that expensive is exactly the slate that gets truncated.** The guard in
   §2 is only credible if running all six is cheap enough to be certain. **Keeping
   the slate affordable is what makes the commitment to complete it real.**

**A DECLARED CONDITIONAL ESCALATION, stated up front so it is not mistaken for a
later improvisation:** *if and only if* an arm is classified `CONVERGED`, that arm
is carried to **R3** as a full three-level Roache triple against the gate carried
unchanged in line 6. That escalation only **adds** work and never removes any, so
it cannot function as answer-directed truncation.

---

## 5. WHAT WOULD MEAN THE LINEAR SOLVER IS **NOT** THE CAUSE — the falsification arm

> ### **IF ALL SIX ARMS ARE `DIVERGENT` (OR `STALLED`), THE LINEAR SOLVER IS NOT THE CAUSE OF VMFL007's NON-CONVERGENCE.**
> ### **THAT OUTCOME IS A REAL FINDING ABOUT THIS CASE, NOT A FAILURE OF THIS RUNG.**

It would redirect **R3** to the candidates measured in §10 but deliberately **not**
tested here:

- **(a) the CONVECTION SCHEME.** `div(phi,U) bounded Gauss linear` is **unbounded
  central differencing** at an axial cell-Péclet of **186.11 / 93.06 / 46.53**
  against the classical central-differencing boundedness limit of **2**. **No
  level of this family reaches it** — 2 326 axial cells would be needed against
  the finest level's 100. §10.1 records a controlled comparison already on disk.
- **(b) the RELAXATION FACTORS** `p 0.3` / `U 0.7`.
- **(c) the MESH.** Aspect ratio **160** and **73 of 625 cells (11.7 %)**
  under-determined (§10.2) — Sanaa's *"pick different meshing"*.

**A partial outcome is also a finding and is reported as one:** if some arms
converge and others do not, the linear solver is **partially** implicated and R3
registers the converging arm on a triple. Nothing about that reading is decided
after the fact — it is here, before compute.

---

## 6. THE DETERMINISM CONTROL — cheap, and it can fail

**A1 is run 1's configuration re-run in a new directory.** The case is serial and
deterministic, so A1's gate series must reproduce run 1's L1 series.

**Frozen test:** A1's `areaAverage(p)|inlet` at iteration 10000 against run 1's
measured **9.449536950130e+144**, relative tolerance **1e−9**.

> **If it fails, this box is not reproducing its own frozen configuration and
> THE WHOLE SLATE IS `NOT A RESULT`** — no arm comparison means anything if the
> control cannot reproduce itself. If run 1's series is not on disk the control is
> reported as **COULD NOT RUN**, never as passed.

---

## 7. COST (`CLAUDE.md` rule 12) — and run 1's cost model was WRONG, by how much

> ### **RUN 1'S COST MODEL WAS WRONG. Stated plainly, as instructed.**

| | |
|---|---|
| run 1's point estimate, whole triple | **15 core-min** |
| run 1's assumed rate | 2.115e−6 core-s per cell-iteration (VMFL001) **× 4** = **8.46e−6** |
| **MEASURED rate, run 1 L1** | **233 wall s / 6.25e6 cell-iterations = 3.728e−5 core-s per cell-iteration** |
| **the assumed rate was low by** | **4.4066×** |
| projected whole triple at the measured L1 rate | **81.55 core-min** |
| **run 1's estimate was therefore low by** | **5.44×** |

**And the rate model itself does not hold on this case — disclosed rather than
glossed.** L2 measured **6.309983e−6 core-s per cell-iteration** against L1's
**3.728e−5**: the same case, **5.9081× cheaper per cell-iteration at 4× the
cells.** Cost per outer iteration is the number of **inner** sweeps, and on a
diverging solve that count wanders. **A per-cell-iteration rate is therefore not a
valid basis for this case, and R2 does not use one.**

**R2's basis is a direct measurement instead of a model**, because every arm runs
**the same 625-cell mesh for the same 10 000 iterations as run 1's L1**:

| | |
|---|---|
| **A1, MEASURED** | **3.8833 core-min** — run 1's L1, the identical configuration |
| A2–A6, estimated | **1–3× A1** ⇒ ≈4–12 core-min each. **This is a WEAK basis and is labelled weak**: the pre-flight's per-arm `ExecutionTime` at iteration 1 was resolution-limited at 0.03–0.04 s and could not discriminate |
| **POINT ESTIMATE, slate** | **30 core-min** |
| **CAP, per arm** | **20 core-min** (`timeout 1200`) — **5.15× A1's measured** |
| **CAP, slate** | **90 core-min** (`timeout`-independent; checked before each arm launches) — **3× the point estimate** |
| ranks | 1 (serial); arms run sequentially; core-min = wall_s × 1 / 60 |
| **derived dollars at the slate cap** | **$0.077** at $0.0513/core-h |
| `cost_basis` | **A1 MEASURED from run 1's log; A2–A6 ESTIMATED, weakly, and said so.** The **rate** is owner-stated, not measured — this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5) |

**An overrun STOPS the arm**; the arm is recorded `CAP-STOPPED` and **is not
re-run and does not get a new budget**. **An overrun of the slate cap stops the
slate**; the unlaunched arms are reported `MISSING`. $0.077 is **325× under** the
$25 pre-authorisation — **and the caps still bind**, because a blanket is not a
per-item reading (`CLAUDE.md` rule 9).

**Contention, recorded and NOT used to excuse anything.** Run 1's L1 ran at
loadavg **9.32 on 16 cores** with five co-resident solvers, so its **3.8833
core-min is a GROSS figure** and the clean figure is unknown. At the time of this
freeze the box carries loadavg **5.64/16**, three `buoyantBoussinesqSimpleFoam`,
one DAFoam container, and **the peer VMFL003-M2 four-arm ladder is live (pid
2218904, 45:51 elapsed)**. Contention raises serial wall time, never lowers it.
**Estimate-versus-actual calibration is owed at completion** — one row in
`docs/COST_CALIBRATION.md` (rule 12; charter §5.7). **A close-out without it is
incomplete.**

---

## 8. CHANGE THE LINEAR SOLVER AND NOTHING ELSE — machine-checked, not promised

Every non-`fvSolution` input of R2 is **byte-identical to the blob frozen for run
1 at `48f7a9bf`**, verified by `git hash-object`:

| input | blob |
|---|---|
| `case/0/U` | `b626d65ada23d57c62337f1a26e411c1bdc3cd16` |
| `case/0/p` | `54562f8cbc730c083492ac97d21c9d7c214414a3` |
| `case/constant/transportProperties` | `db848a12eb939d1ac0ad81bedea135f536926f38` |
| `case/constant/turbulenceProperties` | `f68f346789696b45b8d245b57ef06e1fc0aaad55` |
| `case/system/blockMeshDict.template` | `9ea967ebeedf20eb9428c7785abf966eadbf01a3` |
| `case/system/controlDict.template` | `fe8524ab1fb2abe1c440b3685c65cb16202e8f65` |
| `case/system/fvSchemes` | `ad718abf3cdc834b17478c2c391affeba1dbf2b2` |

**`case/system/fvSolution` DOES NOT EXIST in `case/`, deliberately** — the arm
supplies it, so no arm can silently inherit a stale one. The launcher **aborts**
if it is ever found there.

**Three asserts make this a fact rather than a claim, and all three are shown able
to fail:**

1. the seven blobs above are re-hashed at launch and any mismatch **aborts**;
2. every arm file is re-hashed against its registered blob and any mismatch
   **aborts**;
3. every arm is **brace-matched-diffed against the A1 control** and must differ
   **only inside the `p { ... }` entry**. **Mutation-tested in the pre-flight: a
   moved relaxation factor (`p 0.3` → `p 0.5`), a changed `U` solver, and an added
   `residualControl` block were each caught and aborted** — measured, not asserted.

**Mesh, `endTime`, relaxation, schemes, viscosity model, geometry and the gate all
stay identical to run 1.** The mesh is identical **including its flagged advisory
of §10.2** — repairing it here would be a confound and is left to R3.

### 8.1 Declared confounds — the honest residue

1. **Wall time is not comparable across arms.** A different `p` solver costs a
   different amount per iteration. Cost is recorded per arm and is **never used as
   evidence about convergence**.
2. **A1 is not bit-identical to run 1 as a directory** (new mtimes, new path). It
   is asserted identical in **field values** by §6's determinism control.
3. **The `p` solver's `tolerance`/`relTol` are held**, so where a solver has no
   analogue of a smoother the **preconditioner** carries the variation. That is
   the registered variable and each arm names its own form in §2.
4. **Contention is uncontrolled** (§7). It moves wall time only; the case is
   serial and deterministic, so field values are unaffected.

---

## 9. THE PREDICTION, MADE BEFORE ANY ARM RUNS

> ### **THIS LANE PREDICTS THE FALSIFICATION ARM: ALL SIX CONFIGURATIONS DIVERGE, AND THE LINEAR SOLVER IS EXONERATED.**

**The grounds are measured, from run 1's own artifacts, and they are stated so the
prediction can be checked rather than admired:**

1. **The divergence starts at iteration 2, before any linear-solver stress.**
   `time step continuity errors : sum local` reads **0.0832213752667** at
   iteration 1, **162.401798376** at 2 and **685.538668204** at 3 — three decades
   in two iterations, while the coefficient field is still well-conditioned.
   `areaAverage(p)|inlet` is already **3.022e+04 m²/s²** at iteration 1 against a
   physical **60.52**, and **sign-flipping** by iteration 5.
2. **From iteration 904 the coefficient field is UNIFORM, so the agglomeration
   hypothesis has nothing left to degrade on.** `nuMinAll` and `nuMaxAll` are
   *both* pinned at **1e−8** for the last 9 096 iterations of L1. GAMG from that
   point is solving a **constant-coefficient** Laplacian. The leading diagnosis
   handed to this lane — *"GAMG's agglomeration degrades on strongly varying
   coefficients"* — was correctly labelled **consistent-with, not established**;
   **it is not consistent with this trajectory**, and this lane says so with the
   measurement rather than deferring to it.
3. **The SIGFPE has a complete arithmetic explanation and is a symptom, not a
   cause.** L2's `areaAverage(p)|inlet` reached **6.034959177466e+211** at
   iteration 9064. A squared inner product overflows double above
   **1.341e+154**. `GAMGSolver::scale` forms exactly such products. **The crash
   site is simply where the first product of two enormous numbers is formed**, and
   any solver forming an inner product would have died in its own inner loop.
4. **The lab's own passing case on the same geometry used the same `p` GAMG
   solver** — VMFL005, register row #3, `PASS` (§10.1). **The p solver is common to
   the case that worked and the case that did not.**

**If any arm converges, this prediction is FALSIFIED and the linear solver IS
implicated — and that is the result that would make this rung worth running.**

---

## 10. THE BUG LIMB AND THE MESH LIMB — what looking actually found

### 10.1 A CONTROLLED COMPARISON ALREADY ON DISK — and it points at the SCHEME

**`VMFL005` (register row #3, `PASS`, tier `GATE REACHED`) is the same geometry,
the same solver, the same bulk velocity and the same `p` GAMG solver as VMFL007 —
and it converged.**

| | VMFL005 (**PASSED**) | VMFL007 (**DIVERGED**) |
|---|---|---|
| geometry | 0.1 m pipe, D = 0.0025 m, wedge | **identical** |
| solver / model | `simpleFoam`, steady, laminar | **identical** |
| bulk velocity | 2 m/s | **identical** |
| `p` linear solver | **GAMG** | **GAMG** — *the same* |
| relaxation | `p 0.3` / `U 0.7` | **identical** |
| **axial cell Péclet** | **200 / 100 / 50** | **186.11 / 93.06 / 46.53** — *slightly LOWER* |
| **`div(phi,U)`** | **`bounded Gauss linearUpwind grad(U)`** | **`bounded Gauss linear`** — **UNBOUNDED CENTRAL** |

**VMFL005's own frozen `fvSchemes` says why, in the case's own words:**

> *"The convection term is named explicitly and made upwind **because of the high
> cell Peclet number**."*

**VMFL005 ran at a HIGHER cell Péclet than VMFL007 and converged, because it
upwinded. VMFL007's registration did not carry that across.** This is the bug limb
of Sanaa's rule 2 returning something, and it is the strongest single candidate
for the divergence.

**Three honest caveats, so this is not over-read.** The two cases also differ in
**viscosity model** (Newtonian ν = 1e−5 vs power-law), in **wedge angle** (5° vs
1°), and in **aspect ratio** (8 vs 80). **It is therefore a strong candidate and
not a proof** — and it is emphatically **NOT tested in R2**, because changing the
scheme would confound the registered variable. **It is R3's first arm.**

### 10.2 THE MESH LIMB — an advisory run 1's check never ran, and a hypothesis this lane REFUTED against itself

`checkMesh -allGeometry -allTopology` on the L1 mesh **fails one check**: **73 of
625 cells (11.7 %) have wellposedness determinant < 0.001**, minimum
**7.61962843538e−05**. **Run 1 ran plain `checkMesh` only, which does not perform
this check, and correctly recorded `Mesh OK`; that record is TRUE and is not
withdrawn.** `MESH_STANDARD` §6 does not list cell determinant among the hard
errors, so the birth certificate's verdict is **`flagged`**, not `broken` — **and
the advisory is recorded, never annotated away.**

> **A HYPOTHESIS THIS LANE FORMED AND THEN REFUTED AGAINST ITSELF, recorded so
> nobody re-opens it.** I suspected the 1° wedge — chosen in run 1 to push the
> `sec(t/2)` bias below the reference's own rounding — had bought that bias at the
> cost of wellposedness. **Measured: holding the 25×25 topology and varying the
> wedge total angle 1° / 5° / 10°, the under-determined cell count is 73 at ALL
> THREE angles and the minimum determinant moves only 7.61962843538e−05 →
> 7.56303252844e−05 (0.7 %) across a 10× change in angle.** **The 1° choice is
> EXONERATED: it costs no wellposedness.** The cause is the **80:1 axial:radial
> cell stretching** (aspect ratio 160), which is identical at every angle — the
> same structural choice that produces the axial Péclet number of §10.1.

**R2 does not change the mesh.** It is R3's third candidate.

---

## 11. THE LITERATURE LIMB — ON THIS BOX ONLY, AND **SUBMISSIONS ARE PARKED**

**`CLAUDE.md` rule 7 and charter §8: this lane files nothing, posts nothing,
registers nothing and asks nothing upstream, ever. Reading is fine; sending is
Sanaa's alone and is taken by her.** `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md`
§4.4 is explicit — *"Drafts only: … never post, comment, or create accounts"* —
and its §4 obliges a **docket proposal, not a memo**, once this team acts on the
clause; that proposal is drafted for the supervisor in the lane report and is
**not filed here**.

`docs/papers/`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md` and
`docs/standards/` were swept. **Four on-box findings bear on this rung:**

1. **`N-D30` (dafoam) — a DIRECT PRECEDENT FOR THIS EXACT SWAP.** *"Swapping
   `GAMG` for `smoothSolver`/`GaussSeidel`/`nSweeps 1` on `p` in a transonic
   `DARhoSimpleCFoam` case **removes the forward-AD build's NaN** and makes BOTH
   builds' continuity error worse."* **This lab has already measured that this
   swap can change a NaN outcome** — which is arm **A6**. It also warns that the
   swap **worsened the continuity error**, so a converging A6 must be read with
   that in mind.
2. **The cfd team's `DPW8_V2` L4 divergence diagnosis (`C-4`) — the same
   experimental shape, already run in this lab.** Two arms, *"Arm A relaxation,
   Arm B momentum-upwind; both arms graded, no gate issued"*. **Both of its arms
   are exactly the two candidates §5 redirects R3 to**, and *"no gate issued"* is
   the same discipline as §4's `NOT A RESULT` ceiling.
3. **`N-AV5` — this team's own finding, and it is a control.** VMFL001 laminar
   `simpleFoam` at `p 0.3 / U 0.7`, `p` GAMG / `U` smoothSolver, no
   `residualControl`, central schemes — **reached Ux 4.69187e−14 at 1 024 cells.**
   **The configuration is not intrinsically broken.** VMFL001's axial cell Péclet
   is ≈**0.16**, against VMFL007's **186** — a factor of ≈1 170.
4. **`L-...` on `RE_SIGFPE` — a warning this comparator heeds.** A regex hunt for
   `SIGFPE` in an OpenFOAM log has a **measured 100 % false-positive rate**,
   because every run prints `trapFpe: Floating point exception trapping enabled`
   at startup. **`grade_vmfl007_r2.py` therefore never greps for it: `rc` is read
   as an integer from `RUN_RC.txt` on disk.**

**Nothing on this box addresses GAMG agglomeration on a strongly
variable-coefficient Laplacian directly, and nothing addresses non-Newtonian
SIMPLE convergence.** That gap is itself a finding and is reported as one; it is
**not** filled by reaching off the box.

---

## 12. THE PRE-FLIGHT (charter v1.4 Clause B) — ALREADY RUN, AND WHAT IT FOUND

**In scratch under `/tmp/claude-1000/`, OUTSIDE `verification/runs/`**, so it
cannot create a `0/` or a time directory that would trip the age guard or consume
the run the guard protects. **Measured cost: ≈1.9 core-minutes of the 5 core-min
the supervisor authorised** — an aborted first attempt (~10 s), the three-angle
wedge-determinant comparison of §10.2 (~15 s), a six-arm mesh-and-solve smoke
(44 s) and the launcher's own `--smoke` path (43 s): ≈112 wall s, serial.

- **All six arms launch clean**: `rc = 0` on one iteration, 625 cells; every arm
  instantiates `viscosityModels::powerLaw` **and** `laminar { model Stokes; }`;
  **zero** mentions of `generalizedNewtonian`; all **six** monitors written.
- **Five distinct solver tags in the logs** — `GAMG` (A1, A2), `DICPCG`,
  `GAMGPCG`, `DICPBiCGStab`, `smoothSolver`. **A1 and A2 print the SAME tag**, so
  the log alone cannot tell them apart; the comparator therefore establishes each
  arm's identity by hashing **the `fvSolution` that actually ran in the run
  directory** — *evidence is derived from what EXECUTED, never from what was
  DECLARED*.
- **Launcher guards exercised and each one fired**: no `--prereg-sha` → abort; an
  `--arm` flag → abort (there is none); a non-commit sha → abort.
- **The mesh birth certificate** is `mesh/birth_certificate_L1.json` with its
  `checkMesh` and `-allGeometry` logs beside it — **this team's first**, against
  the **23 checked-but-uncertified** meshes charter v1.4 names.
- **A recorded observation that changed nothing.** First-iteration `p`-solver
  counts were A1 **429**, A2 **1**, A3 **1**, A4 **26**, A5 **1**, A6 **114**.
  **The slate order and the §3 criterion were both fixed and committed before this
  was seen, all six arms run regardless, and one iteration is not evidence about
  convergence.** It is recorded because a number seen and not written down is the
  one that quietly steers a later choice.

**A defect this lane found IN ITS OWN comparator, caught by its own mutation
control, and repaired before the freeze.** The planted-zero control was first
written with a **value-relative** tolerance (`1e−9 × |value|`). On run 1's diverged
series, values reach **9.4e+144**, where adding the **1.234e−3** plant changes
nothing — the plant is far below the floating-point resolution of the number it is
added to — so the read-back delta is exactly **0.0** and a value-relative
tolerance of **1e+135 waves it through**. **The control would have certified a
reader provably unable to see its own plant.** It now requires the plant to be
recovered to within **0.1 % of itself**, and the mutation control that caught it is
a permanent selftest check. **Run 1's frozen comparator does NOT share this defect
— it uses an absolute `PLANT_DAT_TOL = 1e−12` and would have refused correctly.
This was mine, not the frozen artifact's, and it is recorded that way.**

---

## 13. THE GRADING PATH, FIXED AT THIS COMMIT

| artifact | path (all under `cases/ansys_verification/VMFL007_R2/`) |
|---|---|
| **comparator** | `grade_vmfl007_r2.py` |
| **launcher** | `run_vmfl007_r2.sh` |
| **arms** | `arms/A{1..6}_*.fvSolution` — blobs listed in §2 and in both scripts |
| **case inputs** | `case/**` — blobs in §8 |
| **mesh certificate** | `mesh/birth_certificate_L1.json` + `log.checkMesh.L1` + `log.checkMesh.allGeometry.L1` |

`run_vmfl007_r2.sh --prereg-sha <sha>` **refuses to start a solver** unless
`<sha>` is a real commit carrying **this file**, and unless
`grade_vmfl007_r2.py --verify-frozen <sha>` confirms the comparator on disk **is**
the committed blob. Run outputs go to
`verification/runs/ansys_verification/VMFL007_R2/<arm>/` and nowhere else.

**The evidentiary ordering, which is the point of committing in two acts:** the
machinery landed **first**, at **`1387b89f3fb304b75dc83399700e36201731dc6f`**,
2026-08-25T17:36Z, in a commit whose message states that no graded compute had
run and none was created — and
`verification/runs/ansys_verification/VMFL007_R2/` did not exist at that commit.
Run 1's close-out landed **between** the two, at
**`2793f23e47125f6c241540d77428fed09bd59ef5`** (verdict `NOT A RESULT`, tier
`NOT HELD`, register row #8, calibration row `C-72`). **This document — the slate, the criterion,
the caps, the labels — lands separately and afterwards.** The criterion therefore
cannot have been chosen to fit an answer, because at neither commit did an answer
exist.

---

## 14. WHAT THIS LANE COULD NOT VERIFY — said plainly

1. **That any arm will converge.** §9 predicts none will. It is a prediction.
2. **That the convection scheme IS the cause.** §10.1 is a strong candidate with
   three named uncontrolled differences. **R2 does not test it and this document
   does not claim it.**
3. **The cost of arms A2–A6.** No measurement exists at 10 000 iterations; the
   pre-flight's iteration-1 timings were resolution-limited. The estimate is
   **weak and labelled weak**, and the caps carry the risk.
4. **The size of the contention effect.** Named, never measured, never subtracted.
5. **The mechanism by which the divergence begins at iteration 2.** Measured that
   it does; not established why.
6. **Whether the 73 under-determined cells contribute at all.** Measured that they
   exist and that the wedge angle does not cause them. Their effect is untested.

---

## 15. THE VERDICT VOCABULARY THIS RUNG MAY PRODUCE

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and nothing else. **Current state: `PENDING`** —
`verification/runs/ansys_verification/VMFL007_R2/` does not exist.

**Decided now:** the **case-level verdict of R2 is `NOT A RESULT`** on any
outcome, because R2 is single-grid (§4). The **tier** is
**`NOT HELD`** — R2 seeks no credential and produces none. **The product is the
arm classification table**, and it is a finding whichever way it lands.

**The gate can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the
reverse.**

---

## 16. RECORD-UPDATE DUTY (charter §7, v1.4 Clause C) — DRAFTED, NOT LANDED

**CHARTER/DOC UPDATE LINE:** drafted for the supervisor in
`cases/ansys_verification/VMFL007_R2/LANE_REPORT.md` — **four `N-AV` numerics
candidates** (the scale-invariant-residual blindness; the `nuMin` floor as a
positive-feedback amplifier of divergence; `SIGFPE` in `GAMGSolver::scale` as an
overflow symptom; the VMFL005/VMFL007 scheme comparison) and **two lesson
candidates**. **NOT LANDED by this lane**: `N-*` and `L-*` numbers are assigned at
commit from the tail (`CLAUDE.md` rule 11) and these are the supervisor's to land
after its read.

---

## 17. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-25 | Frozen. Six-arm linear-solver/preconditioner slate in a fixed order; convergence criterion frozen before compute; falsification arm and its prediction declared; per-arm cap 20 core-min, slate cap 90; case-level verdict ceiling `NOT A RESULT` (single grid). No graded compute had run at this commit and `verification/runs/ansys_verification/VMFL007_R2/` did not exist. |
