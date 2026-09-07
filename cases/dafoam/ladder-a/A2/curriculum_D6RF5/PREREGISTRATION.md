# DRAFT — NOT FROZEN — awaiting supervisor check-1 read and freeze

**`D6RF5` — A2 wing convergence probe, the non-orthogonal-correction repair. Successor to `D6RF4`.**

Drafted 2026-09-06 by a `lab-lane` on the dafoam-supervisor's brief. **The freeze and the enqueue
belong to the dafoam-supervisor and are not taken here.** No gate, threshold, cap or label in this
file is registered until that supervisor freezes it by sha (`VERIFICATION_CHARTER.md` §2b; `CLAUDE.md`
rule 2). Until then nothing here is a registration: it is a lane's prediction-first proposal, written
so the supervisor can read it as a diff, size every predicted number against its own bar, and freeze
it — or send it back.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed or uploaded anywhere (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10).

---

## THE BRIGHT LINE, STATED FIRST BECAUSE IT IS THE WHOLE POINT OF THE SUCCESSOR

**`primalMinResTol` AND `primalMinResTolDiff` DO NOT MOVE IN THIS ITEM.** They are carried forward
byte-identical at `1e-08` and `1000`, the effective accept floor stays **`1.0e-05`**
(`= primalMinResTol × primalMinResTolDiff`, `N-D42`, `N-D43`), and this item registers an executable
refusal (`ACCEPT_FLOOR_UNMOVED`, §6) that reads both values back out of the container log and stops
the grading if either differs — in **either** direction, because the registered value is a value and
not an inequality.

**DAFoam's own documented remedy for "Primal solution failed" is to raise `primalMinResTol` or
`primalMinResTolDiff` — i.e. to WIDEN the accept floor** (`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md`
§1, sourcing the DAFoam FAQ [W4]). **The lab FORBIDS the stock remedy** (`N-D43`; Sanaa 2026-09-04: the
case is worked until it passes its gate, and the gate is never widened to fit). **D6RF5's fix is the
numerics, never the bar.** Whether a successor may ever register a different acceptance rule remains
**escalated to Sanaa and unruled**; this item takes no position on it and does not pre-empt it.

**And the carried floor is not portable.** `primalMinResTolDiff` is `1000` on this A2-wing case (floor
`1e-05`) and `100` on the S1 CBFS family (floor `1e-06`) — `N-D43 CORRECTION`, 2026-09-06. `1e-05` is
registered here because this case has run at it, not carried across a family from memory.

---

## 0. WHY A SUCCESSOR, AND WHAT THIS ITEM ACTUALLY CHANGES

`D6RF4` (frozen `ed809aec`, graded 2026-09-06, **`NOT A RESULT`**, **5.4 core-min of a 54.0 core-min
cap**) tightened the linear-solver stopping rule (`relTol 0.1 → 0.001`, `tolerance 0 → 1e-12`,
`nNonOrthogonalCorrectors 0 → 1`). That **crushed the inner p-solve ~207×** (its corrected final
p-solve reached `initRes 6.34e-08`, well under floor) **and still failed DAFoam's post-`End`
acceptance**, because the binding residual is not the inner linear solve — it is a **nonlinear
steady-state plateau** the inner solver was already crushing.

**The root cause is established and verified at source** (`D6RF4/RESULTS.md` amendment `b030f1e2`;
`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md`, `1586fcf9`):

- **The binding field is `p`'s UNCORRECTED FIRST solve.** DAFoam's `Primal min residual 1.658293702e-05`
  (log `:2121`) is **byte-identical** to `p`'s uncorrected first-solve `initRes` (log `:2107`) and is
  the **maximum initial residual across all states** that outer iteration. It is **`1.658×` the
  `1.0e-05` floor** (over by 65.8 %). `nuTilda` at `1.40915531e-05` (`1.409×`, over by 40.9 %) is a
  **genuine SECOND over-floor field**, but it is not the binding one, and a repair that fixes only `p`
  still fails at `nuTilda`.
- **Mechanistic cause, sourced:** the mesh's max non-orthogonality **`71.47582467` exceeds DAFoam's own
  default `maxNonOrth: 70`** (log `:217/:275/:578`; DAFoam FAQ [W4]). OpenFOAM's Laplacian splits into
  an orthogonal (exact, implicit) part and a **non-orthogonal correction (approximate, explicit)** part;
  at 71.5° that correction term is large and, carried lagged into each outer iteration's first pressure
  assembly, **the uncorrected first-solve `initRes` floor IS the magnitude of that explicit correction
  term** — irreducible at fixed mesh and fixed scheme, which is exactly why "run longer" and "tighten
  `relTol`" both already failed. The `nuTilda` trace is **monotone-asymptotic, not oscillatory** (log
  `:1959`–`:2112`), the signature of a persistent explicit source term, not an under-resolved linear
  solve.

**This item changes the DISCRETISATION of the non-orthogonal correction — the thing that IS the binding
residual — and it does not change the acceptance rule.** It is `RANK 1 + RANK 2` of the sourced,
ranked fix list in `D6RF4_CONVERGENCE_RESEARCH.md` §3, the regime-correct pair for the 70–85°
non-orthogonality band ([W1] OpenFOAM v11 fvSchemes; [W2] CFDpilot mesh-quality).

**A change to the non-orthogonal correction scheme changes the discrete residual, and therefore the
converged `CD`/`CL` and the delivered gradient.** That is not a defect and it is not hidden: it is why
this item cannot re-use `D6RF4`'s `G-SOLN` (which required `CD`/`CL` to MATCH the ancestor — appropriate
when only the linear-solver stopping rule moved), and it is why the FD-vs-adjoint bright line (`G-FD`)
is a gate here rather than a downstream report. **§3 states this explicitly.**

**What this item may not conclude is in §8, and the first entry is that it may not conclude anything
about whether the accept floor is reachable in general** (`N-D43`).

---

## 1. THE ESTABLISHED MEASUREMENT THIS ITEM IS BUILT ON — TWO OVER-FLOOR FIELDS, ONE COMMON CAUSE

Source, read at freeze from the artefact, not recalled:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe/P_conv_20260906T190038Z_83499.log`.
Per-field initial residuals at the final outer iteration (`Time = 1000`), from `D6RF4/RESULTS.md` §2.3
and `D6RF4_CONVERGENCE_RESEARCH.md` §0:

| field | `initRes` at `Time = 1000` | ratio to floor `1.0e-05` | status |
|---|---|---|---|
| `U0` | `2.050400149e-07` | 0.0205× | under |
| `U1` | `7.782685238e-07` | 0.0778× | under |
| `U2` | `5.580946633e-08` | 0.0056× | under |
| `he` | `9.791852881e-09` | 0.00098× | under |
| **`p` (1st, uncorrected)** | **`1.658293702e-05`** | **`1.658×`** | **OVER — binding (= `primalMinRes`)** |
| `p` (2nd, corrected/final) | `6.337682167e-08` | 0.0063× | under (linear solve reaches `1e-8`) |
| **`nuTilda`** | **`1.40915531e-05`** | **`1.409×`** | **OVER — genuine second field** |

**Both over-floor residuals are nonlinear steady-state plateaus, not linear-solver failures.** The
linear solves converge deeply every outer iteration (`p` corrected `finalRes 6.3e-11`, `nuTilda
finalRes 1.8e-09`). **This is the whole reason `D6RF4`'s tighter inner solve did not close it, and the
whole reason D6RF5 attacks the SCHEME rather than the solver tolerance.**

**Mesh, `checkMesh` (log `:1908`, `:1911`):** `Mesh non-orthogonality Max: 71.47582467 average:
11.65405026`; `Max aspect ratio = 606.6863871`. The max non-orthogonality places this case in [W2]'s
**70–85° band**, whose prescription is precisely **`limited 0.333` on the Laplacian + 3 non-orthogonal
correctors** — the two changes §2 registers.

---

## 2. THE FIX — TWO SCHEME CHANGES, EACH ON THE LEGAL SIDE OF THE BRIGHT LINE

Both changes go into a **new `d6rf5_fvSchemes_LIMITED` file** (and, for Fix #2, a
`d6rf5_fvSolution` file), derived from the frozen `D6RF4` inputs, with a `*_DELTAS_from_d6rf4.diff`
beside each — **owed at freeze, §9.** `primalMinResTol`/`primalMinResTolDiff` appear in neither file.

### 2.1 Fix #1 — `limited corrected 0.333` on the Laplacian AND snGrad (targets the binding field directly)

The A2-wing base `fvSchemes` (read from the D6RF4 run tree,
`.../CURRICULUM-D6RF4-a2-wing-convergence-probe/base/system/fvSchemes`) currently carries:

```
laplacianSchemes { default   Gauss linear corrected; }   // ψ = 1 (full correction)
snGradSchemes    { default   corrected;             }   // ψ = 1
```

D6RF5 changes both to the **regime-correct limited correction**:

```
laplacianSchemes { default   Gauss linear limited corrected 0.333; }
snGradSchemes    { default   limited corrected 0.333;             }
```

**Mechanism.** `ψ = 0.333` caps the explicit non-orthogonal correction term at ≤ 0.5× the orthogonal
part [W1]. Because the `p` uncorrected first-solve `initRes` floor **is** the magnitude of that
correction term (§0, §1), capping the term directly lowers the binding residual. The same cap bounds
`nuTilda`'s diffusion-Laplacian explicit correction (the second over-floor field). **The coefficient
must MATCH in both blocks** — [W1] warns that a mismatched laplacian/snGrad correction coefficient
causes "subtle residual errors difficult to diagnose"; a freeze-time check asserts the two `0.333`
values are equal (§9).

**Honest caveat, and it drives the gate design.** `limited` reduces spatial accuracy relative to
`corrected`. The discrete adjoint differentiates the **exact discrete residual**, so the converged
`CD`/`CL` and the delivered gradient **will shift** relative to `D6RF3`/`D6RF4`. This is expected, not a
defect; `G-FD` (§3.2) is what confirms the adjoint still matches finite difference on the **same
changed discretisation**, which is the property that actually matters. **CONFIRMED at freeze-prep (2026-09-06): `limited corrected <coeff>` is a scheme DAFoam's
`DARhoSimpleFoam`** (the compressible A2 MACH-wing solver — D6RF4/D6RF5, `d6rf4_opt_runScript.py:66`)
**supports and differentiates.** The compressible pressure residual `fvm::laplacian(rhorAUf, p_)`
(`DAResidualRhoSimpleFoam.C:199`) consumes the laplacian/snGrad scheme via **runtime fvSchemes
selection** — no scheme string is frozen into the operator — and the limiter's non-orthogonal
correction is AD-taped in the shared `libfiniteVolumeADR.so`; DAFoam imposes **no** snGrad/laplacian
scheme whitelist (the only restriction anywhere is on `ddtScheme`, `DASolver.H:275`). This DISCHARGES
the §9 owed differentiability check; Fix #1 may freeze. (The research doc's uncited assertion is now
cited at source. Note: this item is COMPRESSIBLE `DARhoSimpleFoam`, NOT `DASimpleFoam` — corrected
2026-09-06.)

### 2.2 Fix #2 — `nNonOrthogonalCorrectors 1 → 3`, WITH THE PREDICTION THAT IT ALONE MAY NOT CLOSE THE BIND

```
SIMPLE { nNonOrthogonalCorrectors 3; }   // was 1 in d6rf4_fvSolution_TIGHT
```

**Mechanism.** Iterating the explicit non-orthogonal correction three times per outer iteration drives
the *corrected* pressure solve and the field it carries forward to convergence, killing the spurious
divergence high non-orthogonality induces [W2]. [W2]'s 70–85° prescription is explicitly **3 correctors
WITH `limited 0.333`** — Fix #1 and Fix #2 are the paired remedy, not alternatives.

> **REGISTERED PREDICTION, BEFORE COMPUTE, so it is on the record and can be wrong:** the binding field
> is the **first (corrector-0, uncorrected)** p-solve `initRes` (§0). **More correctors improve the
> CORRECTED solve and the carried-forward field; by mechanistic reasoning they may NOT shrink the
> FIRST-solve residual, which is the correction magnitude itself.** So **Fix #2 alone is predicted
> possibly-insufficient for the binding field**, and Fix #1 (`limited 0.333`, which caps the correction
> magnitude that the first solve reports) is predicted to be the load-bearing change. **This is
> reasoning, labelled reasoning; it is not a result.**
>
> **HOW IT IS MEASURED, so the prediction is falsifiable rather than rhetorical.** The plateau
> mini-sweep's convergence table (§4) is graded per field, and `G-CONV` (§3.1) reads the `p` FIRST
> (uncorrected) solve `initRes` explicitly and separately from the corrected one — exactly the two
> numbers `D6RF4/RESULTS.md` §2.3 had to disentangle by hand. If, at `Fix #1 + Fix #2`, the `p` first
> solve is `< 1.0e-05`, the pair worked; if it is not, the record names which change moved it and which
> did not, and §5's `F5` isolates Fix #1's contribution by running the ancestor scheme as the trivial
> baseline. **A repair that reports only `primalMaxRes` cannot make this distinction, and this item
> reports every field's first-solve residual so it cannot be missed a third time.**

**Not in this item, and named so the omission is deliberate** (`D6RF4_CONVERGENCE_RESEARCH.md` §3):
`RANK 3` (nuTilda under-relaxation `0.7 → 0.5`) is held back unless `nuTilda` binds after Fix #1+#2 —
its trace is monotone, not oscillatory, so relaxation reduction is predicted low-yield; `RANK 4`
(first-order `div(phi,U)`) is held back for its accuracy cost; `RANK 6` (SIMPLEC) is held back pending
DAFoam-support verification; `RANK 7` (re-mesh below 70°/40°) is a further successor with its own mesh
registration. **D6RF5 is the cheapest regime-correct pair, measured before anything more invasive.**

---

## 3. GATES — REGISTERED BEFORE COMPUTE, EVERY ONE POST-HOC

The item's landed verdict is a **conjunction**: `PASS` requires `G-CONV` **and** `G-FD` at a plateau
step, with `G-SCHEME` and the finiteness clause able only to turn a `PASS` or a `GATE FAIL` **into**
`NOT A RESULT` (never the reverse — `CLAUDE.md` rule 5's permitted direction of travel). The ladder:

| outcome | landed label |
|---|---|
| `G-CONV` `GATE FAIL` (fix did not close convergence) | **`GATE FAIL`** — FD/adjoint legs do NOT run; `G-FD` reads `NOT A RESULT` for want of a converged primal |
| `G-CONV` `PASS` **and** `G-FD` `PASS` at a plateau step | **`PASS`** |
| `G-CONV` `PASS` **and** `G-FD` `GATE FAIL` at a plateau step | **`GATE FAIL`** — converged, but the changed scheme broke FD↔adjoint agreement (a real finding) |
| `G-CONV` `PASS` **and** the FD triple/step is not at a plateau, or is non-monotone | **`NOT A RESULT`** (§4) |
| `G-SCHEME` fail (run did not use the registered schemes/correctors) OR accept floor moved | **`NOT A RESULT`** — the number describes a case nobody registered |
| any graded value non-finite | **`NOT A RESULT`** (finiteness clause, §3.4) |

### 3.1 `G-CONV` — the convergence gate, per field, and it reads `p`'s FIRST solve explicitly

> **`G-CONV`. For the tightened D6RF5 baseline primal, the final-iteration `initRes` of EVERY field in
> `{U0, U1, U2, he, p_first_uncorrected, p_corrected, nuTilda}` must be `< 1.0e-05`, and the primal
> must exit `rc=0` with `Primal solution failed!` absent from its log.**
>
> **Threshold `1.0e-05` = `primalMinResTol × primalMinResTolDiff` = `1e-08 × 1000`, carried forward
> unchanged.** The gate introduces no bar; it makes the bar DAFoam applies post-`End` gradeable **per
> field, including the uncorrected first p-solve** — the field `D6RF4/RESULTS.md` §2.3 had to identify
> by hand — so a failure names the field rather than a maximum.
>
> **Reported beside the verdict, pass or fail:** the full per-field `initRes` table at the final
> iteration; each field's ratio to `1.0e-05`; and the `p`-first and `nuTilda` `initRes` trajectories at
> the print interval, so plateau-vs-descent is visible to the reader rather than asserted.
>
> `PASS` iff every listed field is `< 1.0e-05`. `GATE FAIL` if any is `≥ 1.0e-05`. `NOT A RESULT` if the
> primal did not run or any value is non-finite (§3.4).

**REGISTERED PREDICTION, with the arithmetic:** at `D6RF4`'s scheme (`corrected`, `ψ = 1`, 1 corrector)
the `p` first solve plateaued at **`1.658e-05` = `1.658×` the floor** (measured, §1). `limited corrected
0.333` caps the explicit correction the first solve reports at ≤ 0.5× the orthogonal part [W1] — a
predicted factor of up to ~2 on the correction magnitude — and 3 correctors converge the corrected
field. **The requirement is a `1.658×` drop on `p` and a `1.409×` drop on `nuTilda`.** The mechanism
predicts the `limited` cap clears `p`; whether it also clears `nuTilda` is **less certain** (nuTilda's
plateau is a diffusion-correction plateau the same cap bounds, but by a smaller measured margin). **This
is the measurement the item exists to make.** If `nuTilda` remains the sole binder after Fix #1+#2, that
is a `GATE FAIL` naming `nuTilda`, and §8 says the successor is owed `RANK 3`, never a looser floor.

### 3.2 `G-FD` — the FD-vs-adjoint bright line, graded AT A PLATEAU STEP

`G-FD` exists as a gate (not a report) precisely because Fix #1 changes the discrete residual. The
adjoint differentiates the exact discrete residual; finite difference of the **same** discrete residual
must agree with it. **`G-FD` tests self-consistency of the changed discretisation, NOT accuracy against
`D6RF3`** — a shift in `CD`/`CL` from the ancestor is expected and is not graded (it is reported, §3.3).

> **`G-FD`. For the registered representative design variable, the relative error between the adjoint
> gradient and the central-difference FD gradient, EVALUATED AT THE PLATEAU STEP identified by the §4
> mini-sweep, must be `< [BAND-FD]` and show `0` sign flips across the plateau.**
>
> **`[BAND-FD]` and the plateau-step selection are pre-registered in §4 and are NOT chosen after seeing
> the data** (`DAFOAM_CHARTER.md` §3: never select the step after seeing which one agrees). The band is
> carried from this family's FD bright-line convention (`DAFOAM_CHARTER.md` §7; the D6RF3-lineage band D
> at 5.0 %) and is **owed a final value at freeze, stated beside its predicted margin** (§9).
>
> `PASS` inside `[BAND-FD]` at a `CONVERGING`/plateaued step with 0 sign flips. `GATE FAIL` above the
> band. `NOT A RESULT` if the FD step is not at a plateau, the sweep is non-monotone, the adjoint or an
> FD leg did not run, or any value is non-finite.

**This gate only runs if `G-CONV` PASSes** — an FD or adjoint gradient off a non-converged primal is a
statement about a case nobody registered (research doc [S3]: the adjoint requires a converged primal
state). If `G-CONV` fails, `G-FD` reads `NOT A RESULT` for want of a converged primal and no FD/adjoint
compute is spent.

### 3.3 `G-SCHEME` — the anti-cheat gate: prove the run used the REGISTERED discretisation (replaces D6RF4's `G-SOLN`)

`D6RF4`'s `G-SOLN` required `CD`/`CL` to **match** `D6RF3` to `1e-3` relative, because `D6RF4` only
tightened the linear-solver stopping rule (`N-D42`: that computes the same answer). **That gate is
INAPPLICABLE to D6RF5**, which deliberately changes the discretisation: a match would be surprising, a
mismatch is expected. Re-using it would gate against the very effect the fix is designed to have.

> **`G-SCHEME`. The grader reads back, out of the run's own case files / container log:
> `laplacianSchemes` and `snGradSchemes` are `limited corrected 0.333` (equal coefficients);
> `nNonOrthogonalCorrectors == 3`; and (via `ACCEPT_FLOOR_UNMOVED`) `primalMinResTol == 1e-08` and
> `primalMinResTolDiff == 1000`. It REFUSES (`NOT A RESULT`) if any differs.**
>
> This is the honest anti-cheat for a scheme change: it proves the measurement describes the
> **registered configuration**, so a `G-CONV`/`G-FD` `PASS` cannot be quoted for a run that quietly used
> different schemes or a widened floor. It is **strictly restrictive** — it can only turn a `PASS` or a
> `GATE FAIL` into a `NOT A RESULT`, never the reverse.
>
> **Reported, NOT gated:** the converged `CD`/`CL` and their shift from `D6RF4`'s measured
> `CD = 0.0184758685` / `CL = 0.3999751808` (or `D6RF3`'s, cited at freeze). The shift is the physical
> price of `limited 0.333` and is recorded for the successor, **never used to pass or fail this item.**

### 3.4 The finiteness clause — carried from `D6RF4`, and still strictly restrictive

A non-finite value in any graded quantity folds into its gate as **`NOT A RESULT`** naming the artefact,
the key and the value. It can turn a `PASS` or a `GATE FAIL` INTO a `NOT A RESULT` and do nothing else;
it can never produce a `PASS` and never move a row in the permissive direction. Asserted by a mutation
harness driven both ways (a planted `NaN`/`±Inf` must produce `NOT A RESULT`; an unmutated control must
not) — carried from `d6rf4_finiteness_mutation.py`, §6, §9.

---

## 4. THE PLATEAU MINI-SWEEP — PRE-REGISTERED, BEFORE ANY FD LEG

The FD-vs-adjoint bright line is only meaningful at a step where the FD estimate has **plateaued** —
large enough that subtractive cancellation / round-off is negligible, small enough that truncation error
is negligible. Selecting the step after seeing which agrees is forbidden (`DAFOAM_CHARTER.md` §3, §7).
So the plateau step is chosen by a **registered rule over a registered sweep**, before grading.

**Registered sweep.** Central-difference FD of the registered representative DV at
`h ∈ {[H-SET]}` — a geometric ladder spanning at least four decades around the family's usual working
step, **the exact set owed at freeze, §9** (the D6RF3-lineage step and the `DAFOAM_CHARTER.md` §7
five-step protocol fix the anchor; a candidate ladder is `{1e-2, 1e-3, 1e-4, 1e-5, 1e-6}`, to be
confirmed by the supervisor against this case's DV scaling).

**Registered plateau rule.** The plateau is the contiguous run of `h` values over which consecutive FD
estimates agree to within **`[PLATEAU-TOL]`** relative (candidate `1 %`, owed at freeze). The graded
plateau step is the **geometric-centre** step of that run. If no two consecutive estimates agree within
`[PLATEAU-TOL]`, there is **no plateau** and `G-FD` reads **`NOT A RESULT`** — a five-step sweep that
never plateaus is not silently reduced to its least-bad step.

**Registered reporting (`DAFOAM_CHARTER.md` §7):** the full five-step FD table, the adjoint value, the
per-step relative error against the adjoint, the identified plateau run and its centre step, and the
sign-flip count across the plateau — printed beside the verdict whether `G-FD` passes or fails.

**Decomposition disclosure (`DAFOAM_CHARTER.md` §5):** the sweep and the adjoint are run at the SAME
`np` and decomposition, disclosed in the table; if the primal runs `np > 1`, the decomposition method
(and `simple` subdivision) is stated beside every number. **The first FD verification of a changed
discretisation is run at `np = 1`** unless the supervisor registers otherwise, because a gradient
verified at one `np` is a statement about that `np` only.

---

## 5. FALSIFIERS — §21-COMPLIANT: each names the gate it is predicted to fail, with the arithmetic

`DAFOAM_CHARTER.md` §21.3: a registered trivial baseline **names the gate it is predicted to fail**,
that gate **must be the one whose verdict the withdrawal clause withdraws**, and the pre-registration
**shows the predicted value beside that gate's own bar with the inequality written out.** A falsifier
whose predicted value does not fail its named gate **is not a falsifier**.

> ### `F5` — `G-CONV`'s trivial baseline. THE DELIBERATELY-WRONG SCHEME, AND ITS VALUE IS ALREADY MEASURED
>
> **Probe:** the identical D6RF5 baseline primal re-run with `D6RF4`'s **scheme** — `laplacianSchemes
> Gauss linear corrected`, `snGradSchemes corrected` (`ψ = 1`, the full uncapped correction),
> `nNonOrthogonalCorrectors 1` — everything else (the tightened `relTol`/`tolerance`/`minIter`,
> `endTime`, mesh) held.
>
> **Named gate: `G-CONV`. That gate's own bar: `1.0e-05`.**
>
> **Predicted value: `p` first-solve `initRes = 1.658293702e-05`.** This is not an estimate — it is
> `D6RF4`'s **MEASURED** binding residual at exactly these schemes, from the log named in §1.
>
> **The inequality: `1.658e-05 > 1.0e-05`. `G-CONV` FAILS at the wrong scheme, by `1.658×`, at zero
> additional compute risk** (the number already exists). This is the §21.1 property — arithmetically
> bound to fail its named gate on the page — that `S1FDP`'s limb 2 lacked.
>
> **Withdrawal clause, and it withdraws the gate it names and no other:** if the wrong scheme **also
> passes** `G-CONV`, then `G-CONV` is not measuring the non-orthogonal-correction discretisation, §1's
> mechanism is refuted, **`G-CONV`'s verdict is withdrawn**, and no claim about the repair may be made.

> ### `F-STEP` — `G-FD`'s trivial baseline: the same FD probe at a deliberately-wrong step (`DAFOAM_CHARTER.md` §4)
>
> **Probe:** the FD gradient of the representative DV at `h` **one decade off the plateau step**, all
> else held.
>
> **Named gate: `G-FD`. That gate's own bar: `[BAND-FD]`.**
>
> **Predicted value: OWED AT FREEZE.** Per `DAFOAM_CHARTER.md` §21.3 the predicted relative error of
> the wrong-step FD estimate must sit **beside `[BAND-FD]` with the inequality written out, before the
> freeze**, and the step is rescaled or the target corrected if the prediction does not clear the bar.
> **A lane cannot compute this without either the plateau sweep or a lineage FD estimate; it is flagged
> as a §9 freeze-owed number and, until it carries a predicted value that fails `[BAND-FD]`, `F-STEP` is
> registered as a REPORTED probe only and NO withdrawal clause rests on it** (§21.3 permits a reported
> probe; it forbids resting a withdrawal on an unsized one).

> ### `F-FINITE` — the finiteness clause. If the §3.4 mutation harness fails in EITHER direction — a
> planted `NaN`/`±Inf` that does not produce `NOT A RESULT`, or an unmutated control that does — the
> clause is not established and the item reports `NOT A RESULT` for want of a working guard rather than
> shipping gates it cannot trust.

---

## 6. CONTROLS AND STRICT COMPLETION — CARRIED FROM `D6RF4` BY REFERENCE, RE-PLANTED FOR THIS ITEM

Every instrument below is derived from the frozen `D6RF4` instrument named, with a
`*_DELTAS_from_d6rf4.diff` beside it and an md5 recorded at freeze (`DAFOAM_CHARTER.md` §18.3;
existence asserted before any hash). **Owed before freeze, §9.**

1. **Planted-zero control (`CLAUDE.md` rule 3).** Carried from `d6rf4_cd_plant_control.py`
   (`PLANT = 1.234e-03`, `PLANT_REL_TOL = 1.0e-9`). Every comparator plants a known perturbation into
   the same object the gate reads, reads it back off disk, and **REFUSES** if the reader cannot see it —
   a control that finds nothing to plant into refuses rather than reporting a silent pass. **A zero from
   a reader not shown able to see a non-zero is not evidence.** The gate reads through the imported plant
   function's symbol, and a freeze check asserts the identity of the imported symbol, not the module
   name.

2. **`ACCEPT_FLOOR_UNMOVED` (`N-D43`; the bright line, executable).** Carried from
   `d6rf4_accept_floor_control.py`. Reads `primalMinResTol` and `primalMinResTolDiff` back out of the
   arm's own container log and **REFUSES (exit 2)** unless they are exactly `1e-08` and `1000` and their
   product is `1.0e-05` — **in either direction** (a tightened floor refuses too, because the registered
   value is a value, not an inequality). Planted both ways per the `PRODUCT_WRITER` pattern: a mutated
   log with `primalMinResTolDiff 1e12` must trigger the refusal, an unmutated log must not. This item
   cannot silently widen — or narrow — the bar it was forbidden to move, and the refusal is executable
   rather than promised.

3. **Strict completion + age guard (`CLAUDE.md` rule 4).** A run is done only if `rc = 0`; an `End`
   line; last time `== endTime`; the required fields present; `ExecutionTime` count `== endTime`; and
   **every field at `endTime` NEWER than the case's own `0/T`** — the age guard, at full `stat -c '%.9Y'`
   precision (`D6RF4` amendment 2026-09-06T16:20Z: `%Y` truncation is fail-open by up to 1.000 s; the
   repair asserts a decimal point at every call site, `CLAUDE.md` rule 14). Carried from
   `d6rf4_run_arm.sh` / `d6rf4_grade.py` / `d6rf4_age_datum_control.py`, with the age-datum control
   re-planted on real nanosecond mtimes.

4. **`freeze_check` extracts its instrument list from the code, not from memory** (carried from
   `d6rf4_grade.py`), extended to cover any new run-derived quantity D6RF5 introduces (the plateau step,
   the FD table) with a registered null reading — a run-derived quantity with no registered null reading
   refuses at freeze, not at grading. **`D6RF4`'s registered-null-reading table (its §5) is carried and
   extended**: `G-CONV` per-field residuals read `UNRESOLVED, bar_state=BAR_NOT_PRODUCED` if the
   baseline primal does not run; `G-FD` reads `NOT A RESULT` if the adjoint or an FD leg does not run;
   `eta_raw` reads `UNRESOLVED` if `baseline_repeat` does not run.

5. **Root-staging (`d6rf4_stage_root.sh`) and the launcher-not-frozen refusal (`PERMISSION`).** `D6RF4`
   was bitten three times by a dropped chain-driver / staging layer (its 2026-09-06T16:57Z amendment).
   D6RF5's launcher and stager are derived from `D6RF4`'s **post-repair** versions, and the
   clause-by-clause accounting of any dropped layer (its §3) is a §9 freeze requirement — an unaccounted
   clause is that defect a fourth time. The launcher carries `PERMISSION=NOT_FROZEN` and aborts before
   any staging until the supervisor fills the freeze sha.

---

## 7. COST — PER LEG, IN THIS FILE, IN CORE-MINUTES

**`cost_basis`: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED, not measured**. Unit:
core-minutes, `wall_s × ranks ÷ 60`. Ranks `4`.

**Measured basis, from `D6RF4`'s own ledger:** the tightened `P_conv` primal (relTol 1e-3, tol 1e-12,
minIter 5, 1 corrector, `endTime 1000`) ran at `ExecutionTime 57.43 s` → `3.83` core-min of solve, and
**`5.4` core-min gross** including container frame (`D6RF4/RESULTS.md` §7: `container_wall_s=75`,
`delivered_cores_mean=3.3475`). D6RF5's primal adds Fix #2's two extra p-solves per outer iteration and
Fix #1's `limited` correction; both are **strictly more work per outer iteration** than `D6RF4`. The
per-primal figure is therefore taken as **`D6RF4`'s measured `5.4` core-min × a DERIVED `1.4`
multiplier ≈ `7.6` core-min** — the `1.4` is a reasoned upper-ish estimate for `+2` pEqn solves against
a total that is not pEqn-dominated, and **§7.1 names it as the quantity the completion report
calibrates.**

Each leg figure below is **gross** — it includes that leg's share of the container frame — because the
`5.4` core-min basis it is scaled from is itself `D6RF4`'s gross per-primal figure. There is therefore no
separate frame row to add; a separate row would double-count the frame.

| leg | what it is | basis (core-min) | core-min |
|---|---|---|---|
| `L1` | D6RF5 baseline primal (`limited 0.333` + 3 correctors) — **`G-CONV`** | `5.4 × 1.4` | **7.6** |
| `L2` | `baseline_repeat`, same schemes — buys `eta_raw` (§6.4 null reading) | `5.4 × 1.4` | **7.6** |
| `L3` | `F5` trivial baseline: `D6RF4` schemes (`corrected`, 1 corrector) | `5.4 × 1.0` | **5.4** |
| `L4` | adjoint solve, representative DV, at the plateau step — **input to `G-FD`** | `5.4 × 1.9` (DERIVED, UNMEASURED for this case) | **10.3** |
| `L5–L8` | FD plateau mini-sweep: 4 of the 5 `h` steps as perturbed primals (baseline reused as the reference), representative DV | `4 × 7.6` | **30.4** |
| | **estimate** (sum of legs, frame included per leg) | `7.6+7.6+5.4+10.3+30.4` | **`61.3` → register `62.0`** |

**Only `L1`, `L2`, `L3` run unconditionally. `L4`–`L8` (the adjoint and the FD sweep) run ONLY if
`G-CONV` PASSes** (§3.2) — a non-converged primal spends no FD/adjoint compute. So the **realised** cost
if the fix fails convergence is `≈ 20.6` core-min (`L1+L2+L3`); the `62.0` estimate is the full-run
figure and the cap is sized to it.

**Cap, by the family's ADOPTED form** `max(3.0 × estimate, 1.25 × (4/3) × estimate)` — a MAX, never a
product (`docs/LAB_STATE.md` block `S-29` §7.4):

`max(3.0 × 62.0, 1.6667 × 62.0) = max(186.0, 103.3) =` **186.0 → register cap `186.0` core-min.**

**Dollars, DERIVED at $0.0513/core-h, NOT MEASURED:** estimate `62.0` core-min `= 1.033 core-h → $0.053`;
at the `186.0` cap `= 3.100 core-h → $0.159`. Both far under the `$25` pre-authorisation. **An overrun
STOPS the run; it does not get a new budget** (`CLAUDE.md` rule 12).

**Cap-versus-deadline reachability and `TMO` are owed at freeze** (§9), computed the way `D6RF4` §8.2's
`--cap-arithmetic` instrument computes them, so `residual = cap×60÷ranks − (TMO + frame)` is stated with
neither stopping condition decorative.

### 7.1 Estimate-versus-actual is OWED AT COMPLETION (`CLAUDE.md` rule 12)

At completion this item compares the pre-registered estimate against the actual in core-minutes from the
ledger, states the ratio actual/predicted, attributes the gap (contention / waste / misprediction —
waste named separately, never absorbed), and lands a row in `docs/COST_CALIBRATION.md` under that file's
append rules and the rule-10 private-index protocol. **The specific quantities named in advance:** the
per-primal `1.4` multiplier (`ExecutionTime(L1) / ExecutionTime(L3)` measures it directly, since `L1`
and `L3` are the same primal at the two schemes in the same container) and the **`1.9` adjoint
multiplier**, which is DERIVED and UNMEASURED for this case and which `L4` measures for the first time.
**Lineage cost carried, not written off:** `D6RF2` 4.6 + `D6RF3` 2.067 + `D6RF4` 5.4 = **12.07 core-min**
to date; with `D6RF5`'s `62.0` estimate, lineage-to-date would reach **≈ 74.1 core-min, $0.063 derived.**

---

## 8. WHAT THIS ITEM MAY NOT CONCLUDE

1. **Nothing about whether `1e-08 × 1000` is reachable in general.** `N-D43` (as corrected 2026-09-06)
   records one measured miss (this A2 case) and one UNKNOWN (S1 CBFS); a `G-CONV` `PASS` here says this
   case reaches the floor **at these schemes**, and no more.
2. **Nothing about `cl05` or `cl06`.** Like `D6RF4`, this probe runs the `cl04` point (CL target 0.4,
   the mildest); the other two points are `PENDING` until a primal runs at each. The full multipoint FD
   arm is a further successor (`D6RF4` §8.2's reasoning: not defensible to buy a ~900 core-min arm to
   learn a ~70 core-min fact).
3. **Nothing about the acceptance rule.** `primalMinResTol`/`primalMinResTolDiff` are untouched and §6
   instrument 2 refuses if they are not. A `G-CONV` `GATE FAIL` here is **evidence for Sanaa's desk, not
   a licence to widen anything.**
4. **Nothing about the accuracy of the `limited 0.333` solution relative to `D6RF3`/`D6RF4`.** The
   `CD`/`CL` shift is reported (§3.3), never graded; `G-FD` grades adjoint↔FD **self-consistency of the
   changed discretisation**, not accuracy against the ancestor. A converged, self-consistent, less
   spatially-accurate primal is a `PASS` here and a flag for the successor, not a failure.
5. **Nothing about `D6RF4`, `D6RF3` or `D6RF2`, which stay `NOT A RESULT`.** This item does not regrade
   them.
6. **Nothing about the `1.4`/`1.9` cost multipliers** beyond what `L1/L3` and `L4` measure.
7. **Nothing about whether Fix #2 alone would have sufficed** beyond what `F5` (Fix #1 removed) and the
   per-field `G-CONV` table jointly measure.

---

## 9. STATE OF THIS DRAFT — WHAT A FREEZE STILL OWES

**Done here:** the successor's ground in the established root cause (§0, §1); the two scheme changes with
the mechanism and the honest accuracy caveat (§2); the explicit prediction that Fix #2 alone may not
close the binding first-solve residual, and how that is measured (§2.2); the four gates including the
per-field `G-CONV` that reads `p`'s first solve, the FD-vs-adjoint `G-FD` at a plateau step, and the
scheme-registered anti-cheat `G-SCHEME` that replaces `D6RF4`'s inapplicable `G-SOLN` (§3); the plateau
mini-sweep with its registered selection rule (§4); the `F5` falsifier whose predicted value is already
measured (§5); the carried controls and strict-completion requirements (§6); the per-leg budget in
core-minutes with the conditional FD/adjoint legs and the cap by the adopted MAX form (§7).

**Owed before any freeze, and NOT done here:**

1. **The instrument files**, each derived from the frozen `D6RF4` instrument with a
   `*_DELTAS_from_d6rf4.diff` beside it: `d6rf5_fvSchemes_LIMITED`, `d6rf5_fvSolution` (correctors 3),
   `d6rf5_fvSchemes_D6RF4_ORIGINAL` (the `F5` scheme), `d6rf5_grade.py`, `d6rf5_fd_endpoint.py` (with the
   plateau sweep), `d6rf5_run_arm.sh`, `d6rf5_stage_root.sh`, and the carried controls. **None written
   yet.**
2. **The three owed numbers**, each on the page before the freeze: `[BAND-FD]` (the FD bright-line band,
   with `F-STEP`'s predicted wrong-step value beside it, §5); `[H-SET]` (the plateau-sweep step ladder,
   §4); `[PLATEAU-TOL]` (the plateau agreement tolerance, §4). Until `F-STEP` carries a predicted value
   that fails `[BAND-FD]`, it is a reported probe with no withdrawal clause (§21.3).
3. **DAFoam support for `limited corrected` in `DARhoSimpleFoam`** (the compressible A2 solver) —
   **DISCHARGED 2026-09-06, confirmed at source** (§2.1): compressible pressure residual
   `fvm::laplacian(rhorAUf, p_)` at `DAResidualRhoSimpleFoam.C:199` selects the scheme via runtime
   fvSchemes; limiter correction AD-taped in `libfiniteVolumeADR.so`; no snGrad/laplacian whitelist
   (only `ddtScheme` restricted, `DASolver.H:275`). Fix #1 may freeze on this clause. (Was written
   `DASimpleFoam` in draft — corrected to the compressible solver.)
4. **The coefficient-equality check** (laplacian and snGrad `0.333` equal, [W1]) as an executable freeze
   check (§2.1).
5. **The clause-by-clause accounting** of any staging/chain layer dropped from `D6RF4` when D6RF5 is
   built (`D6RF4` 2026-09-06T16:57Z amendment §3), so no clause is dropped a fourth time (§6.5).
6. **The instrument table with md5s** (`DAFOAM_CHARTER.md` §18.3), existence asserted before any hash;
   `ACCEPT_FLOOR_UNMOVED`, the planted-zero control and the age-datum control shown to fire both ways.
7. **`TMO`, the frame allowance, and the `--cap-arithmetic` reachability identity** at the registered
   cap (§7).
8. **The pre-freeze fragility sweep** (`D6RF4`'s 2026-09-06T02:32Z amendment): controls whose premise
   the freeze changes, prose asserting the pre-freeze state (this line-1 DRAFT banner among them), and
   any safety property resting on a value the freeze changes — re-planted before the act, not repaired
   after. **Pin the count of every duplicate-prone assignment, not its appearance** (L-493).
9. **The supervisor's four personal `SUPERVISION_CHARTER.md` §3 checks, none delegable to a lane:** the
   measurement-script diffs read **as diffs**; the crash triage; the big-claim verification — §1's
   mechanism is corroborated and now measured at `D6RF4`, but Fix #1's *sufficiency* is a claim this item
   exists to test; and **this file COMMITTED before any compute.**
10. **The freeze itself, by sha, by the dafoam-supervisor.** Not taken here.

**SUBMISSIONS PARKED.**

---

## 10. SUPERVISOR SIZING AND CHECK-1 READ — dafoam-supervisor, 2026-09-07T~0340Z (draft still NOT FROZEN)

This section discharges the sizing half of §9 item 2, the representative-DV choice, and the §9 item 9
measurement-script **check-1 read** on the *lineage* instrument this successor derives from. **It does
NOT freeze the item** — the freeze still owes the authored D6RF5 instruments (§9 item 1, none written)
and my check-1 read of *those* diffs (§9 item 9). What is fixed below is the design the authoring lane
must implement; nothing here launches compute.

### 10.1 Check-1 read, completed on the lineage FD instrument (not delegated)

Read as source: `curriculum_D6RF4/d6rf4_fd_endpoint.py` (the measurement script D6RF5's
`d6rf5_fd_endpoint.py` derives from). The FD machinery it implements — and which D6RF5 **carries
unchanged**, because D6RF5 changes the *discretisation*, not the *FD method*:

- **Central differences** `(J+ − J−)/(2s)` (`:464`), per `FAMILY_SUPERVISION_GUIDELINES.md` §4.2–4.3.
- **A 2-point clearance/ratio mini-sweep, NOT a 5-step full-ladder rule.** `CLEARANCE_FLOOR = 5.0`,
  `RATIO_MIN = 2.0`, `PLATEAU_TOL = 10.0`, `ETA_FLOOR = 1e-14` (`:126–129`). The `LADDER` is the
  *candidate* set; clearance selects `s_lo` (smallest step whose signal/noise clearance ≥ 5), ratio
  selects `s_hi` (smallest step ≥ 2·s_lo); the pair is graded, with the coarse side of `s_hi` an
  acknowledged strength-of-evidence blind spot (`:82–93`, DAFOAM_CHARTER §20.2 — not a breach).
- **Per-DV `LADDER`** (`:130–134`): shape `{1e-3, 3e-3, 1e-2, 3e-2}`; twist / patchV `{1e-3 … 3e-1}`.
- **`COMPONENTS`** (`:135–141`): `shape[46], shape[18], shape[0], twist[0], patchV_cl05[1]`.

### 10.2 The correction this sizing makes to §3.2/§4/§5, and why

**§4's candidate ladder `{1e-2,1e-3,1e-4,1e-5,1e-6}` and its candidate `[PLATEAU-TOL]=1%` are BOTH
rejected as mis-sized, and the lineage machinery is registered instead.** Grounds, measured:

1. **`{…1e-5,1e-6}` drives a shape DV into subtractive cancellation.** The lineage deliberately floors
   the shape ladder at `1e-3`; a shape-FFD FD at `1e-5`/`1e-6` is a claim about round-off, not the
   derivative (DAFOAM_CHARTER §7 harness floor: a shape-derivative FD **below ~2.5–5 %** is "a claim
   about the harness"). A ladder reaching `1e-6` would manufacture a false plateau in the noise.
2. **`[PLATEAU-TOL]=1%` sits BELOW the shape-DV harness floor** (2.5–5 %, §7) and would spuriously
   report "no plateau" (→ `NOT A RESULT`) on a perfectly good gradient. The lineage `PLATEAU_TOL=10%`
   is the resolution the instrument actually has and is registered.
3. **The §7 cost table (4 FD primals, L5–L8) already assumes the 2-point mini-sweep, not a 5-step
   sweep.** Registering the 5-step rule would silently underprice or under-run the item. Carrying the
   lineage machinery makes §4 and §7 self-consistent.

### 10.3 THE FIXED NUMBERS (registered; replace every `[OWED]` placeholder above)

| symbol | FIXED value | basis |
|---|---|---|
| **`[BAND-FD]`** | **5.0 %** relative, **0 sign flips** | DAFOAM_CHARTER §2 PASS band (band D); per-component rel err for the single rep DV. Self-consistent with the §7 2.5–5 % shape-DV harness floor: a PASS is expected to land at/above the floor, and a number far below it is flagged as a harness claim, not celebrated. |
| **`[H-SET]`** | **candidate ladder `{1e-3, 3e-3, 1e-2, 3e-2}`**, clearance_floor 5.0 → `s_lo`, ratio_min 2.0 → `s_hi` (the lineage 2-point mini-sweep) | `LADDER["shape"]`, `CLEARANCE_FLOOR`, `RATIO_MIN` carried verbatim from `d6rf4_fd_endpoint.py:126–134`. |
| **`[PLATEAU-TOL]`** | **10.0 %** (agreement between `s_lo` and `s_hi`) | `PLATEAU_TOL` carried verbatim (`:128`); consistent with the harness floor per §10.2(2). |
| **representative DV** | **`shape[46]`** (single) | An interior FFD shape control point (high index, away from the LE/TE corner where `getRotationMatrix3d`'s degenerate-rotation branch fires — DAFOAM_CHARTER §9), and one of the lineage's five named `COMPONENTS`. It inherits the ladder/clearance machinery. **NEAR_ZERO rule (no substitution):** if `shape[46]`'s adjoint fails the clearance floor (marked `NEAR_ZERO`/`NO_S_HI` by the plan logic), `G-FD` reads **`NOT A RESULT`** and a *successor* re-registers a different component — the step/DV is NEVER re-chosen after seeing which one agrees (DAFOAM_CHARTER §3). |

### 10.4 `F-STEP` (§5) — upgraded from unsized to sweep-measured

The 2-point mini-sweep evaluates both a fine (`s_lo`) and a coarse (`s_hi`) step, and `[H-SET]`'s
coarsest rung `3e-2` is more than a decade above the fine side. **The deliberately-wrong step is that
coarsest rung, and its datum is produced BY the sweep itself at zero extra compute.** Predicted
value: **> `[BAND-FD]` (> 5.0 %)** at `3e-2`, indicatively **~14 %** — grounded in the lineage's only
measured coarse-step instance, `D15_D16_FD_STEP_TABLE.md:234` (D16 PATCHED CL `shape[6]`: coarse
**14.0978 %** vs fine 1.1268 %; instrument `:90–92`). **Inequality on the page: `~14 % > 5.0 %`.**
Because this borrows a coarse-step magnitude from an adjacent case/DV, the withdrawal clause on
`F-STEP` is registered as **conditional**: it rests on the sweep's OWN coarse-side number once
measured (which the run produces), not on the borrowed 14 %. Until then `F-STEP` is the reported
probe §5 already permits — but with a predicted inequality on the page, not a blank.

### 10.5 What still owes a freeze after this section

Unchanged from §9 except item 2 (now discharged): **item 1** (author the D6RF5 instruments to the
above design), **item 9** (my check-1 read of *those authored diffs* — this section read only the
lineage), and items 4–8, 10. **A `lab-lane` is dispatched to author to this fixed design; the freeze
by sha is taken only after I read the authored measurement-script diffs.**

### 10.6 Costed core-min, brought to the chief BEFORE compute (unchanged by this sizing)

§7 stands: **estimate 62.0 core-min**, **cap 186.0 core-min** (adopted MAX form), **realised ≈ 20.6
core-min if `G-CONV` fails** (L4–L8 gated on `G-CONV` PASS). Ranks 4. Dollars DERIVED: est
$0.053 / cap $0.159 at $0.0513/core-h — far under the $25 pre-authorisation. The sizing carries the
2-point mini-sweep the §7 table already priced, so no cost figure moves.

---

## 11. AUTHORED-INSTRUMENT ADDENDUM — lab-lane, 2026-09-07 (draft still NOT FROZEN)

This section discharges §9 items 1 and 4–8 for the authored D6RF5 instruments. It is an
**addendum**; it does **not** edit §10 or any struck text, and it registers no new gate,
threshold, cap or label. **The freeze is NOT taken here** — every `run_arm.sh` carries
`PERMISSION=NOT_FROZEN` and aborts at G-FREEZE, and the dafoam-supervisor's check-1 read of the
authored measurement-script diffs (§9 item 9) and the freeze by sha (§9 item 10) remain owed.

### 11.1 §9 item 1 — the instruments, authored, each with its DELTAS diff

Every file below was derived from the frozen D6RF4 instrument of the same role, the parent md5
verified on disk before the derived file was written, with a `*_DELTAS_from_d6rf4.diff` beside it.
The producer `d6rf5_opt_runScript.py` is a **byte-identical carry** of `d6rf4_opt_runScript.py`
(md5 `137539e0a99be27f27fdb69e063b2a87` unchanged) — the bright line
(`primalMinResTol 1e-8`/`primalMinResTolDiff 1e3`) lives in its `daOptions` and is therefore
carried untouched. The producer-chain instruments (`endpoint_locus`, `endpoint_physical`,
`extract_endpoint`, `anchor_gate`, `units_assert`) are self-rename carries with no substantive
logic change. The load-bearing substantive changes are in `d6rf5_grade.py`, `d6rf5_fd_endpoint.py`,
`d6rf5_finiteness_mutation.py`, the three config files, and `d6rf5_run_arm.sh`.

### 11.2 §9 item 4 — the coefficient-equality freeze check, EXECUTABLE

`d6rf5_grade.py:coefficient_equality_check()` reads the frozen `d6rf5_fvSchemes_LIMITED`, extracts
the `limited corrected <c>` coefficient from the `laplacianSchemes` and `snGradSchemes` blocks, and
reports `equal` iff **both are `0.333`**. It is folded by `gate_scheme` (a mismatch → `NOT A RESULT`)
and by `--freeze-selfcheck` (which refuses if not equal). Existence is asserted before any read.
Run at authoring: `laplacian=0.333 snGrad=0.333 registered=0.333 equal=True`.

### 11.3 §9 item 5 — clause-by-clause accounting of the staging/chain layers

`d6rf5_run_arm.sh` and `d6rf5_stage_root.sh` are derived from D6RF4's **post-repair** versions. No
layer is dropped; the discretisation-install layer is *changed in kind* (fvSolution→fvSchemes) and
*added to* (a second per-leg install of `d6rf5_fvSolution`), never removed:

- **G-FREEZE guard** — carried; `PERMISSION=NOT_FROZEN` aborts before any staging (exactly one
  `PERMISSION=` assignment in the file).
- **Instrument md5 staging (S6)** — carried; the two fvSolution files are replaced in the staged set
  by `d6rf5_fvSchemes_LIMITED`, `d6rf5_fvSchemes_D6RF4_ORIGINAL` and `d6rf5_fvSolution`, each md5-asserted on both sides of the copy.
- **Discretisation install (S9)** — REWORKED: installs `d6rf5_fvSchemes_LIMITED` over the base scheme
  at every fvSchemes site (pre-image asserted `= 58dbed0a…`, the base D6RF4 ran), and
  `d6rf5_fvSolution` (correctors 3) at every fvSolution site; both loops assert their own trip count,
  and the whole-tree read-back refuses if any fvSchemes still carries the base (unlimited) md5.
- **Runtime per-leg install** — REWORKED: `install_fvschemes` swaps the scheme per leg
  (LIMITED for L1/L2, D6RF4_ORIGINAL for L3) and sets `nNonOrthogonalCorrectors` in the SIMPLE block
  only (3 for L1/L2, 1 for L3/F5) via a SIMPLE-scoped `awk`, printing
  `D6RF5_FVSCHEMES_INSTALLED leg=… md5=… sites=… nNonOrthogonalCorrectors=…`.
- **Age-datum production (`%.9Y`)** — carried verbatim; `d6rf5_age_datum_control.py` extracts and
  drives it, and PASSES (defective-launcher discriminator fires).
- **Leg-present + placeholder + units-gate assertions** — carried, adapted to `--mode F5_scheme` and
  the two `install_fvschemes` sites.

**Honest caveat (crash-triage owed to the supervisor):** `run_arm.sh`/`stage_root.sh` are syntax-clean
(`bash -n`) and the age-datum control passes on the launcher, but they were **NOT container-tested**
(no compute ran). The S9 dual-install and the SIMPLE-scoped corrector `awk` are the parts to review;
the F5-leg corrector-1 choice implements §5 literally, and note that F5's *datum* (the p first-solve
1.658e-05) is by §2.2's own mechanism independent of corrector count.

### 11.4 §9 item 6 — the instrument table with md5s (existence asserted before hash)

| instrument | md5 | role |
|---|---|---|
| `d6rf5_fvSchemes_LIMITED` | `8374443e7a374e9d353cffccdb654aaf` | Fix #1 scheme (graded, L1/L2) |
| `d6rf5_fvSchemes_D6RF4_ORIGINAL` | `cf8f745dcc594ce7a9c67ad2d41e4b06` | F5 wrong scheme (L3) |
| `d6rf5_fvSolution` | `67fed3c2ffd2765e51f2563270060648` | Fix #2 (correctors 3) |
| `d6rf5_fd_endpoint.py` | `ad5335a477d278698935017be4913845` | rep DV shape[46], 2-pt sweep, F5_scheme |
| `d6rf5_grade.py` | `69706d0dc03508a66b0460bfec878e6e` | G-CONV (p split) + G-SCHEME + F5 |
| `d6rf5_opt_runScript.py` | `137539e0a99be27f27fdb69e063b2a87` | producer (byte-identical carry) |
| `d6rf5_accept_floor_control.py` | `372062b2cc91ca71ae8e7fec8b88a30b` | ACCEPT_FLOOR_UNMOVED |
| `d6rf5_cd_plant_control.py` | `0fea4d9ae118a73714fa042c18f523fd` | planted-zero (PLANT 1.234e-03) |
| `d6rf5_age_datum_control.py` | `f3ea2b728cb452e97b1384624b353dd5` | age-datum guard |
| `d6rf5_finiteness_mutation.py` | `7d890ea6d70f9a168489a7f542e87ae7` | finiteness harness (F-FINITE) |
| `d6rf5_run_arm.sh` | `7cecbc6a65b6dacfb63b3778df42a7c0` | launcher (PERMISSION=NOT_FROZEN) |
| `d6rf5_stage_root.sh` | `9a0fdf03700961af3a0a759c28cd45b3` | stager |
| `d6rf5_endpoint_locus.py` | `341189ca866f302a7e1bba8eefad3a57` | DV locus (carry) |
| `d6rf5_endpoint_physical.py` | `288ce6d17f462993177250a13c9d4ce6` | DV physical (carry) |
| `d6rf5_extract_endpoint.py` | `95630a223c638095cdfb4de5727d7a88` | DV extract (carry) |
| `d6rf5_anchor_gate.py` | `28a7bb6b884002c810939e4370fb5557` | producer anchor (carry) |
| `d6rf5_units_assert.py` | `ba3389592ab8882732031e61975fc3c4` | units gate (carry) |

md5s are **as authored** and will move if any file is edited before the freeze; the freeze re-hashes
disk against the committed blob (`d6rf5_grade.py:freeze_check`). Controls shown to fire **both ways**,
with evidence beside the case: `d6rf5_accept_floor_DRIVE_EVIDENCE.txt` (1 clean pass, 5 planted drifts
refused in both senses, 3 blind readers refused, real-log exercise), `d6rf5_cd_plant_DRIVE_EVIDENCE.txt`
(positive + 4 blind readers refused), `d6rf5_age_datum_control_DRIVE_EVIDENCE.txt` (defective launcher
refused, repaired passes), `d6rf5_finiteness_DRIVE_EVIDENCE.txt` (F2 established, 50/50 direction 1,
17/17 direction 2 — G-CONV on the p split and G-SCHEME both driven).

### 11.5 §9 item 7 — TMO, frame, and the `--cap-arithmetic` reachability identity

Registered (from §7/§10.6): **cap `186.00` core-min, ranks 4, frame `90` s.** TMO is set so the two
stopping conditions reconcile exactly:

```
cap_wall = 186.00 × 60 / 4 = 2790.0 s
TMO + frame = 2700 + 90    = 2790.0 s      residual = 0.0e+00 s
max spend at TMO = 2700 × 4 / 60 = 180.00 core-min   (cap headroom 6.00)
predicted 62.00 core-min ≤ cap 186.00 : OK
```

`d6rf5_grade.py --cap-arithmetic` prints this and `cap_reachability()` REFUSES unless the identity
holds. `d6rf5_run_arm.sh` computes `TMO = CAP×60/RANKS − frame` from `cap_core_min P_conv = 186.00`,
so launcher and grader agree by construction.

### 11.6 §9 item 8 — the pre-freeze fragility sweep (L-493: pin the COUNT, not the appearance)

Each duplicate-prone assignment was counted and is **exactly one** at authoring:

| assignment | file | count |
|---|---|---|
| `^PERMISSION=` (and `=NOT_FROZEN`) | `d6rf5_run_arm.sh` | 1 / 1 |
| `^PLANT = ` | `d6rf5_cd_plant_control.py` | 1 |
| `^PLANT = ` | `d6rf5_grade.py` | 1 |
| `^ACCEPT_FLOOR = ` | `d6rf5_accept_floor_control.py` | 1 |
| `^PRIMAL_MIN_RES_TOL = ` | `d6rf5_accept_floor_control.py` | 1 |
| `^CONV_FIELDS = ` / `^G_SCHEME_NCORR = ` / `^F5_PREDICTED_P_INITRES = ` | `d6rf5_grade.py` | 1 / 1 / 1 |
| `cap_core_min P_conv → 186.00` | `d6rf5_run_arm.sh` | 1 |
| `install_fvschemes()` def | `d6rf5_run_arm.sh` | 1 |
| line-1 `NOT FROZEN` DRAFT banner | `PREREGISTRATION.md` | 1 |

Safety properties resting on a value the freeze changes: (a) the line-1 DRAFT banner and every
`NOT_FROZEN`/`NOT FROZEN` assertion state the pre-freeze state and are struck/replaced only by the
freeze act; (b) `run_arm.sh`'s `PERM_ASSIGNMENTS` guard asserts exactly one `PERMISSION=` line, so the
freeze cannot leave a second stale one; (c) `freeze_check` re-hashes every FROZEN_PATHS entry against
the committed blob, so any post-authoring edit is caught at grading.

**SUBMISSIONS PARKED. Freeze NOT taken.**

## 12. AMENDMENT — 2026-09-07, RULE-2 PRE-COMPUTE REBASE OF `REGISTERED_BASE` (lab-lane)

**Nature: CLAUDE.md rule-2 PRE-COMPUTE amendment.** D6RF5 carries **zero solver compute** — no
solve has run for this item. This amendment corrects a **config run-root path only**; it changes
**no gate, threshold, band, cap, deadline, label or instrument logic**, and it does **not re-open
the freeze's gates** (§3 gates and the §11 instrument set are untouched). Pure append: nothing above
this section is struck, edited or renumbered. `lines whose number changed above this section: 0`.

**CONDITION (the defect).** `REGISTERED_BASE` — the RUN ROOT into which D6RF5 stages and writes —
still pointed at the **parent D6RF4 occupied run root**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe`, at both
`d6rf5_stage_root.sh:88` and `d6rf5_run_arm.sh:81` (rename omission carried from the D6RF4-derived
instruments). That parent root's `ledger.txt` carries `ITEM=D6RF4`, so the stager's G-ROOT
foreign-item guard aborted **rc=43** ("carries another item: ITEM=D6RF4. Nothing is written into
another item's run root.") **before writing anything** — the launcher was never reached. The
D6RF5-owned run root `CURRICULUM-D6RF5-a2-wing-convergence-probe` **did not exist** at the time this
condition was identified (the rc=43 abort proves nothing could be written to it), consistent with the
rule-2 requirement that a pre-compute amendment name a run directory that does not exist.

**HOW CHECKED.** (1) Ran `d6rf5_stage_root.sh` against the real registered base and observed the
**rc=43** foreign-item abort with the exact `ITEM=D6RF4` line — recorded in `D6RF5_ROOT_STAGING.txt`
(abort at utc `20260907T145453Z`). (2) Audited **every** run-root path reference across the stager,
launcher and grader: the **only** stale run-root reference was `REGISTERED_BASE` at the two lines
above. All other paths are correct **source** roots that must NOT change — `D6R_ROOT`
(`CURRICULUM-D6R-a2-wing-multipoint`, launcher :185/:618 and the G-ROOT.2a guard :195-196),
`D4_ROOT`/`D4_BASE_SRC` (`CURRICULUM-D4-a2-wing-cdmin`, launcher :186, stager :94), grader
`D4_OPT_IPOPT` :219 and `CDLOG_SOURCE` :290 — and the residual `*_from_d6rf4.diff` / `_D6RF4_ORIGINAL`
fvSchemes-lineage artifacts and the PREREGISTRATION prose citing the parent's log are **provenance,
not run roots**, and are left as-is.

**THE FIX.** `REGISTERED_BASE` rebased at both sites to the D6RF5-owned run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF5-a2-wing-convergence-probe`. Two lines changed, one per
file; `git diff HEAD` on each file shows only that line. The stager's G-ROOT guard confirms this is
the intended design: it forbids `ITEM != D6RF5` and writes `ITEM=D6RF5` only into a fresh root it
stages from `D4_BASE_SRC`.

**POST-FIX CONTAINER-TEST (the test §11.3 recorded as still owed — against the REAL base, no BASE
override).** `d6rf5_stage_root.sh` now stages a **fresh** root from `D4_BASE_SRC`, passes all guards
(the foreign-item guard no longer fires — the fresh root's ledger gets `ITEM=D6RF5`), and prints
`D6RF5_STAGE_ROOT COMPLETE base=…/CURRICULUM-D6RF5-a2-wing-convergence-probe staged_now=yes
instruments=10 mode=777 utc=20260907T150224Z` at **exit 0**. This supersedes the §11.3 honest caveat
("NOT container-tested"). Staging copies files into a fresh root; **it is not compute and runs no
solve**, so it produces no gate-relevant datum and D6RF5's zero-compute status stands.

**NOT re-opened, NOT launched.** `PERMISSION` is untouched by this amendment (the re-freeze to the fix
commit is the dafoam-supervisor's act after the non-delegable check-1 read of these deltas), and
`d6rf5_run_arm.sh` was **not** launched.

**SUBMISSIONS PARKED. Freeze gates NOT re-opened.**

## 13. AMENDMENT — 2026-09-07, RULE-2 PRE-COMPUTE REPAIR OF STALE INTERNAL md5 PINS (lab-lane)

**Nature: CLAUDE.md rule-2 PRE-COMPUTE amendment.** D6RF5 still carries **zero solver compute** — no
solve has run for this item; the only container invocations aborted at their in-container self-checks
in ~3 s (ledger `rc=2 ROW=PATCHED container_wall_s=3`). This amendment corrects **md5 pin VALUES
only**; it changes **no gate, threshold, band, cap, deadline, label or instrument logic**, and it does
**not re-open the freeze's gates** (§3 gates and the §11 instrument set are logic-untouched). Pure
append: nothing above this section is struck, edited or renumbered. `lines whose number changed above
this section: 0`.

**CONDITION (the defect).** The D6RF5 instrument set was derived from D6RF4 by rename, and md5 pins
were left at parent D6RF4 values across three previously-repaired layers (5 launcher pins → 991adf07;
`REGISTERED_BASE` → §12/c3b2217f). A **fourth** stale pin remained **inside** a frozen instrument:
`d6rf5_endpoint_physical.py:95` held `MD5_EXTRACT = "c5aace65…"`, which is the md5 of the **parent**
`../curriculum_D6RF4/d6rf4_extract_endpoint.py` (confirmed on disk), not of the D6RF5 extractor
`d6rf5_extract_endpoint.py` (`95630a22…`). Physical's in-container check C1 re-hashes the extractor and
**refuses** when it disagrees, so the container died **exit 2 in ~3 s AFTER every launcher gate had
passed** — the failure the launcher's own md5sum gates could not see, because the launcher pins the
extractor correctly (`MD5_EXTRACT6=95630a22`) while the instrument it stages carried the parent value.

**HOW CHECKED (full fixpoint audit).** Every 32-hex constant in **every** `.py` and `.sh` in the item
dir was enumerated and classified as active guard vs. documentary provenance, and each active guard's
pinned value was compared to its guarded file's **actual on-disk md5**. Result: **16 active guard
pins**; exactly **one** stale (`physical.py:95`). The `MD5_*4`-suffix and `MD5_FVSCHEMES_BASE` launcher
constants are **documentary parent/registered-base provenance** (never dereferenced as guards — `$MD5_*4`
appears nowhere) and correctly hold parent values; `MD5_CEILING_GUARD` (stage_root:103) matches the
external `_common/item_ceiling_guard.py` on disk; the `.py` instruments `units_assert`, `anchor_gate`,
`cd_plant_control`, `accept_floor_control`, `finiteness_mutation`, `age_datum_control`,
`endpoint_locus`, `extract_endpoint` carry **no** md5 pins. No circular pin dependency exists
(`physical` pins `extract`+`opt_runScript`; `extract` pins nothing; `stage_root` **parses** the launcher
for its expected md5s rather than hardcoding them, so editing the launcher does not cascade).

**THE FIX (2 pins across 2 files; fixpoint in 2 edit-iterations).**
(1) `d6rf5_endpoint_physical.py:95` `MD5_EXTRACT`: `c5aace65e1830fddace55e1bac2761c9` (parent D6RF4
extractor) → `95630a223c638095cdfb4de5727d7a88` (the D6RF5 extractor on disk).
(2) That edit shifted `d6rf5_endpoint_physical.py`'s own md5 from `288ce6d17f462993177250a13c9d4ce6`
to `2d7c7f5c3587365c1f528be42f792942`, so `d6rf5_run_arm.sh:337` `MD5_PHYS6` was repinned to the new
value to keep the launcher's own gate of physical consistent (part of the fixpoint). A third full
audit pass then found **zero** stale pins across all 16 guards → **ALL_PINS_MATCH=1**.

**STAGING CLEARED for a clean cold re-fire.** The aborted run root
`CURRICULUM-D6RF5-a2-wing-convergence-probe` was asserted to hold **zero real solver output** (no
numeric solver time dirs, no `log.*`, no `forceCoeffs`/`postProcessing`; `OptView.hst` present is the
**staged D4 reference input**, md5 `70fafa07…`, mtime 2026-08-29; the `mp0x/dRdWColoring_4.bin` are
pre-staged adjoint colorings) — only staging plus the 3 s self-check abort row. Per the launcher's own
re-fire prescription (`d6rf5_run_arm.sh:625-631`: "THE DESTINATION MUST BE ABSENT … a re-fire needs the
partial root ARCHIVED by mv, not deleted"), the root was archived by `mv` to
`…-a2-wing-convergence-probe.ABORTED_SELFCHECK_20260907T150917Z` (evidence preserved). The canonical
path is now absent, so stage S1 (`dst does not exist`) passes and the idempotent stager re-stages a
fresh root from `D4_BASE_SRC` (verified still present).

**NOT re-opened, NOT launched.** `PERMISSION` is untouched by this amendment (the re-freeze to the fix
commit and the launch are the dafoam-supervisor's acts after the non-delegable check-1 read of these
pin deltas). `d6rf5_run_arm.sh` was **not** launched. After commit, disk == HEAD blob for every edited
FROZEN_PATHS entry, so the grader's `freeze_check` holds.

**SUBMISSIONS PARKED. Freeze gates NOT re-opened.**
