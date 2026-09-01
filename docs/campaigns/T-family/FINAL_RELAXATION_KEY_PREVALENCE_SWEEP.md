# Prevalence sweep — the missing `<field>Final` relaxation key (L-426 / N-T9)

> ## AMENDMENT 1 — 2026-09-01. THE HEADLINE OF THIS NOTE IS RETRACTED.
>
> ~~"1,507 `fvSolution` files scanned. 9 AT RISK. All nine are heat-transfer's
> own. **No other team has a case carrying this defect.**"~~
>
> **STRUCK. That conclusion is false.** It is left legible above rather than
> rewritten out, because the original text is what was relayed upward and the
> record should show what was wrong, not only what is right.
>
> It fails on **two independent grounds**, and the second is mine alone:
>
> **(A) The denominator was wrong — I swept only the git repository.**
> `CLAUDE.md` states in terms that run trees live OUTSIDE git, at
> `/home/ubuntu/{closure-data, closure-challenge-benchmark, certonomous-runs}/`,
> and that *"nothing is invisible merely because it is big"*. My `find` walked
> `/home/ubuntu/Certonomous` and stopped. Re-swept on 2026-09-01:
> **`certonomous-runs` holds 1,478 further `fvSolution` files and
> `closure-data` a further 313** — the real denominator is ≈3,298, not 1,507.
> Of the 1,478, **54 are AT RISK candidates in flag-setting families** (mostly
> `pimpleFoam` under `W4-repro-fromscratch/tutorials/Airfoil_DynamicStall/unsteady/`),
> and 769 more have no `application` key and would need the §4.2 inference.
> `closure-data` has **0** in a flag-setting family. **Those 54 are MACHINE
> CANDIDATES ONLY — not hand-checked**, because they are outside this team's
> territory; their owners must hand-check them before any of them is called a
> defect (`L-425`).
>
> **(B) DAFoam runs its own control fork, which this sweep could not see.**
> Reported by the dafoam team and **carried here as THEIR measurement,
> attributed, not reproduced by me**: `pimpleControlDF` carries the same
> `loop()` with `setFinalIteration` unguarded and its `Info` behind `debug=0`,
> so **"banner present, iteration lines absent" signals a LIVE control, not an
> absent one** — and a sweep keyed to OpenFOAM's control-class names
> systematically under-reports DAFoam cases. Their figure: **165 of 246
> dictionaries across eight D12-family run trees are exposed**, all inherited
> byte-identical from the upstream tutorial. **I could not verify this on this
> box: DAFoam is not installed here** — no `pimpleControlDF`, no `dafoam`
> module, no `DASolver` source anywhere on the filesystem — so it is recorded
> on their authority and not on mine. Their landed verdicts remain
> `NOT A RESULT` and the exposure direction cannot manufacture a `PASS`, so
> nothing there is retracted; but **the prevalence total is not this note's to
> state as final.**
>
> **What survives unchanged:** the nine files in §4.3 are still at risk, still
> correctly classified, and still heat-transfer's own. What is retracted is the
> word **"no other team"** and the completeness of the count.
>
> The corrected risk condition is in §1.1; the methodological finding is §6.

**Status: MEASUREMENT, not a verdict.** This note answers the "prevalence unmeasured"
gap left open by `L-426` and `N-T9`. It grades nothing, re-opens nothing, and
files nothing upstream. Findings on other families' cases are recorded here for
the heat-transfer supervisor to hand to the chief, who routes.

**Scope of action taken: READ-ONLY.** Nothing outside `docs/campaigns/T-family/`
was modified. No other team's `fvSolution`, case or script was touched, no team
was contacted, no solver was launched. `verification/runs/T-family/T23G_runs/`
was excluded from the sweep entirely (12 `fvSolution` files) because a solver is
live in that tree.

---

## 1. The risk condition, derived from the OpenFOAM v2606 source

Derived here from the tree at `/usr/lib/openfoam/openfoam2606`, not taken from
the lesson text. Every path below was read for this note.

**A `Final`-suffixed relaxation key is queried IF AND ONLY IF
`mesh.data().isFinalIteration()` is true at the instant `relax()` is called.**

The lookup chain, for equations and for fields, differs from each other and both
matter:

| caller | resolves name via | looks in | on a miss |
|---|---|---|---|
| `fvMatrix<Type>::relax()`, `fvMatrix.C:1249-1262` | `psi_.select(...isFinalIteration())` | `relaxationFactors/equations` | `relaxEquation()` returns false → **`relax(coeff)` is never called**, silently |
| `GeometricField::relax()`, `GeometricField.C:1160-1174` | appends `"Final"` inline at `:1166` | `relaxationFactors/fields` | `relaxField()` returns false → **no relaxation**, silently |

`select(bool final)` returns `this->name() + "Final"` (`GeometricField.C:1186`).
Keys match in FULL — `keyType::match` (`keyType.C:66`) calls `regExp::match`,
which is `std::regex_match` (`regex/regExpCxxI.H:297`) — so `"(U|h|k|omega)"`
does not match `UFinal`, while `".*"` and `".*Final"` do.

### 1.1 Where the flag is set

> **CORRECTED BY AMENDMENT 1.** This section originally read *"`setFinalIteration`
> is called in exactly **four** places tree-wide"* and listed four. ~~four places~~
> **It is SIX**, and the claim of completeness was wrong in two ways at once — one
> inside the tree I read, one outside it.

`setFinalIteration(true)` appears at **six** sites in the v2606 tree, excluding
the commented-out call at `pisoControl.C:45` (re-measured 2026-09-01 by
`grep -rn "setFinalIteration(true)"` over `src/` **and** `applications/`):

- `pimpleControl.C:245` and `:253`, inside `pimpleControl::loop()`.
- `chtMultiRegionFoam/fluid/solveFluid.H:5` and `solid/solveSolid.H:24`, under
  `finalIter = (oCorr == nOuterCorr-1)` (`chtMultiRegionFoam.C:111`).
- **`chtMultiRegionFoam/chtMultiRegionTwoPhaseEulerFoam/fluid/solveFluid.H:3`**
  and **`.../solid/solveSolid.H:3`** — the sibling solver, **missed by the
  original enumeration**.

**No practical consequence for this repository, verified rather than assumed:**
`chtMultiRegionTwoPhaseEulerFoam` appears in no `controlDict`, script or queue
entry anywhere here. The miss is recorded because the *stated condition* was
incomplete and would fail on any case that ever adopts that solver — an honest
near-miss is worth more on the record than a silent fix.

**AND THE LIST IS STILL ONLY AS WIDE AS ONE TREE.** It enumerates the OpenFOAM
v2606 installation. It cannot see a **fork** — DAFoam's `pimpleControlDF` carries
its own `loop()` with the same call — and a fork is invisible to this method by
construction. Any future use of this condition must ask *which solver binary
actually runs*, not merely which class names appear in `/usr/lib/openfoam`.

**It is NOT set by:**

- **`simpleControl`** — no such call exists. A steady `simpleFoam`-style solve has
  no outer loop and its `relaxationFactors` block legitimately carries no `Final`
  keys. **This is not a defect and a sweep that flags it is worthless.**
- **`pisoControl`** — the call is present but **commented out**, `pisoControl.C:45`.
- **`chtMultiRegionSimpleFoam`** — no call anywhere in its subtree.

### 1.2 `nOuterCorrectors 1` — verified, and it is worse than "also at risk"

`finalIter()` is `converged_ || (corr_ == nCorrPIMPLE_)` (`pimpleControlI.H:94`),
and `nCorrPIMPLE_ = pimpleDict.getOrDefault<label>("nOuterCorrectors", 1)`
(`pimpleControl.C:48`).

So at `nOuterCorrectors 1` the first and only outer iteration satisfies
`corr_ == nCorrPIMPLE_`, the flag is set, and **`Final` keys are used on the only
sweep there is**. Because the value *defaults to 1*, a PIMPLE case that never
mentions `nOuterCorrectors` is in this state. This confirms the "I set relaxation
and got none" surprise, and it is reached by omission rather than by choice.

### 1.3 Two escape hatches that make a block immune

Both lookups fall through to a `default` key before giving up —
`relaxEquation()` at `solution.C:401`, `relaxField()` at `solution.C:326`. So:

1. **a `default` entry** in the same sub-dictionary, or
2. **any key that FULL-matches the `Final` name** (`".*"`, `".*Final"`, `"U.*"`)

makes the block safe. `L-426` does not mention the `default` fallback; it is a
real and common immunity and the sweep honours it.

---

## 2. Three refinements to the recorded mechanism

These are things the sweep turned up that the lesson text does not state. None
of them contradicts `L-426`'s measured result.

**(a) Solid regions in `chtMultiRegionFoam` are NOT exposed for relaxation.**
`solveSolid.H` calls `hEqn.relax()` at line 10 but does not call
`setFinalIteration(true)` until line 24. The relaxation lookup therefore happens
while the flag is still false and resolves to the plain `h` key on every sweep.
(The solid *linear solver* is a different matter: `hEqn.solve(h.select(finalIter))`
at `:26` does require `hFinal` in `solvers`, where a miss is a `FatalIOError`.)

**(b) `relax(1)` is NOT a no-op for equations, but IS for fields.**
`fvMatrix::relax(alpha)` applies the diagonal-dominance clamp
`D[celli] = max(mag(D[celli]), sumOff[celli])` (`fvMatrix.C:1206-1211`) *before*
dividing by `alpha`, and corrects the source by `S += (D - D0)*psi`. At
`alpha = 1` the clamp still runs. `GeometricField::relax(alpha)` is
`prevIter() + alpha*(*this - prevIter())` (`GeometricField.C:1155`), which at
`alpha = 1` genuinely changes nothing.
**Consequence:** a block whose equation factors are all `1` still LOSES the
diagonal-dominance enforcement on the final sweep. That is a real but much milder
exposure than losing a 0.9, and it is why the K2b rows below are separated.

**(c) The "only `U` and `h` are exposed" scope is conditional on `coupled`.**
Under `coupled`, `pEqn.H` and `turbulence.correct()` run at
`chtMultiRegionFoam.C:148-152`, after `solveFluid.H:39` has cleared the flag, so
`p_rgh`, `k` and `omega` are never asked for a `Final` key. Under **`coupled false`**
those same calls run inside `solveFluid.H`'s `if (!coupled)` block at `:23-32`,
**within the flag window**, so `p_rgh` (via `pEqn.H:69`), `k` and `omega` ARE
exposed too. `coupled` defaults to **false** (`include/createCoupledRegions.H:1`)
and is turned on by `coupledEnergyField` or by any `T` boundary with
`useImplicit`.

**I checked whether this made the T25R account wrong, and it does not.**
`0/coolant/T:46` and `0/module/T:39` both carry `useImplicit true`, and
`log.solve` shows `Create fvMatrixAssembly.` once and `Solving energy coupled
regions` 11 times. T25R is genuinely `coupled`, so `U` and `h` are indeed the only
exposed fields there. The generalisation matters for *other* cht cases, not that one.

---

## 3. Method

`find`, then per file: brace-matched extraction of `relaxationFactors` and its
`equations` / `fields` sub-dictionaries; the governing `application` read from the
case's own `controlDict`; each declared field tested for a full-match `Final`
counterpart under Python `re.fullmatch`, which is the same full-match semantics as
`std::regex_match`. A `default` key in the sub-dictionary short-circuits to safe.

**A machine finding is a candidate, not a fact** (`L-425`). Every AT RISK
candidate below was opened and read by hand, and one of the ten was reclassified.

---

## 4. Results

**1,507 `fvSolution` files scanned** (plus 12 in `T23G_runs` deliberately not read).

| bucket | count |
|---|---:|
| **AT RISK** (hand-confirmed) | **9** |
| **NOT AT RISK** | **1,498** |
| **CANNOT DETERMINE** | **0**, with a caveat in §4.2 |

### 4.1 How the NOT AT RISK total is composed

| basis | count |
|---|---:|
| no `relaxationFactors` block at all — nothing to lose | 471 |
| `application` read directly; solver never sets the flag (§1.1) | 857 |
| `interPhaseChangeFoam` — it DOES call `pimple.loop()`, so it was tested rather than excused; 0 of 12 at risk | 12 |
| `application` key absent; resolved from the case's own dicts (§4.2) | 103 |
| flag-setting family, tested, has `Final` keys or a `default` | 54 |
| machine-flagged then reclassified by hand (§4.4) | 1 |

### 4.2 The honest caveat on 103 files

103 files have **no `application` entry** in any reachable `controlDict` — mostly
DAFoam cases driven from Python, plus some Ansys VMFL case templates. They are
classified NOT AT RISK on **inference, not on a read solver name**: every one of
the 103 carries a `SIMPLE` dictionary, no `PIMPLE` dictionary, and either
`ddtSchemes { steadyState }` or no `fvSchemes` at all — i.e. a steady solve, whose
control class never sets the flag.

**If a reader requires the `application` key itself, these 103 move to CANNOT
DETERMINE and the buckets become 9 / 1,395 / 103.** Both readings are given
because the inference, while strong, is not a direct measurement. What is *not*
in doubt: under the worst possible assumption — that all 103 ran a PIMPLE-family
solver — all 103 would be at risk, so the inference is doing real work and should
be checked by whoever owns those cases rather than trusted from here.

### 4.3 The 9 AT RISK files — all nine are heat-transfer's own

> **AMENDMENT 1.** ~~**No other team has a case carrying this defect.**~~
> **STRUCK — false.** See Amendment 1 at the head of this note: 54 further
> machine candidates exist in `certonomous-runs`, and the dafoam team measures
> 165 of 246 dictionaries exposed in trees this sweep never opened. What
> remains true is the narrower statement below: every hit **found by this
> sweep, within the git repository** is heat-transfer's own.

Every hit **this sweep found** is in `verification/runs/T-family/` or
`verification/runs/F14-cooling-ladder/`.

**Group 1 — severe. Under-relaxation genuinely lost on the final sweep.**
`chtMultiRegionFoam`, `nOuterCorrectors 5`, `coupled` true, fluid region `coolant`,
`equations { "(U|h|k|omega)" 0.9; }` with no `Final` counterpart and no `default`.
`U` and `h` run the fifth and final sweep unrelaxed.

| file |
|---|
| `verification/runs/T-family/T25R_MODULE_runs/T25R_L1/system/coolant/fvSolution` |
| `verification/runs/T-family/T25R_MODULE_runs/T25R_L2/system/coolant/fvSolution` |
| `verification/runs/T-family/T25R_MODULE_runs/T25R_L2_DT025/system/coolant/fvSolution` |
| `verification/runs/T-family/T25RF_runs/A0/system/coolant/fvSolution` |

`T25R_L1` is the case `L-426` measured diverging. These four are the already-known
instance; the sweep's contribution is that **there are exactly four and no more.**

*Observation, offered without a conclusion:* all four files carry a comment stating
the omission is deliberate — *"The FINAL outer sweep is unrelaxed by omission,
which is what makes the last-sweep initial residual … a meaningful convergence
measure rather than a relaxation artefact."* These files are **untracked** (run
output under a gitignored tree), so `git` cannot date the comment and I cannot
establish whether it predates or postdates the divergence `L-426` measured. I am
recording the conflict, not resolving it: a comment asserting intent sits beside a
measured `Negative initial temperature` abort in the same case.

**Group 2 — mild. Only the diagonal-dominance clamp is lost.**
`buoyantBoussinesqPimpleFoam`, `nOuterCorrectors 2`, all relaxation factors set to
`1`. Per §2(b), the final sweep still loses the `D = max(|D|, sumOff)` clamp on
`U`, `T`, `k` and `omega`; **no under-relaxation is lost, because there was none
to lose.** The `fields { p_rgh 1; }` entry is unaffected — field relax at 1 is a
true no-op.

| file |
|---|
| `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_L050/system/fvSolution` |
| `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_L025/system/fvSolution` |
| `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_D/system/fvSolution` |
| `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_M/system/fvSolution` |
| `verification/runs/F14-cooling-ladder/K2b_runs/K2bU_trans/system/fvSolution` |

**These are completed rungs with results already on record** —
`docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md` and the two K2b ruling
notes. **Re-opening a closed verdict is not proposed here and is not on the table
in this note.** The finding is about future runs built from these dictionaries.

### 4.4 The one reclassification — why hand-checking was not ceremony

`verification/runs/T-family/T15_runs/T15_UP_f/system/fvSolution` was machine-flagged
and is **NOT a defect**:

```
fields    { p_rgh 0.7; }
equations { "(U|T|k|epsilon)" 0.7; ".*Final" 1.0; }
```

The author covered `equations` correctly — `".*Final"` full-matches `UFinal`,
`TFinal`, `kFinal`, `epsilonFinal` — and explicitly chose **1.0 on the final
sweep**. The machine flagged `fields`, where `p_rgh 0.7` has no `p_rghFinal`; but a
missing field key means no relaxation, which is exactly the `1.0` the author
declared one line below for the equations. **The behaviour matches the stated
intent, so it is not a defect** — though the asymmetry is worth a comment in the
file, since it is the same "covered it in one dictionary, not the other" shape that
`L-426` is about.

---

## 5. What this does not establish

- Prevalence is measured **for this repository at this commit**. It says nothing
  about cases that exist only in a queue entry or a generator script.
- The 103 files of §4.2 rest on an inference, and the teams owning them should
  confirm from their own launch paths.
- Severity is **not** graded. Group 2's exposure is real but was not quantified —
  no run was launched, and no claim is made about whether losing the dominance
  clamp changed any K2b number.
- Nothing here is a verdict on another family's work, and nothing has been filed
  or sent.

---

## 6. The methodological finding — why this note's headline was wrong

**A completeness claim built by ENUMERATING call sites is only ever as wide as
the tree you enumerated, and it reads as exhaustive either way.**

The original §1.1 said *"exactly four places tree-wide"*. It was wrong twice, by
the same mechanism, in opposite directions:

| what it missed | why enumeration could not see it |
|---|---|
| `chtMultiRegionTwoPhaseEulerFoam`, 2 further sites | a **sibling** in a subdirectory the first `grep` did not cover — I searched `src/` for the class and `applications/` only for the solver I already had in mind |
| DAFoam's `pimpleControlDF` | a **fork**, in software not installed on this box at all — invisible to any search of `/usr/lib/openfoam`, at any depth |

And the file sweep failed the same way at a larger scale: it enumerated the git
repository and presented the result as *the* prevalence, when `CLAUDE.md` says
plainly that run trees live outside git. **1,791 files were outside the walk.**

**The transferable rule: an enumeration answers "what did I look at", never
"what exists".** Before a completeness claim, name the boundary of the search and
ask specifically what lies outside it — another install, a fork, a vendored copy,
an untracked run tree. Nothing about *reading* the original section revealed the
gap; only widening the boundary did.

This is the same class as `L-425` (a check that looks exhaustive and detects
nothing) and as the tail-guard control error of the same night (a control that
reproduced a superficially similar failure and so certified the wrong thing).
**Three instances in one night of: the artifact looked complete, and complete was
never measured.**
