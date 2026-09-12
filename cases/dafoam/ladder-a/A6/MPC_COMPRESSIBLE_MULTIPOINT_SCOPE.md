# COMPRESSIBLE MULTIPOINT OPTIMISATION — SCOPE AND COST

## **DRAFT · UNFROZEN · NOT A PRE-REGISTRATION · AUTHORISES NO COMPUTE**

**This document freezes no gate, no threshold, no band, no label and no cap. It registers no run,
and no number in it is a registered cost or a prediction.** It exists so that a pre-registration
can be written against measured ground instead of recall. Nothing here may be cited as a
prediction; nothing here licenses a launch.

**Dated 2026-09-12. Team: dafoam. Lane: `lab-lane`, under the `dafoam-supervisor`.**
**ZERO SOLVER CORE-MINUTES WERE SPENT PRODUCING IT.** No container, no `mpirun`, no solver was
invoked. `docker images` was read once as a read-only identity assert (§5.1). Every figure below is
read from the artifact cited beside it, and the ones that are not measured are labelled.

**SUBMISSIONS ARE PARKED.** Nothing in this document or the item it scopes is filed, sent,
emailed, uploaded, posted, registered or commented outside this box, now or ever
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Mandate.** Sanaa named the multipoint optimisations, compressible and incompressible, as a dafoam
deliverable on 2026-09-11. **They are two items, not one item with two arms** — different solver,
different case, different mesh and a different multipoint axis. The incompressible item is being
built elsewhere and is untouched here. **This document scopes only the compressible one.**

---

# 0. THE FOUR THINGS A READER SHOULD TAKE FIRST

1. **A compressible multipoint optimisation HAS landed, and the standing picture that says none has
   is false as stated.** `CURRICULUM-D19M` graded **`GATE REACHED`**, both rows, 2026-09-01, on
   `DARhoSimpleFoam` at M 0.288, NACA0012, 4,032 cells, 35.166 core-min. **§1.1.** What has never
   landed is a compressible multipoint on a **Mach** axis, and no compressible multipoint has
   reached `PASS`.
2. **The reason D19M could not reach `PASS` is the thing that must be bought first.** Its registered
   verdict ceiling names it: *the compressible single-point gradient this optimisation spends has NO
   GRADED VERDICT and its plateau did NOT close.* **§1.1c.** A new item that repeats that mistake
   buys a capped verdict for thousands of core-minutes.
3. **A3's validated 399,360-cell ONERA M6 CANNOT carry this item and something cheaper IS better —
   on three independent grounds, all measured. §2.4.** The honest candidate is **A6 CRM wing-alone,
   41,760 cells**, and its own weakness is named rather than hidden: **it has no validation against
   a public primary at all (§2.3b).** A3 has the reference and no adjoint; A6 has the adjoint and no
   reference. **That is the scoping fact of this item.**
4. **Memory is NOT the wall for a compressible adjoint on this box, and saying it is would be the
   L-15 error a second time. Conditioning is the wall, and it binds between 42,120 and 79,560 cells
   with memory comfortable — peak 11.65 GiB against a 22 GiB cap at the wall. §3.** The one real
   memory question is **N simultaneous solver instances, not cell count**, and the two readings on
   disk disagree by 43 % and cannot be resolved from disk. **§3.4.**
5. **A correction that travels wider than this item: the `59.1 GiB` D8G L3 adjoint figure is a MODEL
   PREDICTION on an arm marked `NOT ATTEMPTED`, not a measurement.** It is affine model M2 at 356,352
   cells. **§3.1b.** The `BLOCKED` it supports is real and is **double** — the second ground,
   conditioning, IS measured, at a mesh 4.48× smaller, and it is the one that should be quoted,
   because a memory number invites renting hardware and a conditioning number does not.
6. **No figure in this document stops a run. §5.5.** Costs are calibration figures; the full expected
   spend is written out as a number instead — **≈ 3,834 core-min for the whole programme, of which
   ≈ 518 is the FD tables alone (§5.5a).**

**Recommendation, with the number that decides it: §6.**

---

# 1. WHAT EXISTS ON DISK ALREADY — MEASURED, NOT ASSUMED

`docs/dafoam/PRIOR_WORK_INVENTORY.md` was read before anything below was called new. Its record
count re-derived on disk rather than quoted: **PART A 42 records (`:39`) + PART B 41 records
(`:508`) = 83.** **The string `multipoint` does not occur anywhere in that file** — checked with a
live control in the same reader (`SO-3`/`mach` return hits at `:72`, `:76`, `:84`), so the zero is a
measured zero, not a grep artefact (`CLAUDE.md` rule 3). **The inventory is therefore silent on
multipoint and is not the authority on it; the authority is the case tree, swept ignore-blind below.**

## 1.1 THE CORRECTION: a compressible multipoint optimisation already landed

| | |
|---|---|
| item | **`CURRICULUM-D19M`** — NACA0012 **compressible α-multipoint shape optimisation**, `DARhoSimpleFoam`, **M 0.288**, ladder A1, **4,032 cells**, np = 1 |
| verdict | **`GATE REACHED`**, both rows; `rows_capped_by_ceiling: ["SHIPPED","PATCHED"]`, each `verdict_before_ceiling: "PASS"` |
| objective | `J = Σᵢ wᵢ·CDᵢ(αᵢ)`, α = 2.787333582 / 4.787333582 / 6.787333582 deg, equal weights, one shared 8-component `shape` |
| optimiser | IPOPT printed **`Optimal Solution Found.`** on **both** rows, 10 iterations, `max_iter` 40 not reached |
| endpoint FD | both rows passed band D and band E on every graded component |
| cost, MEASURED | **35.166 core-min**, ratio **1.0313** against 34.10 predicted, ceiling 149.0 |
| record | `cases/dafoam/ladder-a/A1/curriculum_D19M/RESULTS.md` |

**So S-111's reading — "NO compressible multipoint OPT has ever landed" — does not survive contact
with the disk.** The correct statement is narrower and more useful: **no compressible multipoint has
landed `PASS`, and none has ever run on a Mach axis.** D19M's axis is α; its Mach is fixed at 0.288.

### 1.1b The caveat D19M carries, which a Mach-axis successor must not inherit
`CL` was **unconstrained** (α is the operating point, so there is no DV to trim with) and **the lift
collapsed at all three points, negative at point0**: `CL` final PATCHED **−0.15737 / +0.07216 /
+0.30540** against baseline **0.29875 / 0.50000 / 0.67366** (`RESULTS.md` §2.1). The 25.98 % weighted
drag reduction **grades nothing** (`DAFOAM_CHARTER.md` §9) and is not reportable without the lift
triple in the same frame. **A successor holds `CL` by per-point equality constraint or it reproduces
this.** The A6 base proposed below already does (§2.3).

### 1.1c THE CEILING, VERBATIM — and it is the single most expensive fact in this document
`d19m_grade.py`'s `verdict_ceiling_reason`, registered before the run:

> The compressible single-point gradient this optimisation spends has NO GRADED VERDICT (D19R's
> grader refused rc=2; D19R2 grading attempt 1 = NOT A RESULT) and its plateau did NOT close
> (all_two_sided=false, score_pct=21.060684242435336, binding=[shape[7],CD,fine]). DAFOAM_CHARTER.md
> section 1: a gradient is not a result until an FD table stands beside it at a step PROVED to lie
> in the plateau. This item therefore cannot publish PASS on any row or at item level, whatever its
> gates return. REGISTERED BEFORE THE RUN.

**Still unclosed today.** `cases/dafoam/ladder-a/A1/curriculum_D19R2/RESULTS.md`: grading attempt 1
**`NOT A RESULT`**, grader refused `rc = 2`, no grade JSON written, **0.00096 core-min**, zero solver
core-minutes. **The A1-compressible plateau has no closed reading on disk.**

**The operative consequence for this item: an optimisation whose gradient basis is not itself graded
is ceiling-capped no matter how clean it runs.** That is not a risk; it is a measured outcome that
has already happened once, to the most recent compressible multipoint this lab ran.

## 1.2 Every compressible DAFoam case on disk, swept ignore-blind

Swept with `find … -print0 | xargs -0 grep` rather than `grep -r`, because `grep` is `ugrep` in this
environment and honours ignore files.

| case | solver | M | cells | primal | adjoint | optimisation | external reference |
|---|---|---|---|---|---|---|---|
| **A2** MACH tutorial wing | `DARhoSimpleFoam` | ≈ 0.3 | **38,304** | converged, CD 0.02772949388 / CL 0.4775877833 reproduced to **all ten printed digits** from a pristine clone | **FD `PASS`**, 105 DVs, regraded under the corrected IDWarp derivative (CD/shape 1.71 → **0.0506 %**, CL/shape 1.17 → **0.0219 %**), 18 of 18 `check_totals` rows identical to the published log | IPOPT 47 majors, **`GATE REACHED`** — `converged_to_optimizer_tolerance: false`, no `EXIT` line in `opt_IPOPT.txt` | code-to-code only (the tutorial's own published log) |
| **A3** ONERA M6 | `DARhoSimpleCFoam` | **0.840** | 21,840 / 42,120 / 79,560 / 99,840 / **399,360** / 798,720 | converges 21,840 upward; **10,920 will not converge** — nothing to linearise about | **rungs 1 (21,840) + 2 (42,120) CONVERGE and are FD-verified** with `transonicPCOption 1`; **rung 3 (79,560) `-3` STAGNATION**; **399,360 OOM at 12g and 18g, never produced an adjoint** | **never converged at any size** | AGARD AR-138 Case 2308 — **on disk, and compromised: §2.4** |
| **A6 wing-alone** | `DARhoSimpleCFoam` | **0.850** | **41,760** (D8R) ; 5,568 / 44,544 / 356,352 (D8G family) | converged, `primalMinResTol 1e-8` | **`PASS`, two rows, 517 GMRES iterations, `PetscConvergedReason: 2`**, monotone over six decades | **`PASS`, two rows** — IPOPT printed `Optimal Solution Found.` at **8** (PATCHED) and **12** (SHIPPED) majors, **endpoint FD 20/20 components `PASS`, 0 sign flips** | **NONE — never run against a public primary (§2.3b)** |
| **A6 wing-body** | `DARhoSimpleCFoam` | 0.850 | **579,072** | converged; CD 0.0209014 matches the DAFoam tutorial baseline to **0.0067 %** | **never attempted**; memory-predicted 95–116 GiB against a 30 GiB box — **`BLOCKED`** | never | code-to-code only |
| **A1 D16** | `DARhoSimpleCFoam` | 0.685 | 4,032 | ran | FD-vs-adjoint at baseline | — | — |
| **A1 D19 family** | `DARhoSimpleFoam` | 0.288 | 4,032 | ran | **plateau NOT closed — §1.1c** | **D19M `GATE REACHED`** | — |
| **A1 MAAOA** | `DARhoSimpleFoam` | 0.288 → 0.685 | **130,304** (wall-resolved L3) | **ALL SIX compressible points `Primal solution failed!`** | — | — | — |
| **D17** cone | `DAHisaFoam` | 1.958 | — | inviscid wedge | — | — | — |

### 1.2a The one Mach-axis attempt on record, and it failed at the primal
`MAAOA` (`cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/RESULTS.md`) is the lab's only fixed-lift
Mach sweep. **Item outcome: NO VERDICT OF RECORD** — the frozen reader refused at `rc = 2`. But the
physics survives the bookkeeping (Sanaa 2026-08-26), and it is unambiguous: **all six compressible
points returned `Primal solution failed!`** at M 0.288 / 0.400 / 0.500 / 0.600 / 0.650 / 0.685 on
the 130,304-cell wall-resolved mesh, each running its full 4,000-iteration `endTime` inside its
7,200 s deadline, none retried, none relaxed. Only the incompressible control converged
(`FindFeasibleDesign Converged!`). **Cost: 664.0 core-min gross against 315 registered, ratio 2.108.**

**What this buys the present item:** a **measured refutation** of the cheapest-looking route — put a
Mach axis on the A1 wall-resolved mesh with `DARhoSimpleFoam`. It has been tried, it cost 664
core-min, and the primal does not survive fixed-lift trim anywhere on the axis. **That route is
closed and must not be re-bought.**

## 1.3 The multipoint machinery already exists and is measured
- **The mphys shape.** One `Multipoint` model, N `ScenarioAerodynamic` built from N `DAFoamBuilder`s,
  **one shared `OM_DVGEOCOMP`**, weighted objective as an `om.ExecComp`, per-scenario constraints —
  `cases/dafoam/ladder-a/A1/SO3_MULTIPOINT_SCOPE_MEMO.md` §2, and instantiated in `D6`, `SO-3`,
  `MP-A1`. **Nothing here needs inventing.**
- **Per-point run directories.** One `DASolver` per operating point, each in its own `run_directory`
  (`mp0/mp1/mp2`) — the SO-3aR collision cure (`curriculum_MP_A1/PREREGISTRATION.md` §1.3).
- **Three-point compressible multipoint has run on this box.** `D6` `O_mp`: 3 scenarios, np = 4,
  **20 g cgroup**, `OOMKilled = false`, 30,008 wall s, `rc = 124` at its own registered deadline
  (`docs/COST_CALIBRATION.md` **C-188**). **Three Jacobian colourings** are recorded in that row, so
  three independent adjoint machineries were built and exercised.

---

# 2. THE CANDIDATE — AND WHY THE VALIDATED CASE IS NOT IT

## 2.1 What a multipoint *optimisation* actually requires
Not a primal at every point. **An adjoint at every point, at every major iteration**, plus an FD
table beside it (`DAFOAM_CHARTER.md` §1, §2) and a second one at the final design point (§9). The
candidate must therefore sit inside the **adjoint-capable** window, not merely the primal-capable one.

## 2.2 The adjoint-capable window for `DARhoSimpleCFoam`, measured

| cells | outcome | evidence |
|---|---|---|
| 10,920 | **primal will not converge** — 1000 SIMPLE iterations, residuals plateau 1e-3–1e-5 against a 1e-6 tolerance. Nothing to linearise about. | `cases/dafoam/ADJOINT_MEMORY_ENVELOPE.md` |
| 21,840 | **CONVERGES + FD-verified** (`transonicPCOption 1`) | `cases/dafoam/A3_RUNG3_N52_RESULT.md:88-89` |
| **41,760** | **CONVERGES**, 517 GMRES iterations, `PetscConvergedReason: 2`, monotone over six decades. Peak RSS **9.787 GiB at np = 1**. | `ladder-a/A6/rung_n16_np1/RESULTS.md` §5; `cases/dafoam/EXPERTISE_CURRICULUM.md:65` |
| **42,120** | **CONVERGES + FD PASS**: both adjoint solves `PetscConvergedReason: 2`; `patchV[1]` **0.0077 %**, `twist[1]` **0.2740 %**, `shape[115]` **0.0172 %**. Needed **987** GMRES iterations — **1.91× A6's 517 at the same size.** | `cases/dafoam/A3_RUNG2_N28_RESULT.md:1,13,20-30` |
| 79,560 | **`-3` STAGNATION.** 4,000-iteration cap; total residual reduction **1.31×**; residual change over iterations 1300→4000 **3.79e-07 relative** — flat. **Peak 11.65 GiB against a 22 GiB cap, `MemAvailable` never below 17 GB, no OOM.** | `A3_RUNG3_N52_RESULT.md:20-41, 50-51` |
| 99,840 | `DIVERGED_BREAKDOWN` at `transonicPCOption` off; peak 18.4–20.5 GiB | `ADJOINT_MEMORY_ENVELOPE.md` Option 2 |
| 399,360 | **OOM at 12 g and 18 g. No adjoint has ever existed on this mesh.** | `ladder-a/A3_onera_m6.md`; inventory §1d |
| 579,072 | **never attempted**, predicted 95–116 GiB against 30 GiB | `A6/adjoint_feasibility/RESULTS.md` |

**The window is 21,840 – 42,120 cells confirmed working, with the ceiling BRACKETED between 42,120
and 79,560** (`A3_RUNG3_N52_RESULT.md:62-64`, which explicitly declines to claim 79,560 is *the*
boundary). **Any compressible multipoint candidate sits at or below ~42,000 cells or it is `BLOCKED`
before it starts.**

## 2.3 The candidate: **A6 CRM wing-alone, 41,760 cells** (D8R's mesh)

It is the only compressible case in this lab that has already produced **a converged optimisation
with endpoint FD tables on both toolchain rows**, which is exactly the artefact a multipoint
successor has to reproduce three times over.

| property | value | artifact |
|---|---|---|
| mesh | **41,760 cells**, 45,104 points, 128,574 faces; patches `wing` (2784), `inout` (2784), `sym` (1020) | `cases/dafoam/D8R_RENDER_PREP_2026-09-10.md:28` |
| mesh identity | `points_md5` **`11b84f0de5fdf2d3e947fee8cea412a9`**, equal on all four D8R arms | `D8R_grade_20260828T021329Z.json`, `G-M2_mesh_identity` `PASS` |
| solver / regime | `DARhoSimpleCFoam`, **M 0.850**, transonic, SA, wall-function, `transonicPCOption 1`, `primalMinResTol 1e-8` | `ladder-a/A6/curriculum_D8R/PREREGISTRATION.md` |
| DVs | `twist`, **N = 16**; `patchV` used as the CL trim variable, not a graded DV | same |
| lift | **CL held at 0.5 by `findFeasibleDesign` trim, `tol 1e-3`, `maxIter 4`** — so D19M's lift-collapse caveat does **not** transfer | `PREREGISTRATION.md:35` |
| item verdict | **`PASS`, two rows** | `curriculum_D8R/RESULTS.md` §0 |
| optimiser terminus | `EXIT: Optimal Solution Found.` on **both** rows, **8** majors PATCHED, **12** SHIPPED, `max_iter 30` not reached | `RESULTS.md` §0.1 |
| endpoint FD | **four tables, 20 graded components, 20 `PASS`, 0 `GATE FAIL`, 0 sign flips**; aggregates 0.6458 / 0.0884 / 0.9015 / 0.1068 % against band E 5.0 %; worst single component **3.9170 %** inside band D's 5.0 % | `RESULTS.md` §1 |
| plateau proof | printed per component, not asserted; **worst `min(neighbour) = 2.2739 %` against a 10 % tolerance — 4.40× clearance** | `RESULTS.md` §1 |
| adjoint memory | **9.970 GiB at np = 1** (one instance, one adjoint); primal-only arm **0.658 GiB** | `PREREGISTRATION.md:74` |
| cost, MEASURED | **876.867 core-min**, ratio **0.8447** against 1,038.0, ceiling 2,240.0 | `RESULTS.md` §10; `COST_CALIBRATION.md` C-191 |

### 2.3a Why A6 and not A3 rung 2 (42,120 cells), which is the same size and IS FD-verified
Three measured reasons. (i) **A3's adjoint costs 1.91× A6's at the same mesh size** — 987 GMRES
iterations against 517. On an item that solves six adjoints per major that is the difference between
affordable and not. (ii) **A3 has never converged an optimisation at any size**; A6 has, twice, with
endpoint FD on both rows. (iii) A3's rung-2 FD verification is a **baseline** verification; A6's is a
**final-design-point** verification, which is what `DAFOAM_CHARTER.md` §9 actually requires of an
optimisation and which A3 has never produced.

### 2.3b **A6's weakness, named rather than buried: it has NO external validation**
`cases/dafoam/MATRIX_CONTRIBUTION.md:259`, row `G-27`, in its own words: **"NEVER RUN — no
validation against a public primary"**. The only reference A6 holds is code-to-code — the DAFoam
tutorial's own published baseline `CD = 0.02090`, matched to **0.0067 %**, and that at 579,072 cells,
**not** at 41,760. **A compressible multipoint on A6 is a VERIFICATION item, not a VALIDATION item,
and its pre-registration must say so on its first screen.** It may claim that the adjoint gradient
agrees with finite differences and that the optimiser converged to its own tolerance. **It may not
claim agreement with experiment, because no experiment is in its chain.**

## 2.4 **A3's 399,360-cell ONERA M6 assessed as the brief asks — and something cheaper IS better**

The brief offers A3's transonic case, validated against AGARD AR-138 Case 2308 at pooled RMS
**0.0575** Cp over 260 points (the figure is real and is at
`cases/dafoam/ladder-a/A3/curriculum_A3GC/PREREGISTRATION.md:328`). **It cannot carry this item, on
three independent grounds, and any one of them is sufficient.**

**(1) It has never produced an adjoint and is not predicted to.** OOM at both 12 g and 18 g under
**eight** mitigations (two memory caps, two rank counts, `gmresRestart` 1000→200, `pcFillLevel` 1→0);
`decomposePar` SEGV twice at 24,960. The structural cause is not tunable: **OpenMDAO's reverse sweep
builds a mesh-sized `d[residuals]/d[vol_coords]` block for ANY requested total derivative, so
restricting `wrt=` does not avoid it** (`ladder-a/A3_onera_m6.md`; inventory §1d). The M6-family
memory fit puts it at **67.0 GiB against a 30 GiB box** (§3.2). **A multipoint optimisation needs an
adjoint at every point at every major. Zero adjoints is not a starting position.**

**(2) The AGARD comparison is post-hoc and is registered by nothing.** **46** files matching
`*PREREGISTRATION*` under `cases/dafoam/` were searched ignore-blind and **not one registers a `Cp`
band, an RMS threshold or any gate against AGARD 2308**; the single hit in all 46 is a flow-condition
note at `A3_SUBLU_PREREGISTRATION.md:15` (`MATRIX_CONTRIBUTION.md:780`, which records the control
that makes that zero readable). **A reference the lab has never gated against is not a reference an
item can gate against** without registering it fresh — which is available, but is not a saving.

**(3) A3's geometry differs from the reference it is validated against, and the difference grows
outboard.** `ladder-a/A3_onera_m6.md` NOTE and NOTE 2, 2026-09-11: the AGARD Table B1-1 section runs
a constant 7.06° taper to a **blunt base** of half-thickness `z/l = 7.052e-4`; A3's surface adds a
**rounded cap over the last ~0.4 % of chord** and closes to a point, zero cells across the trailing
edge. The deviation is **span-varying and monotone outboard** — TE half-thickness is flat in absolute
terms (6.8879e-04 / 6.8603e-04 / 7.1352e-04 m root/mid/tip) where the conical loft requires
`t_TE/c` constant, making `t_TE/c` **~1.78× larger at the tip than at the root**. The lab's own
standing consequence: **"A3 MUST NOT BE PRESENTED AS VALIDATING THE ONERA M6 OUTBOARD."** The
worst-agreeing station (η = 0.99, upper-surface RMS 0.1139, mean bias +0.065) is also the most
geometrically wrong one, and the two explanations **cannot be separated from what is on disk**.

**Plainly, as the brief asks: yes, something cheaper is better. A6 CRM wing-alone at 41,760 cells is
9.6× smaller, has a converged optimisation and endpoint FD tables on both rows, and is inside the
adjoint-capable window instead of three walls outside it. The price of choosing it is that the item
loses an external reference it could not have gated against anyway — and the pre-registration says
so rather than letting a reader assume otherwise.**

---

# 3. THE HONEST FEASIBILITY QUESTION, ANSWERED WITH NUMBERS

## 3.1 The two findings the brief asks be checked rather than recalled — both checked, one superseded

**(a) A3 campaign 1 died on a mesh-sized `d[residuals]/d[vol_coords]` matrix.** **CONFIRMED**, and
the mechanism is structural, not a tuning failure — `cases/dafoam/ADJOINT_MEMORY_ENVELOPE.json`,
`structural_cause`, and `ladder-a/A3_onera_m6.md`. A second structural fact rides with it and must
not be forgotten when sizing: **DAFoam rejects OpenFOAM `empty` patches** (`DACheckGeometry.C:278`),
so *every nominally-2D DAFoam case is a true 3D solve and both Jacobian blocks are sized for the 3D
mesh*. **There is no cheaper 2D adjoint path on this installation.**

**(b) D8G's L3 adjoint at 59.1 GiB (46.5 de-biased), BLOCKED on a 30 GiB box and independently
BLOCKED on conditioning.** **CONFIRMED IN SUBSTANCE — AND ONE WORD IN IT IS WRONG EVERYWHERE IT IS
REPEATED, INCLUDING IN THE BRIEF THAT SENT ME LOOKING.** The figures are located, at
`cases/dafoam/ladder-a/A6/curriculum_D8G/PREREGISTRATION.md:448` and `:564`, and they are:

> **L3 adjoint** | M2 → 2,048 + 58,442 = 60,490 MiB = **59.1 GiB**; de-biased by the model's measured
> 1.27× overprediction → **46.5 GiB** | — | — | **NOT ATTEMPTED — see §7**

**`59.1 GiB` IS A MODEL PREDICTION, NOT A MEASUREMENT.** It is model **M2**, affine —
`2,048 MiB fixed + 0.16400 MiB/cell` — evaluated at **356,352 cells** (D8G's L3, A6 CRM wing-alone),
and the arm's own status field reads **`NOT ATTEMPTED`**. No adjoint was ever launched at that level,
so no peak RSS exists for it. **A record that calls it "measured" is wrong, and `DAFOAM_CHARTER.md`
§7 is the clause that makes the distinction load-bearing rather than pedantic: *"The prediction is
what makes the BLOCKED honest"* — a prediction is what §7 requires **before** the launch, and calling
it a measurement afterwards is the failure the same clause names against the NASA-hump `docker stop`
that was published as if a stop were a measurement.**

**The finding is not weakened by the correction; it is sharpened.** The `BLOCKED` is **double**, and
D8G §7 names both grounds precisely so that naming only memory is not the **L-15** error: (1) memory,
M2-predicted 59.1 GiB / 46.5 de-biased against a 30 GiB box; (2) **conditioning, independently** —
`DARhoSimpleCFoam` stagnates at **79,560 cells with memory comfortable** (11.65 of 22 GiB,
`PetscConvergedReason: -3`), and L3 is **4.48×** that size. **Ground (2) is a MEASUREMENT and it
alone is sufficient.** The same double form is on record for A6 wing-body at 579,072 cells
(94.7–116 GiB **and** conditioning — `DAFOAM_CHARTER.md` §7).

**Why it matters here and not only as bookkeeping:** the memory ground is a *prediction* that could
be wrong by the model's own admitted 1.27× bias in either direction; the conditioning ground is a
*measurement* at a mesh **4.48× smaller**. **A reader who carries only the memory number can be
talked into renting hardware. A reader who carries the conditioning number cannot.**

## 3.2 **At what cell count does a compressible adjoint actually fit in 30 GiB?**

From the M6-family fit already on disk (`ADJOINT_MEMORY_ENVELOPE.md` L425-445, three measured
aggregate cgroup points at np = 4, `numpy.polyfit`, **R² = 0.9992**, and read by
`scripts/self_audit.py:4392` on content regexes):

**memory (MiB) = 1.2125 × cells^0.8485** — measured 21,840 → 5,876.6 MiB; 42,120 → 9,991.9;
79,560 → 17,603.8. **The exponent is SUBLINEAR: doubling the mesh costs ~1.8× the memory.**

Inverted (**by me, from the published law, EXTRAPOLATED above 79,560 cells and labelled as such**):

| ceiling | cells | status |
|---|---|---|
| **30 GiB** (whole box) | **≈ 154,900** | **EXTRAPOLATED — 1.95× beyond the fit's top point** |
| 28 GiB | ≈ 142,800 | EXTRAPOLATED |
| 22 GiB (A3 rung 3's own cap) | ≈ 107,500 | EXTRAPOLATED, 1.35× beyond |
| 20 GiB | ≈ 96,100 | EXTRAPOLATED, 1.21× beyond |
| 14 GiB (D8R's O-arm cap) | ≈ 63,100 | inside the fitted range |

Forward, for the cases that matter: **41,760 → 9.86 GiB**, **42,120 → 9.94**, **44,544 → 10.42**,
**79,560 → 17.05** (measured 17.60, −3.1 %), **399,360 → 67.0 GiB**, **579,072 → 91.9 GiB**.

**THE ANSWER, AND IT IS NOT THE USEFUL NUMBER: ~155,000 cells by the fit — and it does not matter,
because the adjoint stops converging somewhere between 42,120 and 79,560 cells, a factor of 2.0–3.7
BELOW that.** Memory is not the binding constraint anywhere in the range this item can occupy.
`A3_RUNG3_N52_RESULT.md:50-51` is the proof in one line: at the wall, **peak 11.65 GiB against a
22 GiB cap**, host `MemAvailable` never below 17 GB, no swap growth, no OOM. **Conditioning binds;
RAM does not. Renting memory buys nothing here** — and `ADJOINT_MEMORY_ENVELOPE.md` AMENDMENT 2 §B
exists specifically to foreclose that decision.

## 3.3 The conditioning wall, and how dry the lever well is
**Twelve conditioning levers eliminated with numbers** (`A3/grading_confirmation/RESULTS.md:215-235`),
including `renumberMesh`/CuthillMcKee (**already spent at mesh build on every rung**: band 73,452 →
1,550), `pcFillLevel 0→1` (residual improves **1.859×**), L3 Richardson (**collapses to double `-5`
at exactly iteration 200**, the first restart boundary), `gmresRestart 200→1000` (**1.647×** against
a pre-registered 10× bar), `-ksp_type lgmres` (**5.10× WORSE**), `-pc_type gamg` (**residual
7.55e+179**, diverged), `asmOverlap 1→2` (**1.062× worse**). The diagnostics refused to discriminate:
preconditioned κ = **9.57e+10** at rung 3; diagonal spread **14.47 decades** at the stalling rung
against **14.40** at the converging one; Hutchinson non-normality **0.617** against a ≥ 3.0 bar — **the
stalling rung is LESS non-normal than the converging one.**

**One genuinely untried free lever remains: `jacMatReOrdering: natural → nd`.** Every A3 rung ran
`natural`; `nd` has never run on M6. Pre-registered as **A3FL1 / A3FL2**, and **neither directory
contains a RESULTS file — `PENDING`**, with a pessimistic prior in its own registration.

**Relevance to this item: none, and that is the point.** The candidate sits at 41,760 cells, inside
the confirmed-working window, **below** the wall. **This item does not need the conditioning problem
solved. It needs to stay away from it, and the mesh choice is what does that.**

## 3.4 **The real memory question: N simultaneous solver instances — and the two readings on disk
disagree by 43 %**

A multipoint model holds **one `DASolver` per operating point, alive simultaneously**, each with its
own `dRdW` / `dRdWTPC` and its own Jacobian colouring. The cell count is unchanged; the instance
count is three.

| reading | figure | basis | what it is |
|---|---|---|---|
| **Scaled from D8's single-instance measurement** | **≈ 28.6 GiB** at np = 1 = `0.658 + 3 × (9.970 − 0.658)` | D8 measured **9.970 GiB** for one adjoint at 41,760 cells np = 1; primal-only arm **0.658 GiB** (`D8R PREREGISTRATION.md:74`) | **EXTRAPOLATED by me.** Assumes each instance carries a full independent Jacobian |
| **Measured, cross-case** | **≤ 20 GiB**, three scenarios, np = 4, `OOMKilled = false` | D6 `O_mp`, A2 MACH wing, **38,304 cells**, `DARhoSimpleFoam`, 30,008 wall s, three Jacobian colourings recorded (`COST_CALIBRATION.md` **C-188**) | **A CEILING, NOT A PEAK.** `OOMKilled = false` at a 20 g cap bounds the peak above; no peak RSS was recorded |

**These cannot be reconciled from disk and I do not pretend otherwise.** Against them: D6 is
`DARhoSimpleFoam` at M ≈ 0.3 and the candidate is `DARhoSimpleCFoam` at M 0.85, whose adjoint carries
a transonic preconditioner matrix D6's does not; 38,304 cells vs 41,760 is close (+9.0 %) and is not
the discrepancy. **If the 28.6 GiB reading is right, a THREE-point multipoint at 41,760 cells does
not fit a 30 GiB box shared with four other teams and the item is `BLOCKED`. If the D6 ceiling
transfers, it fits at a 22 g cap with the aggregate rule satisfied** (22 + 6.52 GiB measured host
non-container RSS = 28.5 < 30.6).

**A TWO-point variant is comfortable under either reading:** `0.658 + 2 × 9.312 = 19.3 GiB` at np = 1
by the pessimistic scaling, below D6's measured three-scenario ceiling by the optimistic one.

**This single unresolved number — three instances or two — is the first thing the recommended
experiment buys (§6.2), and it costs one arm to settle.**

---

# 4. THE BRIGHT LINE, COSTED

> *"A DAFoam gradient is not a result until a finite-difference table stands beside it at a step
> proved to lie in the plateau, and a DAFoam verdict is two rows — shipped and patched — or it is
> not a verdict about DAFoam."* — `DAFOAM_CHARTER.md` §1

## 4.1 Two rows, and both toolchains asserted present by hash, never by version string
`docker images` read once, read-only, zero compute. **Both digests are on this box today:**

| row | image | digest (identity) | IDWarp `libidwarp.so` md5 |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663`, 491,344 B |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425`, 491,344 B |

Both md5s cited to `docs/dafoam/TOOLCHAIN_INVENTORY.md:409-410`; both digests match D8R's own
`G9_toolchain` `PASS`, which asserted `printed_so_md5 == artefact_so_md5` on all four arms. **The two
`.so` md5s are distinct, so the two rows are not one toolchain wearing two labels.** **No version
string identifies anything in this item** — the rotation patch moves issue-57 DOF 0 by seven orders
of magnitude (**210.16 % → 8.56e-06 %**) while the version string reads `2.6.2` either way.

**Cost consequence, stated because it is the most commonly dropped factor: two rows DOUBLES every
figure in §5. A single-row plan is not a DAFoam verdict and is not cheaper — it is incomplete.**

## 4.2 The FD table's true shape on a multipoint objective — **this is the term that gets omitted**

`J = Σᵢ wᵢ·CDᵢ` is a function of **all** operating points. **A single perturbed evaluation of `J`
requires a primal at EVERY point.** That is the multiplication the brief warns about, and it is
structural, not conservative padding.

The charter does not permit the cheap form. §3 requires **a step proved to lie in the plateau, read
per component**, and `VERIFICATION_CHARTER.md` §7 fixes the sweep table with its failed steps as
rows. D8R's registered instantiation — the one that produced a `PASS` — is **central differences,
three steps `{3e-2, 1e-1, 3e-1}` degrees, middle step the reference, plateau tolerance 10 %,
5 graded components + a planted `CTRL`**, and it costs **32 primals per arm** at one operating point.

| form | primals per row | note |
|---|---|---|
| the brief's `N_dv + 1` per point per row, one-sided, single step | 5 + 1 = 6, × 3 points = **18** | **not admissible.** One step proves no plateau (`DAFOAM_CHARTER.md` §3: *"Quoting an FD number from a single step"* is forbidden) |
| **D8R's registered form, lifted to 3 points** | 5 comp × 3 steps × 2 sides × 3 points + 2 η × 3 = **96** | **5.3× the brief's figure** |
| both rows | **192 primals** | |

**A plan that costs 18 primals where the charter requires 96 is the plan that gets cancelled
halfway.** This document costs 96.

## 4.3 The planted control, and the trivial baseline — both owed, both cheap
- **Planted zero (`CLAUDE.md` rule 3).** D8R carried a `CTRL` planted component and
  `grader_controls/F_S_planted.json` / `F_P_planted.json`. **Carried forward; ~2 primals per row.**
- **The registered trivial baseline (`DAFOAM_CHARTER.md` §4): the same probe at a deliberately
  wrong step, an order of magnitude off the registered one.** D8R's `G-TB` passed on both rows.
  On a **multipoint** objective a second candidate exists and is arguably sharper — **score the
  gradient against SHUFFLED weights** (`SO3_MULTIPOINT_SCOPE_MEMO.md` §5 item 5), because the
  weighted objective's gradient is a linear combination. **Both are cheap; which one is registered
  is a registration decision, not this document's.**

---

# 5. COST, UNDER THE CONVENTION ADOPTED 2026-09-12

`docs/COST_CALIBRATION.md`, row `C-20260912T005048.507107Z-c94d1535`, verbatim:

> every future dafoam registration costs `C = F(n) + r(N)·N·iters + W(N, writes)` as **three
> separately named terms, never one**; `F` is cited to a measured `waited_s`, never assumed; `r(N)`
> is anchored at or near the target cell count and **never extrapolated DOWN more than ~4×** without
> widening the band upward by the measured 1.44–2.16× penalty; `W` is costed **per write**; **and
> the registration must state what fraction of `F` is idle-core rent, because that is the number
> that decides `np`.**

## 5.1 `F(n)` — the fixed per-arm term, and **92 % of it is idle-core rent**

**`F(n) = 3.6 × n` core-min**, band 3.6–3.9. **Cited to a measured `waited_s`, not assumed:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple/ledger.txt`,
`D8G_LAUNCH_ASSERTED … waited_s=215 budget_s=352` → 215 s pre-first-iteration + 5 s post-solve and
teardown = 220 s × 4 ÷ 60 = **14.667 core-min at n = 4**. Independently, A3GC's stopped run measured
**15.419 core-min** at n = 4 by the same basis. **17.9× apart in cells (5,568 vs 99,840), 5.1 %
apart in overhead — the constant is mesh-independent.**

**The idle-core-rent fraction, which is the number that decides `np`.** From the cgroup sampler's own
series, `L1-P_20260911T234236Z_2435242.cpu.jsonl`, 14 samples over 196.8 s: for the **first 166.5 s
the container delivered 0.0847–0.2917 cores of the 4 it held — twelve consecutive samples, none above
0.30** — jumping to 1.3153 only at +181.7 s, which is the solve beginning.

| window | delivered of 4 | **IDLE-CORE RENT** |
|---|---|---|
| whole `F` window (`delivered_cores_mean` 0.3150) | **7.88 %** | **92.12 %** |
| first 166.5 s (0.0847–0.2917) | 2.12 – 7.29 % | **92.71 – 97.88 %** |

**≈ 92 % of `F` is cores held and not used** — container start, TensorFlow import, `DASolver`
construction, all essentially serial and I/O-bound. **It is still costed at `n`, because the cores
are genuinely held and unavailable to cfd, heat-transfer and ansys-verification.**

**On a multipoint arm the exposure compounds: three `DASolver` constructions inside one container.**
`F` is paid once for the container but the serial construction phase is ~3× longer, so the honest
figure for a 3-point arm is **`F_mp(n) ≈ 3.6n` with the serial phase extended**, and the arm should
**measure** it rather than inherit `3.6n`.

### 5.1a **The np decision, and it is MEASURED on this exact case**
| basis | per-major cost | source |
|---|---|---|
| **np = 1** | **14.75 core-min/major** (885 s/rank/60) | D8's fitted wall model, `wall(N) = 2,927 + 885N` s, which **reproduces D8's measured 5,251 s at N = 3 to 1.5 %** (`D8R PREREGISTRATION.md:58`) |
| **np = 4** | **34.589 – 37.808 core-min/major** (D8R `O-S` 429.467/12 and `O-P` 316.867/8, after removing `F(4) = 14.4`) | `D8R RESULTS.md` §10 |

**Ratio 2.35 – 2.56×. The same case, the same mesh, the same frozen producer, costs ~2.45× MORE
core-minutes at np = 4 than at np = 1** — and D8R's sampler shows the cores *were* delivered
(`delivered_cores_mean` 3.9501 / 3.9843 / 3.9969 / 3.9826 of 4), so this is real parallel
inefficiency, not contention.

**Therefore: `np = 1` for this item.** It costs 2.45× less of a shared 16-core box that is at load
**61.89** as this is written, and it drops `F` from 14.4 to **3.6 core-min per arm** (of which ~3.3
is idle rent instead of ~13.3). **The price is wall clock, and it is named: np = 1 is ~1.6× slower in
wall.** `COMPUTE_BUDGET_CHARTER.md`'s unit is core-minutes, not wall time, and it decides this.

## 5.2 `r(N)` — anchored AT the target cell count, not extrapolated to it

**The anchor is D8R itself: 41,760 cells, `DARhoSimpleCFoam`, `transonicPCOption 1`, the same mesh by
`points_md5`.** Extrapolation factor = **1.00**, so the 1.44–2.16× coarse-end penalty the convention
mandates for downward extrapolation **does not apply and no widening on that account is taken.** This
is the whole reason A6 is the candidate: the rate is measured where the item will run.

Component rates, np = 1, 41,760 cells, from `curriculum_D8/LANE_REPORT.md` §8 via
`D8R PREREGISTRATION.md:58` and `COST_CALIBRATION.md` **C-76**:

| component | measured | multipoint multiplier |
|---|---|---|
| container + imports + mesh | **231 s** | ×1 (one container) |
| one flow adjoint | **≈ 410 s** | **×3 points × 2 objectives = ×6 per gradient evaluation** |
| warm primal | **78.50 s** | ×3 |
| cold primal | 61–85 s | ×3 |
| cold primal + 5 trim primals | 409 s | ×3 |
| **one-off Jacobian colouring** | **≈ 591 s** | **×3 — one per `DASolver` instance** (D6 recorded three colourings) |
| endpoint primal + 2 endpoint adjoints | 60 + 816 s | ×3 |

**Cross-case corroboration for the multipoint penalty, and it is not flattering.** `C-188`: D6's
3-scenario multipoint measured **31.258 core-min/major against 19.167 registered** (a naive
3 × single-point) — **1.6308×**, *"the ×3 model is short by 63 %."* The row also records that D6's
optimiser was **backtracking** (545 line-search cutbacks, 7 restoration majors) and warns that *"a
rate calibrated on a converging optimiser does not price one that is backtracking, and the
successor's estimate must carry a stall branch."* **So 1.6308× is carried as the BAND TOP and as the
stall branch, not as the point.**

## 5.3 `W` — the write term, costed per write
`W` is costed **per write** because the convention says so and because A3GC costed **zero** writes
and paid **12.26 core-min at four checkpoints** — at 99,840 cells, np = 4, i.e. **≈ 3.07 core-min per
decomposed-field write**. Scaled to 41,760 cells at np = 1 by cell ratio and rank ratio:
**≈ 0.32 core-min per write [EXTRAPOLATED]**. An optimisation arm writing at each of ~20 majors × 3
points: **≈ 19 core-min per O arm.** Small, and **named rather than folded into `r(N)`.**

## 5.4 The three terms assembled — **estimating arithmetic, NOT a registered cost**

### (a) The gradient rung — a multipoint objective gradient with its FD table, both rows, np = 1

| arm | `F(1)` | `r(N)·N·iters` | `W` | total |
|---|---|---|---|---|
| `X` (gradient), per row | 3.85 | 3×591 colouring + 3×409 cold/trim + 3×820 gradient eval + 3×60 endpoint = **94.0** | ~1 | **≈ 99** |
| `F` (FD table, **96 primals**), per row | 3.85 | 96 × 78.50 s = **125.6** | 0 | **≈ 129** |
| **two rows** | | | | **≈ 456** |
| MESH | | | | ≈ 0.2 |
| **ITEM** | | | | **≈ 456 core-min = $0.390 DERIVED, NOT MEASURED** |

Band, carrying D6's 1.6308× on the gradient half only (the FD half is primals and does not stall):
**[380, 620] core-min.** Calibration figure (**NOT a stop — §5.5**) **900 core-min = $0.770 DERIVED**.

### (b) The optimisation rung — priced in full, **and not recommended for registration yet (§6)**

Per-major, 3 points, np = 1: structural **3 × 14.75 = 44.25** core-min/major; with D6's measured
penalty **3 × 14.75 × 1.6308 = 72.16** core-min/major.

| arm | point (20 majors, penalty applied) | upper reading (30 majors) |
|---|---|---|
| `O`, per row | 3.85 + 93.8 (colourings, cold/trim, endpoint) + 20 × 72.16 + 19 (`W`) = **≈ 1,560** | 30 × 72.16 + 117 = **≈ 2,282** |
| `F` endpoint (96 primals), per row | **≈ 129** | ≈ 194 |
| **two rows** | **≈ 3,378** | **≈ 4,952** |
| **ITEM point** | **≈ 3,378 core-min = $2.888 DERIVED** | **upper ≈ 4,952 core-min = $4.234 DERIVED** |

**Both columns are CALIBRATION FIGURES AND NEITHER IS A STOP (§5.5).** The right-hand column is the
honest upper reading of the expected spend at IPOPT's own `max_iter = 30` — **IPOPT's iteration limit
is the optimiser's own stop and is not a budget stop**, and `DAFOAM_CHARTER.md` §9 grades a run that
reaches it `GATE REACHED` or `NOT A RESULT`, never `PASS`.

**Wall clock, stated because np = 1 buys core-minutes with wall:** ≈ 3,378 wall-min ≈ **56 wall-hours
serial across four arms** at the point; ≈ 92 h at the cap. At np = 4 the same item is ≈ 8,200
core-min / ≈ 34 wall-h — **2.4× the shared resource to save 22 hours.**

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED. Every dollar figure
above is DERIVED, NEVER MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **0 GPU-h.**

### (c) What the estimate deliberately does NOT contain, stated rather than approximated
- **The multipoint memory measurement itself.** If §3.4's pessimistic reading holds, the 3-point O
  arm never runs and the optimisation figure is void. **Not padded for; §6.2 buys the answer.**
- **The `F_mp` extension for three serial `DASolver` constructions (§5.1).** Assumed ≈ `3.6n`;
  should be measured, not inherited.
- **Any Mach-point that fails to trim or converge.** D8R's CL trim is `maxIter 4, tol 1e-3` at
  M 0.85; **it has never been exercised at another Mach on this mesh** and a failure there is a
  registered outcome, not a retry (MAAOA's `rc = 97` discipline is the precedent).
- **`G6` dot-product / duality test.** `NOT MEASURED` in D8R — *"the tutorial exposes no
  dot-product/duality test"*. Named so this document cannot be read as implying it.

## 5.5 **NO CAP IN THIS DOCUMENT KILLS A RUN. A CAP IS A CALIBRATION FIGURE AND NEVER A KILL.**

**Every core-minute figure in §5 is a calibration figure.** None of them aborts, stops, refuses or
kills a run on spend, and **no successor may re-arm one as a kill by citing this document.** That
sentence is written in words, here, so a later reader cannot reconstruct a stop out of a number.

**Provenance, and it is RELAYED rather than verified by me.** A peer agent relayed, with provenance,
words attributed to Sanaa's own session turn ~2026-09-12T01:10Z: *"dont forget i dont want any cap on
any run, and that i bumped the volume to 1000 gib"*. **I could not verify it: `etc/sessions/` holds
no record newer than 2026-09-09** (§7). **No agent message is Sanaa's consent** (`CLAUDE.md` rule 9),
so this document does not treat the relay as authority and does not rely on it. It does not need to
— **§5.4 states the full expected spend as a number and leans on no cap at all**, which is what §5.5
requires whether the relay is accurate or not. The precedent for the *content* is on disk
independently and is not relayed: A3GC's and D8G's registrations both carry *"the cap is
CALIBRATION, NOT A STOP for this item"*, cited to Sanaa's Case Protocol closing clause of
2026-09-10 (`COST_CALIBRATION.md`, the A3GC and D8G rows).

**Rule 12's costing and calibration duties are UNTOUCHED and are not suspended by any of this.** This
item still owes: the full cost in core-minutes under the three named terms (§5.1–5.3); the estimate
against the actual at completion, with the ratio, the gap attributed by class, and waste named
separately and never folded into the ratio; and a row in `docs/COST_CALIBRATION.md`. **A completion
report without that comparison is incomplete.**

### 5.5a **THE HONEST FD-TABLE SPEND, STATED AS A NUMBER BECAUSE NOTHING BOUNDS IT**

With no cap to bound it, the FD term is written out in full rather than left to a ceiling:

| | primals | np = 1 core-min |
|---|---|---|
| one operating point, one row (D8R's registered form: 5 components × 3 steps × 2 sides + 2 η) | 32 | 45.7 |
| **× 3 operating points** | **96** | **129.4** |
| **× 2 toolchain rows** | **192** | **258.8** |
| **× 2 (baseline table for the gradient rung + endpoint table for the optimisation rung)** | **384** | **517.6** |

**384 primals and ≈ 518 core-min ($0.443 DERIVED) is the full FD bill across both rungs, and it is
23 % of the entire programme's ≈ 3,834 core-min.** It is the single largest non-optimiser line item
and it is the one most often dropped. **It is not reducible by choosing a cheaper step policy**: one
step proves no plateau and is forbidden outright (`DAFOAM_CHARTER.md` §3), and a one-sided difference
at a single step would cost 18 primals per row where the charter requires 96 — **5.3× smaller and
inadmissible.** The only legitimate reductions are **fewer operating points** (2 instead of 3 → 256
primals, ≈ 345 core-min) or **fewer graded components**, and both are registration decisions with
their own costs, not savings.

**Disk is measured and is NOT a constraint, so decomposed field writes at every operating point are
not a limiting factor.** Measured by me at 2026-09-12T01:16Z, not relayed: `/dev/root` **968 G total,
467 G used, 502 G available, 49 %**. **No disk limitation is registered for this item.** The `W` term
(§5.3) remains costed per write for the *compute* it consumes, which is unrelated to capacity.

### 5.5b **WHAT IS NOT A CAP AND THEREFORE DOES NOT MOVE: MEMORY**

**Memory is physics, not a budget, and removing spend caps does not make an adjoint fit in RAM that
cannot hold it.** The box is 30 GiB total; measured at this write, `available` is **14 GiB** and
falling (18 GiB fourteen minutes earlier) at load **77.81** on 16 cores. The §3.4 question — three
simultaneous `DASolver` instances or two — is untouched by any directive about spend, is the item's
one genuine feasibility unknown, and is what §6.3's experiment buys. **If the answer is that three
instances do not fit, the finding is `BLOCKED` with a measured peak RSS beside it, and that verdict
is worth more than an optimistic plan.**

---

# 6. GO / NO-GO

## 6.1 **The number that decides it: 456 against 3,378 core-minutes — and D19M's ceiling**

**The compressible multipoint optimisation is affordable (≈ 3,378 core-min point, ≈ $2.89 DERIVED,
well inside the $25 pre-authorisation) and it should NOT be registered as one item today.**

The deciding figure is not the price. It is the **ratio 456 : 3,378 = 1 : 7.4** between the gradient
rung and the optimisation rung it feeds — set against the measured fact that **the most recent
compressible multipoint this lab ran spent its full budget and could not publish `PASS` on any row,
because its gradient basis had no graded verdict** (§1.1c). **D19M is the counterfactual, already
paid for: every gate passed, both optimisers printed `Optimal Solution Found.`, both endpoint FD
tables passed bands D and E — and the registered ceiling capped both rows to `GATE REACHED` anyway.**

**Spending 3,378 core-minutes on an optimisation whose multipoint gradient has never been
FD-verified is spending 7.4× the price of finding out whether it can reach `PASS` at all.**
`DAFOAM_CHARTER.md` §2 is not advisory here: **an unverified gradient may not enter an optimisation**,
and the multipoint objective's gradient is a **new quantity** — it is not the single-point `dCD/dx`
that D8R verified (`SO3_MULTIPOINT_SCOPE_MEMO.md` §5 item 2 says the same thing about the
incompressible line).

## 6.2 **RECOMMENDATION**

**GO — on the gradient rung only: ≈ 456 core-min point, band [380, 620], upper reading ≈ 900
($0.39 / $0.77 DERIVED), np = 1, on A6 CRM wing-alone at 41,760 cells, both toolchain rows. Those are
calibration figures and none of them stops a run (§5.5).**

**NO-GO — on the optimisation rung, until the gradient rung lands.** Not on price: on basis.

**And the no-cap directive, if the relay is accurate, STRENGTHENS this recommendation rather than
loosening it.** With no cap to stop an overrun, a 3,378-core-min optimisation launched on an
unverified multipoint gradient has nothing between it and its full spend **and** would still be
ceiling-capped to `GATE REACHED` at the end of it, exactly as D19M was. **Removing the stop makes the
order of the two rungs matter more, not less.**

## 6.3 **The cheapest experiment that settles the open questions before a registration is written**

**One arm, PATCHED row, ≈ 99 core-min ($0.085 DERIVED), np = 1: build the 3-point multipoint model at
M 0.80 / 0.85 / 0.90 on D8R's mesh and take ONE gradient evaluation. No optimiser. No FD table.**

It settles, in one arm, every question this document could not answer from disk:

| open question | what the arm measures | why it cannot be answered from disk |
|---|---|---|
| **Does a 3-instance compressible multipoint fit in memory?** | peak RSS, directly | §3.4 — the two readings disagree by 43 % (28.6 GiB extrapolated vs a ≤ 20 GiB *ceiling*, not a peak) |
| **Does the transonic adjoint converge at OFF-DESIGN Mach on this mesh?** | `PetscConvergedReason` and iteration count at M 0.80 and M 0.90 | every A6 adjoint on record is at **M 0.85 only**; the conditioning wall is a shock-position property and the shock moves with Mach |
| **Does the CL trim hold at another Mach?** | `findFeasibleDesign` convergence at each point | `maxIter 4, tol 1e-3` has never run off M 0.85 on this mesh |
| **What is `F_mp` really?** | `waited_s` for three serial `DASolver` constructions | §5.1 — assumed ≈ `3.6n`, never measured for a multipoint container |
| **Is the ×3-with-1.6308× band right?** | one gradient evaluation against D8R's measured single-point one | §5.2 — the 1.6308× comes from a *different case* whose optimiser was backtracking |

**If it fits and converges at all three Mach numbers, the gradient rung's registration writes itself
from measured numbers. If it does not, the finding is `BLOCKED` with a measured memory number or a
measured `PetscConvergedReason`, and that is worth more than an optimistic plan — it costs 99
core-minutes instead of 3,378.**

**Fallback already priced, if 3 points do not fit: TWO Mach points.** Sanaa's own SO-3 wording is
*"2-3 Mach/alpha"*, so two is inside the mandate. Memory drops to ≈ 19.3 GiB under the pessimistic
reading (§3.4) and the optimisation rung falls to ≈ 2,300 core-min.

## 6.4 What must be in the pre-registration and is NOT settled here
1. **The Mach points and the weights.** M 0.80 / 0.85 / 0.90 is this lane's suggestion, not a
   decision. Equal weights are a choice, not a default (`SO3_MULTIPOINT_SCOPE_MEMO.md` §2).
2. **The trivial baseline (`DAFOAM_CHARTER.md` §4)** — the wrong-step probe, the shuffled-weight
   probe, or both. §4.3.
3. **Whether the item claims verification or validation.** It must claim **verification**; A6 has no
   public primary (§2.3b) and the registration says so on its first screen.
4. **np.** This document recommends np = 1 on measured grounds (§5.1a); the supervisor owns it,
   because changing ranks changes the decomposition and therefore the linear-solver history
   (`DAFOAM_CHARTER.md` §5 — a gradient verified at one np is a statement about that np).
5. **The Roache position.** No grid triple exists for a multipoint objective on this family and none
   is proposed. `GCI_roache` would read `NOT APPLICABLE`, as it did for D19M.

---

# 7. WHAT THIS DOCUMENT COULD NOT VERIFY

- **The `59.1 GiB / 46.5 GiB de-biased` D8G L3 figures ARE on disk and ARE NOT measurements.** They
  are model M2's affine prediction at 356,352 cells on an arm whose own status reads **`NOT
  ATTEMPTED`** (§3.1b). **Every restatement of them as "measured" that I have seen is wrong**, and
  the conditioning ground — which IS a measurement, at a mesh 4.48× smaller — is the one that
  carries the `BLOCKED`.
- **The no-cap directive in §5.5 is RELAYED, NOT VERIFIED BY ME.** I searched `etc/sessions/` for a
  record of the 2026-09-12 turn and **found none** — the newest file there is dated 2026-09-09. The
  costing in §5 is written to stand whether or not the relay is accurate, because it names the full
  expected spend rather than leaning on a cap (§5.5).
- **D6's 20 GiB is a CEILING, not a peak.** `OOMKilled = false` at a 20 g cap bounds the peak from
  above and measures nothing else. No peak RSS was recorded for that arm.
- **Every memory figure above 79,560 cells in §3.2 is EXTRAPOLATED** from a three-point fit and is
  labelled as such at each use.
- **The ~0.32 core-min/write figure in §5.3 is EXTRAPOLATED** from A3GC's 99,840-cell np = 4
  measurement by cell and rank ratio. It has not been measured at 41,760 cells or at np = 1.
- **The 2.45× np = 1 → np = 4 core-minute penalty (§5.1a)** compares a *fitted* np = 1 model (which
  reproduces its own case's measurement to 1.5 %) against *measured* np = 4 arms. It is a
  model-versus-measurement comparison, not two measurements, and is stated as such.
- **No Cp, CD or CL number in this document was produced by it.** Every one is read from the artifact
  cited beside it.

---

*Drafted by a dafoam `lab-lane` under an explicit zero-compute instruction, on a box at load 61.89 of
16 cores with another dafoam run live. No solver, container or `mpirun` was invoked; `docker images`
was read once as a read-only identity assert. No file under
`cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/` was read, written or touched. **This document
is a DRAFT, is UNFROZEN, is NOT a pre-registration, and authorises no compute.***
