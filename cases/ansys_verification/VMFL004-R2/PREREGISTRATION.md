# PRE-REGISTRATION — VMFL004-R2: Plain Couette Flow with Pressure Gradient (re-run of VMFL004)

Bespoke frozen document (the convergence-channel change is argued at length, so this is a
contested case, not a template-speed one). Frozen by sha before any solver starts (rule 2).
Drafted by `ansys-lane-opus48` (Opus 4.8), 2026-08-26.

**This is a re-run of VMFL004 (validation register row #25, verdict `NOT A RESULT`) under
`ANSYS_VERIFICATION_CHARTER` §6 — "a re-run after a repair is a new row citing the old one."
VMFL004's frozen comparator is NOT edited (rule 2); this is a NEW frozen file and a NEW
register row citing #25.**

---

## 0. THE HAZARD THIS DOCUMENT MUST NOT WALK INTO, AND HOW IT DOES NOT

**We already know VMFL004's answer.** Its physics was a textbook PASS: `volAverage(U)_x` =
2.50125 / 2.5003125 / 2.5000781 across L1/L2/L3 against the exact section mean 2.5 m/s, triple
`CONVERGING`, observed order p = 1.99999997, GCI_fine 3.9e-5, relative deviation 3.1e-5 against
a 0.1 % band. It was graded `NOT A RESULT` for one reason only: an inherited
iterative-convergence check demanded the transverse Uy and p residuals fall below 1e-7, which
they physically cannot in this flow.

A re-registration written after seeing that answer, whose gate we already know will pass, would
be **gate-fitting dressed as an R2**, and it would destroy the credential rather than earn it.
This document defends against exactly that in the only way that works:

> **The gate quantity, the reference value, the tolerance band and the tier ceiling are
> CARRIED OVER BYTE-IDENTICAL from VMFL004. They are NOT re-chosen, NOT loosened, NOT
> re-derived. The prior run's value is known to be a PASS, and precisely because of that the
> band, the gate quantity and the reference are held fixed — a gate that is not touched cannot
> have been shaped by the answer.**

The **only** thing that changes is the iterative-convergence channel, and that change is
justified below **on the physics of a 1-D fully-developed flow alone** — an argument that would
stand identically had the answer come out a `GATE FAIL`. That is the test of whether the change
is honest, and it passes it.

---

## 1. Case id + manual page

**VMFL004-R2**, VM2026R1 **p. 21** (title-page verified against the PDF beside the sidecar:
"Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026"). Cites register **row
#25 (VMFL004)**.

## 2. Reference value + unit + source (CARRIED OVER BYTE-IDENTICAL FROM VMFL004)

Section-mean x-velocity **⟨u⟩ = 2.5 m/s, EXACT**. Plane Couette flow with a pressure gradient
between a fixed wall (y=0) and a wall moving at U=3 m/s (y=1 m), dp/dx = −12 Pa/m, ρ=1 kg/m³,
μ=1 kg/m·s (all manual p. 21). Closed form (Munson, Okiishi & Huebsch, *Fundamentals of Fluid
Mechanics*, 5th ed., Wiley 2006 — the manual's own cited Reference):
`u(y) = U·y/b + (1/(2μ))(dp/dx)(y²−by) = 9y − 6y²`, peak 3.375 m/s at y=0.75. The lab evaluates
the section mean itself: `⟨u⟩ = ∫₀¹ (9y − 6y²) dy = 4.5 − 2 = 2.5 m/s`, exact. The manual prints
only Figure .04.2 (an x-velocity profile at x=0.75 m) and no discrete target table, so the gate
is against this lab-evaluated closed-form mean, not against any manual number.

## 3. Reference CATEGORY (CARRIED OVER)

**V** (exact/analytic, lab-evaluated) — a code-verification credential, never physical
validation (P). Per the VMFL019 precedent (closed form, figure-only manual → verdict `PASS`) a
category-V case can still earn a rule-1 verdict of `PASS`; the V/P axis is orthogonal to the
PASS/GATE-REACHED axis.

## 4. Ansys's own reported value (context only, NEVER the gate)

None to quote — the manual publishes Fluent/CFX x-velocity as figures overlaid on the analytic
curve (Figs .04.2 / .04.3); there is no scalar Ansys value in the text.

## 5. GATE expression + tolerance (CARRIED OVER BYTE-IDENTICAL FROM VMFL004)

At the finest level (L3), **`|volAverage(U)_x − 2.5| / 2.5 ≤ 1.0e-3` (0.1 %)**. Band unchanged
from VMFL004: (a) it matches the manual's own agreement class for the neighbouring laminar
cases (VMFL002 ratio 0.999 = 0.1 %); (b) the a-priori O(h²) estimate of the cell-midpoint
quadrature error of the mean, `⟨u⟩_h − 2.5 = h_y²/2`, gives 3.13e-4 / 7.8e-5 / 1.95e-5 at
L1/L2/L3 — even the coarse grid sits an order inside the band, so a fine-grid failure would
signal a real defect. **This band is set a priori exactly as in VMFL004; it is not re-derived
here and it is not loosened.** The triple must be `CONVERGING` (rule 5). **I may not loosen this
band, change the gate quantity, or change the reference, and I have not.**

## 6. Level family (grid triple — 3 levels) — CARRIED OVER

x AND y refined together by ratio **r = 2**. L1 (NX,NY) = (15, 40); L2 (30, 80); L3 (60, 160);
z is 1 empty cell. Solver `simpleFoam` (steady incompressible laminar), ν = μ/ρ = 1 m²/s. Domain
1.5 m (x, cyclic `left`↔`right`) × 1.0 m (y: `movingWall` at y=1 fixedValue (3,0,0); `fixedWall`
at y=0 noSlip) × 0.1 m (z, `empty`). dp/dx = −12 Pa/m imposed as the kinematic body force
+12 m/s² via `fvOptions` (`vectorSemiImplicitSource`, `volumeMode specific` → identical per-cell
source at every level). The gate quantity ⟨u⟩ depends on the y-resolution; refining y by 2
quarters the quadrature error, so the three values are monotone from above, giving `CONVERGING`
with observed order p → 2. **The case files (`case/`) are a byte-identical copy of VMFL004's
`case/` — verified file-by-file. The physics run is identical; only the grader's convergence
channel differs.**

## 7. THE ONLY CHANGE — the iterative-convergence channel, argued on physics alone

VMFL004's frozen `iterative_convergence` required the final initial residuals of **Ux, Uy AND
p** all below a **1e-7** floor. VMFL004-R2 gates iterative convergence on the **driven channel
`Ux_initial` only**, and replaces the transverse floor with an explicit, physics-based
degeneracy-and-boundedness test. Here is the full argument, and it does not depend on what the
answer turned out to be.

### 7.1 Why the transverse residuals are noise, not a convergence signal

This flow is **1-D and fully developed**: streamwise-cyclic in x, driven by a spatially uniform
body force, with the solution `u = u(y)` a function of y alone. The exact fields are therefore:

- **Ux = 9y − 6y²** — the one field with real structure; the momentum equation actually solves it.
- **Uy ≡ 0 everywhere** — there is no transverse physics; the wall-normal velocity is identically
  zero in the exact solution and stays at machine-noise level (O(1e-15)) in the discrete one.
- **p spatially uniform** — the driving is a body force, not a resolved pressure gradient, so the
  pressure field carries no spatial structure; the pressure equation solves a near-null field.

OpenFOAM normalises each equation's residual by that field's **own scale** (a norm of the field
and its diagonal). For a field that is structurally ~zero — Uy and p here — the normalisation
**denominator is ~zero**, so the reported *normalised* "initial residual" is a ratio of two tiny
numbers: it floats at **O(1e-2 .. 1e-1)** and **cannot fall below an absolute floor no matter how
long the solver runs**. It is not a measure of convergence; it is normalisation noise. (This is
the same mechanism `docs/LESSONS.md` L-338 records from VMFL004's own run: at endTime
Ux_initial ≈ 1e-15 while Uy_initial ≈ 9.5e-2 and p_initial ≈ 4.2e-2, and the transverse channels
*bounce* rather than descend.)

Gating iterative convergence on a residual that is structurally incapable of reaching the floor
is a category error — it grades the normalisation of a null field, not the convergence of the
solve. **The driven channel `Ux_initial` is the only residual that measures whether the flow's
actual physics has converged**, and in a correct solve it descends to machine precision
(VMFL004: ~1e-15 ≪ 1e-7).

**This argument is answer-independent.** It rests entirely on the structure of a 1-D
fully-developed flow — the degeneracy of Uy and p — and would be written identically whether the
run ended a PASS or a GATE FAIL. It is not a description of what happened; it is a statement about
what these residuals *are*.

### 7.2 The exemption is NOT a deletion — the transverse criterion, registered explicitly

A channel exempted from the floor without a stated failure criterion is a channel deleted.
It is not deleted here. The transverse channels are still read, recorded, and tested — against
the criterion that is physically meaningful for a degenerate field, with the failing values named
**before** the run:

**(a) Transverse mean-velocity degeneracy — the primary real-failure test.**
`|volAverage(U)_y| ≤ 1e-6 m/s` AND `|volAverage(U)_z| ≤ 1e-6 m/s`. This tests the *premise* of the
exemption: that Uy and p are actually degenerate. The streamwise scale is O(1) m/s (⟨u⟩ = 2.5,
peak 3.375); a converged 1-D solve has ⟨U⟩_y at machine level (VMFL004 measured −6.55e-17), so the
1e-6 m/s ceiling sits ~9–11 orders above the expected value and cannot be tripped by noise.
**What WOULD trip it, and would then be a REAL failure → `NOT A RESULT`:** a transverse mean
velocity above 1e-6 m/s means the field is *not* degenerate — a broken streamwise-cyclic pair
that fails to enforce fully-developed flow, spurious cross-flow, or a genuinely non-1-D solution.
In that case the residual is *not* noise and exempting it would be wrong; the excess IS the
failure, and the case is `NOT A RESULT`. This is the answer to "what value constitutes a real
failure in the transverse channel": **|⟨U⟩_y| or |⟨U⟩_z| > 1e-6 m/s.**

**(b) Transverse residual boundedness — a divergence guard.**
The transverse normalised residuals (`Uy_initial`, `p_initial`) must stay **< 1.0** at endTime.
Bounded normalisation noise floats at O(1e-2) (a normalised residual starts at O(1) at iteration 1
and, for a bounded field, stays at or below its own scale). **A value ≥ 1.0 at endTime means the
field is growing faster than its own scale — divergence, a real failure → `NOT A RESULT`.** This
is complementary to (a): the mean in (a) could stay ~0 by antisymmetry even while a field grows,
so the residual ceiling catches a divergence that the mean would miss. The ceiling 1.0 is a
natural O(1) scale, not a value fitted to VMFL004's measured 9.5e-2 / 4.2e-2 (which sit an order
below it).

**Net:** the transverse channel is not gated on an impossible floor, and it is not deleted. It is
gated on the two things that are physically meaningful for a degenerate field — *is it actually
degenerate*, and *is it bounded* — with the failing values named in advance.

## 8. Controls carried in the comparator (all non-droppable, NONE on an `assert`)

`cases/ansys_verification/VMFL004-R2/grade_vmfl004_r2.py`. `python3 -O` strips `assert`, so no
`assert` carries any refusal, guard, control or gate (verified: `grep -nE '^\s*assert\s'` is
empty); every refusal is `sys.exit(2)` or `raise`.

- **Planted-zero (rule 3), on EVERY reader the verdict consumes.** A zero from a reader not shown
  able to see a non-zero is not evidence. Four planted controls, each planting **1.234e-3** into a
  COPY on disk, reading it back with the SAME reader, and **REFUSING via `sys.exit(2)`** if the
  reader cannot see it: (1) the gate reader `volavg_ux_ms` (Ux of the volAverage row); (2) the
  transverse reader `volavg_uy_ms`; (3) `volavg_uz_ms`; (4) the **driven-convergence reader
  `Ux_initial`** in `solverInfo.dat` — this last one closes a latent rule-3 gap in VMFL004's
  inherited grader, whose convergence check had no planted control, so a blind reader returning 0.0
  would have trivially "passed" `Ux_initial < 1e-7`.
  **Plant calibration (L-340), stated explicitly:** every plant is a **SINGLE-POINT plant into a
  SINGLE-POINT reader** — one component of one row, or one column of one row — **NOT an averaging
  (RMS/mean over N points) reader**, so there is no 1/√N dilution and the reader delta equals the
  plant exactly (the defect that cost this team VMFL011). Verified in the selftest: each of the
  four readers moves by exactly 1.234e-3.

- **Strict completion (rule 4), every clause, WRITTEN OUT IN FULL (not cited by name):** a level is
  complete only if ALL of — (i) `rc = 0`, parsed TOLERANTLY as `^\s*rc\s*=\s*(-?\d+)` so the
  launcher's `rc = 0` (with spaces) is read and an unparseable rc is a REFUSAL not a pass
  (Amendment 5); (ii) an `\nEnd\n` line in `log.simpleFoam` **by exact filename** (a `log*` glob
  matches `log.blockMesh` first and would read the mesher's End line); (iii) **last time == endTime
  (20000)**; (iv) fields **`U` and `p` present** at the endTime directory; (v) **`ExecutionTime`
  count == endTime (20000)**; (vi) the **AGE GUARD** — every field at endTime **strictly newer than
  the case's own `0/`**, because `0/` is touched last at launch and so dates the run allowed to
  produce the answer. The comparator REFUSES (exit 2) rather than degrading. The launcher's own age
  guard additionally REFUSES before compute if `0/` or any time directory (matched by regex
  `^[0-9]+(\.[0-9]+)?$`, never a `[0-9]*` glob that matches `0.orig`) already exists.

- **Roache triple gating (rule 5), Fs = 1.25.** Any level not iteratively converged (driven
  channel) or transverse-degeneracy-failed → `NOT A RESULT`; a triple that is `EXACT` / `STAGNANT`
  / `OSCILLATORY` / `DIVERGENT` → `NOT A RESULT` with the value and both orders printed; only a
  `CONVERGING` triple is graded against the band. The gate can only turn a PASS or GATE FAIL INTO
  `NOT A RESULT`, never the reverse. No GCI is quoted when the three values are not monotone.

- **Plateau/settling clause (Amendment 4):** this is a STEADY simpleFoam run graded on the single
  converged field written at endTime; settling is proven by the **driven-channel residual floor**
  (`Ux_initial < 1e-7`), not by a time-window average, so there is no fractional-window
  minimum-sample exposure. This is the identical structure VMFL004 used and the supervisor accepted.

- **Comparator selftest:** `--selftest` = **30/30, exit 0, IDENTICAL under `python3` and
  `python3 -O`**. **Mutation test** `mutation_test_vmfl004_r2.py`: breaks THREE controls on
  sacrificial copies — the planted-zero refusal, the `transverse_degeneracy` real-failure detector,
  and the driven-convergence gate — and confirms `--selftest` exits NON-ZERO with no full-pass tally
  under BOTH interpreters (**12/12, exit 0 under both**), proving each control is real and
  interpreter-invariant.

## 9. Launcher (`run_vmfl004_r2.sh`) — required artifacts

Carries: launch-time freeze verification of the prereg AND the comparator against HEAD (each
gating with `|| { echo ABORT...; exit 1; }`, shas into `LAUNCH_RECORD.txt`); cap enforcement in
the executable path by `timeout_s = remaining_core_min × 60 / RANKS` with running core-minute
accounting that REFUSES at zero; **no `set -u`** (the v2606 bashrc cycle, reason in the header);
the planted-zero control (in the comparator); the mesh birth certificate (from checkMesh);
`RUN_RC.txt` on BOTH the success and abort paths including the timeout-fired rc=124. **Detached
solver:** `exec setsid timeout … simpleFoam &` then `wait`, with detachment VERIFIED by asserting
(shell conditional, not `assert`) the wrapper's **SID == its own PID** (field 6 of
`/proc/<pid>/stat`), never by the solver's ppid. A pre-flight **smoke** mode exercises the launcher
end-to-end at a tiny endTime and grades nothing.

## 10. CAP in core-minutes + cost_basis

Cap **30 core-min total** across all three levels (running-total drawdown; an overrun STOPS the run
and does NOT get a new budget, rule 12; the cap is also a runaway guard reported to the supervisor).
Estimate: VMFL004 measured **11.4 core-min** total for the identical run (L1 0.35 + L2 1.667 +
L3 9.4; ranks = 1) — this run is byte-identical physics so **~11.4 core-min is the honest estimate**,
well inside the 30 cap. RANKS = 1, so the wall timeout IS the core-minute cap. Rate **$0.0513/core-h
(c7a.4xlarge), REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing
(COMPUTE_BUDGET_CHARTER §5); dollars are DERIVED. Under the 2026-08-21 blanket (<$25 pre-authorised)
and still costed per item.

## 11. Grading path (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL004-R2/grade_vmfl004_r2.py --run-root
verification/runs/ansys_verification/VMFL004-R2`. The launcher re-proves at launch that the prereg
and comparator on disk hash equal to HEAD, and records the shas in `LAUNCH_RECORD.txt`; the grader's
`--verify-frozen <sha>` re-hashes itself against the committed blob.

## 12. FALSIFICATION clause (named before the run so the gate cannot be fit to the answer)

- **The EXACT-collapse risk, named (carried over from VMFL004).** Central differencing
  (`Gauss linear`) is exact for a quadratic, so the discrete cell-centre velocity equals
  `u(y)=9y−6y²` at every node regardless of mesh. Had the gate been a nodal/pointwise quantity, the
  three levels would be byte-identical and the triple would read `EXACT` → `NOT A RESULT`. The gate
  DODGES this by grading the `volAverage`, whose cell-midpoint-quadrature error is O(h²) and
  non-zero → `CONVERGING`. Residual risk: if that quadrature signal (down to ~2e-5) fell below the
  written field precision, the triple would read `EXACT`/`STAGNANT` → `NOT A RESULT`, an honest
  predicted outcome mitigated by `writePrecision 12`.
- **A `GATE FAIL` is a real possible outcome:** a wrong body-force magnitude (source ≠ 12 m/s²), a
  cyclic pair not enforcing fully-developed flow, or the driven channel `Ux_initial` failing to
  reach 1e-7 would each drive `volAverage(U)_x` off 2.5 m/s beyond 0.1 %, OR trip the transverse
  degeneracy test (a broken cyclic showing ⟨U⟩_y > 1e-6 m/s). **The convergence-channel change does
  NOT remove the possibility of failure — it relocates it from an impossible floor to a physically
  real one.**
- **The predicted PASS is not a promise.** The physics of VMFL004 supports a PASS, and this run
  reproduces that physics. But the freeze is committed before this run's numbers exist; if this run's
  triple is not `CONVERGING`, or its fine grid is outside the 0.1 % band, or its driven channel does
  not converge, or its transverse field is not degenerate, the honest verdict is recorded, unsoftened.

**A note on the choice to re-register at all.** I considered whether the honest move is to leave
VMFL004 standing as `NOT A RESULT`. It is not: the block was a category error in an inherited
control, not a genuine ambiguity about the physics, and the fix is argued on the structure of the
flow independently of the answer. Carrying the gate over byte-identical is what lets the
re-registration earn the credential instead of fitting it. **I judge re-registering to be honest,
and proceed.**

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*
