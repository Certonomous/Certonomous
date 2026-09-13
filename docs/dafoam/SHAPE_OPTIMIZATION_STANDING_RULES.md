# [SANAA-DIRECT] 2026-09-13 ~17:00Z — Standing rules for shape optimization: the optimum must survive a mesh it has never seen

Recorded by the chief from Sanaa's own session turn (session identity katie@certonomous.com), byte-exact below the rule. Nothing in the quoted block may be corrected by any future editor. Context: D6R2's 24.7 % weighted-drag reduction, measured on the deformed optimisation mesh, did not reproduce on a freshly extruded mesh of the same family and parameters (FM10: fresh-mesh optimised/baseline ratio 1.206 against 0.753 on the deformed mesh). Her question immediately before: "dafoam team: what was the mach on that case" — answer M 0.29.

---

> dafoam: [SANAA-DIRECT] Standing rules for shape optimization: the optimum must survive a mesh it has never seen
>
> The principle: the optimizer minimizes the discrete drag. Every rule below removes a way the discrete drag can differ from the physical one as a function of the design variables — because that is exactly what the optimizer will find.
>
> A. Before the first iteration
>
> Optimize on a mesh in the asymptotic range. The baseline gets its grid family first; the optimization mesh is the coarsest level whose drag is within the band of the fine level. Optimizing on a mesh whose discretization error is large gives the optimizer a large error to exploit.
> Wall-resolved, not wall functions. Wall functions make friction a strong function of y+, and y+ drifts under warping. y+ ≈ 1 on the optimization mesh, checked on the baseline.
> Trim in the loop. Angle of attack is a design variable with lift as an equality constraint at every condition, so every evaluation is at matched lift by construction. Drag is never compared across different lifts.
> Regularize the design space. Bounds on control-point motion, thickness and curvature constraints, and a smooth parameterization (fewer, smoother modes first; local high-frequency modes only after the smooth optimum is found). Surface wiggles are the cheapest way to fool a discrete drag.
> Fully converged primal and adjoint at every iteration. Residual tolerance an order tighter than the change in drag the optimizer is chasing; a partially converged primal gives gradient noise the optimizer follows.
>
> B. During the optimization
> 6. Warp settings that carry the near-wall layers with the surface (rotation of the near-wall region with the surface, deformation region scaled to the geometry) so first-cell height and orthogonality are preserved under displacement, not stretched — verify the setting names in the warp's documentation and register them.
> 7. A quality budget per iteration: worst-cell skewness, minimum first-cell height relative to baseline, minimum volume, and the y+ range. Logged every iteration; crossing any threshold stops the run.
> 8. Periodic re-meshing with restart. Every N iterations, or whenever the surface displacement exceeds a registered fraction of the local first-cell height, regenerate the mesh from the current smooth surface, spot-check the gradient on the new mesh, and resume from the current design. Accumulated warp error is reset to zero.
> 9. Fresh-mesh checkpoints of the objective. Every N iterations, evaluate the current design on a freshly generated mesh at matched lift. If deformed-mesh and fresh-mesh drag differ by more than the registered tolerance, the run stops and re-meshes; the optimizer is not allowed to keep walking down a slope that only exists on the warped mesh.
> 10. Watch where the gain comes from. Shear and pressure drag split per iteration; where available, a far-field decomposition with the spurious-drag component. Gain arriving in the spurious or friction component with no change in span load or pressure distribution is an artefact signature: stop, re-mesh.
> 11. Bounded design steps. A trust region on the design update sized to the first-cell height, so no single step deforms the near-wall mesh beyond what the warp preserves.
>
> C. After the optimization
> 12. Fresh mesh, matched lift, all conditions, from scratch. The claimed improvement is the fresh-mesh number. The deformed-mesh number is reported beside it, with the difference disclosed.
> 13. Finer level. The optimized shape re-evaluated on the next finer family level; the improvement must survive within the band. An optimum that holds on one mesh only is not an optimum.
> 14. Decomposition on the fresh mesh (shape / twist / trim) before any percentage; drag split on both meshes on the certificate.
> 15. Cause class if it fails: mesh (warp), parameterization (wiggles), trim (lift mismatch), solver (convergence or low-Mach dissipation) — recorded, and the run re-registered with the corresponding rule tightened.
>
> D. What moves up the roadmap because of this
> 16. Adjoint-driven mesh adaptation inside the loop: the adjoint already computed for the gradient gives the drag's discretization-error estimate; refine where it is large at each design. This is the principled version of rules 8 and 9, and the reason that register line now has a date.
>
> Rules 3, 8, 9, 12 and 13 are the ones that would have caught D6R2 before it cost a week; rule 9 is the one that would have caught it on day one. plus whatever else the dafoam supervisor can think of

---

**Chief's reading:** these are standing rules for every dafoam shape optimisation from this moment (rules 1–5 numbered by position in her list). They bind the D6R2 re-registration (D6R3) and every successor; the dafoam supervisor appends its own additional rules below this line as a dated section, never inside the quoted block, and lands the whole as an addendum to `DAFOAM_CHARTER.md`. The D6R2 24.7 % figure is withdrawn from any demo claim; the fresh-mesh number is the claimed number (rule 12).
