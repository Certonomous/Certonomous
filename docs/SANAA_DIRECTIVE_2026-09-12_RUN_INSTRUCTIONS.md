# [SANAA-DIRECT] 2026-09-12 ~18:30Z — run instructions for the urgent 3D cases, checkpoint / launch / monitor / hygiene rules

Recorded by the chief from Sanaa's own session turn, byte-exact below the rule. Nothing in the quoted block may be corrected by any future editor. Context: the box was resized to r7a.4xlarge (16 cores, 123 GiB) and rebooted 17:36Z; every solver died; the census is `docs/RESIZE_CENSUS_2026-09-12.md` and the inventory `docs/SHOOTABLE_3D_INVENTORY_2026-09-12.md`. Earlier the same turn, hers: "before i decide on what to do, for each of these runs, which of them has a completed run with result ... within reasonable accuracy/ band wrt to some reference".

---

> ONERA M6 primal: Agreed.comparison happens now. Same for  D8G CRM wing-body.The band must be registered before the comparison is run. For M6: Cp at the AGARD span stations (the standard six) and shock location at η = 0.65 and 0.90, with the tolerance written down first — otherwise it's a post-hoc match, which your own doctrine doesn't accept. Same for D8G: CL, CD, CM at the DPW condition (Mach 0.85, CL 0.5) against the NTF/Ames CRM tunnel data, band registered, then graded. Both comparisons are hours of work, not runs — the primals exist. For now let's ignore the cubes. (and i am only talking about 3D cases), here is how each case (that i consider urgent) needs to be handled: [SANAA-DIRECT] D6R2 — compressible multipoint optimization, run instruction
>
> Purpose. The design act for company audiences: one wing shape optimized across several flight conditions simultaneously, lift held at each, gain decomposed, gradients spot-verified, optimum confirmed on a fresh mesh.
>
> Before launch
>
> Add restart to the run script: the optimizer writes its history and the design vector every iteration and can hot-start from them; primal fields checkpointed every 30 min wall time, last two kept. Verified by one kill-and-resume test before the real launch.
> Run as ubuntu, never root. 4 MPI ranks. Memory footprint (~17 GB) checked against free RAM by the launcher.
> Registration frozen: the flight conditions and their weights, lift targets per condition, design variables (shape + twist), constraints (thickness, volume, any trim), iteration cap 25 (or to tolerance if you prefer — say which), cost estimate and cap at 3×.
> Parallelism health: the multipoint gradient at 2 and 4 ranks agrees to the registered tolerance before iteration 1. Run
> 6. Detached under the runner, checkpoints as above. Monitor writes the objective, constraint violation and each condition's convergence per iteration.
> 7. Stop rules: objective rises three consecutive iterations → stop, halve the step, resume; any condition's primal fails to converge (the D6/D6R NaN signature) → stop, resume from the last good iterate with the step halved; cap → NOT A RESULT, never raised.
>
> After
> 8. Decomposition, two extra solves at matched lift: twist-only re-trimmed, and the full optimum; table shows shape vs twist vs trim contributions before any percentage is quoted.
> 9. Fresh mesh on the final shape from the family script, re-solve at every condition, confirm the weighted drag within band of the deformed-mesh value.
> 10. Report: gradient spot-check table, parallelism-health line, convergence history, decomposition table, per-condition drag and lift before/after, fresh-mesh confirmation, sections and skin-sensitivity figures to the figure standard, compute table (ranks | core-min | wall), certificate slot honest (single grid, band pending).
>
> What is not done here: full FD sweep, grid family on the optimization (single mesh, disclosed). Purpose. The 3D vehicle act: a real hull with appendages at incidence, forces and moments, stability derivatives and neutral point with bands.
>
> Fix first, then carry the DrivAer fixes across
>
> Triage the L1 stall (pinned at iteration 368): read the residual history and the pressure-solver iterations; classify plateau vs oscillation. A plateau with the pressure solver at its cap is the wall-layer/mesh signature — fix the mesh, do not relax the solver.
> If nothing gets fixed, Apply the DrivAer arm to SUBOFF: blended wall treatment (SST with automatic wall function) so y+ in the buffer zone is tolerated, plus the same layer check (growth ratio, layer coverage on the hull, sail and fins, cells across the appendage roots). Report y+ per patch after the first converged solve; the family is generated from one script so L1/L2/L3 stay similar.
> Register before launch: reference = Roddy 1990 captive-model forces and moments (band per derivative written first), Huang 1992 surface pressure at α = 0 as the anchor; sweep points α = −12, −8, −4, 0, +4, +8, +12; quantities Z, M, hull/fin split; derivatives by linear fit over |α| ≤ 8; neutral point from Z_w and M_w. Cost estimate registered too but doesnt stop the run  Drivaer: what we started yesterday as a fix continues. NASA CRM — wing (Mach 0.85 L2) and wing-body (D8G) (the industry yardstick)
>
> What a company sees: the aircraft everyone benchmarks on, solved to a converged family, CL/CD/CM compared with the tunnel and with the DPW participant scatter, honestly banded.
> Must be true: band registered before grading: CL, CD, CM at Mach 0.85, CL = 0.5, against NTF/Ames data with the DPW scatter as the honest tolerance; committee grids admissible under the two-tier standard with quality disclosed.
> Run plan: apply the symmetry-plane tolerance fix (832 faces) to the wing L2, relaunch; D8G L1 converges already → register the comparison → then L2 on the committee family. Checkpoints every 30 min; these are the long runs, so they get the slot M6 frees.
> Monitor: the L2 stall signature (18 it/6 h) is a mesh defect signature → stop and fix, never wait.
> Deliverable: CL/CD/CM table vs data with bands, Cp at DPW sections, the family and observed order, the register line flipping. 5. MRF impeller — rotating machinery (Whisper/Elroy relevance)
>
> *Register the power-number band as "inside the published range 4.0–6.0" plus the Rushton correlation value as the anchor; converge the fine level; grade the triple. Deliverable: power number vs correlation, torque convergence, velocity field at the blade plane. Checkpoints
>
> Every solver run writes a restartable checkpoint at a fixed wall-clock interval: 30 minutes. The last two checkpoints are kept; older ones purged. writeInterval on iteration count is set so it never exceeds 30 minutes at the measured rate; if the rate is unknown, checkpoint every 200 iterations until it is.
> Every optimization writes its history and design vector every iteration and can hot-start from them.
> Every transient writes fields at an interval that gives at most 30 minutes of loss; time-averaging accumulators are checkpointed with the fields.
> The launcher refuses to start any case whose controlDict or run script does not satisfy 1–3.
> Proof: one kill-and-resume test on one case per solver class, once, before the fleet launches anything; the resumed result must match an unkilled reference to the solver's tolerance.
>
> Launch
> 6. As ubuntu. Never root. Container jobs included.
> 7. Memory guard: the case's footprint (from its class or its previous run) checked against free RAM; refused if it does not fit.
> 8. Core guard: solver ranks plus fleet processes never exceed 16 (or nproc). Waves are scheduled, never oversubscribed.
> 9. Detached under the runner: process, monitor and autograder parented to init. The fleet dying, a supervisor ending, or an ssh session closing never touches a solver.
> 10. Registration frozen before launch: reference and band for the graded quantity (external reference for validation cases, not an internal anchor), cost estimate, cap at 3× the estimate, iteration or time budget, checkpoint interval.
>
> While running
> 11. Monitor writes per iteration: residuals per equation, the graded quantity, cost per iteration, wall time vs cap.
> 12. Stop rules, fixed: residual growth or a field outside bounds → stop; plateau with a stalled linear solver → stop, mesh fix > if doesn twork > model fix > coherent oscillation in the graded quantity → mark "physics voting unsteady> unsteady 
> 13. One registered change per run. Never the same action twice on the same state. Two stops on the same cause → climb the ladder (mesh → numerics → model). Ladder exhausted → park with the action history, write the lesson, next case.
>
> Box hygiene
> 17. Disk above 85% is a defect: graded run trees archived, decompositions and intermediate times purged after grading.
> 18. Load above core count is a defect; swap use above zero for solver jobs is a defect. Both stop new launches until cleared.
> 19. The runner is the only thing that launches. Nothing launched by hand counts as a case.
>
> Reporting
> 20. State lines, not prose. I care about PROGRESS RIGHT NOW. I dont want plumbing and endless verification or reporting. PROGRESS. RUNS > FIX. thats all i want to see for each of these runs, i want to see a quick plan of whats happening/ gonna happen to make them complete and be shootable

---

**Chief's reading, labelled as such and correctable by her.**

1. "cap at 3×" (items 3 and 10) is written alongside her 04:20Z directive #17 (NO CAP, no run stopped by time or budget). The chief reads the two together as: the cap is REGISTERED and, if crossed, the run is graded NOT A RESULT and the cap is never raised (her item 7, "cap → NOT A RESULT, never raised") — the run is not killed by a wrapper. Where they genuinely conflict for a given run, the supervisor asks the chief, who asks her; nothing is killed on a cap in the meantime.
2. Items 1–5 (checkpoints) and 6–10 (launch) are enforced in the runner (`scripts/queue_runner.py`) and are preconditions for every launch. Item 5's kill-and-resume proof runs once per solver class (steady OpenFOAM, DAFoam optimisation, transient OpenFOAM) before any case launches. Item 19: hand launches are not cases.
3. Item 8's core guard at 16 with roughly 1–2 cores for the fleet means waves of ~14 solver ranks. Waves are scheduled by the runner from the registered rank counts.
4. Not 3D and therefore outside this directive: T4e, T23G2, VMFL017, SUP_BOOSTER, T21 (wedge/empty meshes). The cubes (VMFL078, T5f, T18) are set aside on her word "let's ignore the cubes".
5. Comparisons that are hours of desk work, not runs, and start now without a launch: M6 (Cp at the six AGARD stations, shock at η = 0.65 and 0.90, tolerance registered first), D8G (CL/CD/CM at Mach 0.85, CL 0.5 vs NTF/Ames with the DPW scatter as tolerance), SUBOFF (Roddy 1990 / Huang 1992 bands), MRF (4.0–6.0 plus Rushton correlation anchor).
