# SO3aF2 `F1` — SUCCESSOR REGISTRATION, **DRAFT ONLY. UNFROZEN. NOT A PRE-REGISTRATION.**

> **⚠ SUPERSEDED 2026-09-04 BY `FEASIBILITY_PREREGISTRATION.md` ADDENDUM 15 AND ITS CORRECTION 1. READ THOSE, NOT THIS.**
> The supervisor ruled **option a1** — a producer-only addendum to SO3aF2 — and made **three changes** this draft does not carry. **Where they differ, the addendum governs.**
> 1. **`printInterval` IS NOT CHANGED.** §7 arm `XM2` here proposes `printInterval: 1` at 0.55 core-min; the ruling keeps the registered value, and `XM2` is costed at **0.40** core-min with **no adjustment**, because the registered program is then unchanged. **§10's second falsifier is WITHDRAWN with the option change it was written for** — a prediction kept past the change that motivated it is decoration.
> 2. **Arm `R0` is a DIAGNOSTIC, not a graded reading; `XM2` is the graded arm.** §5 of this draft leaves the `rc=7` artefact question to the supervisor; it is now ruled — *bookkeeping never voids physics* makes the preserved log's physics readable, and does **not** make an arm whose producer refused the artefact of record.
> 3. **The addendum states, and this draft does not, that both `F1` readings now come from ONE FILE and therefore SHARE A FAILURE MODE** — a truncated or unwritten log moves both — followed by the discrimination the planted control measured as surviving. **"Registered" is not allowed to do the work that "measured" should.**
>
> **Left in place, not rewritten** (`CLAUDE.md` rule 6 applied to a draft by choice rather than by obligation): it is the case that was built, and the record of what was proposed is worth more than a tidy one.


> **⚠ THIS FILE IS A DRAFT AND MAY NEVER BE CITED AS A FREEZE.** It registers
> nothing, freezes nothing, and authorises no compute. It is a case built for the
> `dafoam-supervisor`, who makes the registration ruling. **NOT QUEUED. NOT
> ARMED. ZERO SOLVER CORE-MINUTES SPENT BY THIS DRAFT. SUBMISSIONS PARKED.**

Dated **2026-09-04**. Author: `dafoam` lab-lane, on the supervisor's brief to
measure whether a primal residual history is obtainable at all.

---

## 1. THE TWO CLAIMS, KEPT APART, BECAUSE THAT IS WHAT THIS ITEM EXISTS TO TEACH

ADDENDUM 13 §A13.1 measured claim 1 and left claim 2 open, deliberately. Both are
now measured. **They are still two claims and are stated as two.**

> **CLAIM A — WHAT THE TWO UNCALLED METHODS DO. MEASURED FROM SOURCE, NOT FROM
> THEIR NAMES.**
> `getResiduals` and `calcPrimalResidualStatistics` were read in the DAFoam
> source shipped inside the registered image. **Neither returns, stores or
> accumulates a per-iteration sequence.** `getResiduals` recomputes the residual
> at the *current* state into a caller-supplied flat array of length
> `getNLocalAdjointStates()` — a spatial field, one entry per local adjoint state
> DOF, with no time or iteration index. `calcPrimalResidualStatistics` returns
> `void`, recomputes the same residuals and **prints** per-equation
> Norm2/Mean/Max to screen. **Calling either would not have produced a history.**

> **CLAIM B — WHETHER A RESIDUAL HISTORY IS OBTAINABLE. MEASURED: YES, AND IT IS
> ALREADY ON DISK.**
> The DAFoam solver log this item already wrote carries a per-equation primal
> residual history for **every** primal, printed by `DAUtility::primalResidualControl`
> and sampled at the `printInterval` DAOption. **Three histories, five samples
> each, five equations each, were parsed out of the preserved
> `XM/XM.log` at zero solver cost.** `printInterval` is settable, so a
> **full per-iteration** history is one option change away.
>
> **Routes NOT tested are enumerated in §6 and are not closed by this claim.**

**Claim A does not imply Claim B and Claim B does not repair Claim A.** The
methods remain unable to supply a history; the log supplies one anyway.

---

## 2. WHAT `F1` IS REGISTERED TO READ, AND THE FINDING THAT FALLS OUT OF READING IT

`FEASIBILITY_PREREGISTRATION.md:279`, the frozen §5 row, in full:

> **F1** | all three points converge — `satisfied the prescribed tolerance`
> counted **3** in the log **AND** three residual histories present, the two
> readings **agreeing** | **counted from the log, both ways** | …

The frozen reader `so3af2_read.py` implements it at `:295–:310`: `n_tol` is
counted from `XM/XM.log`; `n_resid` is `len(j["residual_histories"])` read from
the producer's artefact `XM/so3af2_M.json`; a disagreement **refuses**; `f1` is
`n_tol == 3`.

> **⚠ FINDING — THE PRODUCER DEPARTED FROM THE REGISTERED SCORING METHOD, AND
> THAT DEPARTURE IS WHAT FAILED.** The registration says the two readings are
> **"counted from the log, both ways."** The producer implemented the second
> reading as an **object-attribute lookup on a live `DASolver`** — four guessed
> names, none of which exist (§A13.1). **The route the registration named was
> never the route the producer took, and the route the registration named works.**

This is the same shape as this item's own closure in §A13.3 — *before building an
instrument to reach a state, ask whether something already reaches it* — arriving
one layer up: **before building an instrument to reach a quantity, read what the
registration said the quantity would be read from.**

---

## 3. THE EVIDENCE, BY PATH AND COUNT

Every figure below is the output of a command run 2026-09-04, against files that
were on disk before this draft existed.

| what | value | artefact |
|---|---|---|
| frozen reader md5, still equal to its 2026-08-31 freeze | `d5f4149d43abe3a165ffe7e653b78bee` | `so3af2_read.py` |
| `Running Primal Solver` blocks | **3** | `…/XM/XM.log` |
| `satisfied the prescribed tolerance` lines | **3** | same |
| `Printing Primal Residual Statistics.` blocks | **3** | same |
| `U0 initRes:` lines (likewise `U1`,`U2`,`p`,`nuTilda`) | **15** = 3 primals × 5 samples | same |
| parsed histories: primals × equations × samples | **3 × 5 × 5** | same |
| `U0` initial residual, first → last sample, primal 0 | `1.000000e+00` → `2.535852e-08` | same |
| ledger row for the run that wrote it | `ARM=XM rc=7 wall_s=24 ranks=1 core_min=0.4000` | `…/ledger.txt:6` |
| the same counts in the **earlier** XM log, independently | **3 / 3 / 3 / 15** | `…/XM_rc7_20260903T233132Z/XM.log` |

**Two independent logs, from two separate containers, give the same counts.**

**PLANTED-ZERO CONTROL, RUN IN THE SAME INVOCATION AS THE READING (rule 3).** The
parser was shown able to read a **short** history, not merely a complete one: the
`initRes:` lines were stripped from the third `Running Primal Solver` block of a
copy of the log and the parser re-run. It read **3 blocks, 2 with residuals,
3 tolerance lines** — i.e. exactly the `n_tol=3 / n_resid=2` disagreement the
frozen reader refuses on. **A reader that can only ever read 3 is not evidence
that there are 3.**

---

## 4. THE SOURCE, READ RATHER THAN NAMED

Extracted from the registered image `dafoam/opt-packages:latest`,
digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`,
**by `docker create` + `docker cp` with no container ever started** — nothing was
executed, no solver ran, and the cost is a disk read.

| symbol | file:line inside the image | what the CODE does |
|---|---|---|
| `getResiduals` (python) | `dafoam/pyDAFoam.py:2121–2130` | allocates `np.zeros(getNLocalAdjointStates())`, fills it via the C++ call, returns it. **A snapshot vector, not a history.** |
| `getResiduals` (C++) | `src/adjoint/DASolver/DASolver.C:1157` | `updateStateBoundaryConditions(); calcResiduals();` then copies the current `*Res` fields cell-by-cell into the array. **Recomputes at the current state.** |
| `calcPrimalResidualStatistics` (python) | `dafoam/pyDAFoam.py:901–905` | delegates to `solver`/`solverAD`. **No `return` statement — returns `None`.** |
| `calcPrimalResidualStatistics` (C++) | `src/adjoint/DASolver/DASolver.C:745` | `mode=="print"` prints `Printing Primal Residual Statistics.`, then `calcResiduals()` and per-equation Norm2/Mean/Max via `Info`. **Returns `void`.** |
| where it is called from | `dafoam/mphys/mphys_dafoam.py:353–357` | called with `"print"` immediately after the primal solve — **this is the block in `XM.log`.** |
| the per-iteration printer | `src/adjoint/DAUtility/DAUtility.C:735–800` | `primalResidualControl` prints `<var> initRes: … finalRes: … nIters: …` **only `if (printToScreen)`**; it keeps a running **max** in `primalMaxRes`, overwritten each call. **A max is not a history.** |
| the gate on that print | `DASolver.C:225` → `DASolver.C:2765–2771` | `printToScreen_ = isPrintTime(runTime, printInterval_)`, true when `timeIndex % printInterval == 0 \|\| timeIndex == 1`. **This exactly explains 5 samples over 443 iterations at `printInterval 100`.** |
| the convergence line | `DASolver.C:194` | prints `Minimal residual <primalMaxRes> satisfied the prescribed tolerance <primalMinResTol_>` |

**A NEGATIVE SEARCH, STATED WITH ITS EXACT PREDICATE.** Case-insensitive `hist`
matches **0 lines** in `pyDAFoam.py`, `mphys_dafoam.py`, `DASolver.C`,
`DASolver.H`, `DASolvers.H`, `pyDASolvers.pyx` and `DAUtility.C`. That is a
substring search over **those seven files**, not over DAFoam. **It is evidence
about those files and about nothing else** — the files not searched are named in
§6 and the claim does not reach them.

---

## 5. THE REGISTRATION DECISION, WITH THE OPTIONS SIZED. **THE SUPERVISOR RULES.**

**The finding of §2 makes this option (a): `F1` can be satisfied from a source
that exists, and satisfying it needs NO EDIT TO THE FROZEN READER** — the reader
asks only for `len(j["residual_histories"]) == n_tol`; it never inspects a
history's contents. **Only the producer's source for that list changes**, from a
guessed object attribute to the log the registration named.

### Option a1 — a dated ADDENDUM to SO3aF2, producer-only. **RECOMMENDED.**
Moves no gate, no threshold, no prediction, no band, no cap, no label — and
brings the producer *into* conformity with the frozen §5 scoring method rather
than away from it. Precedented twelve times inside this item.

### Option a2 — a fresh successor item `SO3aF3` with its own freeze.
Cleaner provenance; pays the full registration cost again for a producer change.

**Below is the arm table either option would carry.** It is stated here so the
supervisor rules on a costed thing, not on a promise.

---

## 6. ROUTES **NOT** TESTED — an untested route is not a closed one

Named because §A13.1's own lesson is that a successor who reads a narrow measure
as a wide one gives up a live route.

1. **Calling the two methods on a live `DASolver`.** Their source is read; they
   are still uncalled. Source reading is strong evidence and is not execution.
2. **The OpenFOAM `residuals` functionObject.** `system/controlDict` in every
   staged case (`…/XM/case/mp0/system/controlDict`) has **no `functions` block**,
   and no `postProcessing/` directory exists anywhere under the case tree. A
   `#includeFunc residuals` would write a per-iteration `residuals.dat` to disk
   independent of `printInterval`. **UNTESTED.**
3. **DAFoam source outside the seven files searched** — `DAResidual*`,
   `DAGlobalVar`, `DAOption`, the unsteady solvers, `DAFuncObj`. `primalMaxRes`
   lives in `daGlobalVarPtr_` and is **not exposed through `pyDASolvers.pyx`**
   (searched), but the rest of that tree is unsearched.
4. **`updateDAOption`** (`pyDASolvers.pyx:355`) can change `printInterval` from
   Python at run time. Never exercised.
5. **Whether a `printInterval: 1` run behaves identically otherwise.** The print
   is inside the SIMPLE loop; extra `Info` writes are I/O, not physics, but
   **that is an argument, not a measurement.**

---

## 7. THE ARMS, COSTED. Rule 12; charter §18.1 and §18.2.

**COST ANCHOR — PROGRAM STATEMENT (charter §18.1), all four terms.**
Anchor: `…/ledger.txt:6`, `ITEM=SO3aF2 ARM=XM STAMP=2026-09-03T233357Z rc=7
wall_s=24 ranks=1 core_min=0.4000`. **The program it priced:** ranks **1**;
adjoint **NO**; Jacobian colouring **NO**; tree **COLD** (each operating point
staged fresh into `mp0/mp1/mp2` by the arm, `decomposePar` not run, np=1).
It covers mesh check + IDWarp init + **three converged primals** (443/436/424
iterations) + the refusal.
**MATCH ASSERTION against arm `XM2` below:** ranks 1 = 1; adjoint NO = NO;
colouring NO = NO; tree COLD = COLD. **Matches on all four terms.** The only
registered difference is `printInterval` 100 → 1, whose cost is extra `Info`
lines and is adjusted for explicitly in the table.

| arm | what it does | solver? | estimate (core-min) | cap | basis |
|---|---|---|---|---|---|
| **R0** *(optional, free)* | parse the **preserved** `XM/XM.log` for 3 histories; no container | **NO** | **0.02** | **0.20** | instrument-only. **Cache state: WARM** (the log is 97,084 B, **1 file**, **0 copies**, read minutes ago in this session). Cold estimate on §18.2's own carry-forward, `≈1.0 s / 1000 files` from `C-212`/`C-214`, is still **<0.02** at one file. |
| **XM2** | re-run XM, np=1, producer repaired to parse the log, **`printInterval: 1`**, writes `so3af2_M.json` natively | **YES** | **0.55** | **6.0** *(unchanged from the frozen XM cap)* | anchor 0.4000 above, **+0.15 adjustment** for ≈7,800 extra `Info` lines over 1,303 iterations (≈37 % headroom on wall). **A misprediction here is a calibration row, not a new budget.** |
| **RD** | drive the frozen reader on the artefact XM2 writes; score F1–F5 | **NO** | **0.03** | **0.20** | instrument-only. **Cache state: WARM**, ≈220 files under one run root, 0 copies. |

**Total registered: 0.60 core-min, caps 6.40.** Well inside the item's 9.0
ceiling and inside rule 12's pre-authorisation. `cost_basis`:
**REPORTED-BY-OWNER, NOT MEASURED** — wall seconds and ranks from ledger rows;
the `$0.0513/core-h` rate is owner-stated and this box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER` §5).

**Estimate-versus-actual (rule 12) is owed at completion** as a row in
`docs/COST_CALIBRATION.md`, stating the ratio actual/predicted and attributing
the gap, with waste named separately and never absorbed into the ratio.

---

## 8. THE TWO ROWS. Charter §6 — and they are not both filled, which is the point.

| row | toolchain identity | standing |
|---|---|---|
| **SHIPPED** | image `dafoam/opt-packages:latest`, digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **The only row this work has.** Every count in §3 and every source line in §4 is from this image. |
| **PATCHED** | **NONE.** No patch is involved, none is proposed, and **no patched row is claimed.** | Stated rather than omitted: §6 requires two rows, and *"there is no patched row"* is a row's worth of information. |

---

## 9. THE PLANTED-ZERO CONTROL THE SUCCESSOR MUST CARRY (rule 3)

Not a promise — the mechanism is already demonstrated in §3 and is registered
here as a **refusal**, in the same shape as the frozen reader's Direction B.

**The producer, in the SAME invocation that writes `so3af2_M.json`,** takes its
parsed log, deletes the `initRes:` lines of one `Running Primal Solver` block in
a **scratch copy**, re-parses **from disk**, and asserts the re-read yields
**one fewer** history. **If the planted short read is not visible, the producer
REFUSES and writes no artefact.** A parser that cannot see a short history is
not licensed to report a complete one.

---

## 10. THE FALSIFIER — what would show this draft's central claim is WRONG

The claim is: *a per-primal residual history is recoverable from the DAFoam
solver log, and `printInterval` sets its resolution.*

**Registered falsifier, decided before XM2 runs.** At `printInterval: 1`, for
each of the three primals, the parsed sample count per equation **must equal that
primal's final time index** (the `Time = N` at which its tolerance line prints —
443, 436, 424 on the recorded angles). **If any primal's parsed sample count is
not equal to its final time index, the claim is falsified** and `F1` reverts to
unsatisfied by this route, whatever the histories look like. Two named ways it
could fail honestly: a residual print gated by something other than
`printToScreen_`; or `initRes:` lines emitted for a subset of equations at some
iterations. **Neither is excluded by anything measured so far.**

**A second, independent falsifier of the ADDENDUM 13 ruling itself:** if XM2's
`printInterval: 1` log yields histories but a subsequent direct call to
`getResiduals` *also* returns a sequence, §4's source reading was wrong. The
draft asserts it will not, and names that as the thing to check.

---

## 11. WHAT THIS DRAFT DOES NOT CLAIM

- **It does not claim `F1` will HIT.** It claims the quantity `F1` reads is
  obtainable. Whether three points converge is what the arm measures.
- **It does not touch §0.2.** This item never calls `solve_linear`, cannot show
  SO-3aR's adjoint collision is fixed, and **nothing measured here may be quoted
  toward it.**
- **It does not reopen a gate, a band, a cap or a label.** F1–F5 remain unscored;
  the item remains **PENDING**; MESH remains complete and **NOT A RESULT**.
- **It does not rule.** The registration decision is the supervisor's.
- **It does not resolve the two open defects of §A13.5** — the frame allowance
  (n=1, unresized) and the unexplained census stall. Both stand, with evidence.

**NOT QUEUED. NOT ARMED. NOT FROZEN. SUBMISSIONS PARKED.**
