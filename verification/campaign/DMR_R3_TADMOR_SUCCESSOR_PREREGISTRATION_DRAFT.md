# DMR TADMOR-FLUX SUCCESSOR — a new numerics family — pre-registration (DRAFT — NOT AUTHORISED)

> **DRAFT — NOT AUTHORISED — NOT FROZEN — NO CHECK-4 TAKEN — NO COMPUTE.**
> Prepared by cfd `lab-lane`, 2026-09-07, for the cfd supervisor to relay to the chief.
> This skeleton pre-registers the **FIRST-CHOICE lever** from
> `DMR_R3_NUMERICS_ROBUSTNESS_LEVER_ANALYSIS.md` (§2 lever L1: flux scheme
> Kurganov→Tadmor). It is a §2ay state-(b) NUMERICS-ROBUSTNESS successor. **It becomes
> a pre-registration only when authored to completion (generator + driver + grader
> identity on disk), frozen by sha, and check-4-verified by the supervisor — none of
> which has happened.** Gate V' tol 0.0231 and all bands are held BYTE-IDENTICAL to the
> parent; only the flux scheme changes. Heeds L-501: STEP 0 (§1a) MEASURES the failing
> field/site before this family's verdict is trusted; a crash of this family is a
> MEASURED negative result, never a capability inference.

---

## 0. §2ay classification

Parent of THIS successor: the **DMR positivity successor** (freeze `08efee1a`,
`DMR_R3_POSITIVITY_SUCCESSOR_PREREGISTRATION.md`), verdict **NOT A RESULT** — R1p (1/60)
and R2p (1/120) graded **Gate V' PASS** (position errors 0.01082 → 0.006081 vs tol
0.0231, converging), **R3p (1/240) SIGFPE rc=136** in `Foam::sqrt(...)` at t = 0.11648
of 0.2 (58 %) inside the `rhoCentralFoam` solve, triple therefore incomplete. That
successor had **already** applied Minmod reconstruction + maxCo 0.1; both were live in
the crash. **This is not a capability gap (state a):** the mechanism is a
reconstructed-state / updated-energy excursion into a negative temperature at the flux
level, and a **more diffusive but still-available in-solver flux scheme (Tadmor)** is a
standard our-side lever confirmed present in this build (`readFluxScheme.H:4`,
`rhoCentralFoam.C:167`). This draft opens the Tadmor-flux variant as its own family.

## 1. WHY A NEW FAMILY, NOT A RE-RUN

The parent DMR triple prereg names as a **disqualifier** "any difference in scheme,
constants, boundary conditions, maxCo, write times or rank count between rungs — the
triple requires one numerics family and a difference invalidates it." Therefore the
flux-scheme change is applied **uniformly to all three levels** of a **fresh,
self-contained three-level family** — R1t (1/60, 240×60), R2t (1/120, 480×120), R3t
(1/240, 960×240), nested exactly 2:1 — graded as its OWN Gate V' and its OWN
grid-convergence triple. The original `vanLeer` two-rung pair (2026-08-07 record) and
the Minmod positivity successor are both **untouched**.

### 1a. STEP 0 diagnostic (MANDATORY, runs before this family's verdict is trusted)

Per the lever analysis §1: restart R3p from t = 0.10 (decomposed fields on disk) with
`writeControl timeStep; writeInterval 25;` and a `fieldMinMax` functionObject on
`(T e p rho U)` with `location yes`, no numerics change. This LOCATES whether the
negative temperature is a **cell-centre** value (rhoCentralFoam.C:136, post-update
energy failure) or a **reconstructed-face** value (lines 137/143, reconstruction
overshoot) — the answer-blind measurement L-501 requires. It is a **diagnostic probe,
not a graded triple member**. Cost ≈ 3 core-min (§6). Its result informs whether Tadmor
(this family) is the mechanism-appropriate lever or whether L2/L5 should be reached
first — but this family may be run in parallel with the probe since Tadmor is the
cheapest robust standard lever regardless.

## 2. WHAT FAILED, MEASURED

From `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R3p/`:
- rc 136 SIGFPE, deepest frame `Foam::sqrt(Field<double>&, UList<double> const&)`,
  trapped (`sigFpe::sigHandler`), at t = 0.11648 (58 %).
- dt Courant-limited: `deltaT` constant 2.318e-5, max Courant pinned 0.1001 == maxCo.
- Partial solver cost 1100 core-s = 18.3 core-min to 58 % → ~31.5 core-min to complete.
- Last written field t = 0.10 healthy; failing-step field never written (STEP 0 fixes).

## 3. THE SPECIFIC NUMERICS CHANGE, AND WHY IT SHOULD RECOVER

**Single lever, uniform across R1t/R2t/R3t:** `system/fvSchemes`
`fluxScheme Kurganov;` → `fluxScheme Tadmor;`. Everything else is byte-identical to the
positivity successor: Minmod / MinmodV reconstruction RETAINED, maxCo 0.1 RETAINED,
Euler ddt, `div(tauMC) Gauss linear`, all BCs, write times and 4-rank layout unchanged.

**Why it should recover:** `rhoCentralFoam.C:167` — for Tadmor the interface diffusion
becomes `aSf = -0.5*amaxSf` with `a_pos = 0.5` (symmetric split on the single local
max wave speed), strictly **more numerical diffusion** at the interface than Kurganov's
wave-speed-weighted split. That damps the interface-state excursion driving the negative
temperature, at no dt cost.

**Honest caveat, stated before the run (rule 2):** Tadmor is **more diffusive** than
Kurganov. This family may **run to completion and then GATE FAIL on accuracy** — the
shock could smear past tol 0.0231, or the triple could STAGNATE as added diffusion masks
the formal order. That is a legitimate robustness/accuracy trade finding, still state
(b), NOT a widening of the gate: the tolerance is held (§4). And R3t may **still SIGFPE**
— then the flux-diffusion lever is MEASURED insufficient (a negative result), pointing to
L2 (Courant) or L5 (bounded energy), reported not softened.

## 4. GATES — NO THRESHOLD WIDENED

- **Gate V' (kinematics vs exact theory):** PASS iff `|x_measured − x_exact_at_row| ≤
  **0.0231**` (1.0 % of exact incident-shock travel 2.30940 at t = 0.2, row nearest
  y = 0.9), applied at each of R1t/R2t/R3t. Byte-identical to the parent Gate V.
- **Gate T' (grid-convergence triple, rule 5 in full):** self-convergence triple of the
  Gate V position error across R1t/R2t/R3t (Roache no-exact form, exact 2:1 nesting). A
  non-CONVERGING triple is **NOT A RESULT**; a CONVERGING triple is graded against its
  band; no GCI on a non-monotone triple. No band loosened.
- Controls carried over: planted 7-whole-cell density displacement, planted-absence
  control, and the regression reproducing the 2026-08-07 R1/R2 Gate V positions.

## 5. GRADING PATH — FIXED AT FREEZE, PLANTED-ZERO CONTROL (TO BE AUTHORED)

Grading is by the frozen method-agnostic `verification/runs/DMR_runs/dmr_locator_v2.py`
(blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`, `GATEV_TOL = 0.0231` at :69) — it
grades shock POSITION and reads NO scheme file, so it grades the Tadmor family unchanged;
the driver must hash it against the frozen blob and refuse on mismatch (rule 2). The
planted-zero controls of §4 are mandated before any verdict (rule 3).

**NOT YET ON DISK (this is why the draft is NOT freeze-ready):**
- a **generator** `make_case_tadmor_successor.py` — one word changed vs
  `make_case_successor.py:111` (`Kurganov`→`Tadmor`), to be authored and its output
  diffed against the Minmod successor to confirm EXACTLY that one line moves;
- a **driver** iterating R1t/R2t/R3t to fresh roots
  `verification/runs/DMR_R3_TADMOR_SUCCESSOR_runs/{R1t,R2t,R3t}` (all confirmed ABSENT
  at authoring — rule-4 age/ABSENT guard per level), calling the Tadmor generator,
  carrying rc-inside-the-wrapper (setsid lesson) and the single 60-core-min accumulator;
- the STEP-0 diagnostic restart wired as a separate probe script (not graded).

Freeze requires all three authored and the supervisor's check-4 taken PERSONALLY.

## 6. COST — rule 12 (measured anchors from this session's R1p/R2p and the R3p partial)

4 ranks; anchors: R1p 0.83 core-min, R2p 4.30 core-min (both measured this session,
`PROGRESS.txt`); R3p partial 18.3 core-min @ 58 % → ~31.5 core-min to complete at
maxCo 0.1. Tadmor is the same step count (dt unchanged), if anything marginally cheaper
per step.

| item | h | grid | basis | core-min |
|---|---|---|---|---|
| STEP-0 diagnostic (restart 0.10→crash, dense writes) | 1/240 | 960×240 | ~0.016 endTime × ~157 cm/unit | ~3 DIAGNOSTIC (not graded) |
| R1t | 1/60 | 240×60 | measured R1p 0.83 | ~0.85 MEASURED-ANCHORED |
| R2t | 1/120 | 480×120 | measured R2p 4.30 | ~4.3 MEASURED-ANCHORED |
| R3t | 1/240 | 960×240 | 18.3 cm @ 58 % → 100 % | ~32 MEASURED-ANCHORED |
| mesh/init/reconstruct/locator | | | | ~1.0 |
| **estimate total (incl. STEP 0)** | | | | **≈ 41 core-min** |
| **HARD CAP (the ONE registered cap)** | | | | **60 core-min** |

R3t dominates. An overrun of the 60 cap **stops the run**; no new budget (rule 12). If
R3t SIGFPEs, that is a MEASURED negative result (Tadmor insufficient), reported not
softened. Per-level figures are advisory rule-12 watermarks, NOT per-level caps — the
driver enforces the single 60-core-min accumulator across all steps of all levels and
writes `CAP_BREACH.txt` on breach (mirrors the positivity successor's driver). Dollars:
60 core-min = 1.0 core-h × $0.0513 = **$0.0513 — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5). Well under the $25 ceiling. Calibration row owed at
completion (rule 12).

## 7. DOES THE FINE LEVEL NEED ITS OWN ROBUSTNESS TREATMENT?

**Physically yes, procedurally no — within this family.** Only R3t (1/240) is at risk;
R1t/R2t completed clean at these numerics. But a graded Roache triple requires ONE
numerics family (parent disqualifier), so the fine level CANNOT carry a distinct
scheme/maxCo inside this triple. If Tadmor at uniform maxCo 0.1 still fails R3t, the
distinct fine-level treatment (maxCo 0.05, or first-order T reconstruction) must be
explored as a **diagnostic probe** and then, if it works, graded as its own **uniform**
family under its own prereg and cap (lever analysis §2 L2/L3) — never spliced into this
triple.

## 8. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether a more diffusive but still-standard flux scheme (Tadmor) carries the
  DMR to t = 0.2 at 1/240 and yields a CONVERGING Gate V' triple; and quantify the
  robustness-vs-accuracy trade at Mach 10.
- **Cannot:** claim capability exhaustion — that requires the full §4 measured chain
  (STEP-0 location + L1 + L2 + L3 measured insufficient). Cannot alter the original
  `vanLeer` or Minmod families' standing.

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). DRAFT handed to the
cfd supervisor. NOT frozen, NOT authorised, no compute launched.**
