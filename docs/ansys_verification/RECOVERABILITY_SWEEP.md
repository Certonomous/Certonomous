# RECOVERABILITY SWEEP — Ansys VM backlog, five-point rule-out per case

**REVIEWED AND ADOPTED by the ansys-verification supervisor, 2026-09-06.** Drafted by
`ansys-lane-opus48` (running as **claude-opus-4-8[1m]**); reviewed against the §3
big-claim-verification duty. **Zero compute** — no solver was started; this is a
reading of the register, the per-case pre-registrations/comparators and the manual
against the source charters.

> **SUPERVISOR REVIEW NOTE (what I verified myself vs what stands as lane reading).**
> - **VERIFIED AT SOURCE BY ME:** the headline finding — the cavitation solvers
>   (`interPhaseChangeFoam`, `cavitatingFoam`, DyM/over variants) are present in
>   `/usr/lib/openfoam/openfoam2606/platforms/*/bin/`; `CASE_MAP.md` lines 230-231
>   carry a **false** `OUT OF SCOPE — no interPhaseChangeFoam` ruling that the same
>   file already contradicts at lines 676-687; and **VMFL021-R2 is `GATE REACHED`**
>   (register row #23, Cd 0.6349, triple CONVERGING, GCI 0.55 %, 2.40 % from Nurick).
>   **There is no cavitation capability gap.** The `CASE_MAP` scope note is corrected
>   in a separate commit that cites this sweep.
> - **VERIFIED EARLIER THIS SESSION:** the §2an.5 process-class instrument at source.
> - **ADOPTED AS LANE READING, not each re-verified by me:** the per-row (a)-(e)
>   rule-out cells for the other ~18 cases and the per-case next-fix sources. They are
>   a sound, honest reading; where the lane inferred rather than measured it wrote
>   `[inferred]`, and those (notably the VMFL011-R3 process class) are NOT to be
>   treated as settled. This register is the WORK PLAN the backlog is executed from,
>   not a set of final verdicts.
> - **HEADLINE I STAND BEHIND:** **zero proven capability gaps; every fail carries a
>   live fix path.** That is the answer to Sanaa's audit for this backlog.

**Binding law this sweep operationalises (Sanaa-direct, captured commit `4ae4b33`):**
a `NOT A RESULT` / `GATE FAIL` is **NEVER terminal** until it is **measured** that
OpenFOAM cannot do the case. The only acceptable terminal fail is a **proven
capability gap**. For every other fail the team keeps fixing — fetch papers, read
OpenFOAM source/tutorials, re-read the VM manual, hunt bugs, change
model/numerics/preconditioner/scheme — and **gates are NEVER widened**; fixes come
through **new successor registrations graded by frozen paths**. Research is
**inbound only** (CLAUDE.md rule 7).

**Classification instrument:** `VERIFICATION_CHARTER.md` **§2an.5** (read at source,
lines 7188–7223). MODEL-FORM is a **residual established by elimination**, the LAST
classification a case may reach, never asserted from the look of a result. The five
process classes, checked first, in order:

1. **Completion** — fails strict completion rule (CLAUDE.md rule 4): rc≠0, no `End`,
   last time≠`endTime`, missing fields, `ExecutionTime` mismatch, age-guard. *The
   answer was never produced.*
2. **Convergence / grid** — any level not iteratively converged/plateaued; triple
   `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` (rule 5). → `NOT A RESULT`.
3. **Crash / divergence / refused solve, not yet triaged** — a finding about the
   case/method/toolchain until triage says otherwise.
4. **Instrument** — comparator/reader/grading path shown wrong; a planted-zero
   control refuses (rule 3); an exit code is a crash wearing a refusal's clothes.
5. **Referent** — the reference value, its band or its provenance is itself in
   question. *A disagreement with a wrong reference is not a model-form failure.*

**MODEL-FORM** is reached ONLY when all five are cleared AND: rule 4 holds in every
limb; the triple is `CONVERGING` with GCI quoted at Fs=1.25; the planted control
fired; the reference and band are sound; **and the measured deviation exceeds the
band.** *In one line: the numerics are demonstrably right and the answer is
demonstrably wrong.*

**The five recovery categories** (Sanaa's): **(a) bug · (b) wrong solver selection ·
(c) preconditioner · (d) numerics/scheme · (e) config.** Per category: **RULED OUT**
(name the check/artifact), **NOT RULED OUT** (name the missing check), or **N/A**
(say why).

**CRITICAL HONESTY carried throughout:** where a case's physics was never graded
(an instrument refusal or a completion failure), unrecoverability **cannot be
assessed** — no value was ever produced. That is process class #4/#1, the **least
terminal** state, and the fix is the comparator/config, not the physics. "The
comparator refused" is distinguished from "the solver failed" in every row. Items
**inferred rather than verified at source** are marked `[inferred]`.

**Verdicts were read at the register's COLUMN 4 / row-heading verdict cell**
(`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`), not by token-grep.
Four cases already swept by the supervisor are excluded by instruction: VMFL046-R4,
VMFL046_INVISCID, VMFL072-R2, VMFL034-R2.

---

## SUMMARY

- **Cases swept:** 20.
- **Successes (verdict PASS or GATE REACHED — the gate was met; no fail to
  recover):** 9 — PASS: VMFL001-R2, VMFL006-R2, VMFL033-R2, VMFL038-R2, VMFL045-R2,
  VMFL069-R2; GATE REACHED: VMFL036, VMFL064-R2, VMFL076-R2. For these the five
  recovery categories are **N/A (case holds)**.
- **Fails swept:** 11 — VMFL003, VMFL004, VMFL007-R2, VMFL010, VMFL011-R3, VMFL021,
  VMFL022, VMFL051, VMFL054-R2, VMFL059, VMFL063.
- **Fails already RECOVERED by a named successor that landed a credential:** 2 —
  **VMFL004** → VMFL004-R2 `PASS`; **VMFL021** → VMFL021-R2 `GATE REACHED`.
- **Fails with ANY category still NOT RULED OUT (a live fix path open):** **9** —
  VMFL003, VMFL007-R2, VMFL010, VMFL011-R3, VMFL022, VMFL051, VMFL054-R2, VMFL059,
  VMFL063.
- **Instrument-refusals where NO physics value was ever graded (least terminal;
  unrecoverability cannot be assessed, fix is the comparator):** **1** among the
  deep-swept — **VMFL007-R2** (planted-zero control refused, exit 2). *(VMFL004 is
  an instrument BLOCK but its physics WAS graded and passed the gate, so it is not
  counted here; VMFL059 produced a value too — its gate quantity is mis-specified.)*
- **Genuine capability-gap candidates (proven-terminal):** **NONE.**
  **Notable correction surfaced by this sweep:** VMFL021/VMFL022 (orifice
  cavitation) are marked `OUT OF SCOPE — BY RULING — no interPhaseChangeFoam` in
  `CASE_MAP.md`, but that premise is **false**: `interPhaseChangeFoam` **is present
  on this box** (`/usr/lib/openfoam/openfoam2606/platforms/*/bin/`, alongside
  `cavitatingFoam`), a cavitating solve **actually ran** for both (VMFL021's physics
  was correct — Cd converging toward Cc=0.620, strongly cavitating), and the high-p
  sibling recovered to **VMFL021-R2 `GATE REACHED`**. **No cavitation capability
  gap exists.** Recommend the supervisor correct the CASE_MAP scope note.

---

## MASTER TABLE

Legend: `RO` = RULED OUT · `NRO` = NOT RULED OUT · `N/A` = not applicable · `HOLDS`
= case succeeded, category moot. PC = process class (§2an.5).

| Case | Verdict (col 4) | (a) bug | (b) solver | (c) precond | (d) numerics/scheme | (e) config | PC | Successor named? |
|---|---|---|---|---|---|---|---|---|
| VMFL001-R2 | `PASS` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL003 | `NOT A RESULT` | RO | NRO | NRO | NRO | NRO | #2 conv | VMFL003-M2 (A–D, all NAR) |
| VMFL004 | `NOT A RESULT` | RO | RO | N/A | N/A | RO (fixed) | #4 instr (physics passed) | **VMFL004-R2 `PASS` — RECOVERED** |
| VMFL006-R2 | `PASS` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL007-R2 | `NOT A RESULT` | N/A* | N/A* | N/A* | N/A* | NRO | #4 instr (no physics graded) | VMFL007-R3 (dir exists) |
| VMFL010 | `NOT A RESULT` | RO | RO | RO | NRO | NRO | #2 grid (OSCILLATORY) | none |
| VMFL011-R3 | `GATE FAIL` | RO | RO | N/A | NRO | NRO | #2 grid `[inferred]` | none (R3 is latest) |
| VMFL021 | `NOT A RESULT` | RO | RO | N/A | RO | RO (fixed) | #1 completion (config) | **VMFL021-R2 `GATE REACHED` — RECOVERED** |
| VMFL022 | `NOT A RESULT` | RO | RO | NRO | NRO | NRO | #2 grid (OSCILLATORY) | none |
| VMFL033-R2 | `PASS` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL036 | `GATE REACHED` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (gate met) | n/a — gate met |
| VMFL038-R2 | `PASS` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL045-R2 | `PASS` (tier GATE REACHED) | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL051 | `NOT A RESULT` | RO | RO | N/A | NRO | NRO | #2 grid (OSCILLATORY) | none |
| VMFL054-R2 | `GATE FAIL` | RO | RO | N/A | NRO | NRO | #2 grid (order not asymptotic) | none (R2 is latest) |
| VMFL059 | `NOT A RESULT` | RO | RO | N/A | RO | NRO | #2 (EXACT) / mis-spec gate = config | none |
| VMFL063 | `GATE FAIL` | RO | RO(weak) | N/A | NRO | NRO | #2 grid (GCI 120% ≫ dev) | none |
| VMFL064-R2 | `GATE REACHED` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (gate met) | n/a — gate met |
| VMFL069-R2 | `PASS` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (holds) | n/a — holds |
| VMFL076-R2 | `GATE REACHED` | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS | — (gate met) | n/a — gate met |

`*` VMFL007-R2: the four solver categories (a)–(d) are **premature, not cleared** —
the comparator refused before any physics value was graded, so there is nothing yet
to rule the solver in or out against. The only live category is (e)/the instrument.

---

## PER-CASE NOTES (fails only; successes are HOLDS across the board)

### VMFL003 — Pressure drop, turbulent pipe · `NOT A RESULT` · PC #2 (convergence)
Rule 5 step 1 fired: **all three Roache levels failed the frozen iterative-convergence
residual leg** (L3 missed the ε floor 2.523e−08 by 2.5×; L1/L2 on all four fields).
Δp is fully plateaued at every level, so the residual floor — not the physics value —
is what refuses it. Separately, the **model-level miss is real**: Δp −4.34 % vs the
2.5 % band, and −4.34 % (manual) / −4.55 % (Colebrook closed form) are nearly
identical, so it is not a 3-s.f. chart read but the **k-ε wall-treatment hazard the
pre-registration named as principal risk before compute**.
- **(a) bug — RO:** VMFL003-M2 arms A–D reproduced the residual behaviour; planted/
  plateau controls fired; the ε-floor miss is a physics/iteration fact, not a reader
  defect.
- **(b) wrong solver — NRO:** simpleFoam+kEpsilon is the manual's stated model, but
  no arm tried a different **near-wall treatment** (low-Re wall-resolved vs
  wall-function); the persistent ε residual + model Δp miss both point there.
- **(c) preconditioner — NRO:** ε never reaching 1e−8 can be linear-solver/
  preconditioner conditioning on the ε equation; unexplored.
- **(d) numerics/scheme — NRO:** M2 varied only `endTime` (A/B) and grid (C/D, both
  capped); no scheme change on ε convection/diffusion.
- **(e) config — NRO:** the y+/wall-function band vs the manual's is the named risk;
  a low-Re mesh (y+≈1) + wall-treatment change is the concrete lever.
- **Next fix:** re-register with **kOmegaSST or low-Re kEpsilon, wall-resolved y+≈1**
  (or standard kEpsilon with the wall-function y+ band 30–300 held across all three
  levels), and relax the ε linear solver / residualControl. Source:
  `/usr/lib/openfoam/openfoam2606/tutorials/incompressible/simpleFoam/pitzDaily`
  (wall-function fvSolution/fvSchemes pattern); manual p.19.
- **Successor:** VMFL003-M2 (arms A–D) named — but all four are `NOT A RESULT`
  (endTime/grid, **not** the wall-treatment lever). **No wall-treatment successor
  yet.**

### VMFL004 — Couette + pressure gradient · `NOT A RESULT` · PC #4 (instrument; physics passed)
A **frozen-instrument block over good physics**, not a solver failure. The volAverage
gate is a textbook PASS (2.50125/2.5003125/2.5000781, triple CONVERGING p≈2.0,
extrapolated 2.4999999993, planted-zero fired). The refusal is the inherited
iterative-convergence leg requiring Uy_initial/p_initial < 1e−7, which in this 1-D
fully-developed flow are **normalisation noise** (Ux converged to 3.2e−13).
- **(a) bug — RO; (b) solver — RO; (c)/(d) — N/A** (physics converged);
  **(e) config — RO (fixed):** the gate was graded on the driven Ux in the successor.
- **Next fix / Successor:** **VMFL004-R2 `PASS` — RECOVERED.** No open path.

### VMFL007-R2 — Non-Newtonian pipe · `NOT A RESULT` · PC #4 (instrument refusal, NO physics graded)
**The comparator refused (exit 2) on its planted-zero control (rule 3)** — not the
solver. `--verify-frozen` rc 0, `--selftest` 43 checks/0 failures, actual grade rc 2.
**No physics value was ever produced, so unrecoverability CANNOT be assessed** — this
is the least-terminal state. The fix is the comparator, not the physics.
- **(a)–(d):** premature — nothing graded to rule the solver in/out against.
- **(e) instrument — NRO:** the planted-zero plant must be sized to the reader (same
  class of miscalibration seen in VMFL011-R2).
- **Next fix:** repair the planted-zero control and re-register. Source: the sibling
  repair pattern in `cases/ansys_verification/VMFL011-R3/` (a working planted control
  for a pipe profile reader); manual p.29.
- **Successor:** `cases/ansys_verification/VMFL007-R3/` **directory exists** — named.

### VMFL010 — Laminar 90° tee-junction · `NOT A RESULT` · PC #2 (grid, OSCILLATORY)
Rule 5 step 2: the grid triple is **OSCILLATORY**. L3 flow-split is 0.26 % from the
reference 0.887 (inside the 3 % band) — **near-agreement does not rescue a
non-CONVERGING triple**. The solve is sane; the grid triple is the problem.
- **(a) bug — RO; (b) solver — RO** (simpleFoam/icoFoam correct for 2D laminar tee);
  **(c) precond — RO** (steady laminar, well-conditioned).
- **(d) numerics/scheme — NRO:** a non-monotone triple signals the levels are not in
  the asymptotic range or the flow-split functional is mesh-alignment sensitive.
- **(e) config — NRO:** rebuild a **structured, cleanly-refined (r=2) triple** at the
  junction so the split converges monotonically.
- **Next fix:** structured hex triple with r=2 refinement; source:
  `/usr/lib/openfoam/openfoam2606/tutorials/incompressible/icoFoam/cavity`
  (structured refinement pattern); manual p.39.
- **Successor:** none named.

### VMFL011-R3 — Triangular driven cavity · `GATE FAIL` · PC #2 (grid) `[inferred]`
`rms_vs_benchmark = 0.034088` at L3 vs band ≤ 0.030 — exceeds by 13.6 %; sequence
0.040264/0.034775/0.034088 is **monotone decreasing**, clean `End`, rc=0, nothing
inferred by the R-RC rung. The rms is **still falling with refinement**, so the band
may be crossable by further grid refinement — that keeps this in grid, not model-form.
- **(a) bug — RO** (R-RC-1 confirmed rc measured, clean End); **(b) solver — RO**
  (icoFoam/simpleFoam correct; earlier R-versions' instrument refusals are fixed);
  **(c) precond — N/A** (laminar).
- **(d) numerics/scheme — NRO:** add an L4 finer level and/or a higher-order
  convection scheme; the metric is still moving.
- **(e) config/referent — NRO:** the rms is against a **digitised** benchmark (Jyotsna
  & Vanka) — referent digitisation error (§2al/§2am) is not yet bounded.
- **Process-class caveat `[inferred]`:** classified #2 because the metric has not been
  shown grid-converged; if a 4-point ladder shows a CONVERGING triple with GCI < the
  13.6 % excess and the benchmark digitisation is bounded, it could escalate to a
  MODEL-FORM candidate. Not there yet.
- **Next fix:** L4 refinement + linearUpwind→linear convection; source
  `.../tutorials/incompressible/icoFoam/cavity`; benchmark Jyotsna & Vanka (verify
  digitisation against the manual figure, p.41).
- **Successor:** none beyond R3.

### VMFL021 — Orifice cavitation A (high p) · `NOT A RESULT` · PC #1 (completion via config)
**NOT a capability gap and NOT a physics failure.** The cavitating solve ran and was
going right — strongly cavitating (min α 0.064→0.0022), Cd converging 0.663→0.642
toward Cc=0.620, stable at P1=2.5e8 Pa. It failed on **two config/instrument defects**:
`controlDict` had `writeInterval 0.01` against `endTime 0.003` under adjustable write
control, so **no `endTime` field directory was ever written** at any level (rule 4
completion).
- **(a) bug — RO; (b) solver — RO** (`interPhaseChangeFoam` present and producing
  correct cavitating physics); **(c) precond — N/A; (d) numerics — RO** (converging);
  **(e) config — RO (fixed):** write-control corrected in the successor.
- **Next fix / Successor:** **VMFL021-R2 `GATE REACHED` (Cd=0.634868) — RECOVERED.**

### VMFL022 — Orifice cavitation B (low p) · `NOT A RESULT` · PC #2 (grid, OSCILLATORY)
Again **not a capability gap** — the cavitating solve ran. L3 Cd=0.759182,
Roache triple **OSCILLATORY** (d21 +0.00173, d32 −0.01649, R=−0.1049), p/GCI `None`
(comparator correctly refused GCI on a non-monotone triple). L3 is 2.669 % from the
reference (inside the 5 % band) but rule 5 gates it.
- **(a) bug — RO** (sensible cavitating Cd; refusal is correct); **(b) solver — RO**
  (interPhaseChangeFoam present).
- **(c) preconditioner — NRO:** low priority but unexamined.
- **(d) numerics/scheme — NRO; (e) config — NRO:** OSCILLATORY triple → build a
  monotone grid triple with finer near-orifice resolution, mirroring the VMFL021-R2
  recovery recipe that reached GATE REACHED.
- **Next fix:** monotone triple + refined near-orifice mesh; source
  `/usr/lib/openfoam/openfoam2606/tutorials/multiphase/interPhaseChangeFoam/cavitatingBullet`;
  manual p.87 (Nurick 1976 reference).
- **Successor:** none named for VMFL022 (VMFL021-R2 recovered the high-p sibling; the
  same recipe is the obvious lever). **NOT RECOVERED.**

### VMFL051 — Prandtl-Meyer isentropic expansion · `NOT A RESULT` · PC #2 (grid, OSCILLATORY)
Two independent rule-5 clauses fire; the triple is **OSCILLATORY** (R=−1.3486 per
CASE_MAP). Ma=3.2294 at L3 is inside the ±0.5 % band, but a non-CONVERGING triple is
NOT A RESULT whatever the value. The solve is sane.
- **(a) bug — RO** (value near-exact); **(b) solver — RO** (rhoCentralFoam correct
  for inviscid supersonic expansion); **(c) precond — N/A** (density-based explicit).
- **(d) numerics/scheme — NRO:** the volAverage(Ma) over a gate zone is shock/
  expansion-position sensitive; a line-sample functional or grid family unexplored.
- **(e) config — NRO:** monotone grid triple + gateZone placement.
- **Next fix:** monotone triple with a Mach functional sampled on a downstream line
  (less position-sensitive than a volume zone); source
  `/usr/lib/openfoam/openfoam2606/tutorials/compressible/rhoCentralFoam/obliqueShock`;
  manual p.165. NB the sibling VMFL045 (oblique shock) recovered via R2 — same solver
  family.
- **Successor:** none named.

### VMFL054-R2 — Trapezoidal driven cavity · `GATE FAIL` · PC #2 (grid, order not asymptotic)
A **finding about our band, not the solver.** u_x at cavity centre L3=−164.753,
triple **CONVERGING**, R=0.0923, GCI=0.011 % (GCI limb PASSES), but observed
**order p=3.438 ∉ [1,3]** (order limb FAILS) — and both limbs were required. The
prereg itself states p=3.438 is a **3-point pre-asymptotic estimate** that cannot
distinguish super-2nd-order from a pre-asymptotic artefact.
- **(a) bug — RO** (CONVERGING, GCI tiny, reproduced); **(b) solver — RO**
  (icoFoam/simpleFoam correct for laminar cavity); **(c) precond — N/A.**
- **(d) numerics/scheme — NRO:** a **4th finer level** gives a 4-point order estimate
  in the asymptotic range, which would very likely land p in [1,3].
- **(e) config — NRO:** the order-band lever is a **4-level ladder as a new
  registration** (the band [1,3] is frozen and is never widened).
- **Next fix:** add L4 for a 4-point order estimate; source
  `/usr/lib/openfoam/openfoam2606/tutorials/incompressible/icoFoam/cavity`;
  manual p.173.
- **Successor:** none beyond R2.

### VMFL059 — Conduction in a composite block · `NOT A RESULT` · PC #2 (EXACT) → root cause config
The rightWall triple is **EXACT** (rule 5 step 2). But **there is nothing wrong with
the solve** — all three levels rc=0, `End` present, last time==endTime 0.05, age
guard passed, planted-zero passed on both patches. The root cause is a **mis-specified
gate quantity**: the gated rightWall temperature is a **boundary-imposed value**, so
it is grid-invariant by construction → EXACT.
- **(a) bug — RO; (b) solver — RO** (chtMultiRegion/laplacianFoam correct);
  **(c) precond — N/A; (d) numerics — RO** (clean conduction solve).
- **(e) config — NRO:** the gate must be re-specified onto a quantity that **varies
  with the grid** — an interior temperature or the conductive heat flux — as a new
  registration.
- **Next fix:** new registration gating on the **interior side-wall temperature at a
  cell centre or the conductive heat flux** (a RESULT, not a BC); source
  `/usr/lib/openfoam/openfoam2606/tutorials/heatTransfer/chtMultiRegionFoam`;
  manual p.185 (choose the side-wall temperature that is computed, not imposed).
- **Successor:** none named.

### VMFL063 — Separated laminar flow over a blunt plate · `GATE FAIL` · PC #2 (grid, GCI ≫ deviation)
Row takes the worse of two limbs. Limb A (continuum): LR/(2t)=5.600 at L3 vs target
4.0 = **40.0 % deviation** on a 10 % band, on a **CONVERGING** triple — but
**GCI_fine = 120.62 %** at Fs=1.25 (p=0.143, barely above the 0.05 floor). Limb B
(same-discrete-problem identity) PASS. **The discretisation uncertainty is ~3× the
deviation, so the numerics are NOT demonstrably right and a MODEL-FORM conclusion is
blocked** — this is grid, not model-form, despite the nominally CONVERGING state.
- **(a) bug — RO** (limb B identity PASS confirms reader integrity); **(b) solver —
  RO(weak):** laminar icoFoam/simpleFoam is appropriate; reattachment-length capture
  is a resolution question, not a solver-family one `[lean RO]`; **(c) precond — N/A.**
- **(d) numerics/scheme — NRO:** GCI 120 % says the grid is nowhere near converged —
  finer mesh + higher-order convection needed **before** the 40 % gap can be read as
  physics.
- **(e) config — NRO:** streamwise/separation-region resolution; refinement ratio.
- **Next fix:** refine the triple (finer, separation-region graded mesh) to bring
  GCI below the deviation; higher-order scheme (linearUpwind→linear). Source
  `/usr/lib/openfoam/openfoam2606/tutorials/incompressible/simpleFoam/pitzDaily`
  (separated-flow meshing); manual p.193.
- **Successor:** none named.

---

## NOTE-CASES (not deep-swept) — does GATE REACHED / PENDING count as a fail under Sanaa's bar?

- **VMFL002 — `GATE REACHED`:** **NOT a fail.** dP and outlet-T rise both inside 2 %
  at L3, both triples CONVERGING. The gate was **met**; GATE REACHED is a credential
  at the tier ceiling (analytical reference → the comparator does not print PASS), not
  a failure to recover.
- **VMFL021-R2 — `GATE REACHED`:** **NOT a fail** — it is the **recovery** of
  VMFL021 (Cd=0.634868, gate met). Confirms the cavitation capability.
- **VMFL023 — `GATE REACHED`:** **NOT a fail.** St=0.166 at L3, triple CONVERGING
  (p=1.914). Gate met at the permitted ceiling.
- **VMFL017-R2 — the task labels this PENDING; the register shows a split:** the
  **base VMFL017 is `PENDING`** (rhoSimpleFoam DIVERGES — FOAM FATAL; an explicit
  queue/not-yet-gradeable state, "NOT a softened GATE FAIL", CLAUDE.md rule 1) — the
  underlying divergence is **process class #3 (crash/divergence untriaged), the
  least-terminal class, a finding until triaged**. The **VMFL017-R2 row is
  `NOT A RESULT`** (per-level cap fired rc=124 + comparator refused strict completion;
  no gradeable value — **process class #1 completion, unrecoverability cannot be
  assessed**). **Neither PENDING nor this NOT A RESULT counts as a terminal fail
  under Sanaa's bar:** no physics was ever graded, so no capability judgement is
  possible; the fix is more compute / a converging transonic setup, not a proven gap.

---

## FILING NOTE

This is an operational compliance register (a durable, checkable rule-out sweep), not
a findings report, so a repository document is the correct form and it lives under the
team's owned `docs/ansys_verification/` (FILING_CHARTER). Reviewed and committed by the
supervisor under the CLAUDE.md rule-10 private-index protocol. Nothing here is filed,
sent or contacted upstream (rule 7); all research cited is inbound.
