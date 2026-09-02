# VMFL046 — Supersonic Flow with a Normal Shock in a CD Nozzle — PRE-REGISTRATION **FROZEN**

**FROZEN — THIS IS THE FREEZE COMMIT.** Frozen by `ansys-verification-supervisor` at **2026-09-02T23:20:26Z** after a
personal §3 check-4 diff re-read of `grade_vmfl046.py`, `run_vmfl046.sh`, `quasi1d_reference.py` and this
file. Drafted by `ansys-lane-opus48` (`claude-opus-4-8[1m]`) 2026-09-02. **No solver has produced a graded
result for this case.** Gates are CLOSED from this commit; departures land only as dated addenda.

**GRADING PATH PINNED BY SHA (rule 2):**

- comparator `grade_vmfl046.py` — blob **`cbe98dc821cdbeaba0c27363117b65b7ee199dcf`**
- driver `run_vmfl046.sh` — blob **`9d04e63eae3a9e8a34945ebfd8710b04d2d7a48c`**
- reference generator `quasi1d_reference.py` — blob **`0089c7fb56c68d706897fc1ddc91ae3f6c5d6863`** (an INSTRUMENT under §18; graded-path-equivalent)

**SUPERVISOR'S §3 CHECK-4 RECORD.** Gate constants verified against what I ruled: `M_GATE_X 0.9`, `DELTA_M 4.25e-4` (= §18 spread `|1.882125−1.8817|`, verified), `W_PLATEAU 500`, `SHOCK_TOL 0.05` (primary), `GCI_FINE_MAX 0.15` + `MACH_DEV_TOL 0.10` (demote-only), `P_OBS 0.5/2.5`. Comparator `--selftest`: **15 arms, ALL PASS**, run by me — dual plants (both fire), known-bad refusal, Roache CONVERGING/OSCILLATORY, five completion BAD arms incl. `4e-endTimeMismatch`, and two plateau arms (converged / not-converged). Coupling verified: fields write at endTime only (single time dir → clean age guard); centreline writes every 500, so at endTime 20000 the last two samples are exactly `W_PLATEAU` apart; driver sources the v2606 bashrc and asserts BOTH `blockMesh` and `rhoSimpleFoam` on PATH and writes `RUN_RC` — a guard demanding a file no driver writes would refuse every run forever. `§12.2` model-form bounds re-derived by me on an independent path (`dM/M 0.107%`, `dx_shock/x ≤0.63%`), the cap-lifting conclusion robust across a 1.6× sensitivity spread.

**All five §11 items are RULED (charter v1.16 §21, v1.17 §22, v1.18 §23 — commits f9758222 / 8cee7d06 / efa00c9a) and the
rulings are folded into these bytes (§11.2).** VMFL046 is this team's **first genuine `PASS`
candidate** from the never-run set: §18 cleared on form (a), §12.2 re-ruled SAME for the
primary limb (model-form bounds ≪ bands), convergence set to the M(0.9) plateau δ_M=4.25e-4
with LTS the binding fallback, secondaries demote-only. The case is BUILT and validated
**All five §11 items are now RULED
(charter v1.16 §21, v1.17 §22, v1.18 §23 — commits f9758222 / 8cee7d06 / efa00c9a) and the
rulings are folded into these bytes (§11.2).** VMFL046 is this team's **first genuine `PASS`
candidate** from the never-run set: §18 cleared on form (a), §12.2 re-ruled SAME for the
primary limb (model-form bounds ≪ bands), convergence set to the M(0.9) plateau δ_M=4.25e-4
with LTS the binding fallback, secondaries demote-only. The case is BUILT and validated
(valid mesh; converges from cold start under the daemon-equivalent shell; reference
instrument selftest + planted-failure pass; comparator **15** selftest arms all pass incl.
the plateau and last==endTime arms). It awaits only the supervisor's §3 check-4 freeze after
a CLAUSE-B one-iteration smoke. **This candidacy is not a PASS**: it is subject to the graded
run meeting the primary gate, the δ_M plateau (binding incl. if it fails → LTS), and the
demote-only secondaries.

## 1. Case identity
- **Case:** VMFL046, *Supersonic Flow with Normal Shock in a Converging Diverging Nozzle*.
- **Manual:** VM2026R1 **p. 155** (title-page verified 2026-09-02: match).
- **Reference:** F. M. White, *Fluid Mechanics* 3rd ed., pp. 518–531 (1994). **Source class:
  ANALYTICAL** — inviscid quasi-1D isentropic area–Mach + Rankine–Hugoniot normal-shock
  relations. Re-derived independently by this lab in `quasi1d_reference.py` (validated §9).
- **New physics sub-class for this team:** internal compressible nozzle flow with a normal
  shock (we hold external oblique shock and Prandtl–Meyer expansion, not this).

## 2. Physics
Steady, laminar, compressible ideal-gas flow in a CD nozzle: subsonic inlet → sonic throat
→ supersonic → normal shock in the divergent section → subsonic to outlet. γ=1.4.

## 3. Manual data, Ansys's value, and documented assumptions
- **Manual:** length 2 m; exit/throat area ratio 3; inlet total (gauge) 200 kPa; inlet total
  T 500 K; wall T 328 K; outlet gauge static 75 kPa; μ=1.7894e-5 kg/m·s; ideal gas; max
  Mach ≈ 2.2.
- **Ansys value:** centreline Mach vs analytical (Figure .46.2, a curve) — quoted for
  context only when digitized; **never the gate** (the gate is the analytical, which we
  generate ourselves, so no figure is needed — the round's headline finding).
- **DOCUMENTED ASSUMPTIONS (a-priori, ratify at freeze):** (a) **operating pressure
  101.325 kPa** (Fluent default) → absolute inlet total 301.325 kPa, outlet static 176.325
  kPa; sets the shock location. (b) **Contour** (§4). Verified a-priori: this contour +
  back-pressure gives analytical max Mach **2.197** and shock at **x=1.250** — reproducing
  the manual's stated max Mach 2.2, which corroborates the assumptions.

## 4. Geometry / contour — a DOCUMENTED CHOICE (the manual prints no contour)
Straight-walled planar CD nozzle (blockMesh builds it exactly; the quasi-1D reference is the
exact area–Mach solution for THIS A(x)): throat at x=0.5 m, throat half-height 0.1 m,
inlet/throat area ratio 2, exit/throat area ratio 3, L=2 m. HALF the nozzle is modelled by
symmetry about the centreline y=0. A different contour would be a different (equally valid)
registration; this one is frozen.

## 5. Grid triple (r=2, a-priori)
Axial(converging) × axial(diverging) × transverse: **L1 = 40/120/20, L2 = 80/240/40,
L3 = 160/480/80** (all counts double each level; L3 = 51 200 cells). Uniform grading.

## 6. Solver, model, BCs, and the FROZEN scheme choice
- **Solver:** `rhoSimpleFoam` (v2606), steady compressible, laminar. `heRhoThermo` /
  perfectGas / `const` transport (μ=1.7894e-5, Pr 0.72) / hConst (Cp 1004.5, molWeight
  28.96 → R=287, γ=1.4).
- **BCs:** inlet `totalPressure` p0=301325 + `pressureInletVelocity` U + fixedValue T=500;
  outlet fixedValue p=176325 + inletOutlet U,T; wall noSlip + T=328 (manual); centreline
  `symmetryPlane`; front/back empty.
- **FROZEN SCHEME — first-order `upwind` on U and energy, `div(phid,p)` upwind, +
  `limitTemperature` fvOption (150–2000 K) + relaxation U 0.3 / e 0.5.** This is a
  DISCLOSED, deliberate robustness choice: the higher-order `linearUpwind limited` /
  `limitedLinear` schemes **diverge on "Negative initial temperature" at the shock** even
  from a converged restart — the exact failure that killed this lab's VMFL017 (register row
  #19). First-order upwind converges cleanly from cold start. Consequence: **observed
  Roache order ≈ 1** (reflected in the a-priori band, §7) and a grid-smeared shock; a
  higher-order VMFL046-R2 (e.g. staged schemes or rhoCentralFoam) is future work.

## 7. The gate — a-priori, as ruled in charter v1.16–v1.18 (§21–§23). PASS IS AVAILABLE.
Gate quantity: centreline Mach at **x=0.9** — a pre-shock, smooth, supersonic station chosen
from the **analytical** shock location (1.25, a-priori), NOT from the CFD.
- **CONVERGENCE (§22.5, replaces the residual floor).** A level is converged iff the M(0.9)
  **plateau** holds: `|M(0.9)_endTime − M(0.9)_{endTime−W}| < δ_M`, **W=500**, **δ_M=4.25e-4
  Mach**. δ_M = `|1.882125 − 1.8817|`, §18's reference-reproduction spread (generator vs
  NACA-1135), measured for §18 BEFORE the production run → uncontaminated: iteration noise
  below the reference's own uncertainty cannot move a verdict comparing to it. **Binding
  including if it fails** → then `NOT A RESULT` and the **pre-committed LTS / transient-to-
  steady fallback (§22.6); NO loosened floor is available.** residualControl is removed; the
  run goes to endTime (last==endTime is therefore a live rule-4 completion limb).
- **PRIMARY gate (a-priori-clean):** Roache triple on M(0.9) **CONVERGING** (else NOT A
  RESULT, rule 5) **+ shock location within 5 %** of analytical — the only limb that compares
  this solve to the reference, and it is a-priori-clean (its model-form bound 0.18–0.63 % ≪
  5 %, §11 item 2).
- **SECONDARIES are DEMOTE-ONLY (§21.3):** observed order p ∈ [0.5, 2.5], fine-grid GCI ≤
  15 %, pre-shock Mach within 10 %. They may turn a PASS into `GATE FAIL`, **never license a
  PASS**, and being contaminated-loose (built after coarse numbers were seen) **a secondary
  that does NOT fire is printed as NOT evidence of quality.**
- **VERDICT CEILING: `PASS` (§12.2 re-ruled SAME for the primary limb, v1.18 `efa00c9a`).**
  The model-form difference (inviscid quasi-1D reference vs viscous 2-D solve) is BUDGETED,
  not disqualifying: both compared limbs' model-form error is one-to-two orders below their
  bands (M(0.9) 0.107 %, shock location 0.18–0.63 %; §11 item 2). PASS requires primary_ok
  AND no secondary fired; a fired secondary → GATE FAIL; a shock-location miss → GATE FAIL;
  a non-CONVERGING triple or unmet plateau → NOT A RESULT.
- **SHOCK-CAPTURED-vs-JUMP disclosure (§23.4), on the correct ground.** The reference shock is
  a zero-width JUMP; the CFD shock is CAPTURED (smeared). The gate never reads a through-jump
  quantity — it reads shock **location** and **pre-shock** M(0.9). §23.4's rationale "the
  first-order smear is symmetric so its centroid is unbiased" is **tightened here**: first-
  order upwind smear is dissipative and not guaranteed symmetric, so the honest ground is that
  the smear-induced shock-location bias is bounded by the numerical shock **width** (a few
  cells) ≪ the 5 % band (20 cells at L3) and **refines with the mesh** — the band budgets it;
  it does not rest on an unproven symmetry. A future R2 gating through the jump reopens §23.4.

## 8. Cost
- **Ranks:** 1. **Estimate ~12 core-min for the graded triple, a-priori — the smoke cost is
  NOT usable as the estimator here.** The 2026-09-02 calibration lesson (use the smoke cost)
  assumes an UNCONTENDED smoke; this smoke ran under heavy contention (load ~13, dafoam
  chains): L1 0.18 core-min (near-uncontended) but L2 **5.35 core-min** (321 s wall for
  12 800 cells — contention-inflated, not representative). Per the refinement accepted this
  session, a contention-inflated smoke is not the clean estimator; the ~12 core-min figure
  is scaled a-priori from L1's uncontended rate and the L1/L2/L3 cell counts (×~4 per level),
  and any excess at grading is contention WASTE, reported separately (COMPUTE_BUDGET §6), not
  misprediction. Driver running-total cap **30 core-min** (may be tight for L3 under heavy
  contention — flagged).
- **cost_basis:** core-min = wall_s × ranks ÷ 60, MEASURED from the driver; dollars DERIVED
  at $0.0513/core-h, owner-stated, not measured (COMPUTE_BUDGET_CHARTER §5).

## 9. Grading path, reference instrument, and disclosed smoke
- **Comparator:** `grade_vmfl046.py` (pinned by sha at freeze). **Driver:** `run_vmfl046.sh`
  (self-sources OpenFOAM, asserts blockMesh + rhoSimpleFoam on PATH — charter §15). **Case:**
  `case/`. **Reference:** `quasi1d_reference.py`.
- **Reference instrument validated (supervisor's instrument standard):** `--selftest` passes
  independent NACA-1135 anchors (A/A*(M=2)=1.6875, normal-shock M1=2 → M2=0.5774/p2p1=4.5/
  p02p01=0.7209), round-trip inversions, full-nozzle self-consistency, AND a **planted-
  failure arm** (a mutated area–Mach exponent is CAUGHT). ALL PASS.
- **Comparator selftest: 12 arms ALL PASS** — dual plants (centreline + T-field), known-bad
  refusal, Roache CONVERGING/OSCILLATORY, and four completion BAD arms (no-End, missing
  field, age-guard, nonzero rc) each refusing exit 2.
- **§18 REFERENCE INDEPENDENCE — the reference is ALGEBRAIC and the independence is
  PERFORMED (not asserted).** The generator is closed-form: isentropic area–Mach relation
  (`area_ratio`, L24) inverted by bisection root-find (`mach_from_area_ratio`, L40-48), the
  Rankine–Hugoniot normal-shock jump (`normal_shock`, L54), and pointwise station evaluation
  (`mach_distribution`, L62) — **no marching, ODE integration, or spatial stepping**. The
  gate value M(x=0.9) [A/A*=1.53333 from contour arithmetic, pre-shock supersonic branch]
  reproduces across three INDEPENDENT paths: this generator **1.882125**; an independent
  Newton solver (different method) **1.882125** (diff 0); NACA-1135 published-table
  interpolation **1.8817** (diff **4.3e-4**). This is §18 forms 1+3 (independent code path +
  external published value). **§18 is CLEARED; the PASS barrier is model-sameness (§7), not
  reference dependence.**
- **Disclosed smoke (NOT the freeze; scratch), full L1/L2/L3 under a bare daemon-equivalent
  shell** (rhoSimpleFoam confirmed NOT on PATH beforehand; the driver self-sourced; total
  28.2 core-min, contention-inflated): **L1 CONVERGED** (2777 iters, p-residual 9.98e-7,
  0.18 core-min) but **L2 and L3 did NOT converge** — both ran to endTime 20000 with
  p-residuals plateaued at **3.2e-4 / 2.5e-4**, well above the frozen 1e-6 floor. Grading the
  smoke triple, the comparator correctly returned **NOT A RESULT** (rule 5 step 1, L2 not
  iteratively converged) — the guard working. The CFD shock location matched analytical to
  <1 %; coarse max Mach 2.0 vs 2.197 (first-order). **Smoke numbers were not used to set any
  gate (§11.1).** This is the §12.2-shaped finding in item 5 below.

## 10. Guards
Dual planted-zero (rule 3, both gate readers), strict completion (rule 4: rc via RUN_RC,
End + no FOAM FATAL, fields present, age guard, **and last==endTime — which NOW APPLIES,
because residualControl was removed and the run goes to endTime; §22.5**), and known-bad
refusal — all exercised by the 15-arm selftest (§9), incl. plateau and endTime-mismatch arms.
(ExecutionTime-count remains inapplicable and is not checked.)

## 11. THE FIVE ITEMS AND THEIR RULINGS (v1.16–v1.18; folded into the frozen bytes, §11.2)

**RULING SUMMARY.** Item 1 RETAINED demote-only (§21.3). Item 2 §12.2 re-ruled **SAME** for
the primary limb, cap **LIFTED** (v1.18) — VMFL046 a PASS candidate. Item 3 RATIFIED. Item 4
ACCEPTED as disclosed. Item 5 option (b) plateau **δ_M=4.25e-4 over W=500**, LTS the binding
fallback (§22.5/§22.6). Details below.

**§18 DISPOSITION (SATISFIED; named in the frozen bytes per §18.2).** The reference is
closed-form algebra, not a solver; the independent path is closed-form isentropic +
Rankine–Hugoniot evaluated from the manual's stated inputs, and it is PERFORMED in §9
(gate value M(0.9) reproduced by an independent Newton path to the digit and by NACA-1135
published tables to 4.3e-4). §18 is not an open item — it is cleared and recorded.

1. **RULE-2 CONTAMINATION DISCLOSURE (raised against my own work).** Building and
   stabilizing the compressible case necessarily exposed coarse-smoke Mach numbers (max
   Mach ≈ 2.0 and ~9 % pre-shock deviation at L1) before the secondary bands (§7: GCI ≤ 15 %,
   Mach dev ≤ 10 %) were fixed. Those bounds are round-number a-priori choices from
   first-order accuracy, and 10 % is *looser* than L1's ~9 % applied to the finer L3 — so
   they are not fitted-to-pass — but a reader cannot distinguish "a-priori" from
   "convenient" once the numbers are seen (the VMFL029 lesson). **The supervisor must ratify
   or reset the two secondary tolerances from the manual's agreement class independently.**
   The primary gate (CONVERGING triple + shock location ≤ 5 %) is a-priori-clean.
2. **Model-sameness ruling (§7 ceiling) — a-priori error budget, both limbs bounded ≪ band
   (supervisor's §22.2 principle; NO compute, uncontaminated by the production run).** The
   only viscous-vs-inviscid model-form difference on the compared quantities is boundary-layer
   displacement reducing effective area. (i) **M(0.9)** limb: δ*/h = 0.159% at the gate station
   → centreline model-form dM/M ≈ **0.107%** (93× below the 10% band). (ii) **Shock-location**
   limb (the primary a-priori-clean comparison; sensitivity dx/x per dA/A ≈ **0.99**, ~1:1, not
   amplifying): applying the Blasius displacement profile ε(x) to the effective-area matching
   moves the shock from x=1.2485 to 1.2508 → **Δx/x = 0.183%** (27× below the 5% band); a
   conservative TURBULENT BL (Re_x≈8e6, ~4× thicker δ*) gives **0.631%** (still ~8× below).
   **Both comparison limbs' model-form error is bounded one-to-two orders below their bands and
   is budgetable, not disqualifying.** Per §22.2 this supports re-ruling §12.2 **SAME** for the
   primary limb → VMFL046 a genuine `PASS` candidate. The ruling remains the supervisor's.
3. **Documented assumptions to ratify:** operating pressure 101.325 kPa and the frozen
   contour (§3, §4).
4. **First-order scheme (§6):** disclosed; a higher-order R2 is future work.
5. **CONVERGENCE CRITERION — RULED option (b), mechanical form (§22.5).** The residual floor
   1e-6 is unreachable on the finer levels (a PRE-FREEZE PRODUCTION RUN, §20.3, showed L1 to
   9.98e-7 but L2/L3 plateau at ~3e-4 and run to endTime — the steady-shock LIMIT CYCLE; that
   run and every quantity it revealed are named in §9). Option (a) — a loosened ~1e-3 floor —
   was **REFUSED** (chosen knowing it clears 3e-4). **The ruled criterion: the M(0.9)
   plateau, `|M(0.9)_endTime − M(0.9)_{endTime−500}| < δ_M`, δ_M = 4.25e-4 = §18's
   reference-reproduction spread `|1.882125 − 1.8817|` (measured before the run, uncontaminated),
   BINDING including if it fails → then NOT A RESULT and the pre-committed LTS / transient-to-
   steady fallback (§22.6); no loosened floor.** Implemented: `residualControl` removed
   (fvSolution), the centreline sampled every 500 iters (controlDict), the comparator judges
   the plateau (`plateau_and_gate`, DELTA_M/W_PLATEAU). The shock LOCATION keeps its 5 % gate,
   a-priori robust to the ±1-cell hunt (20 cells ≫ 1) — no plateau needed on it.

**Status:** all five items ruled and folded into these bytes; case built; reference +
comparator validated (15-arm selftest); the convergence option implemented. **Remaining before
freeze:** a CLAUSE-B one-iteration smoke (§20.3 — one timestep, coarsest mesh, scratch, bare
shell; it cannot reveal a plateau/order/GCI) to prove the case starts and the driver sources
its environment, then the supervisor's §3 check-4 freeze. **I froze nothing and graded nothing.**
