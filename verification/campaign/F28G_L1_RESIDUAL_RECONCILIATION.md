# F28G L1 — RESIDUAL RECONCILIATION: what `0.1579` is, who was wrong, and what it changes

**Date:** 2026-09-03 (box clock)
**Team:** cfd
**Rung:** `F28G_L1_dp1000_U20`
**Record reconciled:** `verification/campaign/F28G_L1_RESULTS.md`, graded at commit `23eeff7e`
**Addenda landed with this document:** that record's Addendum 1 (§4.1 "and flat") and Addendum 2
(§5's configuration count)
**Compute:** **zero core-minutes.** No solver was launched, no queue row was touched, the queue
daemon (pid 1664) was not contacted, and `JF1G_P1_C2` (pid 491048) was left alone.

---

## 0. What this document is and is not

It is a reconciliation of a **challenge to a number in a graded record**, and of that challenge's
withdrawal. **It does not re-grade the rung and it does not disturb the verdict.**
`F28G_L1_dp1000_U20` remains **`NOT A RESULT`** on the two registered grounds issued at `23eeff7e`.
Nothing frozen was edited (standing rule 6); no submission was made (standing rule 7).

---

## 1. The discrepancy as it was raised

`F28G_L1_RESULTS.md` §4.1 states:

> At iteration 15,000 the gating **initial** residual for `p` is **0.1578798513** — five orders of
> magnitude above its 1e-6 criterion, and flat.

`cfd-supervisor` read the log directly and found the **last** `Solving for p` line to be
`Initial residual = 0.0008638982113`, with a trajectory of 1.0 → 0.001232 → 0.001351 → 0.000864 —
a descent of about three orders followed by a plateau near 1e-3, and **no value of 0.1579 anywhere
in it**. On that reading the record's sentence looked fabricated or misattributed.

**Both readings are of real lines in the same file. Only one of them is of the quantity the solver
actually gates on.**

---

## 2. What `0.1579` is — established from the code, not assumed

**It is exactly what the record says it is: the gating initial residual of `p` at iteration
15,000.** The record's number and its label are **both correct**.

### 2.1 The number is unique and correctly located

`0.1578798513` occurs **exactly once** in the 656,692-line
`verification/runs/F28_runs/F28G_L1_dp1000_U20/log.simpleFoam`, at line **656652**, inside the
`Time = 15000` block that opens at line **656647**:

```
GAMG:  Solving for p, Initial residual = 0.1578798513,   Final residual = 0.000898864967, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0008638982113, Final residual = 8.607258149e-06, No Iterations 9
```

It is in the `Initial residual` field, not the final one (the final on that line is 8.99e-4), and it
is the **first** of the two `p` solves in the block.

### 2.2 Why there are two `p` solves per iteration

`system/fvSolution`, SIMPLE block: **`nNonOrthogonalCorrectors 1`**. Measured on the log:
**30,000** `Solving for p,` lines against **15,000** `Time = ` lines. The first solve of each block
is the gating one; the second is the non-orthogonal corrector.

### 2.3 Which of the two the gate tests — read from the OpenFOAM v2606 source on this box

`/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/solutionControl/solutionControl/solutionControl.C`,
in `maxTypeResidual`:

```cpp
residuals.first() = cmptMax(sp.first().initialResidual());
residuals.last()  = cmptMax(sp.last().initialResidual());
```

and `.../solutionControl/simpleControl/simpleControl.C`, in `criteriaSatisfied()`:

```cpp
const bool absCheck = (residuals.first() < residualControl_[fieldi].absTol);
```

**`residualControl` tests `sp.first()` — the FIRST solve of that field in the time step.** `cmptMax`
is a maximum over *vector components*, not over correctors.

This is the same reading the lab had already settled and boarded: `docs/LAB_STATE.md:24503` cites
these two lines verbatim, and the cfd team's own max-over-equations reducer at commit `184c00af`
implements the principle in terms — *"The reducer takes the FIRST initial residual per field per
time step, then the max over fields."*

### 2.4 Each candidate explanation, tested and disposed of

| candidate | disposition |
|---|---|
| **A max over `{p, Ux, Uy, Uz, k, omega}` belonging to a different equation** | **The two readings coincide, and both name `p`.** First-solve initial residuals at iteration 15,000: `Ux` 4.089e-4, `Uy` 1.021e-2, `Uz` 6.144e-5, **`p` 1.579e-1**, `omega` 1.370e-8, `k` 1.268e-4. The max over equations **is** `p`. The record's attribution is right under either reduction. |
| **The `res p` defect (board 51, `docs/LAB_STATE.md:24501-24513`)** | **Not live in the record** — the record used the first solve, correctly. **Live in the challenge**, see §4. |
| **A final residual, or the wrong column** | No. The figure is in the `Initial residual` field. |
| **A different iteration, or a loose pattern matching another field** | No. One occurrence in the whole log, inside the `Time = 15000` block. |

---

## 3. The ruling, and how the challenge's trajectory arose

**The record is right. The challenge's log read was of the corrector solve.**

The challenge's four sample points were reconstructed exactly. Sampling the 30,000-entry
`Solving for p` stream at positions 1 / 10000 / 20000 / 30000 returns
`1`, `0.001351190853`, `0.001061789099`, `0.0008638982113`.

**Position 1 is odd — a gating solve. Positions 10000, 20000 and 30000 are all even — every one of
them a corrector solve.** So the apparent "descent of three orders" is one gating value compared
against three corrector values, and the "plateau near 1e-3" is the corrector series, which really
does sit near 1e-3 but **is not the quantity `residualControl` tests**. The quoted `0.001351` is
p-line 10000 — iteration 5,000's corrector.

**The true gating trajectory**, measured: iter 1 = 1 · 10 = 0.4029 · 100 = 0.4078 · 1,000 = 0.1803 ·
5,000 = 0.2299 · 10,000 = 0.2109 · 12,500 = 0.1686 · **15,000 = 0.1579**. Last 4,000 iterations:
min 0.1171, max 0.5132, mean 0.1855, stdev 0.0375. **It never falls below 0.0642 in the whole run.**

### 3.1 What it changes for the verdict: nothing. Confirmed, not relayed.

Both registered grounds were re-measured independently for this reconciliation:

- **HIT-CAP ground** is structural: `ITER_CAP = 15000` (`analyse_f28g.py:245`) against the run's
  `endTime` of 15000. **It reads no residual value at all.** Corroborating, re-measured across
  **all eight** `log.simpleFoam` files under `verification/runs/F28_runs/`: `SIMPLE solution
  converged` occurs **0 times in every one**.
- **Not-plateaued ground** reads `postProcessing/forcesDuct/0/force.dat`. Both of the record's
  figures reproduce exactly: over the last 2,000 iterations mean `total_x` = **-0.318607 N** (so
  0.001·|T_mean| = **0.000318607 N**, matching the record's relative limb to six figures) and
  **ptp = 0.0295546 N**, matching the record exactly.

**The 0.1579 figure is corroborative, not load-bearing — and it is also correct. The verdict
`NOT A RESULT` stands undisturbed.**

---

## 4. THE FINDING THAT MATTERS MORE THAN THE NUMBER

**Recorded at `cfd-supervisor`'s explicit instruction, in his terms, and attributed to him.**

The `res p` defect — **taking the last `p` solve instead of the first** — is a defect
`cfd-supervisor` **found, documented and quantified himself**. He settled it at source, boarded it
at `docs/LAB_STATE.md:24501-24513` under the heading *"THE `res p` DEFECT IS NOW QUANTIFIED, AND ON
E3 IT WOULD MANUFACTURE A WRONG `GATE REACHED`"*, and measured it at **46×–210×** across five
E2b/E2c rows, where in every row the last-solve reading **passes** the 1e-6 limb and the first-solve
reading **fails** it. He put it on his own board as a named hazard and referred it upward as an
amendment matter above both lane and supervisor.

**He then committed it by hand, with `tail -1`, against a rung whose verdict he was checking.**

In his own words, relayed here because they are the useful part of the exchange:

> Not a discipline I failed to apply: a specific defect I had catalogued and then performed.

**Why this belongs in a repository record and not in a thread.** The catalogued-and-then-performed
shape is the one this reconciliation exists to preserve. A hazard that is known, written down,
quantified and boarded is *still performed* when the reading is done by hand at the terminal rather
than through an instrument that encodes the rule. The lab's defence against this defect —
`184c00af`'s reducer, which takes the first initial residual per field per time step — **was already
built, and was not in the path** of a supervisor typing `grep … | tail -1`. **The instrument was
correct; the hand-read bypassed it.** That is a statement about where the lab's guarantees actually
live, and it generalises past this rung.

**Also on the record: the challenge was withdrawn in full, by its author, after he re-measured the
correction himself** — the 30,000-vs-15,000 line counts, `nNonOrthogonalCorrectors 1`, and
`0.1578798513` at line 656652 inside the block opening at 656647 — rather than accepting a lane's
report of it. Standing rule 9: a delegate's test is evidence, not the supervisor's read.

---

## 5. A SEPARATE DEFECT FOUND WHILE READING: the case's pressure under-relaxation is a SILENT NO-OP

**Ruled by `cfd-supervisor` a real defect independent of whether it turns out to cause the
plateau.**

`verification/runs/F28_runs/F28G_L1_dp1000_U20/system/fvSolution` carries

```
relaxationFactors { equations { p 0.3; U 0.7; k 0.7; omega 0.7; } }
```

with **no `fields` sub-dictionary**. Traced through the v2606 source on this box:

1. `applications/solvers/incompressible/simpleFoam/pEqn.H` calls `pEqn.solve()` and **never**
   `pEqn.relax()`. The only relaxation applied to pressure is `p.relax()` — **field** relaxation.
2. `GeometricField::relax()` calls `this->mesh().relaxField(name, relaxCoeff)` and applies
   relaxation **only if that returns true**; `relaxCoeff` is initialised to 1.
3. `solution::relaxField` reads **only** `fieldRelaxDict_`, returning false when neither the field
   name nor `default` is present.
4. `solution::read` sets **`needsCompat = false`** as soon as an `equations` sub-dictionary exists —
   so the backwards-compatibility branch that *would* have routed a `p` entry into
   `fieldRelaxDict_` (`if (e.starts_with('p')) fieldRelaxDict_.add(e, value);`) **never runs**.

**Therefore `p` runs unrelaxed at `alpha_p = 1.0`, and the `p 0.3` entry is parsed into the equation
dictionary and never read by this solver.** The irony is worth recording: the older flat form
`relaxationFactors { p 0.3; U 0.7; k 0.7; omega 0.7; }` **would have worked correctly** — adding the
`equations { }` wrapper is precisely what disabled it.

**The caveat stands and is not softened.** Under `consistent yes` (SIMPLEC), which this case sets,
`alpha_p = 1.0` is the *recommended* setting. So this is **not automatically an error and not
automatically the cause of the plateau.** What it unambiguously is: **a mismatch between the
numerics the dictionary appears to specify and the numerics that ran.**

**The class it belongs to.** A dictionary entry that is parsed and never read is a **silent no-op** —
the same class as `SKIP_DIRS = ("launched", "refused")` at `scripts/queue_runner.py:114`, which this
team convicted on 2026-09-03 (`d18b6733`) after `grep -c SKIP_DIRS scripts/queue_runner.py` returned
**1**: its own definition, and no reader. That family is lesson **L-478, "A NAME IS NOT A CONTROL"**
(`3950e931`) — *the source asserts a protection or a setting that no code path delivers*, and the
family is **invisible to planted-input controls**, because there is no input that makes an unread
entry announce itself.

**Binding on the successor:** the F28G successor registration **must not carry this dictionary
forward unexamined**.

---

## 6. The plateau — hypotheses only, and the ruled diagnostic order

**No mechanism is asserted.** This rung's history is the argument for that restraint.

### 6.1 What is measured, not hypothesised

**Four** configurations reached the 15,000 cap with `SIMPLE solution converged` occurring 0 times in
each — the full table is Addendum 2 of `F28G_L1_RESULTS.md`. They span **two meshes**, **two disk
loadings including OFF**, and **two farfield boundary conditions**.

**The actuator disk is exonerated by measurement.** `FEAS_L1_dp0_U20_A2` carries
`U ((0.0 0 0) 0)` — source exactly zero — and plateaus **highest of the four** (last-500 band
0.3317–0.6885). Corroborating: even when on, the source is `((166666.66666666666 0 0) 0)` —
constant `Su`, **`Sp = 0`**, purely explicit, no velocity dependence — so no feedback loop exists.

**The withdrawn pressure-reference hypothesis is dead in code as well as in the BCs.**
`pEqn.setReference(pRefCell, pRefValue)` acts only where the matrix needs a reference, and the
`fixedValue` outlet supplies one.

### 6.2 The hypotheses, each with its separating measurement

- **H1 — relaxation mismatch / SIMPLEC coupling.** `alpha_p` is effectively 1.0 while
  `alpha_U = 0.7` (equation relaxation, which *is* read). **Separating measurement:** two short
  arms, ≤2,000 iterations, one adding `fields { p 0.3; }`, one with `consistent no` plus
  `fields { p 0.3; }`. If the gating residual drops below its all-run minimum of 0.0642 in either,
  H1 is supported; if it stalls in the same band, H1 is dead. ≈7.5 core-min per arm at the
  measured 1.5815e-6 s/cell/iteration.
- **H2 — genuine unsteadiness chased by a steady solver.** **Partially separated already, at zero
  compute:** autocorrelation of the last 4,000 gating values peaks at only **r = 0.207 at lag 10**,
  decaying to r ≈ 0.006 by lag 400; the duct force peaks at **r = 0.425 at lag 6** with a long tail
  r ≈ 0.23 at lag 200. **No sharp peak at any lag, so a clean limit cycle is not supported by what
  is on disk.** Broadband unsteadiness is **not** excluded.
- **H3 — the operating point never equilibrated; the mass flow is still drifting.** Nothing fixes
  the mass flow. **Measured support:** 1,000-iteration block means of duct `total_x` drift
  monotonically **-0.27874 → -0.32022** across iterations 5,000–15,000 and are **still moving at
  15,000**; the cumulative continuity error grows monotonically **1.025e-5 → 0.27796**.
  **Separating measurement:** fit an exponential to the `postProcessing/diskFlow`
  `areaNormalIntegrate(planeFlow) of U` series already on disk.
- **H4 — near-axis wedge cells / extreme aspect ratio.** checkMesh reports max aspect ratio
  **53,458.4** on `mesh_A4/L1` (2,789 cells over threshold) and **the identical 53,458.4** on the
  A2 mesh (2,310 cells) — so the extreme is a geometric property of the wedge, not of refinement.
  Non-orthogonality is benign (max 57.9, average 9.97, checkMesh OK) and skewness 1.24 OK, so this
  hypothesis concerns aspect ratio specifically.
- **H5 — a localiser, not a rival.** At iteration 15,000 only two equations sit far from criterion:
  `p` at 1.579e-1 and **`Uy` at 1.021e-2** (last-4,000 mean 1.32e-2, min 9.40e-3), against `Ux`
  4.09e-4, `Uz` 6.14e-5, `k` 1.27e-4, `omega` 1.37e-8. In this wedge `y` is radial.
  **Separating measurement:** the cell-wise maxima of the `Uy` and `p` residuals, from the
  `residuals` function object already configured and already written to `postProcessing/residuals/`.
  Whether they sit at the duct trailing edge, the inner-surface separation, the disk-zone edge or
  the axis implicates a **different one** of H1–H4.

### 6.3 The ruled order — `cfd-supervisor`, 2026-09-03

1. **H5's localisation** — zero solver compute, from artifacts already written. First, because it
   discriminates among the others.
2. **H3's exponential fit** — zero solver compute, from the `diskFlow` series already on disk.
   *"A growing continuity error over 15,000 steady iterations is not a converging calculation."*
3. **H1's two short arms — only if 1 and 2 leave it live, and only behind a committed
   pre-registration.** Check 4 is the supervisor's and is undelegatable: a draft is brought to him,
   nothing launches.

**H2's transient arm and H4's wedge-angle arm are NOT to be run without a further ruling** — both
cost more than the question currently justifies.

---

## 7. What this reconciliation could not verify, stated plainly

- **Every hypothesis in §6.2 is untested.** No solver was launched. The autocorrelation in H2 is the
  only one carrying evidence already on disk, and it disfavours **only** the clean-limit-cycle form.
- **The residual was not localised in space** — that is item 1 of the ruled order and is not yet done.
- **The three FEAS arms were identified by cell count only** (31,752, matching the figure
  `F28G_L1_RESULTS.md` §6.1 cites for `FEAS_L1_dp1000_U20_A2`). Which `mesh_*` directory built them
  was not established; it is **not** `mesh_A2/L1`, which is 33,864 cells.
- **The reconstruction of the challenge's sample is exact for p-lines 1 / 10000 / 20000 / 30000.**
  The reported value `0.001232` did not fall on one of those four positions; it was matched by
  character (corrector magnitude), **not by identity**.
- **The `res p` defect's status in the JF1 comparator is unchanged by anything here.** This document
  establishes only that it is not live in the F28G record, and that it recurred in a hand-read.
- **`alpha_p = 1.0` was established by source trace, not by instrumenting a run.** No debug-level
  run was made to print the relaxation factors the solver actually resolved.

---

## 8. Verdict and cost

**No verdict is issued by this document and none is entitled.** `F28G_L1_dp1000_U20` remains
**`NOT A RESULT`** exactly as graded at `23eeff7e`, on the two registered grounds, both re-measured
here and both confirmed independent of the challenged figure.

**Cost: 0.000 core-minutes.** Log reads, source reads and arithmetic only. No solver, no queue
contact, no daemon contact.
