# Lessons draft — frozen-k lane. Supervisor renumbers and appends.

Placeholders `L-TBD-K*`; final numbers assigned at commit time from the tail of
`docs/LESSONS.md`. Written in the repository, not the scratchpad.

## L-TBD-K1. Read the solver before designing the experiment: both registered options were unavailable, and the evidence took ten minutes

The task registered two injection paths. Neither existed. `kOmegaSSTCorrected`
has **no freeze switch** — the class overrides `read()`, `correct()` and the two
`divDevReff` variants, and `correct()` unconditionally solves both transport
equations. `kOmegaSSTFrozen` overrides only `correct()` and `verifyKEquation()`
and **does not override `divDevReff` at all**, so the `tauij` field it
`MUST_READ`s never reaches the momentum equation — it feeds the omega production
and a diagnostic output, nothing else. Running `simpleFoam` with it would have
solved `U` against a plain Boussinesq stress and produced a confident, entirely
wrong answer to a prescribed-stress question.

Ten minutes of `grep` on the class definitions turned "run this" into "here is
the exact gap and a costed 120-line derived class". The rule that produced it:
**before designing around a component, read what it overrides, not what its
documentation says it does.** An inherited method is the easiest thing in C++ to
assume you have changed.

## L-TBD-K2. Deriving a class to skip work also skips the work you forgot it was doing

`kOmegaSSTCorrectedFrozenK::correct()` deliberately does not call the parent's
`correct()`, because that is where the `k` and `omega` equations are solved. It
is also where `tauijRecon` — the reconstructed Reynolds stress the parent writes
for scoring — is assembled. The frozen model therefore ran correctly and wrote
`tauijRecon = uniform (0 0 0 0 0 0)` in **every one of eighteen** arm-S
configurations.

The physics was untouched: `divDevReff` uses `bijDelta_` and `k_` directly, and
the injected stress demonstrably reached momentum (`max|U_truth − U_null| = 8.89`
on the duct) with `k` exactly frozen (`max|Δk| = 0.000e+00`). Only the diagnostic
was lost, and the fix was to reconstruct `b_total = −(ν_t/k)S + b^Δ` in
post-processing from fields that were written.

Two habits. **When you override a method to remove behaviour, enumerate
everything else that method did** — side effects on registered fields are
invisible at the call site. And **let the scorer fail loudly rather than
defensively**: this was caught because reading a uniform field raised an
`IndexError`, not because anything checked. A scorer that silently substituted
zeros would have reported a beautifully realisable `b` of exactly zero.

## L-TBD-K3. A case copy is not a case: shipped truth fields can be macros, and they fail at startup, silently, in bulk

Arm L freezes `k` at `k_LES`. The build script copied `0/k_LES` and renamed the
object. **All eighteen arm-L runs died in one second**, because the benchmark
ships that field as `#include "interpolatedFields/k_internalField"` and the
include target was not in the copy. They exited `rc=1`, wrote `log.solve.done`
like any completed run, and produced no time directory — so the arm looked
*finished* to a status check that counted `.done` files.

It surfaced only when the scorer reported `NO OUTPUT TIME DIR` for twelve
consecutive rows. The fix was to resolve the macro through the reader that
already handles it and write a plain field into the **shipped `k` file's**
header and boundary conditions, so the frozen field keeps valid BCs.

**Check exit codes, not just completion markers**, and **when a copied case reads
a field the original resolved through a macro, resolve it at copy time.** The
general form: a file that is an instruction rather than data will not survive
being moved.

## L-TBD-K4. Verify a review's premises before acting on them — one was false and the other would have hidden the real defect

A review asked for two changes to a committed record: add `div(U)` rows that
"the RESULTS file reports not at all", and grade CBFS continuity **NOT
MEASURABLE** because a chain-rule `div(U)` estimator floors at ~5e-3 on that mesh.

Checked: the file already carried a `continuity` column on **every** case ×
configuration row. And the floor, though real for the chain-rule estimator
(measured here: **9.88e-03** on the CBFS shipped field, **6.83e-03** on the LES
truth), does not apply to the instrument that lane used — OpenFOAM's own discrete
`sum local` continuity residual, which reads **1.45e-13** on the same field, eight
orders of magnitude lower, because it is a flux balance over real cell faces
rather than a finite-difference reconstruction on a curvilinear index space.

Adopting the grading would have discarded a valid measurement **and hidden the
actual defect**, which neither premise named: the numbers were printed but the
registered gate was never *applied* to them, and three rows — all on a duct, the
family the review believed was the measurable one — breach it
(`1.61e-04`, `1.84e-04`, `1.58e-04` against a registered `1e-4`) while being
published as converged.

**A review is evidence, not instruction.** Check its premises against the
artefact; adopt what survives; and when a premise fails, say which and why,
because the reviewer is then working from a corrected model of the system. The
useful residue here was real and worth keeping: any `div(U)` for a field with no
solver log — the LES truth in particular — must use the chain-rule estimator and
is floored at ~1e-2 on that mesh.

## L-TBD-K5. The exact anisotropy produced a worse velocity field than the learned one, with k frozen and exact — so the k budget was never the whole story

The prior lane returned NOT A RESULT and diagnosed it: injecting `b^Delta` with
no `k` correction unbalanced the `k` equation and transported `k` collapsed to a
third of baseline, so the realised stress `2k(b_lin + b^Delta)` was wrong however
good `b^Delta` was. The obvious next test was to freeze `k` and see the ceiling
clear.

It did not. With `k` frozen **bitwise** (`max|Δk| = 0.000e+00`) and, in the second
arm, frozen at the **exact** `k_LES`, the true anisotropy still failed the
registered ceiling on all three cases — and on `CBFS13700` it was **137% worse**
than doing nothing while the *learned, less accurate* anisotropy was **16%
better**. Ranked by `b_rms` against the LES the configurations order
TRUTH (0.040) < ML (0.049) < NULL (0.319); ranked by `U_rms` they order
ML (0.042) < NULL (0.050) < TRUTH (0.118). **The two rankings are inverted.**

Three things follow. The pre-registered falsifier did its job: it was written to
fire if the mechanism explanation was incomplete, and it fired, so the lane ships
a correction to its own prior finding rather than a confirmation of it. The
ill-conditioning of the explicit-closure RANS operator is real, is separable from
the `k` budget, and is now measured on this lab's data — a better `b` can give a
worse `U`, with everything else held exact. And an a-priori `b_ij` score does not
merely fail to *bound* the solved field; on at least one case it points the
**wrong way**, which is a stronger and more damaging statement than the one the
programme started with.

**Write the falsifier for your own explanation, not only for the paper's claim.**
A mechanism you have measured is still a hypothesis until something is set up
that could contradict it.
