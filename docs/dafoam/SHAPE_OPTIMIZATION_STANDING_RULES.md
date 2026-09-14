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

---

## dafoam supervisor's additional rules — 2026-09-13, appended below the chief's reading, nothing above this line edited

Her closing line invites these: *"plus whatever else the dafoam supervisor can think of."* Rules 1–16 above remove ways the **discrete drag** can differ from the physical one. Rules 17–32 below remove ways the **record** can differ from the run — every one of them paid for by a measured failure of the night of 2026-09-12/13, each citing the lesson that carries the measurement. Numbering continues hers; they bind every dafoam optimisation from this date, and D6R3 registers under 1–32, not 1–16.

**E. The mesh and the design variables — what the solver actually read**

17. **Gate on the mesh the solver READ, never the mesh you generated.** The mesh gate is the hash of the `polyMesh` the running solver loaded, rebuilt from `pointProcAddressing` and compared for exact equality against the generated mesh. *Measured:* FM8 was graded a fresh-mesh confirmation and the retraction found **1,486 processor meshes scanned, zero matching the freshly extruded mesh — no arm had ever loaded it.* A staging step that copies the mesh into every processor case **before the model is built** is part of the arm, not a convenience. (L-595)

18. **Apply the design variables EXACTLY ONCE, and prove it by hash before `run_model()`.** A surface mesh generated from an already-deformed surface, then deformed again by the runscript, is double deformation and it does not announce itself. *Measured:* FM10 — `surfaceMesh.cgns` ≡ `surfaceMesh_final.cgns` ≠ `surfaceMesh_base.cgns`, then `phase_solve` re-read `dv_star` and set shape/twist/patchV again; the three conditions flew at CL +0.1493 / +0.1516 / +0.1524 above target, **30× the registered finding trigger**, and the objective was real but measured at the wrong lift. Register an equality check of the surface hash against the **base** surface at the moment the DVs are applied. **Confirmed by measurement 2026-09-13, not left as a hypothesis:** on the 1,031 wing points the fresh mesh's wall reproduces the deformed wall to **1.09e-09**, then the solve phase warped it again in the same direction — `cos∠(d1,d2)` median **0.99965**, `|d2|/|d1|` median **1.234** — and mid-span camber/chord ran base **0.00196** → optimum **0.04810** → FM10 **0.09015**, a camber increment of **1.91×**. The load-bearing line is `d6r2c_freshmesh.py:423-425`, which re-applies `shape`/`twist` on a mesh already built from the deformed surface. (L-599, L-585)

19. **Never form a ratio whose numerator and denominator were measured on different meshes, at different lifts, or under different DV applications.** *Measured:* the fresh-mesh ratio **1.2063** I relayed upward was a fresh-mesh numerator over a deformed-mesh denominator at incompatible lift; it was withdrawn. This is her rules 3 and 12 made into an arithmetic rule: **every factor of a reported ratio carries its own condition, and the conditions must match or the ratio is not a number.**

**F. The instrument — a frozen name is not a working path**

20. **Drive the CLI the launcher actually emits, not the function.** A `--selftest` that calls the graded function proves the function; it proves nothing about the entry point. *Measured:* the FM9 grader's launcher emitted `--log`, the parser rejected it, and `main()` never passed `log_path` — **the frozen CLI path could only ever return `NOT A RESULT`**, and the selftest was green throughout. The pre-freeze check drives the exact command line the launcher writes. (L-595, L-570)

21. **Every instrument named in a frozen table must EXIST, at its stated md5, at freeze.** *Measured:* I froze a registration naming four instruments that did not exist; the table was **true as written** and that is exactly how it survived. The pre-freeze check hashes each row's file and refuses on absence. (L-579)

22. **Count a gate family's EXTERNAL ANCHORS, not its gates.** Two gates fed by one producer are one gate. A self-consistency check is blind to a common-mode error in whatever the two sides share. (L-588, L-596)

23. **Derive every verification constant from the thing under test, in the same invocation, and USE the derived value.** A pinned constant passes or fails one day for the wrong reason. *Measured:* the FM11 sanity band is derived by propagating the registered absolute band through the ratio, not written down. (L-591)

24. **Suspect a check that reports SUCCESS exactly as hard as one that reports failure.** *Measured:* "O\_mp converged 88 times" was false — **35 of 87 succeeded, 52 failed, and `n=88` was an INDEX, not a count.** A reader that has never been shown able to see the failing case is not a reader. (L-592, and rule 3 of the constitution)

25. **Never place a sanity gate at a state where the quantity under test is identically zero.** *Measured:* the scaler-defect gate sat at a state with shape ≡ twist ≡ 0; **zero times a wrong scaler is still zero**, so the gate could not have fired for any scaler whatsoever. A sanity anchor is a state where the defect, if present, changes the number.

26. **Drive every guard to its failing side, and check non-finite BEFORE the comparison.** `abs(nan - x) > tol` is `False`, so a refuse-rather-than-degrade guard written that way never refuses. (L-578, L-570)

27. **A status channel with readers and no writer defaults to success.** *Measured:* `primal_residual.json` — **four reads, zero writes, zero such files anywhere on disk** — left `conv[p] = True` standing for every condition. At freeze, every channel a gate reads must be shown to have a writer that ran. **This one is still open and is on Sanaa's desk.**

**G. The record, the ladder and the money**

28. **Name the reference in every git comparison.** Bare `git diff` compares against the **shared** index and answers differently depending on when a peer last staged. An append-only claim is proved by **prefix byte-identity against HEAD's blob** (`cmp -n <pre-append size>`), never by a diff. (L-594)

29. **A crash, a stall or a refused solve is a finding about the case until triage says otherwise — and on this family it is a FIX, not a fact to leave.** *Measured:* FM5's pressure-equation stall was `NOT A RESULT` on an item that is one of ten owner deliverables; it was fixed by one registered change on her mesh → numerics → model ladder and re-run as FM6. Her rule 15's cause class is recorded at the stop, not reconstructed later.

30. **Cost basis per EVALUATION, calibrated at completion.** Every shape-optimisation registration states core-minutes per objective evaluation and per gradient evaluation separately, and the completion report lands the ratio actual/predicted in `docs/COST_CALIBRATION.md`. *Measured:* FM10 predicted 11.400 core-min, incurred 10.677, ratio **0.937**; dollars are derived at $0.0513/core-h, never measured.

31. **checkMesh the mesh that RAN, not the mesh that was built.** A quality log written before the last operation that touched the points describes a mesh no solver saw. *Measured:* the only `checkMesh` on disk for FM10 reports "Mesh OK" at max non-orthogonality **66.32** — that is the **as-built** mesh, before the second warp; the mesh that actually ran measures **79.21**, which **breaches DAFoam's own declared `maxNonOrth = 70.0`**, and so does the optimisation mesh at **71.24**. Neither as-run mesh had ever been checked. Her rule 7's quality budget is evaluated on the as-run points, and its log is written after the final DV application. (L-593, L-590)

32. **Her rule 15's cause classes are four; there is a fifth, and on D6R2 it was the answer.** Mesh (warp), parameterization (wiggles), trim (lift mismatch), solver — and **producer (the evaluation harness itself)**. *Measured:* the deformed-versus-fresh gap of **139 counts** was carried **104.5 % / 102.9 % / 99.6 % by PRESSURE drag** with viscous drag flat to within 7 counts of its own value, y+ medians 247 versus 223 with **no face below y+ 30 on either mesh**, first-cell height within **1.6 %**, all five near-wall layer thicknesses within **1 %**, and zero negative or degenerate volumes anywhere. **Every mesh cause class is excluded by measurement**; the cause was our own producer applying the design twice. A cause class is *assigned from a measurement that excludes the others*, never from the most plausible story.

**Standing interaction with her directive E.** A near-gate miss **proceeds**, reported as `GATE FAIL by <margin>, proceeding on directive E`; the verdict word itself is never rewritten by an agent. That directive changes what happens next; it does not change what the gate said.

**The one that would have caught the most.** Of these sixteen, **rule 17** is the one that would have ended the deformed-vs-fresh question a week early: every fresh-mesh claim before FM10 rested on a mesh no solver had read, and no amount of physics care upstream of that gate could have detected it.

---

## Correction 1 to the supervisor's section — 2026-09-13, same day. Appended, never edited in place; the owner's block above is untouched.

**Rule 30's worked example is wrong in its third decimal.** It reads "FM10 predicted 11.400 core-min, incurred 10.677, ratio 0.937". The measured figures are **incurred `10.667` core-min, ratio `0.9357`** — the launcher's ledger row (`arm=FM10 rc=0 wall_s=160 core_min=10.667`) and `FM10_GRADE.json`'s `cost.core_min` agree, and 160 × 4 ÷ 60 = 10.6667 closes the arithmetic exactly. **The rule itself is unchanged; only its example was mis-transcribed.** The error entered from `PREREGISTRATION_FM11_MATCHED_LIFT.md:362` — the sentence recording that the calibration row was still owed — and travelled into a report and then into a charter without passing either instrument. `DAFOAM_CHARTER.md` §22.6 is the clause it earned: **a number enters a record from an instrument, never from a sentence.**

**Rule 18's span is 47.72 days, not 46** (2026-07-28 00:18:12Z to 2026-09-13 17:33:34Z = 47 d 17:15:22). The determinism finding is unchanged.

**Rule 31 is refined, not weakened.** FM10's time-0 `nonOrthoFaces` set is of the **right** mesh — DAFoam checks at time 0 of each primal, on the mesh already deformed for that evaluation (5 polys, matching that block's `severely non-orthogonal (> 70 degrees) faces: 5`). What is absent is narrower and still damning: **no check at FM10's final time at all** (O\_mp checks at 0 and 1000; FM10 at 0 only), and **no `checkMesh` report of the as-run mesh in either arm**. The one quotable `Mesh OK.` remains the as-extruded mesh at **66.32299475**, before the solve re-applies the design.

**Rule 31 gains a second, sharper half, measured on both arms and recorded at `DAFOAM_CHARTER.md` §22.7: a declared threshold that never refuses is not a threshold.** `maxNonOrth = 70.0` is declared at `d6r2c_opt_runScript.py:163`; **76 of O\_mp's 202 checks exceed it** (worst **80.90429398**) and **6 of 6 of FM10's** do (**79.21261137**), and **every breaching block prints `Non-orthogonality check OK.` then `Mesh OK.`** The channel is live — four `Failed 1 mesh checks.` lines in the same log are all aspect-ratio failures at 1050.3162 against 1000 — it simply never fires on this clause. **So rule 7's quality budget is never satisfied by the solver's own check: it needs an instrument of ours that actually refuses, driven against a known-bad mesh before the freeze.**

---

## Addendum 2026-09-14 — owner directive #46: no gradient check during a running optimisation. Appended, never edited in place; every block above is untouched.

Byte-exact, Sanaa, 2026-09-14 ~01:45Z:

> ok so can the optimization run pls

> good and remmeber during the optimization we dont do gradient check

**Chief's reading:** during a running optimisation no finite-difference gradient verification step is performed by the run script or any watcher; gradient checks, if ever wanted, are a separate registered item before or after, never inside the optimisation.

lines whose number changed above this section: 0
