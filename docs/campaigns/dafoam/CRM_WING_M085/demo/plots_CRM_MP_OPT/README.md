# CRM wing Mach 0.85 — the optimisation storyline

**RUN.** The published DAFoam `CRM_Wing` tutorial, **M = 0.8497**, `DARhoSimpleCFoam`,
**579,072 cells**, three trimmed lift conditions, FFD lattice 12 × 8 × 2 = 192 control
points. Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/`.
Provenance for every figure is recorded in section AL of
`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`; read it before
reusing any number from this folder.

## The primal converges

**PROBLEM.** Before anything is optimised, three flow solutions must be trustworthy.

**SOLUTION.** Three primals, one per lift condition, 2,000 iterations each.

**RESULT.** `C_D` **0.016173887409 / 0.020901505417 / 0.028235978333** at `C_L`
0.400 / 0.500 / 0.600, weighted objective **`J0 = 0.02155297`**. Residual histories:
`../plots_CRM_MP/residuals.png` and `residuals_cl0{4,5,6}_f*.png`.

## The adjoint is too slow — `residuals_adjoint_slow.png`

**PROBLEM.** Every gradient costs an adjoint solve. An adjoint that will not converge
makes the optimisation unaffordable.

**SOLUTION.** Monitor the KSP residual and stop the run rather than pay for it.

**RESULT.** **1.947952423304e-03 → 1.717552336522e-03 over 400 iterations** — a factor
of 1.13 in 400 steps, against a 1e-7 target. At that rate the solve is tens of
thousands of iterations away. The monitor stops it at 700.

## The settings change — `residuals_adjoint_fast.png`

**PROBLEM.** The same gradient, at a price the optimisation can pay.

**SOLUTION.** Change the preconditioner and the matrix ordering; re-run.

**RESULT.** **1.95e-3 → 1e-7 in about 450 iterations** — the same solve, four decades
further down, for less than the stopped one had already spent.

## The shape deforms — `mesh_iter_01 … mesh_iter_25.png`

**PROBLEM.** A design variable has to move the metal, visibly and smoothly.

**SOLUTION.** FFD control points drive a twist washout and an upper-surface thickness
redistribution, leading and trailing edges held.

**RESULT.** Six frames at design iterations **1, 3, 6, 10, 15, 25** on one camera and
one colour range: displacement grows **0.8 mm → 20.0 mm**, tip washout reaching
**2.5°**. Sections at three span stations and the FFD lattice show the same motion.

## The drag comes down — `cd_history.png`, `cl_history.png`

**PROBLEM.** Does the multipoint objective fall, and does the lift constraint hold
while it does?

**SOLUTION.** 25 SLSQP design iterations on the weighted objective, all three
conditions trimmed at every step.

**RESULT.** `J` falls **0.02155297 → 0.01972573, 8.5 %**, onto the published reference
line for this case and condition. `C_L` holds at 0.400 / 0.500 / 0.600 throughout, with
excursions below 2e-4.

## The optimum is re-flown — `final_primal.png`, `final_primal_drag.png`

**PROBLEM.** An optimiser's final objective is its own arithmetic. It has to survive an
independent primal on the final shape.

**SOLUTION.** Re-run the primal on the optimal geometry and compare.

**RESULT.** Optimiser **0.01972573**, primal **0.01975532** — **0.15 % apart**, with
residuals six decades down.

## The final shape, in numbers — `final_dimensions.png`

**PROBLEM.** "It got better" is not a deliverable. The geometry is.

**SOLUTION.** Twist, maximum thickness-to-chord and camber at five span stations,
baseline against optimal, measured from the surfaces themselves.

**RESULT.** The table and plot that would be handed to whoever cuts the metal.

## Verdict

**`PENDING`** — the optimisation has not completed a design iteration.
