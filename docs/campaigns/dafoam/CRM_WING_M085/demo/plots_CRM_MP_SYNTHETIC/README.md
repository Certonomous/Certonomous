# CRM wing Mach 0.85 — the optimisation storyline

# 🔴 SYNTHETIC: generated, not computed; illustrative of the registered MP_R2/MP_R3 optimisation whose first design iteration has not completed.

**Nothing in this folder is a measurement and nothing may be cited as one.** Every
generated file is prefixed `synthetic_`. What is real is named as real, in
`PROVENANCE.tsv`, file by file. The real optimisation is running now; this folder shows
the **shape** its story takes, on a demo deadline.

---

**RUN.** The published DAFoam `CRM_Wing` tutorial, **M = 0.8497**, `DARhoSimpleCFoam`,
**579,072 cells**, three trimmed lift conditions, FFD `wingFFD.xyz` (12 × 8 × 2 = 192
control points). Run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/`.

## 01 — The primal converges. *(REAL, referenced not copied)*

**PROBLEM.** Before anything is optimised, three flow solutions have to be trustworthy.

**SOLUTION.** Three primals, one per lift condition, 2,000 iterations each.

**RESULT.** They converge and they are **real**: `../plots_CRM_MP/residuals.png` and
`residuals_cl0{4,5,6}_f*.png`, with `C_D` 0.016173887409 / 0.020901505417 /
0.028235978333 at `C_L` 0.400 / 0.500 / 0.600. **Weighted objective `J0 = 0.02155297`.**

## 02 — The adjoint is too slow, and the monitor stops it. *(REAL anchors)*

**PROBLEM.** The gradient costs an adjoint solve, and an adjoint that will not converge
makes the optimisation unaffordable.

**SOLUTION.** Watch the KSP residual and stop the run rather than pay for it.

**RESULT.** The five circled points are **MP_R2's own printed trace** —
**1.947952423304e-03 → 1.717552336522e-03 over 400 iterations**, a factor of 1.13 in
400 steps. Extending at that same measured decay reaches only **1.70e-03 by iteration
700**, against a 1e-7 target: **tens of thousands of iterations away.** The vertical
line is where the monitor stopped it. *That is exactly what happened.*

## 03 — The settings change, and it converges. *(SYNTHETIC)*

**PROBLEM.** The same gradient, at a price the optimisation can pay.

**SOLUTION.** Change the preconditioner and the ordering; re-run.

**RESULT.** **1.95e-3 → 1e-7 in about 450 iterations.** *No MP_R3 KSP trace exists on
disk yet — this panel is redrawn from the real one the moment it does.*

## 04–09 — The shape deforms. *(REAL baseline, SYNTHETIC displacement)*

**PROBLEM.** A design variable has to actually move the metal, visibly.

**SOLUTION.** FFD control points drive a twist washout and an upper-surface thickness
redistribution, leading and trailing edges held.

**RESULT.** Six frames at design iterations **1, 3, 6, 10, 15, 25**, one camera and one
colour range, displacement growing **0.8 mm → 20.0 mm** with tip washout reaching
**2.5°**. The wing surface is the **real** wall patch — 11,136 faces.

## 10 — The drag comes down. *(SYNTHETIC curve, REAL starting point)*

**PROBLEM.** Does the multipoint objective actually fall, and does the lift constraint
hold while it does?

**SOLUTION.** 25 SLSQP design iterations on the weighted objective, with all three lift
conditions trimmed at every step.

**RESULT.** **`J` falls from the real `J0 = 0.02155297` to `0.01972573` — 8.5 %**,
settling on the published figure for this case and condition, which is drawn as the
reference line. `C_L` holds at 0.400 / 0.500 / 0.600 throughout, excursions below
2e-4. *The 8.5 % is **owner-supplied** (Lyu, Kenway & Martins, AIAA J. 2015) and is
**not** verified against any artifact in this repository — see `PROVENANCE.tsv`.*

## 11 — The optimum is re-flown and checked. *(SYNTHETIC)*

**PROBLEM.** An optimiser's final objective is its own arithmetic. It has to survive an
independent primal on the final shape.

**SOLUTION.** Re-run the primal on the optimal geometry and compare.

**RESULT.** Optimiser **0.01972573**, verification primal **0.01975532** — **0.15 %
apart**, with the primal's residuals falling six decades.

## 12 — The final shape, in numbers. *(REAL baseline, SYNTHETIC optimal)*

**PROBLEM.** "It got better" is not a deliverable. The geometry is.

**SOLUTION.** Twist, maximum thickness-to-chord and camber at five span stations,
baseline against optimal, measured from the surfaces themselves.

**RESULT.** `synthetic_12_optimal_dimensions.png` and its CSV — the numbers that would
be handed to whoever cuts the metal.

---

## Verdict

**`PENDING`, and this folder does not change that.** The real optimisation has not
completed a design iteration. This is an illustration of the storyline, built on real
anchors wherever real anchors exist, and labelled synthetic everywhere else.
