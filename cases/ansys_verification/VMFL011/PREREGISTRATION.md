# PRE-REGISTRATION — VMFL011: Laminar Flow in a Triangular Cavity

Standard case, filed from `cases/ansys_verification/_template/PREREGISTRATION_TEMPLATE.md`.
Frozen by sha before any solver starts (rule 2). Drafted by `ansys-lane-opus48`
(Opus 4.8), 2026-08-26. The case build (grader, mesh, run script, reference CSV) was
left by a prior dead lane; this lane verified it sound (smoke below), applied the
supervisor's setsid detachment fix to the launcher, and froze it.

1. **Case id + manual page:** VMFL011, VM2026R1 p. 41 (title-page verified).

2. **Reference value + unit + source:** the normalized x-velocity profile
   `u_x/U_wall` along the vertical line that bisects the base of the triangular
   cavity (manual Figure .11.2). Source: **R. Jyotsna & S.P. Vanka, "Multigrid
   Calculation of Steady, Viscous Flow in a Triangular Cavity", J. Comp. Phys. 122,
   107-117 (1995)** — the manual's cited Reference. The manual p.42 prints this only
   as a FIGURE with NO discrete target table, so the benchmark curve is carried as a
   55-row digitised CSV (`reference/vmfl011_benchmark_xnorm.csv`, blob
   `9f11191b8c823eb32edd3f2b74bd29da855aab55`, provenance stated in its header). The
   benchmark's characteristic functional is its recirculation minimum
   **u_min/U_wall = -0.318062 at y = -0.987 m**.

3. **Reference CATEGORY (Sanaa 2026-08-25):** **NEITHER V nor P** — the reference is
   ANOTHER CODE's numerical solution (Jyotsna-Vanka multigrid), i.e. code-to-code
   agreement, doubly indirect here because it is digitised from a figure. Matching it
   is neither exact-analytic verification (V) nor experimental validation (P).

4. **Ansys's own reported value (context only, NEVER the gate):** none to quote — the
   manual overlays the Fluent/CFX profiles on the benchmark curve as figures
   (.11.2 / .11.3); no scalar Ansys value is printed.

5. **GATE expression + tolerance:** at the finest level (L3),
   `rms_vs_benchmark = RMS over the 55 benchmark abscissae of (u_lab/U_wall −
   u_bench/U_wall) ≤ 0.030` (3 % of the moving-wall speed). Band justified a priori,
   not from a run: the reference is a plot digitisation, whose reading error on a
   figure of this size is ~1-3 % of full scale, and the Jyotsna-Vanka curve carries
   its own multigrid discretisation; 3 % covers the digitisation floor plus a modest
   solver-vs-benchmark margin, and is consistent with the manual's figure-agreement
   class. It is a real gate: a wrong Reynolds number, a wrong moving-wall speed or an
   under-resolved recirculation would push the RMS past 3 %.

6. **Level family (grid triple — 3 levels):** base cells NB AND height cells NH
   refined together by ratio **r = 2**: L1 NB=20 NH=40 (800 cells); L2 40×80
   (3 200); L3 80×160 (12 800). Solver `simpleFoam` (steady incompressible laminar),
   ν = μ/ρ = 0.01 m²/s (ρ=1, μ=0.01; manual p.41), Re = U_wall·base/ν = 2·2/0.01 =
   400. Triangular cavity: base width 2 m (x: −1→1, the `movingWall` at y=0 with
   U=(2,0,0)), apex at (0,−4,0) (height 4 m), `sideWalls` noSlip, front/back `empty`.
   The apex is a COLLAPSED-hex block (two coincident vertices genuinely merged, not
   two separate coincident vertices — the latter leaves 20 zero-area faces that
   SIGFPE-killed a prior smoke; the current mesh is the fix). NB is EVEN at every
   level so the bisector x=0 is a cell-face plane identically placed under refinement.
   endTime = 20000 SIMPLE iterations.

   **CONVERGENCE CHANNEL, and why it is NOT rms_vs_benchmark (rule 5 step 2 guard):**
   the Roache triple runs on **u_min/U_wall** — a self-converging FUNCTIONAL of the
   lab solution — NOT on the deviation from the benchmark, because the digitised
   benchmark has a noise floor: rms_vs_benchmark would plateau at that floor and read
   STAGNANT even for a perfectly converging solver. u_min converges toward the true
   triangular-cavity recirculation strength; the triple must be `CONVERGING`.

7. **CAP in core-minutes + cost_basis:** cap **50 core-min total** (running-total
   drawdown; overrun STOPS the run, rule 12; the cap is a RUNAWAY GUARD — a crossing
   is reported to the supervisor who may extend by dated amendment if sound). Estimate
   from a MEASURED pre-freeze smoke on this box (2026-08-26): L3 (12 800 cells) ran a
   500-iteration burst in 59 s = 118 ms/iter, so 20 000 iterations ≈ 2 360 s = 39.3
   core-min at ranks=1 — the cap ADMITS the registered endTime at every level (L1/L2
   are far cheaper). Per-level wall `timeout = remaining × 60 / RANKS`, RANKS=1. Rate
   **$0.0513/core-h (c7a.4xlarge), REPORTED-BY-OWNER, NOT MEASURED** (the box cannot
   read its own billing; dollars DERIVED). Under the 2026-08-21 <$25 blanket, costed
   per item.

8. **Comparator path + sha:** `cases/ansys_verification/VMFL011/grade_vmfl011.py`,
   blob **`e369496bf2e28ccb7145756e1c2442eb11e8e3f7`**. Controls, all non-droppable
   and NONE on an `assert` (python3 -O strips asserts): planted-zero on BOTH channels
   (rms_vs_benchmark and u_min), plant 1.234e-3, read back from disk, REFUSE via
   `sys.exit(2)` if unseen (rule 3); strict completion incl. age guard (rule 4);
   Roache on u_min (rule 5). `--selftest` = 16/16, exit 0, IDENTICAL under `python3`
   and `python3 -O`. Mutation test `mutation_test_vmfl011.py` (blob
   `7feddc844f5b3613c672168fe9db3a4ceb266ad7`): 6/6, exit 0 under both interpreters —
   a defanged refusal FAILS the selftest under both, proving controls are real and
   interpreter-invariant. Launcher `run_vmfl011.sh` (blob
   `17f8bd4b452dccbc3291700e6f9633eb4e6bf636`) carries the launch-time freeze check
   and, per the 2026-08-26 supervisor course-correction, launches each level as
   `setsid timeout … simpleFoam &` and asserts (by shell conditional, not `assert`)
   the wrapper's SID == its own PID.

9. **TIER CEILING declared in advance + reason:** **GATE REACHED**. The reference is
   another code's numerical solution (code-to-code, digitised): it buys NEITHER V nor
   P, so this row cannot reach PASS however good the number. Fallbacks: u_min triple
   `EXACT`/`STAGNANT`/`OSCILLATORY`/`DIVERGENT` → **NOT A RESULT**; `CONVERGING` but
   rms_vs_benchmark > 3 % → **GATE FAIL**.

10. **FALSIFICATION clause (named before the run):**
    - **A `GATE FAIL` is a real possible outcome:** the RMS against the digitised
      benchmark exceeding 3 % — from a wrong Re, wrong wall speed, or an
      under-resolved corner recirculation.
    - **A `NOT A RESULT` is a real possible outcome:** the u_min triple failing to be
      `CONVERGING` — e.g. STAGNANT if u_min plateaus below the mesh's ability to
      resolve the apex recirculation, or OSCILLATORY on a non-monotone corner vortex.
    - **Degenerate-residual guard (lesson from VMFL004, same session):** unlike a 1-D
      fully-developed flow, this cavity is genuinely 2-D, so Uy and p are real
      non-degenerate fields; a MEASURED pre-freeze convergence check (L1, 3 000 iters)
      drove all three initial residuals to Ux 6.6e-14 / Uy 1.2e-13 / p 8.9e-13, far
      below the frozen 1e-7 floor — so the iterative-convergence check will not
      spuriously block this case as it does a degenerate 1-D flow.
    - **Strict completion applies UNMODIFIED (no departure, no substitute conjunct):**
      rc=0; an `End` line in `log.simpleFoam`; last time == endTime (20000); U and p
      present at 20000; ExecutionTime count == 20000; every field at 20000 strictly
      newer than the case's own `0/` (age guard).

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*

**Smoke disclosure (before this freeze, no graded number, nothing under
verification/runs/):** on 2026-08-26 in scratch, L1 (800 cells) and an L3-sized mesh
(12 800 cells) both ran under OpenFOAM v2606 with FOAM_SIGFPE trapping ENABLED and
did NOT trip — rc=0, the bisector set sampled, residuals converging. This exercised
the CASE (a `--selftest` proves the grader, never the case); it did not set any band.
