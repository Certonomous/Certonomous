# CURRICULUM D19O — NACA0012 **COMPRESSIBLE SINGLE-POINT SHAPE OPTIMISATION**, `DARhoSimpleFoam`, M 0.288, BOTH TOOLCHAIN ROWS, np = 1. PRE-REGISTRATION (FROZEN)

**Item id:** `CURRICULUM-D19O`
**Run root (registered, and ABSENT at this freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation`
**Case directory (this document's own home):** `cases/dafoam/ladder-a/A1/curriculum_D19O/`
**Freeze:** this document's own commit. `CLAUDE.md` rule 2: the gates, thresholds, caps and labels below are committed **before** the solver starts, and §11 states the condition and how it was checked.

**Status: `PENDING`.** No arm of this item has run. **Nothing in this document is a result.**

**NOT FILED ANYWHERE.** Nothing in this item is filed, sent, emailed, uploaded, posted, registered, submitted or commented outside this box, now or ever (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** Readiness is not sending, and no reading of this file authorises a send.

**This freeze authorises NOTHING.** It is a freeze, not a launch clearance. The `dafoam-supervisor`'s two personal `SUPERVISION_CHARTER.md` §3 checks — the pre-registration **committed** before compute, and the grader read **as a diff** — come first, and neither is this lane's to make.

---

## 0. THE ONE THING A READER MUST NOT TAKE FROM THIS ITEM

> **THIS ITEM CANNOT PUBLISH `PASS`. NOT ON EITHER ROW, NOT AT ITEM LEVEL, WHATEVER EVERY GATE RETURNS.**

That is not a caution in prose. It is `d19o_grade.py:VERDICT_CEILING = "GATE REACHED"`, applied by `_apply_ceiling()` as the **last step of every composition**, and `G-PROV` **REFUSES (exit 2)** if the ceiling has been removed or widened to `PASS`.

**The reason is `DAFOAM_CHARTER.md` §1, this lab's own bright line:**

> *A DAFoam gradient is not a result until a finite-difference table stands beside it at a step **proved to lie in the plateau**.*

**THE COMPRESSIBLE SINGLE-POINT GRADIENT THIS OPTIMISATION SPENDS HAS NO GRADED VERDICT AT ALL, AND ITS PLATEAU DID NOT CLOSE.** Both facts were re-read from disk at this freeze:

1. **No verdict exists.** `CURRICULUM-D19R` phase 1 ran clean — `MESH X2 S8 N2 S1 R1` all `rc=0`, `chain_rc=0`, every arm inside its cap, **12.416 core-min** — and **its grader REFUSED, `rc=2`, and emitted no verdict**. Its successor `CURRICULUM-D19R2`, built precisely to give D19R a verdict, returned **`NOT A RESULT`** on grading attempt 1 (refusal `G19R-1h`, `MANIFEST_ENTRY_MUTATED` on `system/decomposeParDict`; no grade JSON written).
2. **The plateau did not close.** `/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau/d19r_selected_step.json`: **`all_two_sided: false`**, `s* = {shape 1e-3, patchV 1e-2}`, **`score_pct: 21.060684242435336`**, **`binding: ["shape[7]", "CD", "fine"]`**.

**So why buy it at all?** Because the optimiser is the only instrument that answers a question nothing else on this ladder answers: **does the compressible adjoint drive a descent on this case, and does the gradient still hold at the design point it reaches?** `DAFOAM_CHARTER.md` §9 requires the FD check **at the final design point, not only at the baseline**, and every compressible FD table this lab holds — D15's, D19's, D19R's — was measured **at iteration 0**. That gap is what this item closes, and it can be closed honestly under a ceiling.

**What this item may therefore never be quoted as.** Not *"the compressible adjoint is verified"*. Not *"DAFoam reduces compressible drag by X"*. The only sentence its patched row can license is **"on the patched toolchain `dafoam-idwarp-rot:v1`, and on a gradient whose plateau did not close, …"**.

---

## THE TEN LINES

The ten registered choices, each one a decision that could have gone otherwise.

1. **The quantity minimised is `CD` at `CL = 0.5`**, on the whole 8-component `shape` vector plus `patchV[1]` (angle of attack) as the trim variable. The producer's own program, unchanged.
2. **Two rows, always.** SHIPPED (`dafoam/opt-packages:latest`) and PATCHED (`dafoam-idwarp-rot:v1`). A worse or failed SHIPPED optimisation **is the result**, not waste — §2. `DAFOAM_CHARTER.md` §6.
3. **`shape[7]` IS RETAINED IN THE DESIGN VECTOR AND ITS FD ROW IS A REGISTERED NON-RESULT.** §3. This is the item's central limitation and it is on this document's face, not in a footnote.
4. **The verdict is CEILINGED at `GATE REACHED`.** §0, enforced in code.
5. **np = 1 ON EVERY ARM, and it is a CONDITION ON THE INHERITANCE, not a setting.** §5. It is also what makes D19R2's blocker unreachable.
6. **The endpoint plateau test is D19R's `G19R-1b`, UNCHANGED** — DECADE neighbours, `max` not `min`, tolerance 10.0 %. §6. A half-decade bracket would be weaker, and adopting a weaker test after seeing which test the component failed is what `DAFOAM_CHARTER.md` §3 forbids.
7. **The optimiser is IPOPT, `max_iter = 40` as a CAP, priced at an EXPECTED 12 major rows.** §12. SO-3 mispriced by 7.9× by pricing at `max_iter`; this item does not repeat it.
8. **Seven declared arms**, with the §9 endpoint FD **built into this chain**, not deferred to a successor.
9. **The planted-zero control is sized RELATIVE to the band it must cross**, `PLANT_K = 5.0`, and is proved sufficient by being driven **insufficient** at `PLANT_K_SHRUNK = 0.5`. §4.
10. **No grid triple is registered**, so `CLAUDE.md` rule 5 has no row to act on. §3, and the comparator says so rather than leaving a reader to infer it from an absence.

---

## 1. THE ITEM

Seven arms, in chain order, all at np = 1, all in a 12 GiB cgroup on **cpuset 11**.

| arm | row | kind | what it does | artefact | terminal statement |
|---|---|---|---|---|---|
| `MESH` | SHIPPED | SCRIPT | `preProcessing.sh && checkMesh`, then the byte-identity assertion against D15's frozen mesh. No solve, no optimiser, no adjoint. | `checkMesh.log` | `D19O_MESH_IDENTITY_ALL_OK` |
| `O-S` | SHIPPED | SOLVER | the IPOPT single-point optimisation | `d19o_O.json`, `d19o_xopt.json` | `D19O_O_WRITTEN` |
| `XE-S` | SHIPPED | SOLVER | the **adjoint** gradient at the SHIPPED optimum | `d19o_X.json` | `D19O_X_WRITTEN` |
| `FE-S` | SHIPPED | SOLVER | the **finite-difference** table at the SHIPPED optimum | `d19o_F.json` | `D19O_F_WRITTEN` |
| `O-P` | PATCHED | SOLVER | the IPOPT single-point optimisation | `d19o_O.json`, `d19o_xopt.json` | `D19O_O_WRITTEN` |
| `XE-P` | PATCHED | SOLVER | the **adjoint** gradient at the PATCHED optimum | `d19o_X.json` | `D19O_X_WRITTEN` |
| `FE-P` | PATCHED | SOLVER | the **finite-difference** table at the PATCHED optimum | `d19o_F.json` | `D19O_F_WRITTEN` |

**Arm order is not cosmetic.** Each row's endpoint arms follow **that row's** optimiser, because §9 requires the check at **the final design point** and each row has its own. `XE-S`/`FE-S` read `O-S/d19o_xopt.json`; `XE-P`/`FE-P` read `O-P/d19o_xopt.json`. The launcher refuses to stage an endpoint arm whose own row's optimum does not exist, and `d19o_xf.py` refuses again if the artefact's row does not match the arm's.

**The substrate, every term re-measured at this freeze rather than inherited:**

| what | value | how it was measured here |
|---|---|---|
| solver | `DARhoSimpleFoam` | read from the frozen producer header |
| mesh | **4,032 cells** | `cells: 4032` in `.../CURRICULUM-D19R-.../MESH/checkMesh.log`, re-read |
| Mach | **0.288** | `U0 = 100.0`, `T0 = 300.0` → `a = sqrt(1.4·287·300) = 347.19 m/s`, `M = 0.2880` |
| baseline α | 4.0° | `aoa0 = 4.0` in the producer header |
| `CL` target | 0.5 | `CL_target = 0.5`, and the producer trims α to it before the optimiser starts |
| DV vector | `shape` **8 components**, `patchV` 2 (U0 fixed, α free) | `.../R1/d19r_R1.json` → `baseline_dvs`, re-read |
| constraints | `CL = 0.5`; `thickcon ∈ [0.5, 3.0]`, `volcon ≥ 1.0`, `rcon ≥ 0.8` | the producer header, unchanged |

**THE RISK THIS ITEM BUYS, NAMED RATHER THAN ARGUED AWAY**, inherited verbatim from `curriculum_D19/PREREGISTRATION.md:41`: at M 0.288 the flow is only weakly compressible — density varies by roughly 4 % — so a fair critic says the compressible cell is being filled by a case that is compressible in its solver and its state equation but not dramatically so in its physics. **That objection is accepted, not rebutted.** The capability is nonetheless real: `DARhoSimpleFoam` carries density as a state with a full energy equation, and the adjoint tapes that compressible system, which is what the cell asks.

---

## 2. TWO ROWS, AND WHY THE SHIPPED ROW IS THE INTERESTING ONE

`DAFOAM_CHARTER.md` §6: **a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam.**

**On this exact ground the two rows are measured to be very far apart.** `curriculum_D19/PREREGISTRATION.md:38` records D15's reading: the **SHIPPED** adjoint misses FD by **44.8738 %** on `shape[6]`, where **PATCHED** misses by **0.0072 %** — and `shape[6]` carries **76.414 %** of the `CD` gradient's norm. **The shipped optimiser would therefore follow a ~45 %-wrong DOMINANT search direction.**

**So a shipped row that optimises badly is this item's single most informative output, and it is registered as such before the run** — nobody may later read a shipped-row failure as a wasted arm. The shipped row runs **first**, so that if the chain stops early it is the cheap and informative half that was bought.

**The row is read from the toolchain's own identity, twice, by two independent readers.** The launcher derives it from the **image digest**; `d19o_xf.py` derives it, inside the container, from the **md5 of the `libidwarp.so` this interpreter actually imported**, and **REFUSES to stamp a row it cannot prove** if that md5 matches neither registered toolchain. `G9` then compares both against the registration. A `-row PATCHED` flag would let a mislabelled launch stamp the wrong row into the artefact the endpoint arm reads, and there is no such flag in this instrument.

---

## 3. `shape[7]` — THE HAZARD, ON THIS DOCUMENT'S FACE

### 3.1 What is wrong with it, re-measured here

`shape[7]` is a **near-null component of the `CD` gradient**. Every number below was recomputed at this freeze from D19R's own artefacts, cited by path.

**The full 8-vector `dCD/dshape` at the baseline** (`.../CURRICULUM-D19R-.../X2/d19r_X.json` → `adjoint.CD.shape`, PATCHED, np=2):

| idx | `dCD/dshape[i]` | ratio to idx 7 | share of ‖·‖ |
|---|---|---|---|
| 0 | −7.221766503489e−03 | 34.40× | 11.5255 % |
| 1 | −1.890856088367e−02 | 90.06× | 30.1768 % |
| 2 | +7.285025342493e−03 | 34.70× | 11.6264 % |
| 3 | +9.290536413017e−03 | 44.25× | 14.8271 % |
| 4 | +3.876018809723e−02 | 184.62× | 61.8587 % |
| 5 | +4.092612805124e−02 | 194.93× | 65.3154 % |
| 6 | −1.413381271968e−02 | 67.32× | 22.5566 % |
| **7** | **−2.099480176256e−04** | **1.00×** | **0.3351 %** |

‖`dCD/dshape`‖ = **6.2659254113e−02**. **`shape[7]` is the smallest of the eight, 34.40× smaller than the next smallest and 194.93× smaller than the largest, and it carries 0.3351 % of the gradient's norm.**

**Its FD estimate against step** (`.../S8/d19r_S.json` → `rows[shape,7].fd`, eight levels, np=2):

| step | 3e−2 | 1e−2 | 3e−3 | **1e−3 = s\*** | 3e−4 | 1e−4 | 3e−5 | 1e−5 |
|---|---|---|---|---|---|---|---|---|
| `dCD` | −1.4732e−04 | −2.0891e−04 | −2.0956e−04 | **−2.0649e−04** | −1.9462e−04 | −1.6300e−04 | −4.9843e−05 | **+2.5192e−04** |

**IT CHANGES SIGN BETWEEN 3e−5 AND 1e−5.** The decade neighbour deviations at s\* are **coarse 1.1723882261986174 %** and **fine 21.060684242435336 %** — one-sided, and the fine side fails a 10 % tolerance by more than 2×. Every other component/function pair among the ten is two-sided at s\*, with a worst deviation of **3.334 %** (`shape[6]/CD`, coarse).

**Corroboration on a different functional and a different ground.** `curriculum_D19/PREREGISTRATION.md:34`: D16's independent failure is `CL` on **`shape[6]`** at the coarse end, **14.0978 %** — the same failure mode reached from the other side.

### 3.2 The disposition, registered before the run

> **`shape[7]` IS RETAINED IN THE DESIGN VECTOR. ITS FD ROW IS REGISTERED, IN ADVANCE, AS A NAMED NON-RESULT ON BOTH ROWS, WHATEVER VALUE IT RETURNS.**

**Why RETAIN rather than EXCLUDE, and the choice was made rather than defaulted.** The producer declares `add_design_var("shape", ...)` over the whole 8-vector through **one FFD shape function**, and `thickcon`, `volcon` and `rcon` are defined over that whole FFD. Masking index 7 would be a **different optimisation problem** from the one D15, D19 and D19R measured a gradient for — and the item would then quietly describe a design space nobody has verified either, while its headline read cleaner. **Retaining it admits 0.3351 % of an unproven search direction; excluding it would have bought a tidier verdict with a silent change of subject.**

**And its row is excluded BY NAME from every aggregate.** `DAFOAM_CHARTER.md` §3: a component that does not stabilise is *"flagged and excluded **by name** from any aggregate quoted as agreement — never dropped silently, and never rescued by a step at which it happens to cross."* Implemented as `d19o_xf.EXCLUDED_FROM_AGGREGATE = [("shape", 7)]`, and:

* every aggregate this item writes is over the **four** remaining components and **its own key is named `aggregate_pct_excl_flagged_CD` / `_CL`**, so no reader can take it for an all-component aggregate;
* `shape[7]`'s per-component reading is **computed and published beside the aggregate**, with `graded: false` and `registered_non_result: true`, never instead of it;
* the exclusion and its reason **travel on every record** — the `O`, `XE` and `FE` artefacts and the FD row itself (four sites, counted by a selftest leg).

### 3.3 **AND IT IS NOT RESCUABLE BY A GOOD NUMBER — WHICH IS THE PART THAT MATTERS**

**At s\* on D19R's own np = 1 arm, `shape[7]` agrees with the adjoint to 1.65155 %** — comfortably **inside** the 5 % band D. (FD **−2.065369465905e−04** from `.../S1/d19r_S1.json` against the adjoint **−2.099480176256e−04**.)

**A lane that had seen only that number would have graded it `PASS`.**

`registered_non_result` is therefore set **from the registered list, never from the measured value**. What is missing is not agreement; it is **the proof that the FD estimate at s\* is trustworthy**, and that proof is the plateau, and the plateau did not close. A comparator selftest leg (`B1`–`B5`) plants a `shape[7]` row that agrees to **0.019996 %** *and* whose plateau closes, and requires the gate to return **`NOT A RESULT`** anyway.

### 3.4 What would settle it, named and NOT reached for

**A forward-AD or complex-step reference.** Both images ship `libDASolverADF.so` (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a), so a non-FD reference **is reachable on this box**. `DAFOAM_CHARTER.md` §2 requires a record that reports only an FD table where such a reference was reachable to **state that it did not reach for it, and why**.

**It would settle `shape[7]` outright, because it has no step at all and therefore no plateau to close.** `curriculum_D19R/PREREGISTRATION.md:313` names it as *"the strongest single follow-on this ground admits"* and recommends it to the supervisor whatever D19R returns. **This item does not reach for it either.** The reason is scope: this item is the optimisation Sanaa's branch order selected, and a forward-AD reference is a different instrument on a different rung. **It is named here so the omission is on the face of this document**, and `d19o_stop_marker.sh` carries it to this item's successor so the finding is not re-bought.

### 3.5 The registered non-result is separately gated, so it cannot be skimmed past

`G-PLAT7` re-states the reading as its own gate, per row, so it appears on the record even for a reader who skips `G5_fd`.

---

## 4. GATES, THRESHOLDS AND LABELS — FROZEN NOW

**The vocabulary is the six tokens and nothing else:** `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`. `d19o_grade.py` refuses on any composed verdict outside that set.

| gate | what it reads | threshold | verdict on miss |
|---|---|---|---|
| `G-PROV` | the travelling chain of §0, both links read on disk; and that the verdict ceiling is present and not widened | all limbs | **REFUSAL, exit 2** |
| `G1_completion` | rc = 0, terminal statement present, no fatal token, **age guard** | all of it, per arm | `GATE FAIL` |
| `G-STAGES` | **DECLARED = 7** against EXECUTED = n | — | short > 0 is a **gate input**, not a footnote → `NOT A RESULT` |
| `G-M2_mesh_identity` | mesh cell count | **4032** exactly | `GATE FAIL` |
| `G-NP` | ranks per arm | **1** on every arm | `GATE FAIL` |
| `G9_toolchain` | image digest **and** `libidwarp.so` md5, per row, from inside the container | exact match to §7 | `GATE FAIL` |
| `G10_caps` | per-arm core-min against its cap, and the item total against the ceiling | §12 | `GATE FAIL` |
| `G12_placement` | cpuset | **`11`** exactly | `GATE FAIL` |
| `G-DESIGNPOINT` | that each endpoint arm was evaluated at **its own row's** optimum, from that row's `d19o_xopt.json` | exact byte match on both DV arrays | `GATE FAIL` |
| `G-NOOPT-ENDPOINT` | that no optimiser ran in `XE-*`/`FE-*` | zero optimiser evidence on disk **and** the artefact's own `no_optimiser_ran` declaration | `GATE FAIL` |
| `G-EVALFAIL` | that every declared evaluation was **written**, failures included | `EVALS_DECLARED = 42` per FE arm | `GATE FAIL` |
| `G-OPT9` (per row) | `DAFOAM_CHARTER.md` §9 — see §9 | — | see §9 |
| `G5_fd` (per row) | band D per component and band E on the aggregate, **at the final design point**, with the DECADE plateau proved per pair | **band D ≤ 5.0 %**, **band E ≤ 5.0 %**, plateau tol **10.0 %**, **≥ 4 graded components** | `GATE FAIL`; no plateau or fewer than 4 → `NOT A RESULT` |
| `G-PLAT7` (per row) | the registered non-result, §3 | — | **always `NOT A RESULT`**, set from the list |
| `G-TB` (per row) | the **same** probe at a deliberately wrong step, `h = 1e-8` | `PASS` iff **at most 1** of the 4 graded components passes band D there | ≥ 2 passing → that row's `G5_fd` is **WITHDRAWN to `NOT A RESULT`** |
| `G6_dot_product_duality` | — | **NOT MEASURED** — AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on **both** images. Named, never composed. |
| `GCI` / Roache | — | **NOT APPLICABLE** — see below |

**`GCI` / Roache triple gating.** **No grid triple is registered for this item**: it is a single-grid optimisation on A1's own 4,032-cell mesh. `CLAUDE.md` rule 5 therefore has no row to act on here, and the comparator publishes `"NOT APPLICABLE"` with that reason rather than leaving a reader to infer it from an absence.

**Two readings that are REPORTED and NEVER GATED:**
* **The harness floor.** `VERIFICATION_CHARTER.md` §7 step 4: the harness-sound floor on this stack is **2.5–5 % vector-norm relative error**, and *"a number below that is a claim about the harness."* Published beside every aggregate. Turning it into a gate would convert an honest caveat into a `GATE FAIL` the charter does not authorise.
* **`not_baseline`** on the endpoint design point. An optimiser that legitimately converged at the baseline would otherwise be failed for succeeding. What **is** gated is that the endpoint arm read its own row's `d19o_xopt.json` and used those exact bytes.
* **Benign log lines are COUNTED AND NAMED, never suppressed.** `SIMPLE: no convergence criteria found` is OpenFOAM's banner and is **not** evidence — DAFoam applies its own `primalMinResTol`. `trapFpe:` is an **enablement notice**, not a crash. A suppression a reader cannot see is the same defect wearing the other hat.

**`G12`'s delivered-cores floor is NOT COMPOSED at np = 1** and is registered here as not composed, so nobody later reads its absence as an oversight. At np = 1 an overlapping cpuset costs wall time and could not fail `G12`; the sampler's reading is still published as a number.

### 4.1 Verdict composition, registered here and implemented at `d19o_grade.py:compose_row` / `compose_item`

**Per row, in this order:**
1. optimiser verdict `NOT A RESULT` → **`NOT A RESULT`** (a row whose optimiser is `NOT A RESULT` cannot be rescued by any other gate)
2. `NOT A RESULT` in the endpoint FD or the trivial baseline → **`NOT A RESULT`**
3. `GATE FAIL` in any of the three → **`GATE FAIL`**
4. optimiser `GATE REACHED` → **`GATE REACHED`**
5. otherwise → `PASS` → **then the ceiling applies**

**Item level:** `G-STAGES` short or any row `NOT A RESULT` → `NOT A RESULT`; `GATE FAIL` in any row or in `{G-M2, G-NP, G9, G10, G12, G-DESIGNPOINT, G-NOOPT-ENDPOINT, G-EVALFAIL}` → `GATE FAIL`; `GATE REACHED` in any row → `GATE REACHED`; otherwise `PASS` → **then the ceiling applies**.

**THE CEILING CAN ONLY MAKE A VERDICT WORSE, NEVER BETTER**, and a selftest leg drives that both ways. **The endpoint FD likewise can only make things worse:** an endpoint `PASS` **never** upgrades a `GATE REACHED` optimiser to `PASS`. Registered before the run so it cannot be argued after one.

**The ceiling binds at ROW level and the item inherits**, so the item's own `capped_by_ceiling` reads `false` even when the ceiling did all the work. The record therefore also carries **`capped_by_ceiling_anywhere`** and **`rows_capped_by_ceiling`** — because a true field that leaves a false impression is the defect this lane keeps paying for.

---

## 5. RESOURCES — np, MEMORY, PLACEMENT, AND THE np = 1 PREMISE

**np = 1 ON EVERY ARM.** Enforced in three independent places: `d19o_run_arm.sh:ranks_of` (a selftest leg parses it and requires the set `{1}`), an `MPI.COMM_WORLD.Abort(2)` in `d19o_xf.py`, and `d19o_grade.py:ARM_RANKS` via gate `G-NP`.

**Two reasons, and the second is new to this item.**

1. **`DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across np**, and A4 measured a **16,600×** spread between two decompositions of one mesh (np=4 `scotch` 8.95 % against np=4 `simple` 4×1×1 0.00054 %). The only compressible FD reference on this ground taken **serially** is D19R's `S1` arm, which is the one this item inherits s\* from.

2. **np = 1 MAKES D19R2's BLOCKER UNREACHABLE, AND THAT IS A MEASUREMENT RATHER THAN A HOPE.** D19R2's grading attempt 1 returned `NOT A RESULT` because the age guard refused arm `X2` with `MANIFEST_ENTRY_MUTATED` on `system/decomposeParDict`: OpenFOAM's own `decomposePar` appends a `kahipCoeffs` default sub-dictionary to the file it read, six seconds after the manifest was built. **The guard was right; the manifest pinned a path the run writes.** Across D19R's six arms the mismatch count is **1 on each of the three np = 2 arms** (`X2`, `S8`, `N2`) and **0 on both np = 1 arms** — `MESH` (17 entries) and `S1` (27 entries). **At np = 1 `decomposePar` never runs, so the mutation cannot occur.**

> **THE GUARD IS NOT WEAKENED, AND NO EXCLUSION IS ADDED.** Adding `system/decomposeParDict` to `SOLVER_WRITE_TARGETS` would be a **gate-design decision**, and `docs/LAB_STATE.md` records that opening the compressible gate that way is reserved to Sanaa. This item does not take it.
>
> **THE REGISTERED FALSIFIER, before the run:** if `G1_completion`'s age guard refuses with `MANIFEST_ENTRY_MUTATED` on `system/decomposeParDict` on **any** arm of this item, then **the np = 1 premise above is FALSE**, the item is **`NOT A RESULT`**, and that is reported as a measurement about the ground. It is **never** a reason to weaken the guard after the fact. The comparator flags it explicitly as `np1_premise_falsified`.

**Memory: 12 GiB per arm.** D13 **measured** peak RSS **1.70 GiB** for this 4,032-cell 2-D case at np = 1. The compressible solver carries density and energy as extra states; a crude bound of **2× that footprint plus the adjoint's Jacobian colouring** is **[EXTRAPOLATED]**, not a measurement — **no compressible optimiser arm has ever run on this case** — so 12 g carries better than 3× headroom over it, and **the item's own first solver arm MEASURES it**. `DAFOAM_CHARTER.md` §7: the prediction is written down **before** the launch, and a run stopped by memory is recorded as stopped by memory and is **`NOT A RESULT` about convergence**.

**Aggregate memory ceiling 30.6 GiB**, poll 30 s, bound 14400 s, in the **waiting** form: every wait is a line in `STATUS.<arm>`; at the bound the chain **stops** and names the series file. **A block DISCARDS the arm's remaining budget and buys nothing**, and this document says so where the guard is registered. The reader is `d19o_aggregate_memory.py`, which distinguishes **GO / WAIT / REFUSE** by exit code — because a reader that cannot take its reading would otherwise loop forever reporting "not yet". It is **enumerated in §7**: this is the exact file `SO-2a`'s instrument table omitted while its frozen driver executed it by name.

**H5 memory window:** 45 samples over 60 s, floor **16.0 GiB**, every sample above the floor or the arm does not start.

### 5b. REGISTERED CPU PLACEMENT — cpuset **11**

`mpirun` inside a `--cpus=N` container binds rank 0 to the **first core of the host topology**, so concurrent containers land on the same host core and throughput collapses as `1/N` **while the box reports itself idle** — measured by the D13 lane 2026-08-25: affinity = 0 on all three concurrent arms, **0.250 cores delivered against a 1.0-core quota**, host 61 % idle. So: **pin, and MEASURE the placement rather than infer it from the flag.**

**Registered: cpuset `11`. One core, because every arm runs at np = 1. NOT core 0.**

**The disclosure, READ FROM DISK at this freeze rather than recalled.** Every `CPUSET=` literal under `cases/dafoam/ladder-a/*/curriculum_*/*_run_arm.sh` was enumerated; **core 11 appears in exactly ONE registered set — D5's `8,10,11,13`** (`A2/curriculum_D5/d5_run_arm.sh:124`, an item whose arms are finished). It is **disjoint** from SO-3's `14`, D19/D19R's `1,15`, D15's `2,3`, D16's `4,14`, the SO-1/SO-2 line's `9`, D4's `5,6,7,9`, D6's `2,3,4,14`, D7's `2,3,4,6` and D8R's `0,1,12,15`. **Zero containers were live on this box at this freeze.** `G12` compares the launcher's value against `d19o_grade.py:CPUSET_REGISTERED`, so the two cannot drift apart silently.

---

## 6. THE ENDPOINT FD TEST, AND WHY ITS STRICTNESS IS INHERITED RATHER THAN CHOSEN

`FD_STEPS_ENDPOINT` is s\* **with its DECADE neighbours**:

| DV | coarse | **s\*** | fine |
|---|---|---|---|
| `shape` | 1e−2 | **1e−3** | 1e−4 |
| `patchV` | 1e−1 | **1e−2** | 1e−3 |

s\* is **inherited by citation** from `.../CURRICULUM-D19R-.../d19r_selected_step.json` → `s_star`. It is **not re-derived by a lane that has seen an answer.**

**The plateau rule is `G19R-1b`'s, verbatim: both DECADE neighbour deviations ≤ 10.0 %, `max` over components and over both functions, not `min`.**

> **A HALF-DECADE BRACKET WOULD BE A WEAKER TEST, AND IT IS THE ONE THIS COMPONENT WOULD PASS.** D19R's own arm `R1` — a sensitivity-equalised ladder at κ = 68.4451586423877, spaced ×3.33 rather than ×10 — puts `shape[7]`'s FD at **−2.0994039516741345e−04** against an adjoint of **−2.099480176256e−04**, an agreement of **0.0036 %**, with a fine-side neighbour deviation of **0.2484 %**. `R1` is explicitly `diagnostic_only`, `grades_nothing: true`, and its own artefact states it *"CANNOT produce a PASS, cannot change any gate, and cannot be cited as a plateau."*
>
> **Adopting the spacing that makes the component pass, after seeing that it fails the other, is exactly what `DAFOAM_CHARTER.md` §3 forbids** (*"Selecting the step after seeing which one agrees"*). **The decade rule is kept, unchanged, and `shape[7]` remains a registered non-result.**

**The step sweep runs at the tolerance the graded run uses** — `primalMinResTol = 1.0e-8`, from the frozen producer header, unchanged from D15/D19/D19R. `DAFOAM_CHARTER.md` §3(i): a step sweep at a loose primal tolerance defends nothing.

**The aggregate statistic is NAMED.** It is the **vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` as printed**, over the **four** non-excluded components. `DAFOAM_CHARTER.md` §2: **no paper uses a vector-norm relative error**, and comparing this lab's vector norm against a published per-component average is forbidden. The per-component flags are reported **beside** it, never instead of it.

---

## 7. THE FROZEN INSTRUMENT TABLE — NINE ROWS, IN §18.3's ORDER

`DAFOAM_CHARTER.md` §18.3: an instrument table enumerates **every file the item EXECUTES or IMPORTS**, and **existence is asserted before any md5**. Existence and md5-agreement are different questions and the second cannot be inferred from the first at any level of agreement — not at 8 of 8, not at 800 of 800. **`SO-2a`'s §7 table read *"eight of eight AGREE"* while `so2a_aggregate_memory.py`, which its frozen driver executed by name inside its poll loop, was ABSENT from the freeze commit.**

`d19o_chain_driver.sh` asserts the **existence** of all nine, prints `D19O_18_3_EXISTENCE_OK`, and only **then** checks a single md5. A selftest leg (`c3`) proves that order **in the byte offsets of the file**, not in a comment.

| row | file | md5 | role |
|---|---|---|---|
| 1 | `d19o_chain_driver.sh` | `d732fea8e21d7a4ff541b8b49fc15b14` | drives the seven arms in order; **holds the pins below and is not self-pinned** |
| 2 | `d19o_run_arm.sh` | `2dbb88346c0e7211ae0e9cd65a4041b9` | the launcher — §8 |
| 3 | `d19o_xf.py` | `6f5e7ed9db76bf429b4031c6d87a8bf6` | the instrument: modes `O`, `XE`, `FE`; **its writers build every fixture in this item** |
| 4 | `d19o_runScript.py` | `a5e18503ea29d0e37c3cf1668533cd34` | the producer — §7.2 |
| 5 | `d19o_grade.py` | `419ce2363743bd16109826f2bf75d4f2` | **THE GRADING PATH** — §10 |
| 6 | `d19o_aggregate_memory.py` | `e4ad8d12d60ed2ad4710ce78e60d67cc` | the aggregate-memory reader the driver executes inside its poll loop — **the exact file `SO-2a`'s table omitted** |
| 7 | `d19o_stall.py` | `c719951741b6d76faa07569d2da8b7de` | the IPOPT log reader and the stall detector — §9 |
| 8 | `d19o_age_guard.py` | `0293334b1e63f69fc2af8f54ce922a6c` | the age guard — §5 |
| 9 | `d19o_stop_marker.sh` | `c0ea73225089ce77ff8a558351c3164d` | the stop marker — §13 |

Plus `d19o_decomposeParDict`, md5 **`68ecc827562886fb43c3aedb0627b344`** (an OpenFOAM dictionary, not a program), **byte-identical to `curriculum_D15/d15_decomposeParDict`** — verified by `cmp`, exit 0.

**The suite, not pinned but driven before every launch** (the driver runs all four and **stops the chain** if any refuses, **before staging**, proved by selftest leg `c8`): `d19o_xf_selftest.py` (`ae0fddbbe1333ba97ac9dc920cd88368`), `d19o_grade_selftest.py` (`4c469c6ff48ea4da844695a2b1835db5`), `d19o_run_arm_selftest.sh` (`6b153b1d880f09df1b1bf14d32988a30`), `d19o_chain_driver_selftest.sh` (`3f6140ea1d6674b71be18d6e9768126e`), plus `d19o_repin.sh` (`b5d66b42f2119f945db27f8a88125340`).

**The pins were set ONCE, for all nine together, by `d19o_repin.sh`** — never file by file. **The fail-closed sentinels are the literal strings `MD5_*_UNSET`**, which are **not** well-formed md5s, so `md5sum -c` cannot accept one by accident and the driver refuses on the literal before it even tries. `SO-3` deleted its sentinel because 32 zeros **is** a well-formed md5 and a dead sentinel would be counted as a real pin; this item avoids the class by choosing a sentinel that cannot be mistaken for a hash. A selftest leg (`c5`) drives both conditions.

### 7.1 A DEFECT FOUND AND REPAIRED IN THE REPIN SCRIPT ITSELF, DISCLOSED HERE

**`d19o_repin.sh`'s first run produced a stale pin, and `--verify` caught it.** `MD5_LAUNCHER` lives in the **driver**, and the same script also writes `MD5_XF`, `MD5_RUNSCRIPT` and `MD5_DECOMP` **into the launcher** — so a single pass computed `MD5_LAUNCHER` from launcher bytes that the same pass then rewrote. **That is the `SO-2MR` failure with the repin script as its author rather than a lane.**

**The repair is a FIXPOINT LOOP inside one invocation, which REFUSES if no fixpoint is reached — not a documented instruction to run it twice.** Measured: pass 1 wrote 1 pin, pass 2 wrote 0, fixpoint after 2 passes. `d19o_repin.sh --verify` then reports **every pin matches its file on disk**, 12 of 12 across both targets.

### 7.2 THE PRODUCER IS BYTE-IDENTICAL TO D19R's, AND THE REGISTERED DELTA IS **NONE**

`d19o_runScript.py` is a **byte-identical copy** of `curriculum_D19R/d19r_runScript.py` — `cmp` exit 0. That file is itself D15's with `max_iter` 100→40.

**Verified four ways at this freeze**, because a pin that was not verified is a pin that is being guessed at:

| where | md5 |
|---|---|
| `curriculum_D19O/d19o_runScript.py` on disk | `a5e18503ea29d0e37c3cf1668533cd34` |
| `curriculum_D19R/d19r_runScript.py` on disk | `a5e18503ea29d0e37c3cf1668533cd34` |
| the **committed blob at `HEAD`** for D19R's producer | `a5e18503ea29d0e37c3cf1668533cd34` |
| **the copy in D19R's run root that ACTUALLY RAN** | `a5e18503ea29d0e37c3cf1668533cd34` |

**All four agree.** The **header** above the anchor `# OpenMDAO setup` is **7,614 bytes**, the anchor appears **exactly once**, and the header md5 is **`d1efc43583fbeb59fb5116816b055a07`** — the value D19R asserts as D15's, re-computed here rather than copied. `d19o_xf.py` re-asserts all three (producer md5, anchor count, header md5) **before executing the header**, so the reproduction claim is a property of the bytes and not of a comment.

**Why the optimiser settings live in `d19o_xf.py` and NOT in the producer.** The header ends **above** the driver block, so `max_iter`, `tol` and the IPOPT options are constructed by the frozen instrument. That keeps them in **exactly one place**, pinned with the file that holds them; a selftest leg (`A7`) requires `pyOptSparseDriver` to be **absent** from the header, so the two cannot drift apart.

### 7.3 THE §18.3 EXTRACTION, BUILT HERE — the charter declares this call site **NOT BUILT**

`d19o_chain_driver_selftest.sh` leg **(c4)** performs it: it extracts every `$HERE/`-style path reference from the frozen driver and resolves each against the item directory. **Measured: 11 local dependency names; 9 pinned and guarded; all 11 exist on disk.** The two not in the existence guard are `d19o_xf_selftest.py` and `d19o_grade_selftest.py` — **accounted for by name in the leg itself**: they are driven **before** staging and their absence would fail the selftest loop loudly. Any other unaccounted reference **fails the leg**.

**No registered gate's implementing file is absent.**

### 7.4 Toolchain identity, by digest, never by tag

**Both digests and both library hashes were RE-MEASURED at this freeze from this box** — `docker image inspect` for the digests, and by **running each image and md5-ing the `libidwarp.so` the interpreter actually imported** for the hashes.

| row | image | image digest | `libidwarp.so` md5 | imported from |
|---|---|---|---|---|
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | `/opt/idwarp_patched/idwarp/__init__.py` |
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | `.../miniconda3/lib/python3.10/site-packages/idwarp/__init__.py` |

**A version string is not an identity.** The IDWarp rotation patch changes the reverse-mode derivative by seven orders of magnitude on the defect's own DOFs — issue-57 DOF 0 goes **210.16 % → 8.56e−06 %** — and **the version string still reads `2.6.2` either way**.

### 7.5 The frozen mesh identity

`MESH` asserts, **inside the container** so the kernel's rc carries it, that `constant/polyMesh/{points,faces,owner,neighbour,boundary}` are byte-identical to D15's. The pins are md5s of the **DECOMPRESSED** bytes, because a `.gz` stream can carry an mtime and a gz hash is therefore not a safe cross-run identity. **All five were RE-COMPUTED at this freeze from D19R's own MESH output and AGREE** (selftest leg `r8`): `points 88f00ff725ef2906212ca1e2b040c09f`, `faces 1bcea5c2f5817d0740a03a83050c3c79`, `owner 549e0a9f01be3ebf412017c1e9811ece`, `neighbour 65fd7ca38d534c760f57ce14bdffc834`, `boundary c92a945e9a1405b988ab418e48ab53c3`.

**Tutorial inputs**, frozen because the checkout is not; commit `d3b7e38b058aba2a98a74092e15c41ec455c570d`, all six **re-measured at this freeze**: `runScript.py 6537fa7641c4ccb20056f60f96f63b11`, `genAirFoilMesh.py 681f10659eb90457fca13fc933008b93`, `preProcessing.sh e25c8f8c32886112e3f9591196c695ad`, `NACA0012PS.profile 51dfed28e1bdb4cd33e0d8d7dabd586a`, `NACA0012SS.profile 4a6b8ef4501494c7693b71e88a2eabbf`, `FFD/wingFFD.xyz 6ddf378b028d03d8a18270488bee1759`.

---

## 8. THE LAUNCHER'S OWN GUARDS

`d19o_run_arm.sh`, md5 **`2dbb88346c0e7211ae0e9cd65a4041b9`**, asserted by the driver before staging.

**`G-ROOT.1`:** `BASE` must resolve — through `realpath -m`, so a trailing slash, a `.`, a `..` or a symlink cannot walk around it — to **this item's registered run root**. Anything else aborts at rc = 3 **before any staging**. The staging path begins `rm -rf "$WORK"`; `d4_run_arm.sh` hardcoded another item's root and would have deleted **5,085 files, 384 MB**. Driven by legs `(r1)` and `(r1b)`.

**`G-ROOT.2`** names 14 roots this file must never write, so the abort says **whose** evidence it just protected — D19R's root in particular holds `d19r_selected_step.json`, from which this item's s\* and its entire `shape[7]` registration are read. **The honest size, stated as D19R's parent states it: every one of those roots is already refused at `G-ROOT.1`; `G-ROOT.2` is a second line of defence that cannot fire while `G-ROOT.1` stands, and none of it closed a live hole.** Leg `(r6)` drives every entry against the disk: **14 exist, 0 ghosts** at this freeze.

**`ALREADY_BOUGHT`.** A second invocation against an arm with an `rc=0` ledger row is refused at rc = 3. **Two records for one run is the defect.**

**The cap table is PARSED, not trusted.** Leg `(r2)` reads the comment table and the code table out of the file and requires them to agree on all seven arms **and** that every in-container wall equals `cap×60/ranks − 180`. A peer lane registered a 3.0 core-min cap and its launcher enforced 6.0 by copy-forward with no assertion; **a comment table that contradicts its own code is what a reviewer in a hurry reads.**

**The source-only door.** The comparator's selftest **sources** this launcher to get the real ledger writer. Leg `(r4)` proves that sourcing prints **nothing**, creates nothing and returns 0 — so the suite cannot become a weapon.

**Producer and consumer are driven against each other.** Leg `(r5)` calls the launcher's own `d19o_ledger_row` and requires `d19o_grade.py:_LEDGER` to parse it, on all seven checked fields. **SO-1a's comparator selftest reproduced the row format in a Python constant, so a launcher/reader divergence would have left the suite green and the reader blind on the real run.**

---

## 9. THE OPTIMISER MAPPING AND THE STALL ABORT

### 9.1 The mapping — `DAFOAM_CHARTER.md` §9, per row

> `PASS` **only** where the optimiser itself printed a convergence statement against its **own** tolerance — and then still subject to this item's ceiling.

* IPOPT printed `Optimal Solution Found.` on its `EXIT` line → eligible for `PASS`, **capped to `GATE REACHED`**.
* Stopped by a wall clock, an iteration cap, a budget or the registered stall abort → **`GATE REACHED`** where the registered intermediate threshold was met, **`NOT A RESULT`** otherwise.
* **Never `PASS`, and never described by the size of the improvement it reached.**

**The registered intermediate threshold: ≥ 2.0 % drag reduction against the run's own trimmed baseline, over at least 5 major rows.** A run of fewer than 5 majors has not searched. **2.0 % is deliberately low**, because on a ground whose gradient has no verdict the interesting outcome is *whether the optimiser descends at all*, not how far.

**The standing example this rule is made of.** A2's `opt_IPOPT.txt`: a genuine IPOPT 3.13.5 / MUMPS / L-BFGS run, `tol = 1e-5`, `max_iter = 100`, **47 majors in a 60-minute box**, drag reduced **28.275488 %** at matched `CL ≈ 0.5`. **IPOPT printed no `EXIT` line and no convergence statement anywhere in the log; the table simply stops after iteration 47.** Re-measured here with this item's own parser: **48 rows, `exit = None`**. The 28 % is `GATE REACHED`.

**The `CL` pair travels with EVERY drag number this item publishes.** `d19o_xf.py` writes `CL_baseline_trimmed` and `CL_final` into `d19o_O.json`, and `G-OPT9` republishes both. **A drag reduction at an unstated `CL` is not a reportable number.**

### 9.2 The stall abort — TWO conditions, and ONE OF THEM HAS NEVER FIRED ON A REAL LOG

**Condition A** — **8 consecutive majors** with `alpha_pr < 1.0e-3`.
**Condition B** — dual infeasibility (`inf_du`) **non-decreasing** over **8 consecutive majors**, with a relative tolerance of `1.0e-12` so that floating-point noise in a genuinely decreasing series cannot read as "non-decreasing".

**CALIBRATION, RE-DRIVEN BY THIS ITEM'S OWN PARSER ON 10 REAL IPOPT LOGS AT THIS FREEZE** (`d19o_stall.py --calibrate`):

| log | rows | `EXIT` | A | B |
|---|---|---|---|---|
| `CURRICULUM-D6/O_mp` | 65 | *(none)* | **fires, row 34** | — |
| `CURRICULUM-D6R/O_mp` | 74 | `Invalid number in NLP function…` | **fires, row 34** | — |
| `CURRICULUM-SO1bR/O-P` | 12 | `Optimal Solution Found.` | — | — |
| `CURRICULUM-SO1bR/O-S` | 12 | `Optimal Solution Found.` | — | — |
| `CURRICULUM-SO3/O-P` | 10 | `Optimal Solution Found.` | — | — |
| `CURRICULUM-SO3/O-S` | 12 | `Optimal Solution Found.` | — | — |
| `CURRICULUM-D1/armO` | 12 | `Optimal Solution Found.` | — | — |
| `A2-mach-wing` | 48 | *(none)* | — | — |
| `CURRICULUM-D8/opt` | 4 | `Maximum Number of Iterations Exceeded.` | — | — |
| `CURRICULUM-D5/O48` | 101 | `Maximum Number of Iterations Exceeded.` | — | — |

**Condition A fires on exactly 2 of 10 — both the known D6 stalls — and on NEITHER of the 2 that ended `Maximum Number of Iterations Exceeded`. A CAP IS NOT A STALL, and the detector distinguishes them.**

**Condition B fires on 0 of 10 and is registered `NOT EXERCISED`. It is NEVER reported as a passing control.** A selftest leg proves B *can* fire on synthetic bytes, so its zero is a reading and not a broken reader — `CLAUDE.md` rule 3 applied to a detector. `SO-3` §9.2 records the reason B carries no load: *"dual infeasibility worsening"* was assumed to be a monotone claim and **it is not** — on C-188's own artefact `inf_du` goes `5.71e-03 → 1.14e-03`, a **5× improvement**, on a run that genuinely stalled. **Condition A carries the entire load.**

### 9.3 The stop is the FIRST REACH of the window, and the definition is registered

The abort fires at the **first** major at which an 8-major window is complete — **not** at the end of the longest run of stalled majors. **Re-measured here on `CURRICULUM-D6-a2-wing-multipoint/O_mp/opt_IPOPT.txt`: 65 rows, first reach at row index 34 (0-based) = the 35th row, IPOPT `iter` label 34.** This **independently reproduces** `SO-3` §9.3's reading. A watchdog built on "the longest run" would not have stopped until major 60 and would have saved 6 %, not 46 %.

### 9.4 Every count is cited with its definition or it is not cited

`SO-3` §9.4 measured six plausible definitions of "line-search cutbacks" on one log and got six different numbers, against a record that quoted **545** with no definition at all. **Re-measured here on D6's own bytes by `d19o_stall.cutback_counts`, and every figure reproduces `SO-3`'s exactly:** majors 65, restoration majors 7, `Σ(ls)` **611**, `Σ max(0, ls−1)` **547**, non-restoration `Σ max(0, ls−1)` **450**, non-restoration `Σ(ls)` **507**, majors with `ls > 1` all/non-rest **48 / 44**. **545 is not reachable under any of the six.** Every count this module returns is keyed by the name of its own rule.

---

## 10. THE GRADING PATH

**`d19o_grade.py`, md5 `419ce2363743bd16109826f2bf75d4f2`.**

**A REFUSAL IS `NOT A RESULT`, NEVER A DEGRADED VERDICT, AND IT EXITS 2.** It refuses on a **malformed** artefact and on a broken provenance. It **NEVER** refuses on an **absent** one: **D6 registered a chain stop as a meaningful outcome and its grader refused, exit 2, with ZERO gate readings, because one arm carried no ledger row — leaving 2,257.933 core-min of real optimisation behind an instrument that could not read it (L-322).** Here an absent arm is a **census reading** that `G-STAGES` gates on, and every arm that ran is graded. Selftest legs `E10`–`E13` drive both halves.

**No `assert` statement appears anywhere in the comparator.** `python3 -O` strips them, so an assert is not a guard (L-332). `count_asserts()` proves it and **is itself proved against a planted assert** (leg `F2`) — a zero from a reader never shown a non-zero is not evidence.

**No key is found by a recursive hunt.** Every nested location is an explicit tuple path (`dig()`); a reader that goes looking until it finds something will always find something.

**`--out` is MANDATORY and the DRIVER names it.** SO-1c refused because a comparator composed its own stamped path and wrote to an address the driver never looked at. `verdict` and `rows` sit at the **top level** with the literal key `gates["G-PLAT7"]`, because `d19o_stop_marker.sh` reads them there — and **that contract is DRIVEN in both directions** by leg `(c6)`: the real marker runs on a real artefact the real comparator wrote, then the key is **renamed** and the marker is required to report it absent. **A schema contract that cannot fail is not a contract.**

**The freeze sha is deliberately not written into the comparator.** This document is frozen **after** the instruments, so no sha exists at the moment the comparator is written and a sha written there could only be wrong or back-dated. **The binding runs the other way and is checkable today: this section pins the file by md5, and the driver asserts it with `md5sum -c` before staging any arm.**

---

## 11. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED — WITH A POSITIVE CONTROL

**The condition: this item's registered run root does not exist, no arm of this item has run, and the item id was free.**

**How it was checked at this freeze, and the checker was shown able to see the other answer** (`CLAUDE.md` rule 3 applied to the checker, not to a comparator):

| probe | `CURRICULUM-D19O-a1-naca0012-subsonic-optimisation` | positive control: `CURRICULUM-D19R-a1-naca0012-subsonic-plateau` |
|---|---|---|
| run root, `ls -d` on the literal path | **ABSENT** | **EXISTS** |
| run root, `ls -d` on the glob `*D19O*` / `*D19R*` | **no match** | **matched and listed** |
| case directory `curriculum_D19O` / `curriculum_D19R` | **ABSENT** before this item | **EXISTS** |
| `grep -rn 'D19O'` over `cases/ docs/ verification/ scripts/` | **zero hits** | `D19R2` returns hits in two files |

**The same readers, in the same invocation, returned EXISTS for the things that exist and ABSENT for this item's.** A zero from a reader not shown able to see a non-zero is not evidence, and that applies to an absence check as much as to a comparator.

**No `opt_IPOPT.txt` exists anywhere under `/home/ubuntu/certonomous-runs/CURRICULUM-D19*`** — checked with a reader that returned **20 hits** across the rest of the run tree in the same invocation. **No compressible optimisation has ever run in this lab.** That is the measurement this item exists to change.

**Every path, directory and artefact name cited in this document was verified to exist on disk at this freeze**, except those explicitly named as run outputs that must **not** yet exist (`d19o_O.json`, `d19o_X.json`, `d19o_F.json`, `d19o_xopt.json`, `checkMesh.log`, `ledger.txt`, `D19O_grade_*.json`, `D19O_STOP_MARKER.json`).

### 11.1 THE NAME, AND THE TWO NAMES THIS ITEM DELIBERATELY DID NOT TAKE

**`D19O` — D19, the Optimisation phase.** Derived from precedent on disk, and two adjacent names were refused rather than overlooked:

* **`SO-4` is RESERVED BY SANAA and is NOT taken.** `docs/LAB_STATE.md:1274` carries her own SO-ladder ordering verbatim: *"SO-1 … → SO-2 constraint families → SO-3 multipoint → **SO-4 3-D wing (ONERA M6 / CRM…)**"*. `curriculum_SO3D/PREREGISTRATION.md` §0 records that this family already made exactly this class of error once — *"THE NAME IN THE ORDER WAS WRONG, ON SANAA'S OWN WORDS"*.
* **`D20` is RESERVED BY D19's OWN DOCUMENT and is NOT taken.** `curriculum_D19/PREREGISTRATION.md:41`: *"**D20** — this same design on D16's **transonic** ground — is named here as the immediate successor."* This item is the **subsonic** optimisation, not that one.
* **An `R` suffix would be FALSE.** `D19R` and `D19R2` are the family's `R`-line and denote **re-runs of the same program** (`SO-3a → SO-3aR → SO-3aR2`, `D12 → D12R → D12R2`). This item runs a **different program** — the optimiser — so an `R` suffix would say the wrong thing. The letter `O` follows the family's other shape: `SO-1a` (gradient) → `SO-1b` (optimisation) on the same case.

---

## 12. COST

**Unit: core-minutes** (wall s × ranks ÷ 60). Not wall time and not dollars.

### 12.1 The registered cap table and point prediction

| arm | ranks | **predicted, core-min** | **cap, core-min** | in-container wall | memory |
|---|---|---|---|---|---|
| `MESH` | 1 | **0.20** | **5.0** | 120 s | 12g |
| `O-S` | 1 | **7.57** | **40.0** | 2220 s | 12g |
| `XE-S` | 1 | **1.40** | **10.0** | 420 s | 12g |
| `FE-S` | 1 | **2.98** | **20.0** | 1020 s | 12g |
| `O-P` | 1 | **7.57** | **40.0** | 2220 s | 12g |
| `XE-P` | 1 | **1.40** | **10.0** | 420 s | 12g |
| `FE-P` | 1 | **2.98** | **20.0** | 1020 s | 12g |
| **ITEM POINT** | | **24.10** | | | |
| **ITEM CEILING** | | | **145.0** | | |

**`ITEM CEILING = 145.0 core-min` is `Σ(caps)`, ASSERTED IN CODE** (`d19o_grade.py:g_caps` refuses if the constant and the sum disagree), not restated by hand.

**Caps are CEILINGS. Predictions are ESTIMATES. They are different numbers**, and the rule-12 ratio is taken against the **prediction**, never the cap. `MESH`'s cap is 5.0 while its prediction is 0.20; conflating them would report a 25× underspend.

**The wall column is the C-188 cap frame:** every in-container wall is `cap × 60 / ranks − CAP_MARGIN_S` with `CAP_MARGIN_S = 180 s`. The host-frame margin is charged to the ceiling so the ledger cannot record `core_min > cap` on an arm that reaches its own deadline — **a `GATE FAIL` manufactured by the frame rather than by the run**. The comment table and the code are **both parsed** by selftest leg `(r2)`, which refuses if they diverge.

**Dollars are DERIVED, NOT MEASURED**, at **c7a.4xlarge $0.0513/core-h**, **reported-by-owner** (Sanaa, 2026-08-21/22) — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Point **$0.020606**; ceiling **$0.123975**. **GPU: 0 GPU-h.** Both far under the $25 pre-authorisation, **and the item is still costed here, because a blanket is not a per-item reading** (`CLAUDE.md` rule 9).

**An overrun STOPS THE RUN and does not get a new budget.** The launcher reports at the cap (`D4S_CAP_CROSSED`, run continues, supervisor decides) and **hard-stops** at `CEILING = 4 × cap` (`D4S_CEILING_HIT`).

### 12.2 THE §18.1 COST ANCHOR — THE PROGRAM IS NAMED AND THE MATCH IS ASSERTED

`DAFOAM_CHARTER.md` §18.1 makes a pre-registration **REFUSABLE** if it prices an arm from a prior measurement without stating **what program** that measurement priced, on four terms: **ranks, adjoint yes/no, colouring yes/no, tree cold or already-decomposed** — and then asserting the match.

**ANCHOR A — the optimiser major rate. [MEASURED]**

| term | the anchor's program | **this item's `O` arm** | match |
|---|---|---|---|
| source | `CURRICULUM-SO1bR-a1-naca0012-dragmin-opt`, arms `O-P` and `O-S`, ledger rows | — | — |
| ranks | **1** | **1** | ✔ |
| adjoint | **YES** — one `CD` and one `CL` adjoint per major | **YES**, identically | ✔ |
| colouring | **YES** — the Jacobian is coloured on the first adjoint | **YES**, identically | ✔ |
| tree | **COLD** — staged from `MESH`, `decomposePar` not run at np=1 | **COLD**, identically | ✔ |
| case | A1 NACA0012, 4,032 cells, one FFD shape function + `patchV`, `CD` objective, `CL = 0.5` equality, `findFeasibleDesign` trim before the driver | **identical program** | ✔ |
| **solver** | **`DASimpleFoam` (INCOMPRESSIBLE)** | **`DARhoSimpleFoam` (COMPRESSIBLE)** | **✘ — the one term that differs, and Anchor B is what bridges it** |

**The rate: `O-P` 4.700 core-min / 12 rows = 0.3917; `O-S` 4.717 / 12 = 0.3931. Mean 0.3924 core-min/major, and the two agree to 0.36 %.** Corroborated independently by `C-24` (D1 `armO`, 0.42127 core-min/major on this same A1 case at np = 1). Row counts read from the logs themselves: `Number of Iterations....: 11` → **12 table rows** on all three.

**ANCHOR B — the compressible penalty. [MEASURED], on the same mesh, at the same rank count.**

| term | compressible | incompressible |
|---|---|---|
| source | `CURRICULUM-D19-.../S1` ledger row + artefact | `CURRICULUM-SO3-.../FE-S` and `FE-P` ledger rows + artefacts |
| ranks | **1** | **1** |
| adjoint / colouring | **NO / NO** | **NO / NO** |
| tree | **COLD** | **COLD** |
| mesh | **A1, 4,032 cells** | **A1, 4,032 cells** |
| delivered cores | **0.9930** of 1.0 | **0.9936 / 0.9957** of 1.0 |
| reading | 51 s ÷ **12 primals** = **4.250 s/primal** | 267 s ÷ **102 primals** = 2.618; 272 ÷ 102 = 2.667; **mean 2.642 s/primal** |

**RATIO = 4.250 / 2.642 = 1.6086×.** Corroborated by D19R's own `S1` arm, contention-corrected: 135 s × 0.3956 delivered ÷ 12 = 4.451 core-s/primal → ratio **1.685**, agreeing with 1.6086 to **4.8 %**. (Primal counts read from the artefacts: D19R `S1` 5 components × 1 step × 2 signs + 2 baselines = 12; SO-3 `FE` `evaluations_declared: 34` × 3 scenarios = 102.)

**THE PRODUCT, AND IT IS TAGGED `[EXTRAPOLATED]`, NOT `[MEASURED]`:**

```
0.3924   core-min/major   [MEASURED]      SO-1bR O-P/O-S, A1, np=1, incompressible, single point
× 1.6086                  [MEASURED]      compressible/incompressible PRIMAL ratio, same mesh, np=1
= 0.63122 core-min/major  [EXTRAPOLATED]  the ratio is measured on the PRIMAL and is carried onto a
                                          major that is primal + 2 adjoints + mesh warp
× EXPECTED_MAJOR_ROWS 12  [MEASURED]      SO-1bR O-P, SO-1bR O-S and D1 armO each returned exactly
                                          11 IPOPT iterations / 12 table rows on THIS case at np=1
= 7.5746 -> 7.57 core-min/O arm
```

**The cap of 40.0 core-min per `O` arm prices `max_iter = 40` at that rate (25.25 core-min) with 1.58× headroom, precisely because the point is an extrapolation.**

### 12.3 THE MISTAKE THIS ITEM DOES NOT REPEAT

**`SO-3` registered 228.59 core-min and spent 28.900 — ratio 0.126× — and the entire gap was one mistake: its IPOPT arms were priced at their `max_iter` of 50 majors and converged in 10.** Its `O-S`/`O-P` predictions of 103.0 each cost 7.917 and 6.950 (ratios 0.077 and 0.067). Every non-optimiser arm of SO-3 came in at **0.59–0.88×** of prediction, which is the accuracy this item aims at.

> **THE REGISTERED REPAIR: the `O` arms are priced at an EXPECTED major count of 12, and `max_iter = 40` is the CAP and is priced into the cap alone.** A selftest leg `(c7)` reads the driver's own cost block and requires it to state that basis, to carry the same `EXPECTED_MAJOR_ROWS` as `d19o_xf.py`, and to match `d19o_grade.py:PREDICTED_CORE_MIN` on all seven arms — so the estimate cannot drift between the three files that state it.

### 12.4 `P_COST` — the band, derived from the cost model rather than drawn around the point

**A band that cannot MISS is exactly as useless as one that cannot HIT**, and it is the easier mistake to make once the point estimate is known. The five non-`O` arms are 8.96 core-min; the entire uncertainty is `2 × (majors × rate)`.

| scenario | majors/arm | rate | **item total** | in band? |
|---|---|---|---|---|
| **S0** — both optimisers converge in 4 majors | 4 | 0.6312 | **14.01** | **OUT (low)** |
| **S1** — 8 majors | 8 | 0.6312 | **19.06** | in |
| **S2** — 12 majors, **THE REGISTERED POINT** | 12 | 0.6312 | **24.11** | in |
| **S3** — 20 majors | 20 | 0.6312 | **34.21** | in |
| **S4** — the compressible penalty is itself short by its own margin (×1.6086 → ×2.5) | 12 | 0.9810 | **32.50** | in |
| **S5** — 30 majors | 30 | 0.6312 | **46.83** | in |
| **S6** — `max_iter`, all 40 majors | 40 | 0.6312 | **59.46** | in |
| **S7** — both `O` arms stopped at their 40.0 cap | — | — | **88.96** | **OUT (high)** |

**REGISTERED BAND: `P_COST` = [15.0, 65.0] core-min.** It contains S1–S6 and excludes S0 below and S7 above. The point 24.11 sits at **18 % of the band's width — not centred, deliberately**, because the upside (more majors on a problem that has never been optimised) is the better-evidenced tail.

**WHAT FALSIFIES IT, REGISTERED BEFORE THE RUN.** A graded item total **below 15.0** — both optimisers converging in far fewer majors than the three-run precedent of 12 — **or above 65.0** — the compressible penalty failing to transfer, or an optimiser running to its cap on a gradient that does not descend. **Both are plausible outcomes of this run**, which is the property a usable band must have.

### 12.5 Calibration at completion is owed, and this is where it goes

At this item's completion the comparison of predicted against actual lands as a row in **`docs/COST_CALIBRATION.md`**, under that file's append rules and the rule-10 private-index protocol. `d19o_grade.py:g10_caps` computes `ratio_actual_over_predicted` **per arm against `PREDICTED_CORE_MIN`, never against the cap**, and publishes the `cost_basis` string and the derived dollar figure with its not-measured label. **The completion report is incomplete without that row** (`CLAUDE.md` rule 12).

---

## 13. PREDICTIONS — REGISTERED BEFORE THE RUN, AND A MISS IS A FINDING

**Each token is registered with EVERYTHING it scores, spelled out, so that no reader has to infer a conjunct from a name.** That rule exists because `SO-3`'s `P5_PATCHED_G5J_PASS_4_of_4` reads as though it scores only a pair count and in fact scores three conjuncts.

| token | **everything it scores** | registered prediction |
|---|---|---|
| `P1_cells_4032` | `G-M2` verdict is `PASS` | **HIT** |
| `P2_shipped_optimiser_converges` | `G-OPT9[SHIPPED].ipopt_printed_convergence` is `true` | **HIT** — three single-point IPOPT runs on this case each printed `Optimal Solution Found.` |
| `P3_patched_optimiser_converges` | `G-OPT9[PATCHED].ipopt_printed_convergence` is `true` | **HIT** |
| `P4_majors_in_band` | **BOTH** rows' `ipopt_table_rows` lie in **[8, 20]** | **HIT** — 12/12/12 measured on this case, widened for a solver never optimised here |
| `P5_shipped_row_worse_than_patched` | SHIPPED `drag_reduction_pct` **<** PATCHED's | **HIT** — D15 measured the shipped adjoint 44.8738 % wrong on the component carrying 76.414 % of the gradient norm |
| `P6_patched_endpoint_fd_PASS` | **TWO conjuncts:** (i) `G5_fd[PATCHED]` verdict is `PASS`, **AND** (ii) `aggregate_pct_excl_flagged_CD ≤ 5.0 %` | **MISS** — see 13.1 |
| `P7_shipped_endpoint_fd_GATE_FAIL` | `G5_fd[SHIPPED]` verdict is `GATE FAIL` | **HIT** |
| `P8_trivial_baseline_PASS_both_rows` | `G-TB` is `PASS` on both rows, i.e. at most 1 of 4 components passes band D at `h = 1e-8` | **HIT** |
| `P9_shape7_NOT_A_RESULT` | `G-PLAT7` is `NOT A RESULT` on both rows | **HIT BY CONSTRUCTION** — see 13.2 |
| `P10_item_GATE_REACHED` | item verdict is `GATE REACHED` | **HIT** |
| `P_COST_total_core_min_in_band` | `15.0 ≤ g10["total_core_min"] ≤ 65.0`, behind one measurability guard (`NOT MEASURED` if any run arm reported no `core_min` or `G-STAGES` is short) | **HIT** |

### 13.1 `P6` is registered as a MISS, and the reasoning is registered with it

**The endpoint plateau has never been measured on this ground, and there is a specific reason to expect it not to close.** `DAFOAM_CHARTER.md` §9 records that the IDWarp `getRotationMatrix3d` degenerate-rotation branch is **guaranteed to fire at the undeformed baseline** (`axisMag = 1e-15 < tol = sqrt(eps)`) and that its second regime **D-A2 behaves differently just above the threshold**: measured error against angle reads 1e-5 rad → 4.1e-08, 1e-6 → 6.7e-05, 5e-8 → 1.2e-02. **A design point displaced from the baseline sits on the other side of that guard.** So the endpoint FD is the arm most likely to move, and this lane predicts it moves enough to fail.

**A MISS HERE IS THE BETTER OUTCOME AND IS REGISTERED AS SUCH:** it would mean the patched gradient survives the design point, which is the single most useful thing this item could learn. **`P6` is registered as a MISS so that a HIT cannot later be claimed as expected.**

**Honesty about the prior art of this prediction class:** `SO-3` registered `P6_SHIPPED_G5J_GATE_FAIL` and **MISSED** — its shipped row **PASSED** on the incompressible multipoint. **`P7` here is the same shape on a different solver, and it may miss the same way.** It is registered anyway, with the reasoning, and a MISS will be reported as a finding rather than explained away.

### 13.2 `P9` is a HIT BY CONSTRUCTION, and it is labelled one

`P9` scores a gate this document **registers** as `NOT A RESULT` from a list rather than from a measurement. **Its HIT therefore carries no information about `shape[7]` and may never be reported as evidence that the component behaved as expected.** It is registered so that the gate's behaviour is checked — a `G-PLAT7` that returned anything else would mean the comparator had been edited — and for nothing else. This is the `SO-3` `P_COST` defect named in advance rather than discovered after.

### 13.3 The registered outcome, written before any container starts

**SHIPPED row: `GATE FAIL` or `NOT A RESULT`. PATCHED row: `GATE REACHED`. ITEM VERDICT: `GATE REACHED`.** A predicted `GATE REACHED` is **REGISTERED, not avoided.**

---

## 14. WHAT THIS ITEM WILL NOT ESTABLISH

* **It will not establish that the compressible adjoint is verified.** §0. The gradient it spends has **no graded verdict** and its plateau did not close.
* **It will not establish that "DAFoam reduces compressible drag by X".** Only *"on the patched toolchain `dafoam-idwarp-rot:v1`, and on a gradient whose plateau did not close, …"*.
* **It will not establish anything about `shape[7]`.** §3. Its row is a registered non-result on both rows, whatever it returns.
* **It will not establish anything at np ≠ 1.** §5. A4 measured a 16,600× decomposition spread; nothing here speaks to np > 1.
* **It will not establish a dot-product duality check.** `G6` is `NOT MEASURED`: AV-2 measured that seeding forward mode makes the primal **FAIL** on this exact case on **both** images.
* **It will not establish a grid-converged optimum.** No grid triple, no GCI, and the comparator says so rather than omitting it.
* **It will not establish a transonic result.** M 0.288 is weakly compressible (§1); `D20` is the transonic successor and is not registered here.
* **It will not settle whether the IDWarp defect is absent from any component.** A shipped-versus-patched divergence of 0.000 % is reported with its number and is never read as absence.

---

## 15. NAMED RESIDUALS — WHAT COULD NOT BE VERIFIED AT THIS FREEZE

Each is named rather than papered over. None is a reason not to freeze; each is a reason not to over-claim.

* **R1 — NO ARM HAS RUN.** Every gate is driven against **fixtures plus ten real IPOPT logs**. **Nothing in the suite is validated against a real D19O artefact**, because none exists. The fixtures are built by the instrument's **own writers** (`d19o_xf.build_fd_step` / `build_fd_row` / `build_ctrl_row`) and by the launcher's **own** `d19o_ledger_row`, sourced and called — which removes the SO-1c tautology but does **not** substitute for a real artefact. **A green suite is a result about the comparator, not about the run.**
* **R2 — THE PRODUCER CANNOT BE EXECUTED ON THIS HOST.** `d19o_xf.py` needs `mphys`, `dafoam`, `pygeo` and `idwarp`, none importable outside the containers. Its selftest drives the **header exec-path** (md5, anchor count, compile) and the **AST**; **it does NOT prove the model builds in-container, and it does not prove `OptFuncs.findFeasibleDesign` behaves as the header's tail assumes.** **The first `O-S` arm is the first real test of the producer**, and it is the shipped row — the cheap half.
* **R3 — THE `O` MODE HAS NEVER BEEN EXECUTED IN ANY FORM.** D19R's instrument had no optimiser mode at all; `d19o_xf.py`'s mode `O` is **new code** that constructs the pyOptSparse driver itself. Its `d19o_O.json` and `d19o_xopt.json` writers are exercised only through fixtures built by the comparator's selftest, **not by the producer**. This is the largest single unknown in the item.
* **R4 — THE COMPRESSIBLE MEMORY FOOTPRINT IS `[EXTRAPOLATED]`.** §5. No compressible **optimiser** arm has ever run on this case; the 12 g cgroup rests on D13's measured 1.70 GiB at np=1 plus a crude multiplier. The item's own first solver arm measures it.
* **R5 — THE `1.6086` COMPRESSIBLE RATIO IS MEASURED ON THE PRIMAL AND CARRIED ONTO A MAJOR.** §12.2. A major is primal + 2 adjoints + mesh warp, and the compressible adjoint carries extra states (density, energy) whose cost ratio is **not** separately measured here. The product is tagged `[EXTRAPOLATED]` for exactly this reason.
* **R6 — `d19o_chain_driver.sh` IS NOT SELF-PINNED.** It holds the pins, so it cannot pin itself. Its md5 is recorded in §7 row 1 as a **reading at this freeze**, and nothing in the executable path asserts it. The `d19o_repin.sh --verify` path detects drift in the **pinned** files, not in the driver.
* **R7 — CONDITION B OF THE STALL DETECTOR IS `NOT EXERCISED` ON REAL BYTES.** §9.2. It fires on 0 of 10 real logs. It is proved *capable* of firing on synthetic bytes, so its zero is a reading; it is **never** reported as a passing control.
* **R8 — `d19o_stall.py`'s ROW REGEX IS CALIBRATED ON `print_level 5` IPOPT TABLES ONLY.** All ten calibration logs are that shape. A different `print_level` would change the column count and the parser would return **zero rows** — which `G-OPT9` would read as `NOT A RESULT`, i.e. it fails closed. That is the safe direction and it is stated rather than left to be discovered.

---

## 16. FREEZE

**Frozen at this document's own commit.** From this commit forward:

* **Before first compute**, amendments are legal and **must state the condition and how it was checked**, naming the run directory that does not exist — as §11 does.
* **After first compute**, the gates, thresholds, caps and labels above are **closed**. Changes land only as **dated addenda** that cannot alter a gate, a threshold, a cap or a label. Originals are **struck, never rewritten**.
* **The grading path is fixed at this commit**: `d19o_grade.py`, md5 `419ce2363743bd16109826f2bf75d4f2`, and the driver asserts that value with `md5sum -c` before staging any arm.
* **Nothing is filed, sent, posted, uploaded, registered or commented upstream by any agent, ever.** `CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10. **SUBMISSIONS ARE PARKED.**

**Not cleared to launch by this document.** This is a freeze, not an authorisation. The `dafoam-supervisor`'s **pre-registration-committed** check and **grader-read-as-a-diff** check come first, and neither is this lane's to make.
