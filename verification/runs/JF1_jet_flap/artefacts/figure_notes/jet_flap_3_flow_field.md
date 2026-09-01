# Flow field at the slot

This calculation ran its full 20000 of 20000 iterations and did not reach the convergence target fixed before it started. The pressure channel finished at 1.9e-04, about 191 times the 1e-06 target; it fell early, then flattened and stayed flat.

The turbulence model's energy variable goes slightly negative in a handful of cells and is clipped back to zero on 99 % of iterations, continuously from iteration 91 to the last one. The picture is held by that clipping rather than converged free of it, and that is a real limitation of this result.

This is a different, finer mesh of 46,180 cells from the five calculations on the lift and pressure charts. Its reference area is 1.00 m2 against their 0.01 m2. It is shown for the flow picture only and contributes no point to those charts; the two are never plotted on one axis. Indicative only: no mesh-refinement study, no experiment.
