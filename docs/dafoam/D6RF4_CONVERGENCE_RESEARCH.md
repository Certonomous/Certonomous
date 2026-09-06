# D6RF4 — CONVERGENCE RESEARCH: recoverable-vs-capability-gap, with sourced next fixes

**Written:** 2026-09-06, by a `lab-lane` (dafoam) on the dafoam-supervisor's brief,
answering Sanaa-direct `4ae4b33`: *the only acceptable fail is a proven OpenFOAM
capability gap; otherwise the team keeps fixing until it runs.* D6RF4 came back
`NOT A RESULT` (`cases/dafoam/ladder-a/A2/curriculum_D6RF4/RESULTS.md`) and its
record established a failure but did **not** try a different model/numerics nor prove
OpenFOAM cannot converge this adjoint primal. This document supplies the specific,
sourced next fixes — and the recoverable-vs-gap verdict with its basis.

**Scope discipline.** This is research + written analysis. **No solver was run, no
frozen file was edited.** Every candidate below is a change to a **frozen D6RF4
instrument** (`fvSchemes`, `fvSolution`, or the mesh) and therefore belongs in a
**successor D6RF5, never a D6RF4 edit** — stated once here and repeated per candidate.
**Every web source cited was fetched and read in this invocation**, not recalled.
**SUBMISSIONS PARKED** — nothing was sent, filed or posted outside this box.

---

## 0. THE ONE FINDING THAT REFRAMES THE PROBLEM (log-sourced, resolves RESULTS.md §2.3's open flag)

RESULTS.md §2.3 left an **explicit open question**: whether DAFoam's binding
residual reads the *uncorrected* first p-solve (`1.658e-05`) or the *corrected* final
p-solve, and it attributed the bind to `nuTilda` (`1.409e-05`) with that caveat.

**The log resolves it.** Line `:2121` of
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe/P_conv_20260906T190038Z_83499.log`
reads:

> `Primal min residual 1.658293702e-05`

That number is **byte-for-byte the uncorrected first p-solve `initRes`** at the final
outer iteration (log `:2107`: `p initRes: 1.658293702e-05`), and it is the **maximum
initial residual across all states** that iteration (`U0` 2.05e-07, `U1` 7.78e-07,
`U2` 5.58e-08, `he` 9.79e-09, `p` corrected 6.34e-08, `nuTilda` 1.409e-05). DAFoam's
`primalMinRes` is that maximum, so:

- **The binding field is `p`'s uncorrected (pre-non-orthogonal-correction) first solve,
  at `1.658e-05` — NOT `nuTilda`.** `nuTilda` at `1.409e-05` is a genuine *second*
  over-floor field, but `p` binds because `1.658e-05 > 1.409e-05` and it is the value
  DAFoam prints and compares to the `1e-05` floor.
- This corrects the RESULTS.md graded attribution (`nuTilda` binds). The successor
  must target **`p`'s uncorrected first-solve first**, `nuTilda` second.

**Both over-floor residuals are nonlinear steady-state plateaus, not linear-solver
failures.** The linear solves converge deeply every outer iteration:
`p` corrected `finalRes 6.3e-11` (48 iters, log `:2108`), `nuTilda finalRes 1.8e-09`
(6 iters, log `:2112`). Tightening `relTol` further (already done in D6RF4) cannot move
a plateau the linear solver is already crushing. The `nuTilda initRes` trace is
**monotone-asymptotic** (`1.437e-5 → 1.411e-5 → 1.4095e-5 → 1.40918e-5 → 1.40916e-5`,
log `:1959`–`:2112`) — it flattens onto a floor, it does **not** oscillate. A monotone
plateau above machine zero at fixed relaxation is the signature of a **persistent
explicit (lagged/deferred-correction) source term**, not of an under-resolved linear
solve and not of oscillatory instability.

**The mesh is the common cause.** `checkMesh` (log `:1911`, `:1915`):
`Mesh non-orthogonality Max: 71.47582467 average: 11.65405026`; `Max aspect ratio =
606.6863871` (log `:1908`). Max non-orthogonality **71.48 exceeds DAFoam's own default
`maxNonOrth: 70.0`** (DAFoam FAQ, fetched — see §2). OpenFOAM's Laplacian is split into
an **orthogonal (exact) implicit part** and a **non-orthogonal correction
(approximate) explicit part**; when non-orthogonality is high, that correction term is
large and must be iterated to convergence (CFDpilot, fetched — §2). **The uncorrected
first p-solve `initRes` floor is, mechanistically, the magnitude of that explicit
non-orthogonal correction term** carried lagged into each outer iteration's first
pressure assembly — irreducible at fixed mesh and fixed scheme, which is exactly why
"run longer" and "tighten `relTol`" both already failed.

---

## 1. WHY THIS IS NOT DAFoam's OWN RECOMMENDED FIX

DAFoam's FAQ (fetched, §2) gives exactly two remedies for *"Primal solution failed"*:
(1) raise `primalMinResTol`, or (2) raise `primalMinResTolDiff`. **Both widen the
accept floor** (`primalMinResTol × primalMinResTolDiff`). The lab **forbids** this:
`N-D43` and Sanaa 2026-09-04 — the case is worked until it passes its gate, the gate is
never widened to fit. RESULTS.md §2.4 and §8 already ruled this off-limits. So DAFoam's
documented remedy is unavailable here; the fix **must** be the underlying numerics or
mesh. This document supplies those.

Note also the floor here (`1e-08 × 1000 = 1e-05`) is already **more lenient** than
DAFoam's default (`1e-08 × 1e2 = 1e-06`). The case fails even the lenient bar, which
sharpens the point: the primal genuinely does not converge deeply, and the deficiency
is in the case, not the acceptance rule.

---

## 2. SOURCES (all fetched and read in this invocation)

**Local, title-page-verified papers** (`docs/papers/adjoint_and_optimization/`):

- **[S1] He, Mader, Martins, Maki, *Computers & Fluids* 168 (2018) 285–303**,
  "An Aerodynamic Design Optimization Framework Using a Discrete Adjoint Approach with
  OpenFOAM," doi:10.1016/j.compfluid.2018.04.012. Title page verified (author line,
  DOI, MDOLab preprint banner). File
  `he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.txt`. **Key facts:** the
  DAFoam primal (`simpleFoam` + Spalart–Allmaras) is run to a **flow convergence
  tolerance of `1e-8`**, reached in **6000 (1M cells) / 8000 (10M cells) steps**
  (`:927`–`:928`). "Poor flow convergence is known to be one of the most challenging
  issues" and is tied to **mesh quality / geometry** (DrivAer case, `:1493`–`:1500`;
  geometry smoothing "to improve flow convergence," `:1406`). **This is the capability
  proof:** OpenFOAM `simpleFoam`+SA demonstrably converges **below `1e-5` — to `1e-8`**
  — on adequate meshes.
- **[S2] He, Mader, Martins, Maki, *AIAA Journal* (2020)**, "DAFoam: An Open-Source
  Adjoint Framework...," doi:10.2514/1.J058853. Title page verified. Establishes
  DASimpleFoam as the incompressible SIMPLE primal that the adjoint differentiates.
- **[S3] Kenway, Mader, He, Martins, *Progress in Aerospace Sciences* (2019)**,
  "Effective Adjoint Approaches for CFD," doi:10.1016/j.paerosci.2019.05.002. Title
  page verified. Adjoint requires a converged primal state.

**Web (fetched this invocation):**

- **[W1] OpenFOAM v11 User Guide §4.5, fvSchemes** — `https://doc.cfd.direct/openfoam/user-guide-v11/fvschemes`.
  Non-orthogonal correction schemes: *uncorrected/orthogonal only for very low
  non-orthogonality (~5°); **corrected** generally recommended; **for max
  non-orthogonality above 75°, `limited` may be required**; above 85° convergence is
  generally hard.* `limited` coefficient ψ: **0 = uncorrected; 0.333 → correction ≤
  0.5× orthogonal part (greater stability); 0.5 → correction ≤ orthogonal part (greater
  accuracy); 1 = corrected.*
- **[W2] CFDpilot, "OpenFOAM Mesh Quality: checkMesh, y+ and Non-Orthogonality"** —
  `https://cfdpilot.com/openfoam-mesh-quality`. **40–70°:** add 1–2 non-orthogonal
  correctors, laplacian `corrected` or `limited 0.5`. **70–85°:** **3 correctors** +
  laplacian **`limited 0.333`** ("where the full correction introduces its own
  instability"). **>85°:** rebuild the mesh. Mechanism: Laplacian = orthogonal (exact)
  + non-orthogonal correction (approx); high non-orthogonality → correction term large,
  must be iterated to convergence; without correctors the pressure equation is solved
  inaccurately and velocity develops spurious divergence.
- **[W3] CFDpilot, "simpleFoam Residuals Not Converging"** —
  `https://cfdpilot.com/simplefoam-not-converging`. Turbulence under-relaxation
  `k/epsilon/omega 0.5` (conservative, prevents oscillation); **SIMPLEC (`consistent
  yes`)** allows higher relaxation (`U 0.9`, turbulence `0.7`) and is "typically 30–50%
  faster in iteration count"; `nNonOrthogonalCorrectors 2` + corrected laplacian for
  mesh-quality stalls; **"when forces have stabilised to within 0.1% between successive
  checks, the simulation is converged regardless of what the residual plots show."**
- **[W4] DAFoam FAQ** — `https://dafoam.github.io/get-started-faq.html` and its source
  `https://github.com/DAFoam/DAFoam.github.io/blob/main/pages/mydoc/mydoc_get_started_faq.md`.
  Verbatim: *"This error basically says the first primal solution does not converge to
  the prescribed tolerance (`primalMinResTol`, default 1e-8) ... 1. Increase the primal
  tolerance ... or 2. Increase ... `primalMinResTolDiff` (default 1e2)."* Default mesh
  quality **`"maxNonOrth": 70.0`**. Convergence aids mentioned: **`renumberMesh
  -overwrite`**; and **`div(phi,U) bounded Gauss upwind`** offered as an fvSchemes
  alternative. (FAQ does **not** mention `nNonOrthogonalCorrectors`, `relaxationFactors`
  or `consistent`/SIMPLEC.)
- **[W5] DAFoam runscript doc** — `https://dafoam.github.io/get-started-runscript.html`.
  Confirms `primalMinResTol` default `1e-8` and that adjoint accuracy depends on primal
  convergence; defers fvSchemes/fvSolution to OpenFOAM tutorials (no specific values).

---

## 3. RANKED CANDIDATE FIXES

Ranked by **likelihood of moving the binding field** (`p` uncorrected first solve =
explicit non-orthogonal-correction magnitude) **× cheapness to try**. All are **D6RF5**
changes, not D6RF4 edits.

### RANK 1 — `limited` non-orthogonal correction on **laplacian AND snGrad** (cheapest lever on the binding mechanism)

- **Change:** in `fvSchemes`,
  `laplacianSchemes { default Gauss linear limited corrected 0.333; }` and
  `snGradSchemes { default limited corrected 0.333; }` (currently both `corrected`,
  i.e. ψ=1). **Match the coefficient in both blocks** — [W1] warns mismatched
  laplacian/snGrad correction coefficients cause "subtle residual errors difficult to
  diagnose."
- **Mechanism (targets the binding field directly):** the `p` uncorrected first-solve
  `initRes` floor **is** the magnitude of the explicit non-orthogonal correction term
  (§0). `limited corrected 0.333` caps that term at ≤ 0.5× the orthogonal part [W1],
  directly lowering the first-solve residual floor. It also bounds `nuTilda`'s
  diffusion-Laplacian explicit correction (the second over-floor field's likely
  source). This is the regime-correct choice: max non-orthogonality 71.48 sits in
  [W2]'s **70–85° band → `limited 0.333`**, and above [W1]'s **75° "limited may be
  required"** guidance.
- **Cost:** trivial (two scheme lines); re-run is one primal (~5–18 core-min per the
  D6RF4 ledger/estimate).
- **Caveat (honest):** `limited` reduces spatial accuracy vs `corrected`. Because the
  discrete adjoint differentiates the *exact discrete residual*, the resulting CD/CL
  and the gradient the adjoint delivers will shift slightly; the successor must confirm
  the FD-vs-adjoint check still holds. `limited corrected` schemes are supported and
  differentiable in DAFoam. **Likelihood it moves the binding field: HIGH** (direct
  mechanism, regime-correct source).
- **Source:** [W1], [W2].

### RANK 2 — `nNonOrthogonalCorrectors` 1 → 3 (cheap companion to RANK 1; sources pair them)

- **Change:** `SIMPLE { nNonOrthogonalCorrectors 3; }` (currently `1`).
- **Mechanism:** iterates the explicit non-orthogonal correction to convergence within
  each outer iteration, killing the spurious divergence high non-orthogonality induces
  [W2]. [W2]'s 70–85° prescription is explicitly **3 correctors *with* `limited 0.333`**
  — RANK 1 and RANK 2 are the paired remedy, not alternatives.
- **Cost:** one integer; ~2–3× the pEqn work per outer iteration (bounded by the item
  cap).
- **Caveat (honest — measured claim withheld):** DAFoam's binding number is the
  **first (corrector-0, uncorrected)** p-solve `initRes` (§0). More correctors make the
  *corrected* solve and the carried-forward field more accurate, but by mechanistic
  reasoning they may **not** shrink the *first-solve* residual, which is the
  correction magnitude itself. So RANK 2 **alone** may not move `1.658e-5`; it is
  recommended as the source-paired companion to RANK 1, and its exact effect on
  DAFoam's `primalMinRes` **must be measured, not assumed** by the successor. This
  reasoning is labelled reasoning, not a result.
- **Source:** [W2] (paired), [W3].

### RANK 3 — Reduce turbulence under-relaxation (nuTilda) 0.70 → 0.5 (targets the SECOND over-floor field)

- **Change:** in `fvSolution relaxationFactors.equations`, split `nuTilda` out at
  `0.5` (currently the `"(U|T|e|h|nuTilda|k|epsilon|omega)"` group is `0.70`).
- **Mechanism:** [W3]'s conservative turbulence relaxation (`0.5`) for stalled
  residuals; targets the `nuTilda 1.409e-5` plateau so that once `p` is fixed (RANK 1)
  `nuTilda` does not become the new binding field.
- **Caveat (honest):** the `nuTilda` trace is **monotone-asymptotic, not oscillatory**
  (§0), and relaxation reduction principally helps *oscillatory* stalls; its effect on
  a lagged-explicit-source plateau may be modest. It addresses the *second* field, not
  the binding `p`, so it is lower priority than RANK 1/2. **Likelihood on the binding
  field: LOW; on the second field: MEDIUM.**
- **Source:** [W3].

### RANK 4 — First-order `div(phi,U) bounded Gauss upwind` (DAFoam-recommended robustness; accuracy cost)

- **Change:** `div(phi,U) bounded Gauss upwind;` (currently `bounded Gauss
  linearUpwindV grad(U)`).
- **Mechanism:** removes the **explicit deferred-correction term** in the momentum
  convection (2nd-order → 1st-order upwind). That deferred correction is itself a
  lagged explicit source coupled into `p` and `nuTilda`; removing it can let the
  coupled residual drop. DAFoam's FAQ [W4] explicitly offers `div(phi,U) bounded Gauss
  upwind` as a convergence-aiding fvSchemes alternative.
- **Caveat (honest):** first-order upwind adds numerical diffusion → a **less accurate
  primal**, changing CD/CL and the delivered gradient materially. Acceptable as a
  robustness step to *reach* the floor, but the accuracy trade-off must be weighed;
  prefer RANK 1 (which keeps 2nd-order momentum) first. **Likelihood: MEDIUM; cost:
  trivial.**
- **Source:** [W4].

### RANK 5 — `renumberMesh -overwrite` (cheap; low expected yield here)

- **Change:** renumber the mesh before the primal.
- **Mechanism:** minimises matrix bandwidth, improving linear-solver conditioning [W4].
- **Caveat (honest):** the **linear solves already reach `1e-8`/`1e-9`** here (§0), so
  conditioning is not the bottleneck; this is unlikely to move a *nonlinear* plateau.
  Listed for completeness and because it is nearly free. DAFoam [W4] recommends it
  primarily for *adjoint* (not primal) convergence. **Likelihood: LOW.**
- **Source:** [W4].

### RANK 6 — SIMPLEC (`consistent yes`) — CANDIDATE, VERIFICATION REQUIRED FIRST

- **Change:** `SIMPLE { consistent yes; }`, relaxation `U ~0.9`, turbulence `~0.7`,
  drop the explicit `p` relaxation [W3].
- **Mechanism:** SIMPLEC's better pressure-velocity coupling reaches deeper
  convergence in fewer iterations [W3].
- **Caveat (honest — do not try before verifying):** SIMPLEC changes the pEqn
  algorithm. DAFoam differentiates the *exact discrete residual*, so `consistent`
  must be a mode **DASimpleFoam actually supports and whose differentiated residual
  matches** — the DAFoam FAQ [W4] does **not** mention `consistent`, and I did **not**
  find confirmation that DASimpleFoam supports it. **This candidate is unverified;** the
  successor must confirm DAFoam support (source code / a DAFoam issue) **before** trying
  it, or it risks an inconsistent primal/adjoint. **Likelihood: unknown pending
  verification.**
- **Source:** [W3] (OpenFOAM behaviour); DAFoam support **not established**.

### RANK 7 (ROOT CAUSE) — Re-mesh the A2 wing to max non-orthogonality < 70 (ideally < 40)

- **Change:** regenerate the A2 wing mesh so `checkMesh` max non-orthogonality is below
  DAFoam's default `70` [W4] and ideally below `~40` (where `corrected` alone suffices,
  [W2]); also address aspect ratio 606.7.
- **Mechanism:** eliminates the explicit-correction source *at root*, restoring the
  deep convergence DAFoam achieves on adequate meshes ([S1]: `1e-8` reached). This is
  the **most likely to fully fix** and the only one that removes the cause rather than
  bounding it.
- **Caveat (honest):** most expensive — a new mesh is effectively a new case with its
  own grid-convergence/Roache considerations, and changes the geometry the whole A2
  ladder rests on. A D6RF5+ with its own mesh registration.
- **Source:** [S1], [W1], [W2], [W4].

**Recommended successor sequence:** RANK 1 + RANK 2 together (regime-correct, cheapest,
directly on the binding mechanism) → if `nuTilda` then binds, add RANK 3 → if still
short, RANK 4 → only if scheme/mesh-quality fixes are exhausted, RANK 7 (re-mesh).
RANK 5 is a near-free add-on; RANK 6 only after verifying DAFoam support.

---

## 4. VERDICT ON SANAA'S DICHOTOMY

**RECOVERABLE by named, sourced fixes — this is NOT a proven OpenFOAM capability gap.**

Basis:

1. **OpenFOAM demonstrably has the capability.** `simpleFoam` + Spalart–Allmaras — the
   exact primal DAFoam differentiates — converges **below `1e-5`, to `1e-8`**, on
   adequate meshes ([S1], title-page-verified, `1e-8` in 6000–8000 steps). A capability
   OpenFOAM exercises elsewhere cannot be a capability gap here.
2. **The failure is localised and diagnosed.** The binding residual is `p`'s
   uncorrected first solve = the explicit non-orthogonal-correction magnitude on a mesh
   whose non-orthogonality (71.48) **exceeds DAFoam's own default limit (70)** ([W4]),
   in the 70–85° band the sources tie directly to a residual floor ([W1], [W2]).
3. **Named remedies target exactly that mechanism** (RANK 1–7), none of which has been
   tried on this case.

**Conservative statement, as instructed.** None of these fixes has been **measured** on
this case in this invocation — the verdict is **"recoverable-candidate, fixes not yet
tried,"** not "fixed." Absence of a fix is not being claimed anywhere: multiple sourced
fixes *were* found, so the honest state is "recoverable, successor must run them." A
capability-gap claim would be warranted **only if**, after RANK 1 (`limited 0.333`) +
RANK 2 (3 correctors) and RANK 7 (re-mesh below ~40°), the primal *still* cannot reach
`1e-5` — and then only filed **with that measurement**. That proof does not exist today,
so **the capability gap is NOT proven.**

---

## 5. FROZEN-INSTRUMENT NOTE

**Every candidate in §3 is a change to a frozen D6RF4 instrument** — `fvSchemes`
(RANK 1, 2, 4), `fvSolution` (RANK 3, 6), or the mesh (RANK 5, 7). Under CLAUDE.md
rule 6 and RESULTS.md §8, **none may be applied as a D6RF4 edit.** They belong in a
**successor D6RF5** with its own prediction-first pre-registration, frozen by sha before
compute, its own cost, and — because RANK 1/4/7 change the delivered gradient — its own
FD-vs-adjoint verification. The accept floor (`primalMinResTol × primalMinResTolDiff`)
**stays at `1e-05`** in any successor; widening it is forbidden (`N-D43`; §1 above).

---

## 6. WHAT THIS DOCUMENT DID NOT VERIFY (honest gaps)

- **Not measured:** the effect of any RANK candidate on this case — no solver was run.
- **Reasoned, not measured:** that more `nNonOrthogonalCorrectors` alone may not move
  the *first-solve* `primalMinRes` (§0, RANK 2). Stated as reasoning.
- **Not established:** whether DAFoam DASimpleFoam supports `consistent`/SIMPLEC
  (RANK 6). Flagged as verification-required.
- **Confirmed from the log, correcting RESULTS.md:** the binding field is `p`
  uncorrected (`1.658e-5`), not `nuTilda` (§0) — this is measured from log `:2107`,
  `:2121`.
