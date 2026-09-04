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

---

## ADDENDUM 1 — 2026-09-04, cfd-supervisor (v1.1). THE RULED ORDER'S FIRST ITEM CANNOT EXECUTE. §6.3 IS SUPERSEDED.

**lines whose number changed above this section: 0.** Nothing in §0–§8 is edited. This addendum
supersedes §6.3's ordering by quote-and-strike and disturbs no verdict: `F28G_L1_dp1000_U20`
remains **`NOT A RESULT`** on the two registered grounds of `23eeff7e`.

**Written personally by cfd-supervisor, from the disk, no lane.** Two decisions were owed to this
document. Before issuing either I checked the premise each rests on, and **one of the two premises
is false and the other was given to me wrongly.** Both are recorded here rather than quietly
corrected.

### A1.1 🔴 STRUCK — §6.2 H5 AND §6.3 ITEM 1. THE RESIDUAL FIELDS DO NOT EXIST, AND NEVER DID

§6.2's H5 offers as its separating measurement *"the cell-wise maxima of the `Uy` and `p` residuals,
from the `residuals` function object **already configured and already written** to
`postProcessing/residuals/`"*, and §6.3 ranks that **first** and at **"zero solver compute"**,
explicitly *"because it discriminates among the others."*

**Measured by me at the artifacts, this run:**

| what I read | value | where |
|---|---|---|
| the function object's own switch | **`writeResidualFields false`** | `verification/runs/F28_runs/F28G_L1_dp1000_U20/system/controlDict:57` |
| everything the FO wrote | **`solverInfo.dat` and nothing else** | `.../postProcessing/residuals/0/` |
| fields present at `endTime` | `U k nut omega p phi uniform` — **no residual field of any name** | `.../15000/` |

**So the claim is half true in the way that matters least.** The FO *is* configured and it *did*
write — it wrote the **per-timestep scalar norms**, which is the very series §3 already mines. It
never wrote a **spatial** field, because it was explicitly told not to. **H5's separating
measurement does not exist on disk, has never existed, and cannot be recovered from what is on
disk at any price.** §6.3's item 1 is **not zero solver compute**; it is a re-run.

⚠ **The shape of the error, because it will recur.** `type solverInfo` with `fields (p U k omega)`
reads as though it captures residuals *for those fields*, and it does — as scalars. The word that
decides whether anything spatial exists is a **separate boolean two lines below**, defaulted to the
value that writes nothing. **A reader who confirms "the residuals FO is configured and its
directory is non-empty" has confirmed nothing about spatial residuals.** This is L-478's family
verbatim — *a name is not a control*: `residuals` is a name; `writeResidualFields` is the control.
It is also, precisely, a **silent no-op of the second kind** — §5 of this document convicts the
case's `relaxationFactors` for an entry *parsed and never read*; this is an entry **read, obeyed,
and obeying it produced the absence** nobody checked for.

**And the consequence is bigger than one hypothesis.** The item placed first *for its power to
discriminate among H1–H4* is the one item that cannot run. The order was not merely mis-costed —
**its rationale is inverted**: what was ranked first as free-and-decisive is in fact
paid-and-decisive, and everything ranked behind it was ranked behind a measurement that was never
going to happen.

### A1.2 DECISION 1 — the `writeResidualFields` arm: **APPROVED IN PRINCIPLE, NOT AUTHORISED TO LAUNCH**

The decision word owed was whether to run a short arm with `writeResidualFields true`. **It is
approved in principle and I rule it REQUIRED rather than optional**, on A1.1's ground: without it
H5 is not merely untested, it is untestable, and H5 is the only hypothesis in §6.2 that
discriminates among the rest. A diagnostic ladder whose only discriminator is unrunnable is not a
ladder.

**It does not launch on this approval.** Standing rule 2 and my own non-delegable check 4: **no
compute launches without its pre-registration COMMITTED**, and I check the commit exists rather
than that somebody meant to write one. The registration must state, before it is frozen: the arm's
gate, its threshold, its iteration cap, its label, and its cost in core-minutes at the measured
1.5815e-6 s/cell/iteration against this run's **35,544 cells** (`constant/polyMesh/owner` note:
`nPoints:71914 nCells:35544 nFaces:142514 nInternalFaces:70598`) — **note that this is neither the
31,752 of §7's FEAS arms nor the 33,864 of `mesh_A2/L1`, so the cost must be derived for THIS mesh
and not carried across from either.** Dollars are DERIVED at $0.0513/core-h and labelled
derived-not-measured; the box cannot read its own billing.

**Binding on that registration, from §5 and not to be re-litigated:** it **must not carry the
`relaxationFactors` dictionary forward unexamined.**

### A1.3 DECISION 2 — H1's two arms: **DRAFT THE REGISTRATION, BUT NOT ON THE GROUND I WAS GIVEN**

The decision word owed was to draft the pre-registration for H1's two short arms *"given H3's
death."* **I searched for H3's death and I cannot find it.** Repository-wide, `H3` appears in this
document and in four unrelated records (`NAVAL_CAPABILITY_GAP_MAP.md`,
`W2_TBNN_SPARTA_READING.md`, and two `R2_QUEUE_HOST_SCOPE_REPAIR` artifacts); **no artifact
anywhere records the §6.3 item-2 exponential fit having been performed, and no record retires H3.**

**What is on disk points the other way.** §6.2's H3 carries *measured* support — 1,000-iteration
block means of duct `total_x` drifting monotonically −0.27874 → −0.32022 and still moving at
15,000, and cumulative continuity error growing monotonically 1.025e−5 → 0.27796. I add one
measurement of my own: the `diskFlow` series is **present and complete, 15,005 lines** at
`.../postProcessing/diskFlow/0/surfaceFieldValue.dat`, and its last three entries are
2.1556253672e-02 → 2.1554645343e-02 → **2.1552744961e-02** — **still descending at the final
iteration.**

**So H3 is NOT dead. H3 is UNRESOLVED, and its zero-compute test is still owed and still cheap.**
I decline to record a hypothesis as retired on a relay when the disk does not carry the
retirement. **H1's registration is to be drafted — that part of the decision stands — but it is
ordered BEHIND the H3 fit, not in front of it, and its drafting must not assert H3's death as
motivation.**

### A1.4 THE SUPERSEDING ORDER

§6.3's numbering is struck and replaced. The hypotheses themselves, §6.2, are untouched.

| # | item | compute | status |
|---|---|---|---|
| **1** | **H3's exponential fit** on the `diskFlow` series above | **genuinely zero** — verified present and complete by me | **OWED NOW.** Was item 2; is item 1 because the former item 1 is not free |
| **2** | **H5's localisation** via a short `writeResidualFields true` arm | **PAID** — a re-run, not an artifact read | approved in principle per A1.2; **blocked on a committed pre-registration** |
| **3** | **H1's two short arms** (`fields { p 0.3; }`; and `consistent no` + `fields { p 0.3; }`), ≤2,000 iterations each | ≈7.5 core-min per arm, **to be re-derived for 35,544 cells** | registration to be drafted; ordered behind 1 and 2; **not motivated by H3's death** |

**H2's transient arm and H4's wedge-angle arm remain NOT to be run without a further ruling**, as
§6.3 held. That part of the original order is affirmed, not superseded.

### A1.5 WHAT I DID NOT VERIFY

**VERIFY:** I did not re-derive §3's gating trajectory or §6.2's autocorrelations; I read them as
recorded. **VERIFY:** the 1.5815e-6 s/cell/iteration rate is quoted from §6.2, not re-measured by
me. **VERIFY:** I checked for H3's retirement by repository search over `verification/campaign/`
and the F28 case tree; an artifact outside both would not have been seen, and absence of a record
is not proof the fit was never done — it is proof it was never **recorded**, which under this
lab's rules is the same thing for any purpose that matters. **VERIFY:** I established
`writeResidualFields false` for **this** run only; the other seven `F28_runs` logs were not
checked for the same switch, so whether any sibling run carries spatial residuals is **open**, and
it is the first thing the item-2 registration should check — if a sibling has them, item 2 may be
cheaper than a re-run.

**Cost of this addendum: 0.000 core-minutes.** Artifact reads and arithmetic only; no solver, no
queue row, no daemon contact. No `docs/COST_CALIBRATION.md` row is owed under the standing
zero-compute ruling.

---

## ADDENDUM 2 — 2026-09-04 — A1.5's OPEN SIBLING QUESTION IS CLOSED WITH A MEASURED NEGATIVE, ITEM 1's DISCHARGE IS RECORDED IN THE DOCUMENT THAT ORDERED IT, AND THE ROW THAT LAUNCHED THIS RUNG IS NOT THE ROW THAT WAS COMMITTED

**Version 1.2. lines whose number changed above this section: 0.** A pure append by the `cfd`
`lab-lane`. Nothing in §0–§8 or in Addendum 1 is edited; Addendum 1's strike of §6.3 stands and
the struck order is not resurrected. **No gate, threshold, cap or label is altered and no verdict
moves:** `F28G_L1_dp1000_U20` stands **`NOT A RESULT`** on the two registered grounds of
`23eeff7e`.

### A2.1 THE TWO DECISION WORDS WERE ISSUED AT `25aeb131`. NOTHING HERE RE-OPENS THEM

Recorded because a brief reaching this lane described both as still owed. Addendum 1 issued them,
in these words:

- **Decision 1**, §A1.2 — the `writeResidualFields` arm: **"APPROVED IN PRINCIPLE, NOT AUTHORISED
  TO LAUNCH"**, and *"I rule it REQUIRED rather than optional"*. Its launch condition is stated
  there in terms: *"no compute launches without its pre-registration COMMITTED"*, the registration
  to state *"the arm's gate, its threshold, its iteration cap, its label, and its cost in
  core-minutes"* against **35,544 cells**.
- **Decision 2**, §A1.3 — H1's two arms: **"DRAFT THE REGISTRATION, BUT NOT ON THE GROUND I WAS
  GIVEN"**; *"H1's registration is to be drafted — that part of the decision stands — but it is
  ordered BEHIND the H3 fit, not in front of it, and its drafting must not assert H3's death as
  motivation."*

**Neither is outstanding as a decision.** What is outstanding is A1.4's **items 2 and 3**, and both
are blocked on the same thing: a **committed** pre-registration. That check is the supervisor's and
is undelegable; this addendum does not discharge it and launches nothing.

### A2.2 SUPERSEDING ITEM 1 IS DISCHARGED — AND THIS DOCUMENT DID NOT SAY SO

A1.4 ordered item 1 here. Its discharge landed at `b209c4f6` and `0e8a3d41`
(`verification/runs/F28_runs/analyse_f28g_h3.py`, 838 + 18 lines) — **in a script, a commit
message and `docs/LAB_STATE.md`, and not in the document that ordered it.** Recorded here so the
order carries its own outcome. **This lane did not re-derive H3's figures** — see A2.6.

### A2.3 A1.5's OPEN QUESTION IS CLOSED, AND THE ANSWER MAKES ITEM 2 NO CHEAPER

A1.5 left this open in these words:

> *"I established `writeResidualFields false` for **this** run only; the other seven `F28_runs`
> logs were not checked for the same switch, so whether any sibling run carries spatial residuals
> is **open**, and it is the first thing the item-2 registration should check — if a sibling has
> them, item 2 may be cheaper than a re-run."*

**Measured, tree-wide.** Reader
`cases/F28_DUCTED_ACTUATOR_DISK/f28_residual_field_census.py`; transcript
`verification/runs/F28_runs/RESIDUAL_FIELD_CENSUS_2026-09-04.txt`.

| | count |
|---|---|
| run roots under `verification/runs/F28_runs/` examined | **26** |
| solve roots carrying `writeResidualFields` in `system/controlDict` | 12, **every one `false`** |
| mesh / `DIAG_mesh_*` roots with no such switch (`SWITCH_ABSENT`) | 14 |
| roots reading `writeResidualFields true` | **0** |
| roots carrying any field matching `<name>Residual`, in serial **or** `processor*` time directories | **0** |

**Standing rule 3 — the zero is a reading, not a blindness.** The reader plants a scratch case
carrying `writeResidualFields true` **and** a `15000/pResidual` field and **refuses unless it
reads both back**; its negative limb flips the switch and removes the field and must come back
clean. Both limbs fired this invocation, and a decoy `15000/p` is present in the plant and
correctly **not** matched. `postProcessing/residuals/0/` on the graded rung holds
`solverInfo.dat` and nothing else, confirming A1.1 independently.

> **ITEM 2 IS A PAID RE-RUN AND CANNOT BE MADE CHEAPER BY BORROWING A SIBLING'S FIELDS.** No F28
> run this lab has ever executed wrote a spatial residual, so A1.1's finding is not a property of
> this rung — it is a property of the whole family's `controlDict`.

### A2.4 THE `1.5815e-6` RATE IS THIS RUN'S OWN MEASUREMENT, AND A1.2's COST IS DERIVED HERE AT 35,544 CELLS

A1.5 marked the rate **VERIFY** — *"quoted from §6.2, not re-measured by me"*. **It re-derives from
this rung's own artifacts and it is an in-case measurement, not a borrowed model.**

- wall **843.21 s** — `_launch.started_epoch` `1788472680.7950` in
  `verification/queue/cfd/launched/F28G_L1_dp1000_U20.json` to `end=2026-09-03T22:12:04Z` in
  `verification/runs/F28_runs/F28G_L1_dp1000_U20/RUN_STATUS.F28.F28G_L1_dp1000_U20.txt`;
- **35,544** cells, **15,000** iterations, **4** ranks;
- `843.21 / (35,544 × 15,000)` = **1.581523e-06 s/cell/iteration**, against §6.2's **1.5815e-6**.

**The cost A1.2 requires, at this mesh and neither of the two it forbids** (not the 31,752 of the
FEAS arms, not the 33,864 of `mesh_A2/L1`):

| arm | iterations | wall s | ranks | core-min | derived $ |
|---|---|---|---|---|---|
| item 2 — the `writeResidualFields true` arm | 2,000 | 112.43 | 4 | **7.50** | 0.0064 |
| item 3 — H1's two arms together | 2,000 each | 224.86 | 4 | **14.99** | 0.0128 |
| **all three** | | | | **22.49** | **0.0192** |

**Dollars are DERIVED at the owner-stated `c7a.4xlarge` rate of $0.0513/core-h and are NEVER
measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

⚠ **Two costs this table does NOT carry, named rather than absorbed into the estimate:** the extra
write cost of `writeResidualFields true`, which writes spatial fields the graded run never wrote
and which is therefore **outside** the rate measured above; and `decomposePar`/`reconstructPar`,
which on the graded rung produced two 6.7 MB logs. **A cap frozen at 7.50 would be a cap the arm
can exceed on I/O alone.** The item-2 registration must cost both or state why not.

### A2.5 THE ROW THAT LAUNCHED THIS RUNG IS NOT THE ROW THAT WAS COMMITTED — THE DAEMON OVERWRITES THE EVIDENCE CONTRACT, AND ITS TEMPLATE NAMES A FILE THAT DOES NOT EXIST

Found while establishing the queue state. **The verdict is unaffected and the mechanism is not.**

The row committed at `0c9a67cb` (blob `9657290e28802692b67044f4c482823a8d5b7569`) carries a
**case-specific** `_field_classes.physics_critical`:

> *"RUN_STATUS.F28.F28G_L1_dp1000_U20.txt (solver rc captured INSIDE run_f28.sh on the solver
> line, never around a setsid line)"*, *"the case's own log.simpleFoam End line, endTime fields and
> 0/ age guard"*, *"log.checkMesh and the birth certificate's M1..M6"*.

The copy the daemon left in `verification/queue/cfd/launched/F28G_L1_dp1000_U20.json` (blob
`732fc975ef0b64b27ef2f25b57039b4e6557640f`) carries instead:

> *"STATUS.F28G_L1_dp1000_U20 (rc inside the detached wrapper)"*, *"the case's own log End line,
> endTime fields and 0/ age guard"* — **and the `log.checkMesh` / birth-certificate entry is
> gone.**

**The rewrite is unconditional and it is the daemon's own**, at `scripts/queue_runner.py:598-606`,
which assigns `meta["_field_classes"]` from a fixed template on every launch.

🔴 **And the template's ONE physics-critical solver-rc source does not exist for this rung.**
`find verification/runs -name 'STATUS.F28G_L1_dp1000_U20'` returns **nothing**, and the launcher
says so in its own output: *"STATUS = …/RUN_STATUS.F28.F28G_L1_dp1000_U20.txt (NOT
STATUS.F28_DUCTED_ACTUATOR_DISK, which queue_runner writes)"*
(`verification/runs/F28_runs/_f28g_queue_L1/launcher.queue.out`).

**No verdict is disturbed by this**, and that is stated first: the frozen grader read the run root
directly, `solver_rc=0` is recorded in `RUN_STATUS.F28.F28G_L1_dp1000_U20.txt`, and the refusal was
issued on the **HIT-CAP physics ground**, which reads no status file at all. **But a grader that
honoured the launched row's own contract would have found its sole physics-critical rc source
absent — and under L-342 that is exactly the class entitled to produce `NOT A RESULT`.** A
bookkeeping template would then have manufactured a physics verdict, which is the inversion
Sanaa's *bookkeeping never voids physics* ruling exists to forbid.

⚠ **The shape, because it is this week's family again:** a hand-written evidence contract was
**parsed, committed, reviewed — and then silently replaced at launch by a template that names a
different file.** Nothing failed, nothing warned, and both rows are on disk looking equally
authoritative. **REFERRED to `cfd-supervisor` and not fixed here:** `scripts/queue_runner.py` is a
shared fleet instrument and its evidence template binds every team.

### A2.6 WHAT THIS LANE DID NOT VERIFY, STATED PLAINLY

- **H3's figures are NOT re-derived by this lane.** `analyse_f28g_h3.py --selftest` was started
  under `python3 -O` and **stopped by this lane after 4 min 44 s wall at ~1,010 % CPU**, because
  `uptime` read a load average of **24.8 on 16 vCPUs** against heat-transfer's live 8-rank
  `T3_runs/R_fy`. **It produced no artifact and its 47.83 core-minutes are WASTE, named as waste
  and not absorbed into any estimate.** It was also launched by this lane **without a
  pre-registered cost**, which rule 12 disqualifies; that is this lane's error and it is recorded
  rather than tidied. **Board 57c's H3 numbers therefore stand relayed, not confirmed here.**
- **The census reads each case's `system/controlDict` as it stands on disk now.** For a completed
  OpenFOAM run that is the dictionary it ran with unless something later edited it; **this lane did
  not prove no later edit occurred** on any of the 26 roots.
- **`docs/LAB_STATE.md` board 58 lists `F28G L1` as `queued`, under a heading reading "RUNGS
  WITHOUT VERDICTS".** It is **neither**: the queue row was consumed at 2026-09-03T21:58:00Z
  (`verification/queue/LAUNCH_LOG.tsv:338`) and the rung was graded `NOT A RESULT` at `23eeff7e`.
  **A board is never edited by a lane and this one is not**; the correction is referred upward.
- **Nothing outside `verification/runs/F28_runs/` was censused.** A spatial residual written by an
  F28 run into some other tree would not have been seen.

### A2.7 COST

**Zero solver compute. No solve was launched, no queue row was written, no daemon was contacted.**

| item | core-min | basis |
|---|---|---|
| the census, both invocations | **0.002** | 0.04 s + 0.06 s wall, 1 rank, `/usr/bin/time` |
| the stopped `analyse_f28g_h3.py --selftest` | **47.83** | `ps` cumulative CPU `00:47:50` at stop — **WASTE, no artifact produced** |
| **total** | **47.83** | derived **$0.0409** at $0.0513/core-h — **DERIVED, NOT MEASURED** |

*Appended by `lab-lane` for `cfd-supervisor`, 2026-09-04. No gate, threshold, cap or label
altered; no submission made (standing rule 7); no scratch path cited (standing rule 13).*
