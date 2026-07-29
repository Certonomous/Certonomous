# ONERA M6 — the primal plateaus below its own gate

**Status: documented failure.** The ninth act does not certify. This records why,
because the reason is more interesting than the failure.

Diagnosed by the supervisor directly from `log.run_model`, not relayed from a
summary. Run of 2026-07-29, 399,360 cells, 4 MPI ranks, 3000 iterations, 595 s.

## What the solver said

```
Primal min residual 1.01765521962937e-06
did not satisfy the prescribed tolerance 1e-08
Primal solution failed!
```

Not a crash, not a divergence, not an out-of-memory. The mesh built clean, the
decomposition was clean, and 27.6 GB was available at the start of the solve.
The run completed every iteration it was given and was then refused.

## Why "run it longer" is the wrong instinct

The turbulence residual over the run:

| point in run | nuTilda initial residual |
| --- | --- |
| ~25% | 1.0206e-06 |
| ~50% | 1.0181e-06 |
| ~75% | 1.0216e-06 |
| ~90% | 1.0214e-06 |
| end | 1.0177e-06 |

It reached 1e-06 inside the first quarter and did not move again. **The change
across the entire final third is a factor of 0.997.** This is a fixed point, not
slow convergence. Tripling the iteration budget would spend the time and land on
1.0e-06 again.

This is [L-7](../../../LESSONS.md) in the wild: *"converge harder" is not the
default fix for a plateau — first ask whether the plateau is a genuine fixed
point.* Here it plainly is.

## What is actually limiting it

Every other equation is satisfied. Only the turbulence equation is not:

| equation | initial residual | satisfied against 1e-08 |
| --- | --- | --- |
| U1 | 6.99e-08 | yes |
| U2 | 8.99e-08 | yes |
| he | 2.72e-07 | yes |
| p | 3.73e-07 | yes |
| **nuTilda** | **1.02e-06** | **no** |

The wall resolution is the leading hypothesis, and it is a hypothesis, not a
conclusion: **yPlus min 5.21, max 103.5, mean 33.8.** That straddles the buffer
layer — too coarse to resolve the viscous sublayer, too fine to be a clean wall
function. A turbulence equation that cannot settle while every other equation
does is consistent with that, but this run does not prove it. Testing it means
a mesh with wall spacing chosen for one treatment or the other, and that test
has not been run.

## What was NOT done, deliberately

The gate was not moved. `primalMinResTol` stands at 1e-08, which is the value
the case shipped with. Relaxing a convergence criterion so a run clears it would
have turned this row green and made the other eight rows worth less, because a
reader cannot tell which kind of green they are looking at.

## Numbers this run did produce

Carried here for completeness and **not certified** — they come from a primal
the solver itself refused, and any use of them must say so:

- CD 0.02300356
- CL 0.31311587
- yPlus min 5.21, max 103.5, mean 33.8

The gate this act was built to test — surface pressure against AGARD AR-138 at
seven span stations, eta 0.20 to 0.99 — is therefore **not evaluated**. No Cp
deviation is claimed.
