# ansys-verification — THE REPAIR QUEUE, in Sanaa's order

**Sanaa's directive, 2026-08-31, verbatim** (`etc/sessions/2026-08-31T2130Z_sanaa_ansys_fix_order.md`, commit `733d9403`):

> *"Ansys team must fix the non pass casse sin this order: budget/kill > naming > instrument > referent ceileing > gate design. ( since thats easiest to hardest)"*

Drafted from the committed cause-class block in `docs/ansys_verification/COVERAGE_ROWS.md` (`6a7b1df5`), classed under `VERIFICATION_CHARTER` §2n. **41 non-PASS rows: 35 in this queue, 2 `PHYSICS-FAIL` and 4 `UNCLASSED` outside it by her order.** Every row cites its own record.

## Two facts that shrink the queue, both measured before this was written

1. **THREE `GATE-DESIGN` ROWS ARE ALREADY REPAIRED — today.** Row **21** (VMFL033) → successor landed as row **#48 `PASS`**; row **#47** (VMFL038) → row **#51 `PASS`**; row **#49** (VMFL006) → row **#50 `PASS`**. **The `GATE-DESIGN` backlog is 12 open, not 15**, and counting them as open would overstate the work by a quarter of the largest class.
2. **SEVEN QUEUE ROWS ARE GPU AND CANNOT BE TOUCHED** — the GPU instance is **STOPPED** and Sanaa will say when it is back (her 2026-08-31 answer 4; no entry is pre-filed). Rows **33, 34, 39, 40, 41, 42, 43**. They stay in the queue, visible and not deleted, but they are **blocked on hardware, not on effort.**

**ACTIONABLE NOW: 25 CPU rows. Blocked on GPU: 7. Already converted: 3.**

## 1 — `BUDGET/KILL` (3 rows) — IN FLIGHT TONIGHT

Cap-hit reruns; the cheapest conversions on the register. **The rule-12 line: the old run does not get a new budget — it stays `NOT A RESULT` and is not re-graded. A NEW registration gets a cap correctly sized from the killed run's measured rate**, and each successor must first *prove the run was progressing, not diverging* — a bigger cap on a diverging run buys a second `NOT A RESULT` at higher cost.

| row | case | record cited |
|---|---|---|
| ~~11~~ | ~~VMFL003-M2 arm C~~ | **RECLASSED `GATE-DESIGN` 2026-08-31 — moved to tier 5. See the ruling below.** |
| ~~12~~ | ~~VMFL003-M2 arm D~~ | **RECLASSED `GATE-DESIGN` 2026-08-31 — moved to tier 5. See the ruling below.** |
| ~~32~~ | ~~VMFL017-R2~~ | **MOVED TO THE BACK OF THE QUEUE 2026-08-31 — see the ruling below. Row 32 itself is UNTOUCHED and stands as `NOT A RESULT`.** |

**Rows 11 and 12 are two arms of ONE case, so a single successor converts both.** Both successors dispatched 2026-08-31.

### RULING — **THE `BUDGET/KILL` TIER IS EMPTY. ALL THREE ROWS FAILED INSPECTION, AND SANAA'S "EASIEST" BUCKET CONTAINS NOTHING.**

Two lanes were dispatched to build the three successors. **Both refused, and both were right to.** Rows 11/12 below, row 32 further down. Neither wrote a registration; neither spent a core-minute of solver time.

**ROWS 11 AND 12 — RECLASSED `BUDGET/KILL` → `GATE-DESIGN`, moved to tier 5.**

- **The kill removed nothing.** The gate quantity `dp_pa` reached **within one part in 10⁹ of its own final value by iteration 268** at arm D's killed level — which was killed at **5949**. Rung-wide, of **141.025 core-min** consumed, **132.952 — 94.3 %** — was spent *after* the graded quantity was already within 1 ppm of final. **The cap was not too small for the physics; the frozen `endTime` was ~80× larger than the physics needed.**
- **A bigger cap cannot convert either row, and no assumption about the unfinished iterations is required.** The frozen convergence leg is `RESID_TOL = 1.0e-8` on `p, Ux, k, ε/ω`. **Arm C's three Roache gate levels are ALL COMPLETE at `endTime` with `rc=0`, and all three FAIL that leg** (L3: k 1.861e−08, ε 7.967e−08). **Arm D's L1 and L2 both ran to `endTime` and both fail** (L2: Ux 5.127e−08, k 1.221e−07, ω 1.116e−06). **Rule 5 step 1 puts the disqualifier at the COMPLETE levels**, so whatever the killed level would have done, both arms are already `NOT A RESULT`.
- **The clause is UNMEETABLE, not merely unmet.** ε/ω park at 1.39e−08–7.97e−08 at **every level of every arm** — and **arms A and B ran the full `endTime` on the full budget and hit the same floor** (rows 9, 10). **A defect that survives an unlimited budget is not a budget defect.** It is the same clause behind rows 6, 9 and 10, which are already `GATE-DESIGN`.
- **§2n.3 requires the LOWEST-NUMBERED class the record supports**, and `GATE-DESIGN` (4) beats `BUDGET/KILL` (8). The original classing was sound on what was visible then — "cap fired, no `End`, rule 4 fails" — and this is a refinement on deeper evidence, not an error.
- **§12.2 = DIFFERENT**: the 21,744 Pa reference is the **Moody-chart smooth-pipe branch, an empirical correlation**, which the exact-PDE rule names explicitly. Ceiling `GATE REACHED`; `PASS` unavailable and none sought.
- **A THIRD CONSERVATION-PINNING, and this one lands on a diagnostic rather than the gate.** The `f_dev` diagnostic is built from `pSlabA − pSlabB`, and that slab difference is **bit-identical between L2 and L3 in all four arms — d21 = 0 exactly** — because fully-developed pipe pressure is exactly linear in x and the 500-mesh slab faces are a subset of the 1000-mesh faces. **`f_dev` carries zero axial-mesh information by construction.** The **gate** quantity is *not* pinned (d21 = 0.0745–0.338 Pa, ~7,700× the iterative plateau noise), so the registered gate is sound — only the secondary diagnostic is affected.

**THE SUCCESSOR IS NOT MINE TO AUTHORISE.** The only clause a clean successor could carry unchanged is the one proved unmeetable, so a successor requires **changing a convergence threshold** — and a threshold change is **Sanaa's** under `ESCALATION` §4.1 / D539. **Referred, not decided here.**

**AND THE RULE-2 DOOR IS NOW SHUT ON THESE ARMS.** Establishing all of the above required reading the graded values — **C/L3 = 20,451.523 Pa (−5.943 %)** and **D/L3 = 20,349.106 Pa (−6.414 %)**, both outside the frozen ±2.5 % band. **Any gate, band, threshold, cap, ceiling or label written for these arms from now on is written by someone who has seen the answer.** This is the **third** time today that establishing whether a repair was possible consumed the prediction-first claim on the repair — after VMFL029 and VMFL038. **It is a standing design constraint, not an accident:** where a repair's viability is itself in question, the only clean escape is a threshold fixed by an a-priori argument, as VMFL038-R2's limb-B 0.5 % was.

### RULING — ROW 32 IS CORRECTLY CLASSED AND WRONGLY PLACED: **CAUSE CLASS IS NOT REPAIR CLASS**

A lane was dispatched to build row 32's successor and **stopped without writing one**, which is what it was told to do if the premise failed. The premise failed, and I verified every decisive fact myself:

- **The cap firing was REGISTERED IN ADVANCE.** Pre-Compute Amendment 2 §E, frozen at `45328f8a`, predicted *"L1 is expected to stop at its own cap with rc 124 … and the case is NOT A RESULT."* **I confirmed that text is in the frozen blob.** The run record agrees exactly: `rc=124`, `wall_s=18000`, `core_min=300.0` against `cap_core_min=300`, `End_lines=0`. **This was never an accidentally-undersized cap — it was a cap set ~56× below a known intrinsic cost to BUY A MEASUREMENT OF THAT COST, and all three §E projections landed to ~1 %.** A registered probe that did exactly what it said it would is not a repairable failure.
- **The run was progressing, not diverging** — `Cd` decayed smoothly 0.8138 → 0.7985 over 8 bounded samples, Δt held at `maxCo` 0.2, 98.68 % CPU-bound. But it reached only **0.2254 of ONE flow-through** of the 12.673 in the frozen `endTime`: the forces are 48× the target because the starting vortex has not convected off the aerofoil, not because anything is wrong.
- **NO CAP RESIZE MAKES THIS AFFORDABLE.** From the measured rate: L1 alone **16,871 core-min = $14.42 DERIVED**; the **full triple ≈ 1,231,583 core-min ≈ $1,053.00 DERIVED — 42× the $25/run blanket**, with L3 alone at $923.18. `maxCo` 0.2 → 0.5 buys only 2.5×. **There is no evidence-sized cap that reaches a gradeable triple.**
- **The root cause is the INSTRUMENT.** Row #19 records that the registered `rhoSimpleFoam` **diverged** (`Negative initial temperature T0` at shock formation), forcing the switch to `rhoCentralFoam` — explicit and *acoustically* CFL-limited, and fundamentally mismatched to a **steady** transonic aerofoil at Re = 6.5e6. The cap firing is the symptom.
- **§12.2 = DIFFERENT** (RAE 2822 wind-tunnel experiment, Cook/McDonald/Firmin AGARD AR-138). **Ceiling `GATE REACHED`; `PASS` unavailable.** The lane declined to manufacture `PASS`-capability, as Sanaa's order requires.
- **Conservation-identity check: `Cd`/`Cl` are NOT pinned** — transonic drag is set by shock position/smearing and near-wall resolution, both genuinely mesh-sensitive. So the quantity *is* gradeable in principle; the refinement numbers cannot be had without the infeasible triple.

> **THE GENERAL FINDING, AND IT BEARS ON SANAA'S ORDERING: A ROW'S CAUSE CLASS DESCRIBES WHY IT FAILED, NOT HOW HARD IT IS TO FIX.** Row 32 is *correctly* classed `BUDGET/KILL` — the record plainly supports it — but its repair is an **instrument change**, which is a fresh registration and one of the *hardest* repairs, not the easiest. Sanaa's easiest-to-hardest order assumes cause class predicts repair difficulty; **for this row it does not.** Row 32 therefore moves to the back of the queue and is **not** counted among the cheap conversions. **`BUDGET/KILL` actionable-as-cheap is 2 rows (11, 12), not 3.**

**Row 32's real successor, when it is reached, is a solver decision for the supervisor to authorise:** a steady / LTS-pseudo-transient / dual-time implicit density-based formulation, or a shock-robustified steady `rhoSimpleFoam` that addresses row #19's negative-temperature failure — converging in thousands of pseudo-steps rather than ~2.8e7 acoustic ones. **A single-grid L1-only re-registration is available at ~$18.75 and is explicitly NOT recommended:** no triple, capped at `GATE REACHED` twice over, on the coarsest mesh where transonic drag is most corrupted — the likely outcome is a single-grid `GATE FAIL` that answers nothing.

## 2 — `NAMING/PLUMBING` (1 row)

| row | case | record cited |
|---|---|---|
| 18 | VMFL021 | REGISTER L44 — L3 killed by a **run-dir collision** (a rival lane dispatched onto the same case), ruled at `docs/ansys_verification/VMFL021_022_COLLISION_RULING.md`. Precedence 2 over the also-present `writeInterval` > `endTime` no-field-written defect |

## 3 — `INSTRUMENT` (7 rows — 6 CPU, 1 GPU)

Comparator/reader/guard defects; **the physics was never judged**, so these are re-registrations with a sound instrument rather than re-runs of a wrong answer.

| row | case | note |
|---|---|---|
| 1 | VMFL001 | CPU |
| 25 | VMFL004 | CPU |
| 26 | VMFL011 | CPU |
| 29 | VMFL064 | CPU |
| 31 | VMFL011-R2 | CPU |
| 37 | VMFL007-R2 | CPU |
| 33 | VMFLGPU001 | **GPU — BLOCKED** |

## 4 — `REFERENT-CEILING` (9 rows — 6 CPU, 3 GPU)

**THE HONEST CEILING, AND IT IS NOT NEGOTIABLE.** These rows convert to **clean `GATE REACHED` credentials**, not to `PASS`, unless a **same-PDE** referent exists. Sanaa's order says so in terms and the exact-PDE law (`VERIFICATION_CHARTER` §2h.6.1) makes it charter: a reference that is experimental, a correlation, or exact for a *reduced* model caps at `GATE REACHED` **however clean the run**. **Do not manufacture `PASS`-capability.** A `GATE REACHED` row honestly reached is a real result and this team has eight of them.

| row | case | verdict now |
|---|---|---|
| 20 | VMFL036 | `GATE REACHED` |
| 22 | VMFL023 | `GATE REACHED` |
| 23 | VMFL021-R2 | `GATE REACHED` |
| 24 | VMFL002 | `GATE REACHED` |
| 30 | VMFL064-R2 | `GATE REACHED` |
| 35 | VMFL076-R2 | `GATE REACHED` |
| 39 | VMFLGPU001-R2 | `GATE REACHED` — **GPU BLOCKED** |
| 41 | VMFLGPU004 | `BLOCKED` — **GPU BLOCKED** |
| 43 | VMFLGPU007-R2 | `GATE REACHED` — **GPU BLOCKED** |

## 5 — `GATE-DESIGN` (15 rows — **12 open**, 9 CPU-actionable, 3 GPU)

The hardest class and the one this team knows best: **every one of today's four honest failures was `GATE-DESIGN`, and three are already credentials.** The pattern that works is the R-successor: one substantive change, original frozen files untouched, original row standing.

| row | case | status |
|---|---|---|
| 4 | VMFL051 | open, CPU |
| 6 | VMFL003 (run 1) | open, CPU |
| 9 | VMFL003-M2 arm A | open, CPU |
| 10 | VMFL003-M2 arm B | open, CPU |
| 14 | VMFL010 | open, CPU |
| 16 | VMFL059 | open, CPU |
| 17 | VMFL022 | open, CPU |
| 27 | VMFL076 | open, CPU |
| #44 | VMFL063 | open, CPU — **and the judgment call**: labelled `GATE FAIL` at +40 % vs an experimental reference, but its own `GCI_fine` = **120.62 %** exceeds the discrepancy, so a physics attribution is unsupportable by Roache's own principle and §2n.3 fail-closes away from physics. **If Sanaa reads it as physics the headline becomes 3.** |
| 21 | VMFL033 | **REPAIRED → row #48 `PASS`** |
| #47 | VMFL038 | **REPAIRED → row #51 `PASS`** |
| #49 | VMFL006 | **REPAIRED → row #50 `PASS`** |
| 34 | VMFLGPU002 | **GPU BLOCKED** |
| 40 | VMFLGPU007 | **GPU BLOCKED** |
| 42 | VMFLGPU005 | **GPU BLOCKED** |

## Outside this queue, by Sanaa's order

- **`PHYSICS-FAIL` (2): rows 36 (VMFL011-R3) and 38 (VMFLGPU003)** — one physics, the laminar triangular-cavity miss on CPU and GPU: rms +13.6 % at L3 on a `CONVERGING` triple whose GCI (~3.3 %) is far below the miss, with a proven instrument. **Real physics; repairs on its own merits if at all.**
- **`UNCLASSED` (4): rows 5, 8, 19, 45** — all share one shape: **a run that produced no gradeable answer because the solver crashed or diverged.** That is neither a cap nor an external death (`BUDGET/KILL`'s verbatim scope) nor a referee defect. **The closed eight has no bucket for solver-internal divergence.** Awaiting Sanaa's taxonomy ruling; **they are fail-closed OUT of the physics half, which understates rather than inflates it.**

## Every successor carries this team's standing requirements

Planted-zero **at every level, running before any clause that can refuse**; a **GCI ceiling** beside `P_MIN`; **numeric** time-dir selection with a cardinality refusal; **zero `assert`** under an AST guard; `--selftest` green under `python3` **and** `python3 -O` with every verdict reachable; a **machine-readable JSON grading record frozen with the comparator**; a value-position placeholder discriminator; **`writeFields`** on every fieldValue object; the **§12.2 SAME/DIFFERENT** classification answered before the freeze; a **convergence clause satisfiable** from converged-flat-at-machine-floor to still-descending; **isotropic refinement** (cells ×4, constant aspect ratio); and **the conservation-identity check on every candidate gate quantity** — that one has burned this team twice in one day, on VMFL038's `τ_w` and VMFL029's net wall heat flux.
