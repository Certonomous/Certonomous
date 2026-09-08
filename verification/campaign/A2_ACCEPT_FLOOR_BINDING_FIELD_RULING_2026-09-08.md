# RULING — A2 D6RF convergence: `p_first_uncorrected` IS the binding field; GATE FAIL / not-converged STANDS

**Ruled by:** verification-supervisor (V&V / N-family authority, `VERIFICATION_CHARTER.md` §2, `CLAUDE.md` rule 5).
**Date:** 2026-09-08. **HEAD at ruling:** 907e99ac.
**Routed by:** chief (dafoam referral). **Blocks:** the mandatory D6R2 transonic-multipoint chain's gating question.
**Cost:** 0 solver core-min, $0.00 (a determination on existing law + a source read; no compute).

---

## The question referred

In the A2 `D6RF` convergence gate (`G-CONV`), the pressure solve is split into two
per-iteration measures at the FINAL outer iteration:

- `p_first_uncorrected` = the initial residual of the FIRST (uncorrected) pressure
  solve in the outer iteration. **Measured 1.658293702e-05** (D6RF4 log :2107),
  **1.658× over the registered accept floor 1.0e-05 → fails.**
- `p_corrected` = the initial residual of the LAST (corrected) pressure solve in the
  same outer iteration. **Measured 6.337682167e-08** (log :2108), under floor → passes.
  *(the chief's paraphrase "1.05e-8" is close; the grader's recorded value is 6.34e-8.)*

Source of truth: `cases/dafoam/ladder-a/A2/curriculum_D6RF7/d6rf7_grade.py:367-378`,
`CONV_FIELDS` / `CONV_MEASURED_D6RF4`. The grader ALREADY declares
`p_first_uncorrected` the binding field. The referral asks whether that is a
defensible convergence criterion, or whether binding on `p_corrected` (which passes)
would be admissible.

## Ruling

**Binding convergence on `p_first_uncorrected` is CORRECT and DEFENSIBLE V&V. The
not-converged / GATE FAIL verdict on the binding field STANDS. Switching the binding
field to `p_corrected` is REFUSED.**

### Why — existing law, not a new standard

1. **Iterative-convergence law (rule 5, gating order condition (1)):** "any level not
   iteratively converged or not plateaued → NOT A RESULT." Iterative convergence of a
   steady SIMPLE-class solve (here `DARhoSimpleFoam`) is judged on the OUTER-loop
   residual — the INITIAL residual of each field at the start of each outer iteration.
   That residual is the equation residual assembled from the current solution BEFORE
   that iteration's linear solve corrects it; as the outer loop reaches steady state
   the field stops changing and the initial residual plateaus at its floor.

2. **`p_first_uncorrected` IS that outer-loop measure.** The first (uncorrected) pressure
   solve's initial residual at the final outer iteration is the continuity/coupling
   imbalance carried in from the momentum predictor — i.e. how far the coupled field is
   still moving between outer iterations. This is also exactly what DAFoam's own
   `primalMaxRes` convergence measure reads. At 1.658e-05 > 1.0e-05 the SIMPLE outer
   loop has NOT reached the registered acceptance bar.

3. **`p_corrected` measures the wrong thing for outer-loop convergence.** It is the
   residual of a LATER corrector WITHIN a single outer iteration; a small value there
   reflects only how tightly that iteration's pressure-correction linear system was
   solved to its stopping tolerance. It can be driven arbitrarily small regardless of
   whether the outer loop has converged, so it CANNOT establish steady-state iterative
   convergence. A pass on `p_corrected` is a statement about linear-solve tightness,
   not about the coupled solution being converged.

4. **This is an APPLICATION of existing law, not a new standard.** It follows directly
   from (i) rule 5's iterative-convergence gating order and (ii) standard steady-solver
   residual semantics already embedded in the N-family record (`docs/NUMERICS_KNOWLEDGE.md`:
   convergence judged "against the equation's own INITIAL residual read from the solver
   log"; the SIMPLE outer-loop rows). No new definition is minted, so this does NOT
   escalate to Sanaa as a novel standard.

### The T25 hard guardrail — what is REFUSED

The rule is never changed to fit the answer (T25; rule 2). The answer-fitting move here
is the reverse of a floor-widen: it would SWITCH the binding field from the
physically-meaningful measure (`p_first_uncorrected`, which fails) to the field that
happens to pass (`p_corrected`). Taking the passing field and declaring it the criterion
is gate-widening by field selection. **REFUSED.** The binding field stays the outer-loop
convergence measure. Note the item's own `d6rf7_accept_floor_control.py` independently
freezes the accept floor (`primalMinResTol × primalMinResTolDiff = 1.0e-05`) UNMOVED in
either direction — consistent with, not in tension with, this ruling.

## Consequence for the mandatory chain

Under the fix-until-runs law (2026-09-04, 2026-09-06 directives) a GATE FAIL is a
WAYPOINT, not a terminus. **dafoam owes a numerics fix** that drives the outer/SIMPLE
loop to convergence so the FIRST/uncorrected pressure initial residual falls below the
registered accept floor — more outer iterations, relaxation/`nOuterCorrectors` changes,
or a stronger pressure linear solver/preconditioner, registered as a successor with the
gate, threshold and floor UNCHANGED. The D6R2 transonic-multipoint chain remains
gated behind a D6RF that converges ON THE BINDING FIELD; it does not pass by
re-designating the criterion. This is a numerics fix owed by dafoam, executed through
the registered successor path.

## Method (§3 check-3 — my own read, not a relay)

I read the grading instrument at source (`d6rf7_grade.py:367-378`, `:1851-1863`) and the
measured values it records, and the accept-floor control (`d6rf7_accept_floor_control.py`),
before ruling. The determination rests on rule 5 and existing N-family residual semantics;
no compute was run and no gate, threshold, floor or verdict was moved.
