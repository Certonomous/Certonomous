# PRE-REGISTRATION — VMFL004: Plain Couette Flow with Pressure Gradient

Standard case, filed from `cases/ansys_verification/_template/PREREGISTRATION_TEMPLATE.md`.
Frozen by sha before any solver starts (rule 2). Drafted by `ansys-lane-opus48`
(Opus 4.8), 2026-08-26, on the supervisor's Ruling 2 of the same day.

1. **Case id + manual page:** VMFL004, VM2026R1 p. 21 (title-page verified: "Ansys
   Fluid Dynamics Verification Manual, Release 2026 R1, March 2026").

2. **Reference value + unit + source:** section-mean x-velocity
   **⟨u⟩ = 2.5 m/s, EXACT**. Plane Couette flow with a pressure gradient between a
   fixed wall (y=0) and a wall moving at U=3 m/s (y=1 m), with dp/dx = −12 Pa/m,
   ρ=1 kg/m³, μ=1 kg/m·s (all manual p.21). The closed form (Munson, Okiishi &
   Huebsch, *Fundamentals of Fluid Mechanics*, 5th ed., Wiley 2006 — the manual's
   own cited Reference) is `u(y) = U·y/b + (1/(2μ))(dp/dx)(y²−by) = 9y − 6y²`, peak
   3.375 m/s at y=0.75. The lab evaluates the section mean ITSELF:
   `⟨u⟩ = ∫₀¹ (9y − 6y²) dy = 4.5 − 2 = 2.5 m/s`, exact. The manual prints only
   **Figure .04.2** (an x-velocity profile at x=0.75 m) and NO discrete target
   table, so the gate is against this lab-evaluated closed-form mean, not against
   any manual number.

3. **Reference CATEGORY (Sanaa 2026-08-25):** **V** (exact/analytic, lab-evaluated).
   This is a code-verification credential, never physical-validation (P). Per the
   VMFL019 precedent (closed form, figure-only manual) a category-V case can still
   earn a rule-1 verdict of **PASS** — the V/P axis (credibility category) is
   orthogonal to the PASS/GATE-REACHED axis (verdict). Verified against the record:
   `cases/ansys_verification/VMFL019/RESULTS.md` VERDICT = `PASS`.

4. **Ansys's own reported value (context only, NEVER the gate):** none to quote —
   the manual publishes the Fluent/CFX x-velocity as figures overlaid on the
   analytic curve (Figs .04.2 / .04.3); there is no scalar Ansys value in the text.

5. **GATE expression + tolerance:** at the finest level (L3),
   `|volAverage(U)_x − 2.5| / 2.5 ≤ 1.0e-3` (0.1 %). The band is set a priori, not
   from a run: (a) it matches the manual's own agreement class for the neighbouring
   laminar cases (VMFL002 ratio 0.999 = 0.1 %); (b) the a-priori O(h²) estimate of
   the cell-midpoint-quadrature error of the mean, `⟨u⟩_h − 2.5 = h_y²/2`, gives
   3.13e-4 / 7.8e-5 / 1.95e-5 at L1/L2/L3 (relative 1.25e-4 / 3.1e-5 / 7.8e-6) — even
   the COARSE grid sits an order inside the band, so a fine-grid failure would signal
   a real defect, which is exactly what the gate must catch. It is tighter than
   VMFL019's 1 % and stays a priori. The triple must be `CONVERGING` (rule 5).

6. **Level family (grid triple — 3 levels):** x AND y refined together by ratio
   **r = 2**. L1 (NX,NY) = (15, 40); L2 (30, 80); L3 (60, 160); z is 1 empty cell.
   Solver `simpleFoam` (steady incompressible laminar), ν = μ/ρ = 1 m²/s. Domain
   1.5 m (x, cyclic `left`↔`right` — the manual's "periodic boundaries") × 1.0 m (y:
   `movingWall` at y=1 fixedValue (3,0,0); `fixedWall` at y=0 noSlip) × 0.1 m (z,
   `empty`). The pressure gradient dp/dx = −12 Pa/m is imposed as the equivalent
   KINEMATIC body force −(1/ρ)dp/dx = +12 m/s² via `fvOptions`
   (`vectorSemiImplicitSource`, `volumeMode specific` → identical per-cell source at
   every level, mesh-independent by construction). The gate quantity ⟨u⟩ depends on
   the y-resolution; refining y by 2 halves h_y and quarters the quadrature error, so
   the three values are monotone from above (2.5+3.13e-4 → 2.5+7.8e-5 → 2.5+1.95e-5),
   giving `CONVERGING` with observed order p → 2.

7. **CAP in core-minutes + cost_basis:** cap **30 core-min total** across all three
   levels (running-total drawdown; an overrun STOPS the run and does NOT get a new
   budget, rule 12 — the cap is also a RUNAWAY GUARD: a crossing is reported to the
   supervisor, who may extend by dated amendment if the work is sound). Estimate:
   clean solve ~2–3 core-min total (600 / 2400 / 9600 cells × 20000 steady
   iterations); slack ×~10 taken for the box's ~13–15 loadavg contention tonight.
   Per-level wall `timeout = remaining × 60 / RANKS`, RANKS = 1, so the wall timeout
   IS the core-minute cap. Rate **$0.0513/core-h (c7a.4xlarge), REPORTED-BY-OWNER,
   NOT MEASURED** — the box cannot read its own billing (COMPUTE_BUDGET_CHARTER §5);
   dollars are DERIVED. Under the 2026-08-21 blanket (<$25 pre-authorised) and still
   costed per item.

8. **Comparator path + sha:** `cases/ansys_verification/VMFL004/grade_vmfl004.py`,
   blob **`ddea9d473b6d6092427d29c5997c25af956a7fb6`** (frozen at this commit). It
   carries, all non-droppable and NONE on an `assert` (python3 -O strips asserts):
   the planted-zero control (plant 1.234e-3 m/s into the Ux component of the
   volAverage row on disk, read back, REFUSE via `sys.exit(2)` if the reader cannot
   see it — rule 3); strict completion, every clause incl. the age guard (rule 4);
   Roache triple gating at Fs=1.25 (rule 5). `--selftest` = **19/19, exit 0**,
   IDENTICAL under `python3` and `python3 -O`. The mutation test
   `mutation_test_vmfl004.py` (blob `d672a3845f02229188bcf118846d66ef819e7fa8`)
   confirms a defanged refusal FAILS the selftest under BOTH interpreters (6/6,
   exit 0 under both) — proving the controls are real and interpreter-invariant.

9. **TIER CEILING declared in advance + reason:** **HOLDS** (rule-1 verdict `PASS`
   reachable). The reference is an exact closed form the lab evaluates itself; per
   supervisor Ruling 2 and the VMFL019 precedent, that carries a PASS/HOLDS ceiling,
   not a GATE-REACHED cap. Fallbacks declared: if the grid triple reads
   `EXACT`/`STAGNANT`/`OSCILLATORY`/`DIVERGENT` → **NOT A RESULT** (tier NOT HELD);
   if `CONVERGING` but the fine grid is outside the 0.1 % band → **GATE FAIL**.

10. **FALSIFICATION clause (named before the run so the gate cannot be fit to the
    answer):**
    - **The EXACT-collapse risk, named explicitly.** Central differencing (`Gauss
      linear`) is exact for a quadratic, so the discrete cell-centre velocity equals
      `u(y)=9y−6y²` at every node regardless of mesh. Had the gate been a NODAL /
      pointwise quantity (e.g. a cell-centre velocity), the three levels would be
      byte-identical and the triple would read **`EXACT` → `NOT A RESULT`** under
      rule 5 step 2. The gate DODGES this by grading the `volAverage`, whose
      cell-midpoint-quadrature error of the quadratic is O(h²) and non-zero, so the
      triple is expected `CONVERGING`. RESIDUAL risk, also named: if that quadrature
      signal (down to ~2e-5) fell below the written field precision, the triple
      would read `EXACT`/`STAGNANT` → **NOT A RESULT** — an honest, PREDICTED
      outcome, mitigated by `writePrecision 12`. If it fires, the row is NOT A
      RESULT that was called in advance, worth more than a fitted pass.
    - **A `GATE FAIL` is a real possible outcome:** a wrong body-force magnitude
      (source ≠ 12 m/s²), a cyclic pair not enforcing fully-developed flow, or
      iterative non-convergence (final initial residual above the frozen 1e-7 floor)
      would each drive `volAverage(U)_x` off 2.5 m/s beyond 0.1 %.
    - **Strict completion applies UNMODIFIED (no departure, no substitute conjunct):**
      rc = 0; an `End` line in `log.simpleFoam`; last time == endTime (20000);
      fields `U` and `p` present at 20000; ExecutionTime count == 20000; every field
      at 20000 strictly newer than the case's own `0/` (age guard). The steadyState
      run writes one field set at endTime; there is no adaptive-dt or transient
      substitution.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*

**Build note (not part of the frozen gate):** the `0/U` and `0/p` field files written
by a prior dead lane at 2026-08-25 03:10Z used patch names `inlet/outlet/topWall/
bottomWall`, which do NOT exist in `blockMeshDict` (`left/right/movingWall/fixedWall`);
`simpleFoam` would have aborted on the mismatch. `ansys-lane-opus48` reconciled the
field patch names to the mesh on 2026-08-26 (movingWall = top U=3 fixedValue;
fixedWall = bottom noSlip; left/right = streamwise cyclic; frontAndBack = empty).
No gate quantity, threshold, cap or label depends on this; it is a build repair.
