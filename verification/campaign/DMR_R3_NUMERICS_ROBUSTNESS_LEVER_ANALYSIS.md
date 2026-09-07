# DMR-R3 numerics-robustness successor — LEVER ANALYSIS (DRAFT — NOT AUTHORISED)

> **DRAFT for the cfd supervisor to relay to the chief. This is a PLAN only.**
> No freeze, no compute, no queue row. Prepared by cfd `lab-lane`, 2026-09-07.
> §2ay state-(b) NUMERICS-ROBUSTNESS successor line ("if it's the numerics, change
> the numerics"). Heeds **L-501**: an OSCILLATORY / divergent / SIGFPE outcome has
> multiple causes; the plan DIAGNOSES answer-blind and MEASURES — it never infers a
> capability finding from one SIGFPE. **All gates/thresholds/bands are held
> BYTE-IDENTICAL across every lever below (Gate V' tol 0.0231); only the numerics
> change.**

---

## 0. WHAT ACTUALLY RAN AT R3p — live settings, reconstructed from disk

Grounded in the crashed run
`verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R3p/` (successor prereg freeze
`08efee1a`). The positivity successor had **already** applied lever 1 (Minmod) and
lever 2 (maxCo 0.1); both were LIVE in the crash. This is the single most important
fact for the plan: *the two obvious first levers are already spent and the fine level
still died.*

**`system/fvSchemes` (live at R3p):**
- `fluxScheme Kurganov;` — Kurganov central-upwind (the LESS diffusive of the two
  available: `readFluxScheme.H:4` accepts only `Tadmor` or `Kurganov`).
- `ddtSchemes { default Euler; }` — first-order explicit.
- `interpolationSchemes.reconstruct(rho) Minmod;`, `reconstruct(U) MinmodV;`,
  `reconstruct(T) Minmod;` — **Minmod already in place** (lever 1 of the positivity
  successor). Minmod is the most diffusive of the standard TVD limiters.
- `div(tauMC) Gauss linear;`, `gradSchemes Gauss linear`, `laplacian Gauss linear
  corrected`.

**`system/controlDict` (live at R3p):**
- `adjustTimeStep yes;`, `maxCo 0.1;` (**lever 2 already in place**), `maxDeltaT
  5e-4;`, initial `deltaT 1e-6;`.
- `writeControl adjustableRunTime; writeInterval 0.02;` — so the last WRITTEN field is
  t = 0.10; the crash at t = 0.11648 wrote nothing. **The failing-step field was never
  written** — same blind spot the parent flagged.
- `endTime 0.2;`.

**`system/fvSolution`:** `(rho|rhoU|rhoE)` solved `diagonal`; `(U|e|h)` `smoothSolver`
GaussSeidel, tol 1e-9, relTol 0.01. Standard rhoCentralFoam.

**Crash signature (log tail + PROGRESS.txt):**
- rc = 136 = SIGFPE, deepest named frame `Foam::sqrt(Field<double>&, UList<double>
  const&)` in `libOpenFOAM.so`, via `rhoCentralFoam`. **Trapped** (`sigFpe::sigHandler`
  in the trace) — a real trapped exception, not a silent NaN.
- Died at **t = 0.11648 of 0.2 (58 %)**. The parent `vanLeer`/maxCo-0.2 run died at
  t = 0.10863 (54 %). **Minmod + maxCo 0.1 bought ~4 % more physical time and did not
  reach completion.**
- **dt is Courant-limited, not a runaway:** `deltaT` constant at **2.318e-5**
  (≈ half the parent's 4.32e-5, consistent with maxCo halved), max Courant pinned at
  **0.1001 == maxCo** right up to the fault. `adjustTimeStep` is clamping dt to hold
  Co = maxCo; dt is far below `maxDeltaT`. **The effective time-step lever IS the
  Courant number** (adjustable-vs-fixed is moot here — see lever (b)).
- Cost of the partial R3p solve: **1100 core-s = 18.3 core-min** (275 s wall × 4
  ranks) to reach 58 %. Linear extrapolation to 100 %: **≈ 31.5 core-min** for a
  completing R3-level solve at maxCo 0.1.

**Answer-blind field diagnosis — WHICH `sqrt`?** rhoCentralFoam.C has two sqrt-of-Field
sites reached every step:
- **line 136** `volScalarField c("c", sqrt(thermo.Cp()/thermo.Cv()*rPsi));` — the
  **cell-centre** sound speed. `rPsi = 1/psi ∝ R·T`, so a negative argument here ⟺ a
  **negative cell-centre temperature**, i.e. a negative internal energy produced by
  the conservative update after `thermo.correct()` (an energy/positivity/Courant
  failure).
- **lines 137–145** `cSf_pos`, `cSf_neg` — the **reconstructed FACE** sound speeds. A
  negative argument here ⟺ a **reconstructed face temperature undershoot** below zero
  (a limiter/reconstruction failure).

The stack trace names only `Foam::sqrt(Field&,...)` — it **cannot tell these two apart**.
That is precisely the L-501 ambiguity: the same SIGFPE has two distinct physical
causes pointing to two DIFFERENT levers (flux/reconstruction diffusion vs
Courant/positivity). **The plan therefore opens with a MEASUREMENT that disambiguates
them, and does not pick a lever on the strength of the trace alone.**

---

## 1. STEP 0 — the answer-blind diagnostic (locate the field and the site) — MANDATORY FIRST

Before any lever is graded, MEASURE which field goes negative and where. Restart R3p
from the last healthy written field (t = 0.10, decomposed fields already on disk) with
**dense instrumentation and no numerics change**:

- `controlDict`: `startFrom latestTime;` (t = 0.10), `writeControl timeStep;`
  `writeInterval 25;` (every ~25 steps through the failing window), everything else
  byte-identical to R3p.
- add `functions { fieldMinMax { type fieldMinMax; libs (fieldFunctionObjects);
  fields (T e p rho U); location yes; writeControl timeStep; } }` — logs min/max **and
  the cell location** of the extremum every step.

**What it measures / falsifiable outputs:**
- If `min(T)` (cell centre) trends toward and crosses zero at a locatable cell before
  the crash → the FPE is at **line 136**, a **post-update energy/positivity** failure →
  the Courant / flux-diffusion / bounded-energy levers are the relevant ones.
- If cell `min(T)` stays strictly positive up to the last written step yet the run
  still SIGFPEs → the negative value lives on a **reconstructed face** (line 137/143) →
  the **reconstruction / flux-scheme diffusion** lever is the relevant one.
- The reported extremum LOCATION tells us the region (Mach-stem foot, reflected-shock
  triple point, or the reflecting wall) — a physics anchor, not a guess.

**Cost:** restart covers only t = 0.10 → ~0.116 (≈ 0.016 of endTime); at the measured
R3 rate (~157 core-min per unit endTime) that is **≈ 2.5 core-min solver + ~0.3
overhead ≈ 3 core-min** (reuses the existing decomposition). Cheapest and most
decisive spend in the whole plan. **This is not a graded triple — it is a diagnostic
probe; it produces a MEASUREMENT, not a verdict.**

---

## 2. LEVER ANALYSIS — §2ay state-(b) options, ordered by robustness-per-cost

Every lever keeps Gate V' tol **0.0231** and every band byte-identical; only the
numerics move. Costs are at **4 ranks**, anchored on this session's measured R1p
(0.83 core-min), R2p (4.30 core-min) and the R3p partial (18.3 core-min @ 58 % →
~31.5 core-min to complete at maxCo 0.1). A graded Roache triple requires **one
numerics family** — the parent DMR triple prereg makes "any difference in scheme,
constants, maxCo, write times or rank count between rungs" a **disqualifier** — so a
lever applied inside a graded triple must be applied **uniformly to R1'/R2'/R3'**. A
fine-level-only change can only be a **diagnostic probe**, never a graded triple
member (see lever (b)).

### Lever L1 — flux scheme Kurganov → **Tadmor** (uniform, all three levels) — FIRST CHOICE
- **Exact dict change:** `system/fvSchemes` `fluxScheme Kurganov;` → `fluxScheme
  Tadmor;` (generator `make_case_successor.py:111`; one word). Nothing else moves —
  Minmod reconstruction and maxCo 0.1 are RETAINED.
- **Physical rationale:** confirmed available in this build (`readFluxScheme.H:4`;
  `rhoCentralFoam.C:167` `if (fluxScheme == "Tadmor") { aSf = -0.5*amaxSf; a_pos =
  0.5; }`). Tadmor replaces Kurganov's wave-speed-weighted interface split with a
  **symmetric split using the single local maximum wave speed** and a symmetric
  numerical-diffusion term `-0.5*amaxSf`. That is strictly **more numerical diffusion**
  at the interface than Kurganov — it damps the interface state excursions that drive
  the reconstructed-state or updated-energy into a negative temperature.
- **Expected effect on the R3p FPE:** raises the robustness ceiling at the flux level
  without touching dt or accuracy of the time integration; directly targets a FACE
  (line 137/143) overshoot and softens a marginal cell-update (line 136).
- **Cost:** same step count as R3p (dt unchanged; Courant-limited at maxCo 0.1), Tadmor
  is if anything marginally cheaper per step. R1' ~0.85, R2' ~4.3, **R3' ~32
  (MEASURED-ANCHORED from the 58 % partial)**, overhead ~1 → **≈ 38 core-min total**,
  under a 60 core-min cap. Cheapest robust in-solver lever that keeps a VALID triple.
- **Falsifiable proposition:** *If the Kurganov→Tadmor family reaches t = 0.2 at 1/240
  and yields a CONVERGING R1'/R2'/R3' Gate V' triple, the crash was flux-scheme
  interface diffusion and Tadmor cures it.* *If R3' still SIGFPEs at a similar time
  fraction (~55–60 %), added central-scheme diffusion is insufficient — the defect is
  a deeper positivity/energy failure, not interface diffusion, and Tadmor is refuted as
  a standalone cure.*

### Lever L2 — Courant reduction at the fine level: maxCo 0.1 → 0.05
- **Exact dict change:** `system/controlDict` `maxCo 0.1;` → `maxCo 0.05;`. `adjustTimeStep`
  stays `yes` (see note below).
- **Physical rationale:** dt is Courant-limited (measured: Co pinned at maxCo). Halving
  maxCo halves dt, halving the per-step conservative-update excursion and the CFL of
  the explicit Euler step — more margin against a locally negative internal energy
  (line-136 mechanism). Targets a **cell-update positivity** failure, NOT a face
  reconstruction overshoot.
- **adjustableRunTime vs fixed dt — does it matter?** **No, not for the crash.** With
  `adjustTimeStep yes` the solver already clamps dt to hold Co = maxCo (measured:
  deltaT constant, Co = 0.1001). A `fixed deltaT` would only change behaviour if set
  BELOW the Courant-implied dt — which is arithmetically identical to lowering maxCo.
  So "fixed small dt" is not an independent lever; it is lever L2 by another name.
  `adjustableRunTime` for WRITE timing is orthogonal to the crash (it only sets when
  fields are written, and its coarseness is why the failing step was never captured —
  addressed by STEP 0's `writeControl timeStep`).
- **Cost & the triple-consistency constraint:** halving dt doubles the R3-level step
  count → R3 solver ~**64 core-min** alone. A **uniform** maxCo-0.05 triple (required
  for a valid graded triple) would cost R1' ~1.7 + R2' ~8.6 + R3' ~64 + overhead ≈
  **~75 core-min — OVER the 60 cap**; it needs its own ~90 core-min cap in its own
  prereg. A **fine-level-only** maxCo 0.05 can be run only as a **diagnostic probe**
  (R3 single level, ~64 core-min if it completes, less if it crashes) — it is NOT a
  graded triple member because it would break family uniformity.
- **Falsifiable proposition:** *If the fine-level maxCo-0.05 probe reaches t = 0.2, the
  crash is Courant/positivity-limited and the fix is a smaller step (graded as a
  uniform maxCo-0.05 family under a raised cap).* *If it SIGFPEs at ~the same time
  fraction as maxCo 0.1, the failure is NOT Courant-limited — a clean measured
  elimination pointing to reconstruction/flux (favouring L1) or to a genuine positivity
  gap (L4).*

### Lever L3 — Tadmor + maxCo 0.05 combined (uniform)
- **Exact dict change:** both L1 and L2 together, uniform on all three levels.
- **Rationale:** if L1 and L2 each help but neither alone reaches t = 0.2, the combined
  diffusion + halved step is the strongest **standard** in-dict configuration.
- **Cost:** ~75+ core-min (dominated by R3' at halved dt) → own ~90 core-min cap and
  own prereg. Deploy only if L1 and L2 are each measured to help but not cure.
- **Falsifiable proposition:** *If the combined family reaches t = 0.2 and converges,
  the standard levers together are sufficient; if it still SIGFPEs, the standard in-dict
  levers are MEASURED-exhausted (→ §3 capability/tooling finding).*

### Lever L4 — most-bounded reconstruction (Minmod is already the floor)
- **Exact dict change:** among the standard TVD limiters usable as `reconstruct(...)`
  in v2606 — SuperBee, MUSCL, vanLeer, vanAlbada, **Minmod** — Minmod is **already the
  most diffusive**; there is no MORE-robust standard TVD limiter to switch to. The only
  genuinely more-bounded move is to collapse reconstruction toward **first order**
  (e.g. `reconstruct(T) limitedLinear 1` behaves near-Minmod; a true first-order face
  state removes reconstruction entirely). This trades away the formal second order.
- **Rationale / caveat:** if STEP 0 shows the negative value is on a **reconstructed
  face** (line 137/143), first-order reconstruction of T (and/or e) removes the
  undershoot by construction — but it is the most **accuracy-destructive** lever and
  will very likely **GATE FAIL on accuracy** (shock smearing beyond tol 0.0231) or
  STAGNATE the triple. **This is not "widening" the gate — it is an honest accuracy/
  robustness trade measured against the held bar.**
- **Cost:** ~same as L1 (dt unchanged) → ~38 core-min uniform.
- **Falsifiable proposition:** *If first-order T reconstruction reaches t = 0.2 but
  GATE FAILs Gate V' on accuracy, the limiter was masking the answer — a real trade
  finding, not a process failure.*

### Lever L5 — bounded internal energy / positivity-preserving update (OUT of standard dict levers)
- **Exact change:** none is available in a dict. Vanilla `rhoCentralFoam` has **no
  in-loop bound on T or e** (no `bound(T, TMin)` after `thermo.correct()`; confirmed
  from `rhoCentralFoam.C` — the only clip is `v_zero` on wave speeds). Bounding energy
  requires either a **solver-code modification** (a `bound(e, eMin)` / `T.max(TMin)`
  patch, a lab solver build) or switching to a **positivity-preserving flux/solver**
  not present in vanilla v2606.
- **Rationale:** this is the correct fix IF the failure is a genuine post-update
  negative internal energy (line 136) that the standard flux/limiter/Courant levers
  cannot prevent.
- **Cost:** a solver build + verification is a SEPARATE cfd successor with its own
  pre-registration and its own cap — NOT costed here as a dict lever.
- **Status:** **this lever marks the boundary between "standard levers" and a
  capability/tooling finding.** Reaching it as the only remaining route — after L1, L2
  and the STEP-0 diagnostic are MEASURED — is what would constitute a measured
  exhaustion (see §4). It is never reached by inference from one SIGFPE.

**Ordered by robustness-per-cost (best first):**
`STEP 0 (diagnose, ~3 cm)` → **L1 Tadmor (~38 cm, keeps valid triple)** → L2 fine-level
maxCo-0.05 probe (~64 cm, diagnostic) → L3 combined (~75+ cm) → L4 first-order recon
(~38 cm, accuracy-risky) → L5 bounded-energy (solver build, separate successor).

---

## 3. GATES ARE HELD BYTE-IDENTICAL ACROSS ALL LEVERS

Explicitly, for every lever above: **Gate V' PASS iff `|x_measured − x_exact_at_row| ≤
0.0231`** (`dmr_locator_v2.py:69` `GATEV_TOL = 0.0231`), applied at each of R1'/R2'/R3';
**Gate T' = rule-5 self-convergence triple**, no band loosened; graded by the frozen
method-agnostic `dmr_locator_v2.py` (blob `52aacf9669…`). No lever touches a gate,
threshold, band, cap-per-lever wiring, or label. Only `fvSchemes`/`controlDict`
numerics move. A lever may honestly **GATE FAIL on accuracy** (especially L4) — that is
a result, not a widening.

---

## 4. MEASURED EXHAUSTION vs a lever that works — what the chief authorises against

- **A lever WORKS** iff its uniform graded family reaches t = 0.2 at 1/240 AND yields a
  CONVERGING R1'/R2'/R3' Gate V' triple inside the held band (rule 5). Then the DMR
  Mach-10 case has a defensible 1/240 result under changed-but-honest numerics.
- **A lever GATE-FAILs on accuracy** iff it completes but the triple exceeds tol 0.0231
  or stagnates — a real robustness/accuracy trade finding, still state (b), reported not
  softened.
- **MEASURED EXHAUSTION (a capability/tooling finding)** requires ALL of: (i) STEP 0 has
  LOCATED the offending field and site (line 136 cell-T vs 137/143 face-T) with a
  min/max reader shown able to see a non-zero (plant-the-zero, rule 3); (ii) the
  standard in-dict levers relevant to that located mechanism have each been RUN and
  measured insufficient — at minimum L1 (Tadmor) and the L2 fine-level Courant probe,
  and L3 if each helped partially; (iii) the only remaining route is L5 (a solver-code
  bound / positivity-preserving solver not in vanilla v2606). Only THEN is it honest to
  write "the standard numerics-robustness levers do not carry a Mach-10 DMR to 1/240 in
  vanilla rhoCentralFoam v2606" — a tooling finding that MOTIVATES a solver-build
  successor. **It is never inferred from one SIGFPE (L-501), and never from L1 alone.**

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This is a DRAFT
plan for the cfd supervisor to relay to the chief; execution is the supervisor's after
the chief approves the direction. No compute launched.**
