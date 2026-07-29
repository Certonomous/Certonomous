# B3 adjoint blocker — supervisor debugging session

Taken over by the global supervisor per the standing rule that work an agent has
failed at repeatedly comes back to the supervisor. This records what was
established, including two of my own setup errors, and what remains open.

## The failure, restated

Square-duct field inversion (worth 62.9% of our closure deficit). Stages 1 and 2
pass: the macro reader works, and the CBFS primal converges to within 0.087% of
B2's independent baseline. Stage 3 fails: PETSc `KSPConvergedReason = -9`
(`DIVERGED_NANORINF`) at **GMRES iteration 0**, nonzero initial residual ~7.1e-4,
**zero iterations completed**.

This is not a gradient blow-up. Nothing has been optimised, so there is no step
size or optimizer to tune — the first application of the adjoint operator
produces NaN/Inf. It is a linear-algebra failure inside a single adjoint solve.

Previously ruled out by the agent: primal under-convergence (tightened 100x),
the objective function (a standard force objective fails identically), and
preconditioner fill level (1 and 4 both fail).

## What I established this session

**1. The primal state is clean — the NaN is generated in the adjoint, not
inherited.** Checked every converged field directly:

| field | min | max | non-positive | NaN/Inf |
| --- | --- | --- | --- | --- |
| k | 7.39e-09 | 0.0277 | 0 | 0 |
| omega | 0.0624 | 131.88 | 0 | 0 |
| nut | 3.68e-08 | 0.00897 | 0 | 0 |
| p | −0.0692 | 0.1035 | 2036 (gauge, expected) | 0 |

Nobody had established this before. It rules out a poisoned input state.

**2. `primalVarBounds` was never set — and setting it does NOT fix this.**

The case uses low-Re wall treatment with `k` fixed at **1e-15** at the wall.
SST's F2 blending contains `sqrt(k)`, whose derivative `1/(2*sqrt(k))` is of
order 1e7 there and undefined if k crosses zero under adjoint perturbation. Since
`primalVarBounds` was absent from every runScript, DAFoam was running on
defaults, so this looked like a live and genuinely untried lever.

Tested with a floor of `kMin = 1e-10` (five orders above the wall BC), plus
floors on omega and nut. **REFUTED: identical `PetscConvergedReason -9`, total
iterations 0, after 177.61 s.** The k-singularity hypothesis is dead, and the
bounds lever is eliminated.

**3. The SST-versus-SA discriminator is still OPEN, and that is my failure to
land it, not a result.**

The strongest remaining test is whether the failure is specific to the SST
adjoint, since SA is DAFoam's most exercised adjoint path. My attempts did not
produce a valid test:

- First attempt: I swapped the RAS model without creating a `nuTilda` field.
  SA's transported variable simply was not there. My error.
- Second: I hand-wrote a `nuTilda` header that OpenFOAM rejected
  (`unexpected class name`). My error; rebuilt it from the existing `nut` header.
- Third: stale `processor0`/`processor1` directories, copied along with the case,
  still held the old SST decomposition with no `nuTilda`. This is the known trap
  already documented on this project. Cleared them.
- Fourth: now a PETSc segfault (exit 59), which suggests the runScript's state
  declarations are still inconsistent with SA after my edit of `normalizeStates`.

**No conclusion about SST-versus-SA can be drawn from any of these.** Converting
a working SST case to SA is more invasive than a model swap plus one field.

## Where this goes next

1. **Build the SA case from a DAFoam SA tutorial** rather than converting the SST
   case, then port the CBFS mesh and boundary conditions into it. That gets a
   valid discriminator instead of fighting a half-converted setup.
2. **Test the `empty` to `symmetry` patch conversion**, which stage 2 introduced
   for mesh warping. Run the adjoint on a variant with the original patch types
   to see whether the conversion is what poisons the Jacobian. Untested.
3. If both come back clean, the remaining suspect is the variance objective's
   coupling to `UData`, which would need a DAFoam-side look.

## Cost

Roughly 6 core-minutes across four attempts on a 21,000-cell case. Cheap. The
value was in eliminating the bounds hypothesis, which looked plausible and is now
closed.
