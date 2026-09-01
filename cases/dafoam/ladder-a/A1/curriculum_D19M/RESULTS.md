# CURRICULUM D19M — RESULTS. **`GATE REACHED`**, both rows, seven arms of seven, 35.166 core-min

**Item verdict: `GATE REACHED`.** Both rows `GATE REACHED`. **Both rows composed raw `PASS` and were capped by the registered ceiling** — `rows_capped_by_ceiling: ["SHIPPED", "PATCHED"]`, `capped_by_ceiling_anywhere: true`, and every row carries `verdict_before_ceiling: "PASS"` and `capped_by_ceiling: true`.

| | |
|---|---|
| item | **D19M** — NACA0012 **compressible α-multipoint shape optimisation**, `DARhoSimpleFoam`, M 0.288, ladder A1, 4,032 cells, np = 1 |
| objective | `J = Σᵢ wᵢ·CDᵢ(αᵢ)`, three operating points **α = 2.787333582 / 4.787333582 / 6.787333582 deg**, equal weights 1/3, one shared 8-component `shape` vector |
| grading path | `d19m_grade.py`, md5 **`1893fc078fb5d0997d4f1c9c4a917bfe`** |
| freeze | `c7d7bf10`, through Amendment 3, 2026-09-01T06:30:47Z — **66 s before first compute** (chain stamp 06:31:53Z) |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint` |
| grade artefact | `D19M_grade_20260901T083034Z.json` (+ `.out`, + `D19M_STOP_MARKER.json`) |
| chain | `STATUS.D19M_chain` — `chain=COMPLETE stamp=20260901T083035Z chain_rc=0 declared=7 executed=7`, all seven arms `rc=0` |
| **cost, MEASURED** | **35.166 core-min** against **34.10** predicted (ratio **1.0313**), band [25.0, 85.0], ceiling 149.0. **$0.030067 DERIVED, NOT MEASURED** |

**THE CEILING IS THE HEADLINE, AND IT IS THE HONEST CAVEAT A READER MUST TAKE FIRST.** Every gate passed. Both optimisers printed their own `Optimal Solution Found.` Both endpoint FD tables passed band D and band E on every graded component. **And the item still cannot publish `PASS` on any row**, because the compressible gradient it spends **has no graded verdict** and **its plateau did not close**. That ceiling was registered before the run, is applied by `d19m_grade.py:_apply_ceiling()` as the last step of every composition, and `G-PROV` refuses (exit 2) if it is removed or widened.

**THE CEILING IS NOT A FAILURE.** Nothing measured here failed. The ceiling is a statement about the *basis* this item stands on, not about this item's own gates: it is what stops a clean sweep on a thin foundation from being published as a verification. Read `capped_by_ceiling` on a **row**, never the item-level field — see §7.1.

---

## 1. THE SEVEN ARMS

| arm | row | rc | wall s | ranks | core-min | predicted | ratio | cap |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 1 | 0.167 | 0.20 | 0.835 | 5.0 |
| `O-S` | SHIPPED | 0 | 486 | 1 | 8.100 | 8.64 | 0.937 | 40.0 |
| `XE-S` | SHIPPED | 0 | 182 | 1 | 3.033 | 2.60 | 1.167 | 12.0 |
| `FE-S` | SHIPPED | 0 | 383 | 1 | 6.383 | 5.71 | 1.118 | 20.0 |
| `O-P` | PATCHED | 0 | 485 | 1 | 8.083 | 8.64 | 0.936 | 40.0 |
| `XE-P` | PATCHED | 0 | 181 | 1 | 3.017 | 2.60 | 1.160 | 12.0 |
| `FE-P` | PATCHED | 0 | 383 | 1 | 6.383 | 5.71 | 1.118 | 20.0 |
| **item** | | | **2,110** | | **35.166** | **34.10** | **1.0313** | **149.0** |

**Zero arms over cap** (`arms_over_cap: []`), and the item did not approach its 149.0 ceiling. Longest arm 486 wall s, so **no row matches the `COMPUTE_BUDGET_CHARTER.md` §2 3,600-s stall rule** — cleaned equals gross. `memavail_pre_GiB` never read below 28.0 against a 12 GiB per-arm memory grant.

**Gate readings.** `G-STAGES` (7 declared, 7 ran, 0 short), `G-M2_mesh_identity` (4,032 == 4,032), `G-NP` (np = 1 on all seven), `G-ALPHA`, `G-DESIGNPOINT`, `G-NOOPT-ENDPOINT`, `G-EVALFAIL`, `G9_toolchain`, `G10_caps`, `G12_placement`, `G1_completion`, `G-OPT9` ×2, `G-MP-STRUCT` ×2, `G5_fd` ×2, `G-TB` ×2 — **`PASS`**. `G-PLAT7` **`NOT A RESULT`**, both rows, **as registered**. `G6_dot_product_duality` **`NOT MEASURED`**. `GCI_roache` **`NOT APPLICABLE`**.

`hard_gates` carries **eleven readings drawn from ten distinct gates**; `gate_fail: []` and `not_a_result: []` — zero hard readings are anything but `PASS`.

---

## 2. THE OPTIMISATION — BOTH ROWS CONVERGED, AND THE LIFT COLLAPSED

`α` is the **operating point** and is **not** a design variable here: `add_design_var("patchV", ...)` is gone, registered as removed rather than silently dropped. **The consequence is that `CL` is UNCONSTRAINED — there is no DV to trim with — so the three-`CL` triple travels with every drag number this item publishes.** The grade artefact says so in its own `_cl_travels` field, and this record carries it everywhere.

| row | IPOPT | iters / table rows | `max_iter` | cap reached | J baseline | J final | **weighted drag reduction** |
|---|---|---|---|---|---|---|---|
| SHIPPED (`O-S`) | `Optimal Solution Found.` | 10 / 11 | 40 | **no** | 0.017310713248142783 | 0.01281255542906026 | **25.98482 %** |
| PATCHED (`O-P`) | `Optimal Solution Found.` | 10 / 11 | 40 | **no** | 0.017310713248142783 | 0.012812539312422978 | **25.98491 %** |

### 2.1 THE DRAG TRIPLE AND THE LIFT TRIPLE, SIDE BY SIDE — NEITHER IS REPORTABLE WITHOUT THE OTHER

| | point0, α = 2.787° | point1, α = 4.787° | point2, α = 6.787° |
|---|---|---|---|
| `CD` baseline | 0.012653042938099815 | 0.0163267535192322 | 0.02295234328709633 |
| `CD` final, PATCHED | 0.011620047210203866 | 0.012051987264322876 | 0.014765583462742194 |
| `CD` final, SHIPPED | 0.01162132168420181 | 0.012052127261985068 | 0.014764217340993903 |
| `CL` baseline | 0.2987459621941071 | 0.49999949596851295 | 0.6736631644915069 |
| **`CL` final, PATCHED** | **−0.15737009883292363** | **0.07216486641740512** | **0.305403456283111** |
| **`CL` final, SHIPPED** | **−0.15774906382065684** | **0.07176073224580666** | **0.304951489323866** |

**THE LIFT COLLAPSES AT ALL THREE POINTS, AND GOES NEGATIVE AT point0.** That is not a defect in the optimiser and not a surprise: with `CL` unconstrained and `α` fixed, the cheapest way to reduce `Σ wᵢ CDᵢ` is to shed lift. **A 25.98 % drag reduction at unstated lift is not a reportable number**, and it is not reported as one anywhere in this record.

> **`DAFOAM_CHARTER.md` §9 forbids grading an optimisation by the size of its improvement.** The 25.98 % grades nothing. It is an input to the registered intermediate threshold (≥ 2.0 % over ≥ 5 majors) and to nothing else; the verdict comes from IPOPT's own printed statement and then from the ceiling. The grade artefact records this in `_improvement_grades_nothing`.

The stall detector's condition A did not fire on either row (`stall_condition_A: null`); condition B is recorded `NOT EXERCISED`.

---

## 3. THE ENDPOINT FD TABLE, BESIDE THE ADJOINT

`DAFOAM_CHARTER.md` §2's bright line — **an adjoint gradient is not a result until a finite-difference table stands beside it at a step proved to lie in the plateau.** This item has one, produced by its own `FE-S` / `FE-P` arms at each row's own optimum, and **it is the first FD table any compressible multipoint objective in this lab has ever had.**

Graded components: **`shape[0]`, `shape[3]`, `shape[6]`** (3 of 3, against a registered minimum of 3). `shape[7]` is excluded **by name**; §3.2.

### 3.1 PER COMPONENT, `J` AND `CL`, BOTH ROWS

`s* = 1e-3`; plateau rule is D19R's `G19R-1b` unchanged (decade neighbours, `max` over both sides, tol 10.0 %). Band D 5.0 % per component on `J` **and on each scenario's `CL`**; band E 5.0 % on the aggregate.

| row | component | `J` adjoint | `J` FD at s* | `J` rel % | plateau two-sided | plateau score % | `CL` rel % (point0 / point1 / point2) |
|---|---|---|---|---|---|---|---|
| SHIPPED | `shape[0]` | — | — | **0.145801** | true | 0.4466 | 0.004766 / 0.014120 / 0.001929 |
| SHIPPED | `shape[3]` | — | — | **0.108995** | true | 0.3332 | 0.005220 / 0.005536 / 0.011435 |
| SHIPPED | `shape[6]` | — | — | **0.036983** | true | 2.1462 | 0.010110 / 0.046241 / 0.143663 |
| PATCHED | `shape[0]` | −0.003382200437339747 | −0.0033768259902981074 | **0.159157** | true | 0.4312 | 0.001646 / 0.012270 / 0.004898 |
| PATCHED | `shape[3]` | 0.0025079828176175108 | 0.0025097542272816895 | **0.070581** | true | 0.2959 | 0.005255 / 0.005514 / 0.008885 |
| PATCHED | `shape[6]` | — | — | **0.006478** | true | 2.1417 | 0.009726 / 0.031776 / 0.145321 |

**Zero sign flips on any component, any quantity, any scenario, either row.**

> **THE BRIGHT LINE HOLDS ON ITS FACE, COMPONENT BY COMPONENT AND NOT MERELY IN AGGREGATE.** `DAFOAM_CHARTER.md` §2 asks for a step **PROVED to lie in the plateau**. **Every FD step at `s* = 1e-3` in this item is proved two-sided in the plateau — on both rows, for `J` and for all three `CL` scenarios.** `plateau_two_sided: true` on every reading above; the worst `plateau_J` score is 2.1462 % (SHIPPED `shape[6]`) against a 10.0 % tolerance, and the worst `plateau_CL` score across all eighteen row×component×scenario readings is 0.9144 % (PATCHED `shape[6]`, point2). **No component in this item is graded on an unproved step**, and this record can show that one component at a time rather than asking a reader to accept it from a vector norm.

| row | **aggregate `J`** (excl. `shape[7]`, 3 components) | **aggregate `CL`** | band D | band E | `G5_fd` |
|---|---|---|---|---|---|
| SHIPPED | **0.0465723 %** | **0.0193471 %** | 5.0 % | 5.0 % | **`PASS`** |
| PATCHED | **0.0302475 %** | **0.0186699 %** | 5.0 % | 5.0 % | **`PASS`** |

**BOTH AGGREGATES SIT BELOW THE HARNESS-SOUND FLOOR, AND THAT IS A CLAIM ABOUT THE HARNESS, NOT A VERIFICATION.** `VERIFICATION_CHARTER.md` §7 step 4 puts the harness-sound floor on this stack at **2.5–5 % vector-norm relative error**, and *"a number below that is a claim about the harness."* 0.0466 % and 0.0302 % are ~54× and ~83× below the floor's lower edge. The floor is **REPORTED, NEVER GATED**, as registered, and the grade artefact carries that sentence on its own face in `_harness_floor`. **This record does not claim a sub-percent verification.**

### 3.2 `shape[7]` — PUBLISHED BESIDE THE AGGREGATE, NEVER INSTEAD OF IT, AND STILL `NOT A RESULT`

`G-PLAT7` returns **`NOT A RESULT` on both rows**, `set_from: "REGISTERED LIST, never from the measured value"`.

| | SHIPPED | PATCHED |
|---|---|---|
| `J` adjoint | −0.0025482332696776604 | −0.0025436854682665084 |
| `J` FD at s* | −0.0025448875965458986 | −0.002541729606822009 |
| **`J` rel %** | **0.13147** | **0.07695** |
| plateau `J` two-sided | true | true |
| plateau `J` score % | 2.9194 | **2.9438** |
| `CL` rel % (p0 / p1 / p2) | 0.039368 / 0.012045 / 0.017221 | 0.033065 / 0.012419 / 0.013213 |
| **verdict** | **`NOT A RESULT`** | **`NOT A RESULT`** |

**THE REGISTERED NON-RESULT HELD, AND THAT IS THE POINT.** The numbers above are good — better than two of the three graded components — and they change nothing. D19R measured `shape[7]/CD` one-sided at **21.060684242435336 %** on the fine side of `s* = 1e-3` at the baseline, and the component changes sign between 3e-5 and 1e-5. D19O then measured that at *its* optimum the component is 28× larger and its plateau closes. **Neither observation licenses grading it here**: this item optimises a different objective and reaches a different design point, and **promoting a component after seeing a good number is exactly the move the registration exists to prevent.** What these numbers license is a *successor* registration made in advance.

### 3.2a **WHAT THE `shape[7]` PLATEAU IS NOT, BEFORE WHAT IT IS**

**IT IS NOT A PROMOTION. IT DOES NOT CHANGE THIS ITEM'S VERDICT.** `shape[7]` is `NOT A RESULT` here **by registration, on both rows, whatever it measured**, and it stays excluded by name from every aggregate. **Registration beats a favourable measurement.** Nothing below is used by this item for anything.

**IT IS NOT A REPLICATION OF D19O'S READING.** D19O optimised a *different objective* and reached a *different design point*. Two agreeing observations at two different optima of two different problems **corroborate**; they do not replicate.

**WHAT IT IS.** `shape[7]`'s plateau **also closes at D19M's design point** — two-sided on both rows, `plateau_J` score **2.9194 %** (SHIPPED) and **2.9438 %** (PATCHED) against a 10.0 % tolerance, `J` rel **0.13147 %** and **0.07695 %**, no sign flip, and all three `CL` scenarios two-sided as well. **That is a SECOND independent optimum at which the component that failed to close at D19R's baseline does close, after D19O's.** It corroborates D19O's reading that **`shape[7]`'s near-nullity is a property of the BASELINE, not of the component.**

**WHO MAY USE IT.** A successor registering `shape[7]` as **gradable in advance**, and only that. **The successor's case is now stronger than D19O left it, because it rests on two design points rather than one** — and it is still a case to be made *before* a run, in a freeze, by a document that does not yet know the answer.

### 3.3 THE TRIVIAL-BASELINE CONTROL — THE FD INSTRUMENT IS SHOWN ABLE TO GO RED

`G-TB` re-evaluates the same three components at **step 1e-8**, five orders below `s*`, where the FD numerator is at or below this case's measured primal repeatability at np = 1. It **must** fail band D, and it does:

| row | `shape[0]` | `shape[3]` | `shape[6]` | components passing band D | `G-TB` |
|---|---|---|---|---|---|
| SHIPPED (`FE-S`) | **108.617 %** | **90.771 %** | **50.732 %** | 0 of 3 (max allowed 1) | **`PASS`** |
| PATCHED (`FE-P`) | **109.741 %** | **90.608 %** | **52.258 %** | 0 of 3 (max allowed 1) | **`PASS`** |

`withdraws_row_fd_verdict: false` on both rows. **A `PASS` on a band is worth what the instrument's demonstrated ability to `GATE FAIL` is worth**, and this is that demonstration, on the real arms.

---

## 4. THE MULTIPOINT STRUCTURAL IDENTITY — `G-MP-STRUCT`

The one identity a multipoint item can violate silently: `dJ/dx` must equal `Σᵢ wᵢ · dCDᵢ/dx`, component by component, over all **8** `shape` components (not just the graded three). Tolerance `rtol = 1e-10`.

| row | XE arm | components | **worst relative residual** | `G-MP-STRUCT` |
|---|---|---|---|---|
| SHIPPED | `XE-S` | 8 | **4.2547e-12** | **`PASS`** |
| PATCHED | `XE-P` | 8 | **7.8671e-12** | **`PASS`** |

This is a **hard** gate on both rows and can emit `NOT A RESULT`; it emitted `PASS`.

**`G-ALPHA` is the companion gate, and it guards the defect a multipoint item carries invisibly.** If a scenario is silently wired to the wrong angle, *every band still passes* — the FD table and the adjoint are both taken at that same wrong angle. `G-ALPHA` reads the three α back **from the model itself and from the DV path**, on both `FE` arms, and every one matched its registered value with `abs_err = 0.0` against a 1e-12 tolerance. **`PASS`, zero mismatches.**

---

## 5. TWO-ROW AGREEMENT — REPORTED AS MEASURED, AND NOT DRESSED UP

Per component, `|dJ_SHIPPED − dJ_PATCHED| / |dJ_SHIPPED| × 100`, computed from `G-MP-STRUCT`'s own `dJ` values:

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| divergence % | 0.338 | 1.725 | 0.211 | 1.116 | **2.190** | 0.317 | 0.034 | 0.178 |

**Worst 2.190 % on `k4`.** These are eight measured numbers and **nothing more is claimed from them.** In particular they are **not** a "the two rows agree" finding: the rows converged to two *different* optima (their final `CD` and `CL` triples differ in the fifth and fourth decimal respectively), so each row's `dJ` is evaluated at a different design point, and a divergence measured across two different points cannot be separated into toolchain difference and design-point difference. **This item does not measure the IDWarp defect's reach, and it does not claim to** — D19O's own §3.2 finding rests on two nearly-identical optima, and this item adds a second such pair, not a discriminating one.

---

## 6. CONTROLS AND INSTRUMENT INTEGRITY

### 6.1 THE BIRTH REGISTER — 9 READERS, **9 BORN, 0 NOT BORN**

Sanaa's 2026-08-28 requirement: no instrument grades anything until *"was THIS reader ever shown able to see a non-zero THROUGH THE REAL CODE PATH?"* is answered YES, **demonstrated on this run root against these files**, not on a build-time fixture.

| reader | produces → gate | zero passes a gate | born | against |
|---|---|---|---|---|
| `R1_read_ledger` | core_min, rc, ranks, cpuset, digest → G1/G9/G10/G12/G-NP | no | ✓ | REAL |
| `R2_read_fatal_tokens` | fatal-token list → G1 | **yes** | ✓ | REAL |
| `R2b_read_benign_counts` | benign line counts → reported, never gated | no | ✓ | REAL |
| `R3_read_mesh_cells` | cell count → G-M2 | no | ✓ | REAL |
| `R4_read_optimiser_evidence` | optimiser marker list → G-NOOPT-ENDPOINT | **yes** | ✓ | REAL |
| `R5_read_X` | adjoint totals → G5_fd, G-TB | **yes** | ✓ | REAL |
| `R6_read_F` | FD derivative table → G5_fd, G-TB, G-PLAT7 | **yes** | ✓ | REAL |
| `R7_read_ipopt` | convergence statement, rows, stall → G-OPT9 | **yes** | ✓ | REAL |
| `R8_read_alphas` | the three α read back → G-ALPHA | **yes** | ✓ | REAL |

**6 of the 9 are readers whose zero would pass a gate** — precisely the population `CLAUDE.md` rule 3 exists for. The numeric plants were read back exactly: `R5_read_X` 56 values and `R6_read_F` 64 values at plant `1.234e-03`, worst residual **1.7932703932910243e-16** on both; `R1` planted 6.384234 against an unplanted 6.383 and read back 6.384234; `R3` planted 4,039 against an unplanted 4,032 and read back 4,039; `R7` ran both legs — positive leg converged, negative (stripped) leg did not.

**The plants never touch a graded artefact.** Every one is written to a separate copy under `grader_controls/`, and **the item's verdict is composed from the unplanted bytes alone.**

### 6.2 `asserts_in_grader: 0` IS THE CORRECT AND INTENDED VALUE

L-332: `python3 -O` strips `assert` statements, so a comparator that refuses through `assert` refuses through nothing under the flag it is run with. `d19m_grade.py` therefore refuses through a **`Refusal` exception**, at **38 refusal call sites**. **The zero is a design property, not a missing control**, and it is verified as such by the supervisor rather than inferred from the field.

### 6.3 `G-EVALFAIL` — THE EVALUATION CENSUS

4 components × 4 steps (3 decade + 1 trivial baseline) × 2 signs + 2 baselines = **34 evaluations** per `FE` arm, each of which is **3 primals** (one per operating point) = **102 primals per arm**. Measured: **34 declared, 0 failed, census matches**, on both arms. **`PASS`.**

### 6.4 `G9_toolchain` — IDENTITY BY DIGEST AND HASH, NEVER BY VERSION STRING

SHIPPED `sha256:9d45679d…f07fc` / `libidwarp` md5 `f0fcb488e0e98156575cd19548e91663`; PATCHED `dafoam-idwarp-rot:v1` `sha256:2927768a…f6d35` / md5 `85f59e87253e0a71a813f64ca6e4c425`. Zero mismatches across all seven arms. **All three images report DAFoam 5.0.0** — which is exactly why the version string is not the identity.

### 6.5 WHAT WAS **NOT** MEASURED, NAMED RATHER THAN LEFT TO BE INFERRED

* **`G6_dot_product_duality`: `NOT MEASURED`.** Named, never composed. AV-2 measured that seeding forward mode makes the primal **FAIL** on this exact case on **both** images.
* **`GCI_roache`: `NOT APPLICABLE`.** No grid triple is registered — this is a single-grid optimisation on A1's own 4,032-cell mesh. `CLAUDE.md` rule 5 has no row to act on, and the comparator says so rather than leaving a reader to infer it from an absence.
* **`G12_placement`'s delivered-cores floor: NOT COMPOSED**, and registered as not composed. At np = 1 an overlapping cpuset costs wall time and could not fail the gate; the sampler's reading is still published as a number. Registered cpuset `13`.
* **`G-DESIGNPOINT`'s `not_baseline` flag: REPORTED, NEVER GATED** — an optimiser that legitimately converged at the baseline would otherwise be failed for succeeding. What *is* gated is that each endpoint arm read **its own row's** `d19m_xopt.json` and used those exact bytes; both arms did (`row_match`, `shape_match`, `patchV_match`, `xopt_present` all true).

---

## 7. THE CEILING, AND HOW TO READ IT

`verdict_ceiling_reason`, verbatim from the artefact:

> The compressible single-point gradient this optimisation spends has NO GRADED VERDICT (D19R's grader refused rc=2; D19R2 grading attempt 1 = NOT A RESULT) and its plateau did NOT close (all_two_sided=false, score_pct=21.060684242435336, binding=[shape[7],CD,fine]). DAFOAM_CHARTER.md section 1: a gradient is not a result until an FD table stands beside it at a step PROVED to lie in the plateau. This item therefore cannot publish PASS on any row or at item level, whatever its gates return. REGISTERED BEFORE THE RUN.

And the basis here is **thinner than D19O's, not thicker**: D19O verified a single-point `CD`; **the multipoint objective `J` had never had an FD table on compressible ground at all** before this item's own `FE` arms. `G-PROV` links the chain and asserts the basis artefact still carries its marker: `CURRICULUM-D19R`'s `d19r_selected_step.json` exists, carries `"all_two_sided": false`, and its item verdict is `NOT A RESULT`.

### 7.1 A READING TRAP IN THE ARTEFACT'S OWN FIELDS — DO NOT QUOTE `capped_by_ceiling` FROM THE TOP LEVEL

The top-level object carries **`capped_by_ceiling: false`** and **`verdict_before_ceiling: "GATE REACHED"`**, while both rows carry `capped_by_ceiling: true` and `verdict_before_ceiling: "PASS"`.

**Both are literally true and the top-level pair is the misleading one.** The ceiling **binds at row level and the item inherits** (pre-registration §, composition rules): by the time item composition ran, its inputs were already the two capped `GATE REACHED` rows, so item-level `_apply_ceiling()` found nothing left to cap. **A reader who quotes the top-level `capped_by_ceiling: false` will state the opposite of what happened.** The pre-registration anticipated exactly this and is why the record also carries `capped_by_ceiling_anywhere` and `rows_capped_by_ceiling` — *"a true field that leaves a false impression"* is the failure mode those two fields were added to close. **Quote `capped_by_ceiling_anywhere: true` and `rows_capped_by_ceiling: ["SHIPPED", "PATCHED"]`.**

---

## 8. PREDICTIONS — **ELEVEN REGISTERED, ELEVEN HIT, AND THAT IS WEAKER EVIDENCE THAN IT LOOKS**

| token | registered | measured | |
|---|---|---|---|
| `P1_cells_4032` | HIT | `G-M2` `PASS`, 4,032 | **HIT** |
| `P2_alpha_gate_PASS` | HIT | `G-ALPHA` `PASS`, all α `abs_err = 0.0` | **HIT** |
| `P3_mp_struct_PASS_both_rows` | HIT | `PASS`/`PASS`, worst 4.25e-12 / 7.87e-12 | **HIT** |
| `P4_both_optimisers_converge` | HIT | both printed `Optimal Solution Found.` | **HIT** |
| `P5_majors_in_band` | HIT | 11 and 11, both ∈ [8, 24] | **HIT** |
| `P6_rows_agree_at_the_endpoint` | HIT | \|0.046572 − 0.030248\| = **0.0163 pp** ≤ 1.0 pp | **HIT** |
| `P7_endpoint_fd_PASS_both_rows` | HIT | `G5_fd` `PASS`/`PASS` | **HIT — and it is a registered REVERSAL of D19O's P6/P7** |
| `P8_trivial_baseline_PASS_both_rows` | HIT | `PASS`/`PASS`, 0 of 3 passing at `h = 1e-8` | **HIT** |
| `P9_shape7_NOT_A_RESULT` | HIT BY CONSTRUCTION | `NOT A RESULT` both rows | **HIT, and it carries no information** |
| `P10_item_GATE_REACHED` | HIT | `GATE REACHED` | **HIT** |
| `P_COST_total_core_min_in_band` | HIT | 35.166 ∈ [25.0, 85.0] | **HIT** |

**`P7` IS THE ONE THAT CARRIED RISK, AND IT IS A REVERSAL.** D19O registered that its patched endpoint FD would **miss** and its shipped endpoint FD would **`GATE FAIL`**; both were wrong, both rows passed. D19M registered **the opposite of its predecessor's prediction, because its predecessor's measurement refuted the reasoning.** That reversal is the one place in this table where the registration could have been embarrassed and was not.

**AND ELEVEN-FOR-ELEVEN IS NOT A BOAST.** `P9` scores a gate this document *registers* and therefore confirms only that the comparator was not edited. `P1`, `P2`, `P3` and `P8` were near-certain before the run. **A prediction sheet that goes 11/11 mostly tells you the sheet was safe**, and this item's registration is honest enough to have said so of `P9` in advance. The single informative hit is `P7`.

---

## 9. COST CALIBRATION (`CLAUDE.md` rule 12)

**35.166 core-min actual against 34.10 predicted, ratio 1.0313.** Band [25.0, 85.0] — inside. Ceiling 149.0 — not approached. **$0.030067 DERIVED, NOT MEASURED**, at c7a.4xlarge $0.0513/core-h, owner-reported 2026-08-21/22; **the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU: 0 GPU-h.**

**WASTE: NONE IDENTIFIED.** No arm stalled, no arm was re-run, no arm crossed a cap, nothing was discarded. Longest arm 486 wall s against the 3,600-s stall rule — **cleaned equals gross at 35.166 core-min.**

**THE ATTRIBUTION IS MISPREDICTION, MILD, AND IT IS TWO ERRORS THAT NEARLY CANCEL.**

| term | registered basis | measured | |
|---|---|---|---|
| `O` arm rate | **0.72255** core-min/major `[EXTRAPOLATED]`, × 12 expected rows → 8.64 | `O-S` 8.100/11 = **0.7364**, `O-P` 8.083/11 = **0.7348** | **the RATE was right to ~1.9 %** |
| `O` arm total | 8.64 | 8.100 / 8.083 (**0.937 / 0.936**) | **the shortfall is one fewer major**, not a bad rate |
| `XE` arm | 2.4415 (SO-3 incompressible mean) × **1.0667** = 2.60 | 3.033 / 3.017 → **3.033 / 2.4415 = 1.242** | **the compressible penalty on an XE arm is ≈1.24×, not 1.07×** |
| `FE` arm | 102 primals × **3.3571 s** (D19O's measured *single-point* compressible endpoint primal) = 5.71 | 383 s / 102 = **3.755 s/primal**, ratio **1.118** | **a multipoint endpoint primal costs ~12 % more than the single-point one the rate was measured on** |

**THE EXPECTED-MAJOR PRICING WORKED, AND THIS IS THE THIRD ITEM CONFIRMING IT.** SO-3 priced its `O` arms at `max_iter` and registered 228.59 against a spend of 28.900 — a factor of **7.9** overestimate. D19O switched to pricing at *expected* majors and landed at 0.6715. **D19M priced at an expected 12 major rows, ran 11, and landed at 1.0313.** `max_iter = 40` is a **cap** and is priced into the 40.0 core-min per-arm cap and nowhere else. **A cap is not an estimate**, and pricing one as the other is the single largest source of this family's historical estimate error.

**THE TWO TERMS THAT WERE UNDER-PRICED, AND THE HONEST LIMIT ON THE ATTRIBUTION.** The `XE` under-price (1.16×) and the `FE` under-price (1.12×) are both **anchors carried across a change of kind** — an incompressible `XE` anchor scaled by a compressible factor taken from elsewhere, and a *single-point* `FE` primal rate applied to a *multipoint* endpoint. **Both are the same error D19O's own §5 named**: a ratio measured on one configuration and carried onto another without measuring it there. **The mechanism behind the 12 % `FE` gap is NOT MEASURED here** — three `DASolver` instances in one process is the obvious candidate and this record does not assert it, because nothing in this run separates it from ordinary cache and memory-traffic effects.

**FORWARD RULES THIS ITEM MEASURES, for A1 compressible at np = 1:**
* a **compressible multipoint(3) optimiser major** prices at **≈ 0.735 core-min/row** — measured twice, on two rows, agreeing to 0.2 %;
* a **compressible multipoint(3) endpoint primal** prices at **≈ 3.755 s** — measured twice, identical to the millisecond at 383 s / 102 on both arms;
* a **compressible `XE` (adjoint-totals) arm at 3 operating points** prices at **≈ 3.02 core-min**, i.e. **1.24×** its incompressible 3-point twin, not the 1.07× that was registered.

The calibration row for this item is `docs/COST_CALIBRATION.md`.

---

## 10. WHAT THIS ITEM DOES **NOT** ESTABLISH

* **It does not establish that the compressible multipoint gradient is verified.** Its basis is *thinner* than D19O's: `J` had never had an FD table on compressible ground at all before this run, and the single-point gradient it rests on still has **no graded verdict**.
* **It does not establish a `PASS` on anything.** Both rows were capped from raw `PASS`. That is the ceiling, registered before the run.
* **It does not establish anything about `shape[7]`.** §3.2. Its numbers are published and its verdict is `NOT A RESULT`.
* **It does not establish a sub-percent verification.** §3.1 — both aggregates are claims about the harness.
* **It does not establish that the IDWarp defect is baseline-only.** D19O's finding rests on two optima that were nearly the same point; this item adds a second such pair, not a discriminating one. **The item that settles it is the deliberately-displaced-design-point successor.** §5.
* **It does not establish a trimmed-`CL` result.** `CL` is unconstrained and the triple travels. §2.1.
* **It does not establish anything at np ≠ 1**, on a transonic ground, or on a grid triple.

---

## 11. WHAT A SUCCESSOR MUST KNOW

Lifted from the item's own `D19M_STOP_MARKER.json`, field `what_a_successor_must_know`, verbatim and not strengthened:

> D19M spends a COMPRESSIBLE gradient that has NO GRADED VERDICT: D19R's grader refused rc=2 and D19R2's grading attempt 1 returned NOT A RESULT. D19R's plateau did NOT close — all_two_sided=false, score_pct=21.060684242435336, binding=[shape[7],CD,fine]. AND THE MULTIPOINT OBJECTIVE J HAS NEVER HAD AN FD TABLE ON COMPRESSIBLE GROUND AT ALL — this item's own FE arms are the first. `shape[7]` is a REGISTERED NON-RESULT here, excluded BY NAME from every aggregate, and this item's verdict is CEILINGED at GATE REACHED: IT CANNOT PUBLISH PASS.

### 11.1 THE STRONGEST FOLLOW-ON — `the_strongest_follow_on`, verbatim

> A FORWARD-AD or COMPLEX-STEP reference. Both images ship libDASolverADF.so (docs/dafoam/TOOLCHAIN_INVENTORY.md section 6a), so a non-FD reference IS reachable on this box. It would settle shape[7] OUTRIGHT, because it has no step at all and therefore no plateau to close. D19R section 11 named it as the strongest single follow-on this ground admits and did not reach for it. NEITHER DID D19O AND NEITHER DOES D19M — three items now, each saying so on its own face. D19O sharpened the target: the component differs by 28x between baseline and optimum, so a non-FD reference AT BOTH POINTS would separate the defect from the configuration definitively.

**Three items have now named it and none has bought it.** `DAFOAM_CHARTER.md` §2 requires that where forward-AD or complex step is reachable you say why you did not reach for it: **the reason on record is `G6_dot_product_duality`'s — AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on both images.** That is an obstacle, not an absence of the capability, and it is the obstacle a successor has to clear.

### 11.2 WHY D19M STILL RUNS BOTH ROWS — `what_D19O_measured_about_the_two_rows`, verbatim

> At D19O's optimum the SHIPPED and PATCHED rows agreed to 0.0232 % on shape[6], where D15 measured the shipped row 44.8738 % wrong AT THE BASELINE on this same ground. The IDWarp degenerate-rotation branch fires when axisMag = 1e-15 < sqrt(eps), certain on an undeformed mesh and false on a deformed one. THIS IS WHY D19M STILL RUNS BOTH ROWS: the agreement is CONFIGURATION-DEPENDENT, and a one-row item would bake it in and destroy the only instrument that can detect it.

### 11.3 WHAT A SUCCESSOR MAY REGISTER IN ADVANCE — `what_D19O_measured_that_a_successor_may_register_in_advance`, verbatim

> D19O (RESULTS.md section 3.1) MEASURED that at ITS optimum shape[7]'s |dCD| is 5.887e-03 against 2.099e-04 at the baseline — a factor of 28 — and that its plateau CLOSES there (two-sided, coarse 0.974 % / fine 1.061 %). ITS NEAR-NULLITY IS A PROPERTY OF THE BASELINE, NOT OF THE COMPONENT. That is evidence a successor may use to register shape[7] as GRADABLE IN ADVANCE. It did NOT license D19O to grade it, and it does not license D19M: this item optimises a different objective and reaches a different design point, and promoting a component after seeing a good number is the move the registration exists to prevent.

**D19M's own `shape[7]` numbers (§3.2) are a second data point for that successor registration and are not used as one here.**

---

## 12. THE THREE PRE-COMPUTE AMENDMENTS, AND WHAT EACH COST

All three landed **before first compute**, when `CLAUDE.md` rule 2 still permits amendment, each stating its condition and how it was checked. **No gate, threshold, cap, band, label or prediction moved in any of them.**

* **Amendment 1** (`766fb630`) — three pins went stale inside the freeze, and `--verify` reported *"every pin matches"* while never reading the document.
* **Amendment 2** (`7c88751d`) — `compose_item` tested its eleven-reading `hard` list for `"GATE FAIL"` and **never for `"NOT A RESULT"`**, so a hard gate that could not read its own subject would have fallen through to `PASS` and been presented as `GATE REACHED`. **That inverts `CLAUDE.md` rule 5's only permitted direction.** Repaired with three legs plus a control proving they detect the patch rather than a constant. **The sweep found three gates that can reach `NOT A RESULT`, not the one the amendment was pointed at.** The defect was inherited from `d19o_grade.py`, where it is now recorded as a dated note; **it survived a run in which every gate passed**, which is how a fail-open survives.
* **Amendment 3** (`c7d7bf10`) — a published count was wrong **in both units** (readings vs distinct gates), and the repair tripped L-405 on this very document. `hard_gates._note` now carries the counted-in-code figures: eleven readings, ten distinct gates, four readings and three gates able to emit `NOT A RESULT`.

**A NOTE ON UNITS, NOT AN ERROR AND NOT REPAIRED.** `d19m_grade.py:1547-1548`'s inline comment says *"The other eight"* where the published `hard_gates._note` says seven. **Both are correct and they count different sets**: the comment's eight includes `G-STAGES`, and the comment itself says so — *"and G-STAGES which is handled separately"* — while `_note` counts only readings inside the `hard` list, which `G-STAGES` is not in. **The grader is frozen and has had first compute; nothing here is to be touched.** Recorded so a reader who diffs the two numbers does not go looking for a defect that is not there.

**Amendment 2 is the one that mattered to this item.** `G-ALPHA` and `G-MP-STRUCT` are hard gates that *can* emit `NOT A RESULT`, and `G-ALPHA` exists because a multipoint item can carry a wrong operating point invisibly. Under the unrepaired composition, the one gate protecting this item's weakest surface could have returned `NOT A RESULT` and been published as `GATE REACHED`. **On this run it returned `PASS`, so the repair changed no number here — and that is exactly why it had to be made before the run and not after.**

---

**SUBMISSIONS PARKED.** Nothing in this item is filed, sent, uploaded, registered, posted or commented outside this box (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). The stop marker carries the same sentence in its own `submissions` field.
