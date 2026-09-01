# CURRICULUM D19M — NACA0012 **COMPRESSIBLE ALPHA-MULTIPOINT SHAPE OPTIMISATION**, `DARhoSimpleFoam`, M 0.288, BOTH TOOLCHAIN ROWS, np = 1. PRE-REGISTRATION (FROZEN)

**Item id:** `CURRICULUM-D19M`
**Run root (registered, ABSENT at this freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint`
**Case directory:** `cases/dafoam/ladder-a/A1/curriculum_D19M/`
**Freeze:** this document's own commit. `CLAUDE.md` rule 2.

**Status: `PENDING`.** No arm of this item has run. **Nothing here is a result.**

**NOT FILED ANYWHERE. SUBMISSIONS PARKED** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**This freeze authorises NOTHING.** The `dafoam-supervisor`'s two `SUPERVISION_CHARTER.md` §3 checks — pre-registration **committed** before compute, and the grader read **as a diff** — come first.

---

## 0. WHY THIS ITEM EXISTS, AND THE ONE THING A READER MUST NOT TAKE FROM IT

**Sanaa's standing branch order** (`055376a0`), verbatim: *"before i switch, the compressible multipoint should also be queued if the compresible single pt was ran. if not the compressible single pt should be ran."*

**The compressible single point HAS now run.** `CURRICULUM-D19O` completed 2026-09-01: seven arms of seven, all `rc=0`, `chain_rc=0`, **16.184 core-min**, item verdict **`GATE REACHED`** (`curriculum_D19O/RESULTS.md`). **The first limb of the order is discharged and the second now fires.** This item is that second limb.

> **THIS ITEM CANNOT PUBLISH `PASS`.** `d19m_grade.py:VERDICT_CEILING = "GATE REACHED"`, applied by `_apply_ceiling()` as the last step of every composition; `G-PROV` **REFUSES (exit 2)** if it is removed or widened.

**THE CEILING IS RE-DERIVED FOR THIS ITEM RATHER THAN COPIED**, because the supervisor asked for the reasoning and not the constant. The answer is that it stays, and for a **stronger** reason than D19O's:

1. **The compressible gradient basis still has no graded verdict.** D19R's grader refused `rc=2`; D19R2's grading attempt 1 returned `NOT A RESULT`. Unchanged by D19O, which was ceilinged for exactly this.
2. **D19R's plateau still did not close on `shape[7]`** — `all_two_sided: false`, `score_pct: 21.060684242435336`.
3. **AND THE MULTIPOINT OBJECTIVE `J = Σᵢ wᵢ·CDᵢ(αᵢ)` HAS NEVER HAD AN FD TABLE ON COMPRESSIBLE GROUND AT ALL.** D19O verified a *single-point* `CD`. This item's own `FE` arms are the **first** FD table any compressible multipoint objective in this lab has ever had. **The basis here is thinner than D19O's, not thicker.**

---

## THE TEN LINES

1. **The quantity optimised is `J = Σᵢ wᵢ·CDᵢ(αᵢ)`** over **one shared 8-component `shape` vector**, with three operating points and **equal weights 1/3**.
2. **Two rows, always** — and §2 records the specific reason D19O's finding makes this *more* necessary, not less.
3. **α is the OPERATING POINT and is NOT a design variable.** `add_design_var("patchV", ...)` is **gone**, and its removal is registered, not silent. **Consequence: `CL` is unconstrained and the three-`CL` triple travels with every drag number.**
4. **`shape[7]` is retained in the DV vector and its FD row is a REGISTERED NON-RESULT** — carried forward from D19O **unchanged**, and §3 states why D19O's own contrary measurement does not license changing it.
5. **The verdict is CEILINGED at `GATE REACHED`** — §0, re-derived.
6. **np = 1 on every arm.** §5.
7. **The endpoint plateau test is D19R's `G19R-1b`, unchanged** — decade neighbours, `max` not `min`, 10.0 %.
8. **Seven arms**, with the §9 endpoint FD in this chain.
9. **The optimiser is IPOPT, `max_iter = 40` as a CAP, priced at an EXPECTED 12 majors.** §12.
10. **Two gates exist here that D19O did not have** — `G-ALPHA` and `G-MP-STRUCT` — because a multipoint item can carry two defects invisibly that a single-point one cannot. §4.1.

---

## 1. THE ITEM

Seven arms, chain order, all np = 1, 12 GiB cgroup, **cpuset 13**.

| arm | row | kind | what it does | artefact |
|---|---|---|---|---|
| `MESH` | SHIPPED | SCRIPT | `preProcessing.sh && checkMesh` + byte-identity against D15's frozen mesh | `checkMesh.log` |
| `O-S` | SHIPPED | SOLVER | the IPOPT multipoint optimisation | `d19m_O.json`, `d19m_xopt.json` |
| `XE-S` | SHIPPED | SOLVER | the **adjoint** at the SHIPPED optimum | `d19m_X.json` |
| `FE-S` | SHIPPED | SOLVER | the **FD table** at the SHIPPED optimum | `d19m_F.json` |
| `O-P` | PATCHED | SOLVER | the IPOPT multipoint optimisation | `d19m_O.json`, `d19m_xopt.json` |
| `XE-P` | PATCHED | SOLVER | the **adjoint** at the PATCHED optimum | `d19m_X.json` |
| `FE-P` | PATCHED | SOLVER | the **FD table** at the PATCHED optimum | `d19m_F.json` |

**The operating points, and the centre is a QUOTATION rather than a choice:**

| | α, degrees | weight |
|---|---|---|
| `point0` | **2.787333582** | 1/3 |
| `point1` | **4.787333582** | 1/3 |
| `point2` | **6.787333582** | 1/3 |

**4.787333582° is D19O's OWN MEASURED trimmed angle at `CL_target = 0.5`** on this exact compressible case, read from `.../CURRICULUM-D19O-.../O-S/d19o_O.json` → `dv_trimmed.patchV[1]`. Using SO-3's incompressible centre (5.13918623195176) would have been a number from a different solver on a different state equation. **The ±2° half-width and the equal weights are LANE-CHOSEN and registered as lane-chosen.** All three lie inside the tutorial's own `[0.0, 10.0]` aoa bound.

**ONE `DASolver` PER POINT, EACH IN ITS OWN `run_directory` (`mp0 mp1 mp2`), BEHIND ONE SHARED `OM_DVGEOCOMP`.** Two collisions this is built not to repeat: **SO-3aR died** because three builders with no `run_directory` shared one case directory and each renamed its solution to the same time; **D6 built `geometry_<pt>` per scenario**, which makes `J` a statement about three design vectors that happen to be equal. The launcher stages the three case copies and selftest leg **(r9)** parses **both** files to prove the directory names agree.

---

## 2. TWO ROWS — AND D19O'S FINDING IS THE REASON, NOT AN ARGUMENT AGAINST

D19O measured that **at its optimum the SHIPPED and PATCHED rows agreed to 0.0232 %** on `shape[6]`, where D15 measured the shipped row **44.8738 %** wrong **at the baseline** on this same ground. The mechanism is `DAFOAM_CHARTER.md` §9's own: the IDWarp `getRotationMatrix3d` degenerate-rotation branch fires when `axisMag = 1e-15 < sqrt(eps)`, **certain on an undeformed mesh and false on a deformed one**.

> **A reader could take that as an argument for collapsing to one row. IT IS THE OPPOSITE.** The rows agree **at an optimum** and diverge **at a baseline** — the agreement is **configuration-dependent**. Running one row would **bake in** a property that D19O has just shown is not a property of the toolchain at all, and would destroy the only instrument capable of detecting it. `DAFOAM_CHARTER.md` §6 is unmoved: **a DAFoam verdict is two rows or it is not a verdict about DAFoam.**

**And this item reaches a different optimum from D19O's**, on a different objective, so whether the endpoint agreement reappears here is an open question this item answers rather than assumes.

**The row is read from the toolchain's own identity, twice**: the launcher from the image digest, `d19m_xf.py` from the md5 of the `libidwarp.so` **this interpreter actually imported**, which **REFUSES** to stamp a row it cannot prove. There is no `-row` flag.

---

## 3. `shape[7]` — THE REGISTRATION IS CARRIED FORWARD UNCHANGED, AND THAT IS A DECISION

**D19O MEASURED, at its own optimum:** `|dCD/dshape[7]| = 5.887300e−03` against **2.099480e−04** at the baseline — **a factor of 28** — and **its plateau CLOSES there** (two-sided, coarse 0.974 % / fine 1.061 %), agreeing with the adjoint to 0.1682 %. `curriculum_D19O/RESULTS.md` §3.1 records the finding as: **its near-nullity is a property of the BASELINE, not of the component.**

> **THAT DOES NOT LICENSE GRADING IT HERE, AND THIS ITEM DOES NOT.** `EXCLUDED_FROM_AGGREGATE` still names `("shape", 7)`. `G-PLAT7` still returns **`NOT A RESULT`** on both rows, **set from the registered list and never from a measured value.**

**Two reasons, registered before this run:**

1. **D19O's reading is at D19O's optimum on a SINGLE-POINT objective.** This item optimises `J = Σᵢ wᵢ·CDᵢ` and will reach a **different design point**. **Nothing measured at one optimum is a statement about another** — which is the same sentence that justified the endpoint arms existing at all.
2. **The evidence a successor needs is now ON RECORD, and registering it IN ADVANCE is what a successor may do.** Promoting a component *after* seeing a good number is precisely the move the registration exists to prevent. D19O did not do it with its own measurement in hand; neither does D19M.

**The aggregate is therefore over THREE components** (`shape[0]`, `shape[3]`, `shape[6]`) of four, and its key is literally `aggregate_pct_excl_flagged_J`. `shape[7]`'s own reading is **published beside it, never instead of it** (`DAFOAM_CHARTER.md` §3).

---

## 4. GATES, THRESHOLDS AND LABELS — FROZEN NOW

**Vocabulary: the six tokens and nothing else.**

| gate | threshold | miss |
|---|---|---|
| `G-PROV` | the travelling chain + the ceiling present and not widened | **REFUSAL, exit 2** |
| `G1_completion` | rc = 0, terminal statement, no fatal token, **age guard** | `GATE FAIL` |
| `G-STAGES` | DECLARED 7 vs EXECUTED n | short → `NOT A RESULT` |
| `G-M2_mesh_identity` | **4032** cells exactly | `GATE FAIL` |
| `G-NP` | ranks = **1** on every arm | `GATE FAIL` |
| **`G-ALPHA`** | the three α read back through **both** model paths, to **1.0e-12 absolute**; weights equal the registered ones | `GATE FAIL` |
| **`G-MP-STRUCT`** (per row) | `∂J/∂x` == `Σᵢ wᵢ ∂CDᵢ/∂x` from the artefact's **own** components, relative **1.0e-10** | `GATE FAIL` |
| `G9_toolchain` | image digest **and** `libidwarp.so` md5, per row | `GATE FAIL` |
| `G10_caps` | per-arm cap; item ≤ **149.0** core-min | `GATE FAIL` |
| `G12_placement` | cpuset = **`13`** | `GATE FAIL` |
| `G-DESIGNPOINT` | each endpoint arm at **its own row's** optimum | `GATE FAIL` |
| `G-NOOPT-ENDPOINT` | zero optimiser evidence in `XE`/`FE` | `GATE FAIL` |
| `G-EVALFAIL` | **`EVALS_DECLARED = 34`** per FE arm (= **102 primals**) | `GATE FAIL` |
| `G-OPT9` (per row) | `PASS` only on IPOPT's own statement; else `GATE REACHED` iff **≥ 2.0 %** weighted-drag reduction over **≥ 5** majors; else `NOT A RESULT` | — |
| `G5_fd` (per row) | band D **5.0 %** per component on `J` **and on each scenario's `CL`**; band E **5.0 %** aggregate; plateau **10.0 %**; **≥ 3 graded components** | `GATE FAIL` / `NOT A RESULT` |
| `G-PLAT7` | **always `NOT A RESULT`** | — |
| `G-TB` | `h = 1e-8` on `J`; ≥ 2 of 3 passing **withdraws** `G5_fd` | `GATE FAIL` |
| `G6` | **NOT MEASURED** · `GCI` | **NOT APPLICABLE** (single grid, said explicitly) |

### 4.1 THE TWO GATES A SINGLE-POINT ITEM DOES NOT NEED, AND WHY THEY ARE GATES

**`G-ALPHA` guards the one defect a multipoint item carries INVISIBLY.** If a scenario is silently wired to the wrong angle, **every band still passes** — because the FD table and the adjoint are *both* taken at that same wrong angle, and they agree with each other perfectly. The item would publish a clean verdict about a flow condition nobody registered.

> **THIS IS DRIVEN, NOT ASSERTED.** Comparator selftest leg **`E-MP4`** builds a fixture with `point0` wired **one whole degree off** and requires `G5_fd` to read **`PASS`** — proving the FD gate is blind to it — while `G-ALPHA` reads `GATE FAIL` and carries the item. **A gate whose necessity is only argued is not shown to be necessary.**

**`G-MP-STRUCT` guards the D6 defect.** `∂J/∂x` must reconstruct from the artefact's own `∂CDᵢ/∂x` under the registered weights. If it does not, `J` is not a statement about one shared design vector. Leg `E-MP6` scales one scenario's `dCD` by 1.5 and requires `GATE FAIL`.

### 4.2 Composition

**Per row:** optimiser `NOT A RESULT` → `NOT A RESULT`; `NOT A RESULT` in endpoint FD / trivial baseline / **mp-struct** → `NOT A RESULT`; `GATE FAIL` in any of the four → `GATE FAIL`; optimiser `GATE REACHED` → `GATE REACHED`; else `PASS` → **then the ceiling**.

**Item:** `G-STAGES` short or any row `NOT A RESULT` → `NOT A RESULT`; `GATE FAIL` in any row or in `{G-M2, G-NP, G9, G10, G12, G-DESIGNPOINT, G-NOOPT-ENDPOINT, G-EVALFAIL, G-ALPHA, G-MP-STRUCT×2}` → `GATE FAIL`; `GATE REACHED` in any row → `GATE REACHED`; else `PASS` → **then the ceiling**.

**The ceiling can only make a verdict WORSE.** It binds at row level and the item inherits, so the record also carries `capped_by_ceiling_anywhere` and `rows_capped_by_ceiling` — a true field that leaves a false impression is the defect this family keeps paying for.

---

## 5. RESOURCES, np, AND THE RELAXATION EXPOSURE

**np = 1 on every arm**, enforced in three places (`ranks_of`, an `MPI.Abort`, `G-NP`). Two reasons: `DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across np; and **np = 1 makes D19R2's `MANIFEST_ENTRY_MUTATED` blocker unreachable**, because `decomposePar` never runs. Measured across D19R's six arms: mismatch count 1 on each np=2 arm, **0 on both np=1 arms**. **No exclusion is added to the age guard** — that is a gate-design decision reserved to Sanaa. **Registered falsifier:** if the guard refuses on `system/decomposeParDict`, the np=1 premise is FALSE, the item is `NOT A RESULT`, and that is reported as a measurement.

**Memory 12 GiB per arm.** D13 measured 1.70 GiB peak RSS at np=1 on this case; **three `DASolver` instances in one process** is bounded crudely by `3 × 1.70 ≈ 5.1` GiB plus one shared mesh/FFD/IDWarp footprint. **That bound is `[EXTRAPOLATED]` — no compressible multipoint arm has ever run** — and 12 g carries better than 2× over it. Aggregate ceiling 30.6 GiB in the waiting form; H5 floor 16.0 GiB over 45 samples.

**Cpuset 13.** Read from disk: across `cases/dafoam/ladder-a/*/curriculum_*/*_run_arm.sh`, core 13 appears in exactly **one** registered set, D5's `8,10,11,13` (A2, finished). **Disjoint from D19O's `11`**, SO-3's `14`, D19/D19R's `1,15`, D15's `2,3`, D16's `4,14`, the SO-1/SO-2 line's `9`, D4's `5,6,7,9`, D6's `2,3,4,14`, D7's `2,3,4,6`, D8R's `0,1,12,15`.

### 5b. RELAXATION EXPOSURE (L-426) — **NOT EXPOSED**, and the reason is the solver class

> **`relaxation exposure checked: NOT EXPOSED — solver class is SIMPLE (simpleControl), which never sets the final-iteration flag.`**

**Three measurements, re-driven by this lane rather than accepted:**
1. In OpenFOAM v2606, `setFinalIteration` is called from **exactly one class** — `pimpleControl.C`, four sites — plus one **commented-out** line at `pisoControl.C:45`. **`simpleControl.C` contains ZERO occurrences.** Under a SIMPLE control the flag never leaves its default and `select()` never appends `Final`.
2. **D19O's real launch path constructed `simpleControl`:** its `O-S` log carries `SIMPLE: no convergence criteria found` **4×** and **zero** occurrences of `PIMPLE`, `nOuterCorrectors` or `outer corrector`.
3. **Zero of 165 `fvSolution` files under `cases/dafoam/` declare `PIMPLE` or `nOuterCorrectors`.**

> **THE IMMUNITY IS A PROPERTY OF THE SOLVER CLASS, NOT OF THE FILE, AND THIS REGISTRATION SAYS SO RATHER THAN CLAIMING THE DICTIONARY IS CORRECT — IT IS NOT.** This ground's `fvSolution` carries `fields { "(p|p_rgh|rho)" 0.30; }` and `equations { "(U|T|e|h|nuTilda|k|epsilon|omega)" 0.70; }` — **bare alternations with no `Final` form, which is precisely the vulnerable spelling.** It is safe only because nothing in this item ever constructs a PIMPLE control. **If any successor moves this ground to an unsteady solver, the file becomes exposed the moment it does, with no warning and no log line.** And *"only one outer corrector"* is not a defence: `pimpleControl` sets the flag true even at `nCorrPIMPLE_ == 1` via its `finalIter()` branch. **The defence is that there is no PIMPLE control at all.**

---

## 6. THE ENDPOINT FD

s\* = **1e-3** for `shape`, inherited **by citation** from `.../CURRICULUM-D19R-.../d19r_selected_step.json` → `s_star.shape`. Steps **{1e-2, 1e-3, 1e-4}** — s\* with its **decade** neighbours, `G19R-1b`'s rule verbatim, `max` over both sides at 10.0 %. **A half-decade bracket would be a weaker test and is the one `shape[7]` passes; adopting it after seeing which test the component failed is what `DAFOAM_CHARTER.md` §3 forbids.**

**The aggregate statistic is NAMED:** the vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` as printed, over the **three** non-excluded components, on `J`; and separately on the three per-scenario `CL`. §2 of the charter: **no paper uses a vector norm**, and comparing this against a published per-component average is forbidden.

**Census:** 4 components × 4 steps (3 decade + 1 trivial baseline) × 2 signs + 2 baselines = **34 evaluations**, each of which is **3 primals** (one per operating point) = **102 primals per FE arm**.

---

## 7. THE FROZEN INSTRUMENT TABLE — TEN ROWS, §18.3's ORDER

Existence is asserted for all of them, and `D19M_18_3_EXISTENCE_OK` printed, **before a single md5** — proved in the byte offsets by chain-driver selftest leg **(c3)**.

| row | file | md5 | role |
|---|---|---|---|
| 1 | `d19m_chain_driver.sh` | `c4af7e139aa3a90537706ce70138fe41` | drives the seven arms; **holds the pins, not self-pinned** |
| 2 | `d19m_run_arm.sh` | `267ec3fccb6058da3e37c92af691198b` | the launcher |
| 3 | `d19m_xf.py` | `3b029c4ee4032c459b116bcf128d802e` | the instrument; **its writers build every fixture** |
| 4 | `d19m_runScript.py` | `d1ae2ac5a620d9308b0d50059e944cf4` | the producer — **NEW**, §7.1 |
| 5 | `d19m_grade.py` | `f1f78bf4e78072057dc13e25cf1ffda9` | **THE GRADING PATH** |
| 6 | `d19m_aggregate_memory.py` | `b6c816491107740c297fc99c2ba2b46d` | the aggregate-memory reader the driver executes |
| 7 | `d19m_stall.py` | `2c37822bcf6107fc368b5743701e3018` | the IPOPT reader and stall detector |
| 8 | `d19m_age_guard.py` | `b61de171e111712fe106e5d43e8a0258` | the age guard |
| 9 | `d19m_stop_marker.sh` | `656266a74eaf786fe32e8516b5c58196` | the stop marker |
| 10 | `d19m_decomposeParDict` | `68ecc827562886fb43c3aedb0627b344` | **byte-identical to `d15_decomposeParDict`** (`cmp` exit 0) |

Suite (driven before every launch, not pinned): `d19m_xf_selftest.py` `76732f1675df1e39edd0fa787b935feb`, `d19m_grade_selftest.py` `7b7b29e4fe94a1681301939c22973608`, `d19m_run_arm_selftest.sh` `5c68d243e375724e539289fe865a1f6d`, `d19m_chain_driver_selftest.sh` `273ed9f1fc8bb72c7dcdc3404b39337e`, `d19m_repin.sh` `5777e78c20655605fa4138dba81a1009`.

### 7.1 **THE PRODUCER IS NEW, AND THE D15 HEADER-IDENTITY CLAIM IS NOT AVAILABLE TO THIS ITEM**

D19O's producer was **byte-identical** to D19R's, which is D15's, so D19O could assert `HEADER_MD5_SHARED_WITH_D15` and stand its reproduction claim on bytes. **A multipoint model cannot be that file** — it needs three builders, three mesh subsystems, three `patchV{i}` outputs and an `ExecComp`.

**So `d19m_runScript.py` is a NEW producer with its own md5 and NO inherited reproduction claim, and this document says so rather than implying a continuity that does not exist.** Selftest leg `A7` requires the string `HEADER_MD5_SHARED_WITH_D15` to be **absent** from the instrument.

**What IS carried, and is checkable on bytes:** the **PHYSICS BLOCK** — `U0`, `p0`, `T0`, `nuTilda0`, `A0`, `rho0` and the whole of `daOptions` — is **byte-identical to D19O's**, modulo the single `aoa0` line a multipoint model cannot carry. It is delimited by explicit markers and `d19m_xf.py` asserts its md5 **`c66504acc57bd9ef009599e883d2ef3b`** separately from the file's, **before executing it**. Selftest leg `A4` re-derives that block from **D19O's real file on disk** rather than from a remembered hash.

**So: "the physics is D15's" is a property of bytes; "the model is D15's" is no longer true, and only the first is claimed.**

### 7.2 Toolchain identity

| row | image | digest | `libidwarp.so` md5 |
|---|---|---|---|
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |

Mesh identity pins (md5 of the **decompressed** polyMesh files) re-verified by leg `(r8)` against **D19O's own MESH output**: `points 88f00ff725ef2906212ca1e2b040c09f`, `faces 1bcea5c2f5817d0740a03a83050c3c79`, `owner 549e0a9f01be3ebf412017c1e9811ece`, `neighbour 65fd7ca38d534c760f57ce14bdffc834`, `boundary c92a945e9a1405b988ab418e48ab53c3`.

### 7.3 `D19O-DRIVER-DEF-1` IS REPAIRED HERE, WHERE IT IS FREE

D19O's driver wrote its pre-launch selftest output to **`$HERE` — the git working tree** — leaving four untracked files beside the frozen instruments on every launch. It was not repairable in place because D19O's driver was pinned and the item had had first compute. **This driver writes to `$BASE/selftests`**, where run outputs belong.

**And the repair carries a trap that was caught by reading the guard rather than by running into it:** `mkdir -p "$BASE/selftests"` at the point the selftests run **would create the run root**, and the staging block is guarded by `if [ ! -d "$BASE" ]` — so it would have **silently skipped staging entirely** and every later md5 would have failed on files never copied. The output therefore goes to a `mktemp` directory and is **moved into the run root after staging**. Leg `(c8)` proves `selftests < staging < move < launch` in the byte offsets.

---

## 8. THE LIVE PLANTED-ZERO CONTROLS — NINE READERS, SIX OF WHICH PASS A GATE ON A ZERO

`CLAUDE.md` rule 3, answered **on the run root**, not on a fixture. Every reader is a named function; every control plants into a copy under `grader_controls/`, reads back **through the real reader**, and **REFUSES (exit 2)** if the plant is not recovered. Every control carries a **degeneracy arm**. `n_not_born != 0` refuses.

**`R8_read_alphas` is new in this item** — `G-ALPHA`'s reader, and it is on the zero-hazard list because an empty read gives the gate nothing to compare. Its control plants a **one-degree** change and requires the reader to see it.

**Seven blinding legs (`H1`–`H7`) blind one reader at a time and require a refusal**, plus `H6b` for `R8`. On a full fixture: **9 readers, 9 born, 0 not born, all against `REAL` targets, 6 carrying the zero hazard.**

---

## 9. THE OPTIMISER MAPPING

`PASS` only where IPOPT printed its **own** convergence statement — and then still capped. Otherwise **`GATE REACHED`** iff **≥ 2.0 %** weighted-drag reduction over **≥ 5** major rows, else **`NOT A RESULT`**. Never `PASS`, never described by the size of the improvement.

**Stall condition A** (8 consecutive majors, `alpha_pr < 1e-3`) is armed on the O arms; **condition B is registered `NOT EXERCISED`** — it fires on 0 of the 10 real logs this family has, and is never reported as a passing control.

**The three-`CL` triple travels with every weighted-drag number.** `CL` is unconstrained here because α is the operating point and there is no DV to trim with. **A weighted-drag reduction at unstated lift is not a reportable number.**

---

## 10. COST

| arm | ranks | predicted | cap | wall | memory |
|---|---|---|---|---|---|
| `MESH` | 1 | 0.20 | 5.0 | 120 s | 12g |
| `O-S` / `O-P` | 1 | **8.64** | 40.0 | 2220 s | 12g |
| `XE-S` / `XE-P` | 1 | **2.60** | 12.0 | 540 s | 12g |
| `FE-S` / `FE-P` | 1 | **5.71** | 20.0 | 1020 s | 12g |
| **ITEM** | | **34.10** | **149.0** | | |

`ITEM_CEILING = Σ(caps) = 149.0`, **asserted in code**. Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h reported-by-owner: point **$0.029156**, ceiling **$0.127395**. **GPU 0.** Walls are the C-188 frame (`cap×60/ranks − 180`), parsed against the code by leg `(r2)`.

### 10.1 §18.1 — THE PROGRAM STATEMENT AND THE MATCH

**All three anchors are `[MEASURED]`, on this same A1 case at np = 1, single-point IPOPT with adjoint and colouring on a cold tree:**

| anchor | value | source |
|---|---|---|
| incompressible **multipoint(3)** major | **0.67738** core-min | SO-3 `O-P` 6.950/10, `O-S` 7.917/12 |
| incompressible **single-point** major | **0.39237** core-min | SO-1bR `O-P` 4.700/12, `O-S` 4.717/12 |
| **compressible** single-point major | **0.41854** core-min | **D19O** `O-S` 5.400/13, `O-P` 4.217/10 |

Two derived ratios: **multipoint(3)/single = 1.7263** and **compressible/incompressible on a major = 1.0667** (D19O's own finding, which corrected the 1.6086 *primal* ratio D19O had extrapolated from).

```
0.41854 [MEASURED, compressible single] x 1.7263 [MEASURED, multipoint ratio]
= 0.72255 core-min/major   [EXTRAPOLATED]
x EXPECTED_MAJOR_ROWS 12   [MEASURED: SO-3 multipoint 12 and 10 rows; D19O 13 and 10]
= 8.67 -> REGISTERED 8.64 core-min per O arm
```

> **AN HONESTY NOTE ON A "CORROBORATION" THAT IS NOT ONE.** The alternative route — SO-3's measured multipoint major × D19O's measured compressible-major penalty — gives **0.72255**, agreeing to **0.000 %**. **That agreement is a TAUTOLOGY, not evidence:** `cs × (mp/sp)` and `mp × (cs/sp)` are the same product reassociated. **It is recorded here as arithmetic, not as independent confirmation**, because presenting it as corroboration would be exactly the kind of false comfort this lab's cost rows exist to prevent.

**`XE` = 2.4415 (SO-3's XE mean, 3 points, incompressible) × 1.0667 = 2.60.** **`FE` = 102 primals × 3.3571 s** — D19O's own measured compressible **endpoint** primal (2.350 core-min / 42 primals) — **= 5.71 core-min.**

**`max_iter = 40` is the CAP and is priced into the 40.0 core-min per-arm cap and nowhere else.** SO-3 registered 228.59 and spent 28.900 (0.126×) by pricing at `max_iter`; D19O priced at expected majors and came in at 0.6715. Leg `(c7)` requires the driver's cost table to match `d19m_grade.py:PREDICTED_CORE_MIN` on all seven arms.

### 10.2 `P_COST` band — **[25.0, 85.0] core-min**

Fixed non-`O` arms total **16.82**. Scenarios: 4 majors → 22.58 (**OUT low**); 8 → 28.34; **12 → 34.10 (THE POINT)**; 20 → 45.62; 30 → 60.02; 40 (`max_iter`) → 74.42; both O at cap → 96.82 (**OUT high**). The point sits at **15 %** of the band's width — low, deliberately, because more majors on an objective never optimised is the better-evidenced tail. **Both edges are reachable outcomes of this run.**

---

## 11. THE RULE-2 CONDITION

**The registered run root does not exist; no arm has run; the item id was free.** Checked with readers shown able to return the other answer in the same invocation: `curriculum_D19M` **ABSENT** while `curriculum_D19O` **EXISTS**; `/home/ubuntu/certonomous-runs/*D19M*` **no match** while `*D19O*` matched; `grep -rn 'D19M'` over `cases/ docs/ verification/ scripts/` **zero hits**.

**The name.** `D19O` = D19's **O**ptimisation (single point); `D19M` = D19's **M**ultipoint, on the same subsonic compressible ground. `SO-4` remains Sanaa's reserved 3-D-wing slot; `D20` remains reserved by `curriculum_D19/PREREGISTRATION.md:41` for the **transonic** ground; an `R` suffix would falsely say "re-run of the same program".

---

## 12. PREDICTIONS

| token | what it scores | registered |
|---|---|---|
| `P1_cells_4032` | `G-M2` `PASS` | **HIT** |
| `P2_alpha_gate_PASS` | `G-ALPHA` `PASS` — all three α read back to 1e-12 on both paths | **HIT** |
| `P3_mp_struct_PASS_both_rows` | `G-MP-STRUCT` `PASS` on both rows | **HIT** |
| `P4_both_optimisers_converge` | both rows' `ipopt_printed_convergence` true | **HIT** — three compressible/multipoint IPOPT runs on this case have each printed it |
| `P5_majors_in_band` | both rows' `ipopt_table_rows` ∈ **[8, 24]** | **HIT** |
| `P6_rows_agree_at_the_endpoint` | \|shipped `agg_J` − patched `agg_J`\| ≤ **1.0** percentage point | **HIT** — D19O measured 0.043 % vs 0.053 % on its own optima, and §2's mechanism predicts the same here |
| `P7_endpoint_fd_PASS_both_rows` | `G5_fd` `PASS` on both rows | **HIT** — and this is a **reversal** of D19O's registered P6/P7, made *because* D19O refuted them; §12.1 |
| `P8_trivial_baseline_PASS_both_rows` | `G-TB` `PASS` both rows | **HIT** |
| `P9_shape7_NOT_A_RESULT` | `G-PLAT7` `NOT A RESULT` both rows | **HIT BY CONSTRUCTION — carries no information** |
| `P10_item_GATE_REACHED` | item verdict `GATE REACHED` | **HIT** |
| `P_COST_total_core_min_in_band` | 25.0 ≤ total ≤ 85.0 | **HIT** |

### 12.1 `P7` IS A REVERSAL, AND THE REVERSAL IS THE POINT

D19O registered `P6` (patched endpoint FD would **MISS**) and `P7` (shipped endpoint FD `GATE FAIL`). **Both were wrong**: both rows passed, at 0.053 % and 0.043 %. **This item predicts the opposite of what its predecessor predicted, because its predecessor's measurement refuted the reasoning — and that is what a prediction ledger is for.** If `P7` misses here too, the finding is that the endpoint agreement is *not* general even on this ground, which is a real result about the mechanism rather than about this lane's luck.

**`P9` carries no information** and is registered as such: it scores a gate this document *registers*. It confirms the comparator was not edited and nothing else.

---

## 13. WHAT THIS ITEM WILL NOT ESTABLISH

* **Not that the compressible multipoint gradient is verified.** Its basis is *thinner* than D19O's: `J` has never had an FD table on compressible ground at all.
* **Not a `PASS` on anything.** The ceiling.
* **Not anything about `shape[7]`.** §3.
* **Not that the IDWarp defect is baseline-only.** D19O's finding rests on two optima that were nearly the same point; this item may add a second data point but cannot settle it. **The item that settles it is the deliberately-displaced-design-point successor, which is separately registered and is NOT folded into this one.**
* **Not anything at np ≠ 1**, on a transonic ground, or on a grid triple.
* **Not a trimmed-`CL` result.** `CL` is unconstrained; the triple travels.

---

## 14. NAMED RESIDUALS

* **R1 — NO ARM HAS RUN.** A green suite is a result about the comparator.
* **R2 — THE PRODUCER IS NEW AND CANNOT BE EXECUTED ON THIS HOST, AND THIS RESIDUAL IS LARGER THAN D19O's.** D19O's producer was byte-identical to a file that had already run four times. **This one has never run in any form**, carries **three** `DAFoamBuilder`s where D19O had one, and assembles a weighted objective through an `ExecComp` that no compressible item has ever built. The selftests drive its AST, its physics md5 and its DV declarations; **they do not prove the model builds.** The first `O-S` arm is the first real test.
* **R3 — `d19m_xf.py` mode `O` IS NEW CODE** and its writers are exercised only through fixtures.
* **R4 — THE 12 GiB FOOTPRINT IS `[EXTRAPOLATED]`.** Three `DASolver` instances in one process has never been measured on compressible ground.
* **R5 — THE MULTIPOINT COST RATIO 1.7263 IS MEASURED INCOMPRESSIBLE** and carried onto a compressible major. D19O's own R5 was exactly this shape one level down and **it missed by 1.5×**; this one may too.
* **R6 — `d19m_chain_driver.sh` IS NOT SELF-PINNED.** It holds the pins.
* **R7 — CONDITION B OF THE STALL DETECTOR IS `NOT EXERCISED`** on real bytes.
* **R8 — THE α BRACKET HALF-WIDTH AND THE EQUAL WEIGHTS ARE LANE-CHOSEN.** Only the centre is measured. A different bracket is a different objective, and nothing here says ±2° is the right one.

---

## 15. FREEZE

Gates, thresholds, caps and labels above are closed at first compute. Before then, amendments are legal and must state the condition and how it was checked. **The grading path is fixed at this commit: `d19m_grade.py`, md5 `f1f78bf4e78072057dc13e25cf1ffda9`**, asserted by the driver with `md5sum -c` before staging.

**Not cleared to launch by this document.**

---

## AMENDMENT 1 — 2026-09-01, BEFORE FIRST COMPUTE. **THREE §7 PINS WENT STALE INSIDE THIS DOCUMENT, AND `--verify` COULD NOT SEE IT**

**lines whose number changed above this section: 0.** Appended at the foot; nothing above is edited.

**THE RULE-2 CONDITION.** No compute has happened. The registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint` **DOES NOT EXIST** — re-asserted in the same shell invocation as this amendment, against the same positive control as §11 (D19O's root, which the same reader returns as **EXISTS**). Zero `d19m_` containers have ever existed. The freeze window is open and closes at the first arm.

### A1.1 THE DEFECT — `D19M-PREREG-PIN-1`

**§7's table was authored, and THEN two pinned files were edited.** The `XE` prediction was corrected from **3.10 to 2.60** after the table was written — a better-derived number, and the right correction — which rewrote `d19m_grade.py` (`PREDICTED_CORE_MIN`) and `d19m_chain_driver.sh` (its cost block), and the subsequent `d19m_repin.sh` run rewrote the driver again. **The document went to commit `5a505de945595709dee5f6f8ab3d315145ad1a4e` carrying two hashes that no longer named their files**, and a third (`d19m_repin.sh`, in the suite line) went stale immediately afterward when this amendment's own repair was applied to it.

**THIS IS THE SO-2MR FAILURE, INSIDE A FREEZE**: editing a file rewrites the very bytes every declaration of its md5 pins, so every such declaration is stale the instant the file is saved.

**AND `d19m_repin.sh --verify` REPORTED "every pin matches its file on disk" WHILE IT WAS TRUE.** It was not lying: it read the **DRIVER**, the **LAUNCHER** and the **INSTRUMENT**, and in those three the pins *were* correct — the repin fixpoint had done its job. **What it never read was this document.**

> **THE EXECUTABLE PINS AND THE DOCUMENTED PINS ARE DIFFERENT CLAIMS, AND A CHECK THAT READS ONLY THE FIRST CANNOT SEE THE SECOND GO WRONG.** That is the transferable finding, and it is the same shape as `DAFOAM_CHARTER.md` §18.3's — an md5-agreement control over a subset reads agreement on every pin it holds while something it does not hold is wrong.

**How it was caught:** by re-deriving every §7 hash from disk **after** the commit, as the post-commit verification of the grading path. `git cat-file blob HEAD:…/d19m_grade.py` returned `94b72950…` against a document saying `f1f78bf4…`.

### A1.2 THE REPAIR — THE CHECK NOW READS THE DOCUMENT

`d19m_repin.sh --verify` now parses `PREREGISTRATION.md`'s own pin tables and compares every documented hash against its file, printing `PREREG-DRIFT` per mismatch and **failing**. Driven at this amendment: it reported **all three** stale pins, **including its own file**, which is the leg that matters — a checker blind to itself is the shape this lab keeps paying for.

**NO GATE, THRESHOLD, CAP, BAND, LABEL OR PREDICTION MOVES.** `VERDICT_CEILING = "GATE REACHED"`, `ITEM_CEILING = 149.0`, `PREDICTED_CORE_MIN` Σ = 34.10, bands 5.0/5.0, plateau 10.0, `TB_STEP` 1e-8, `MAX_MAJORS` 40, `EXPECTED_MAJOR_ROWS` 12, `ALPHAS`, `WEIGHTS`, `MP_STRUCT_RTOL` 1e-10, `ALPHA_ABS_TOL` 1e-12, `EXCLUDED_FROM_AGGREGATE`, cpuset 13, np 1 — **all unchanged.** The amendment corrects three RECORDED HASHES and adds one CHECK; it makes more runs refusable and none pass that would previously have failed.

### A1.3 THE CORRECTED PINS

**THE STRUCK VALUES, SPELLED ONCE SO A GREP FOR THEM LANDS HERE:** `d19m_grade.py` was recorded as `f1f78bf4e78072057dc13e25cf1ffda9`; `d19m_chain_driver.sh` as `c4af7e139aa3a90537706ce70138fe41`; `d19m_repin.sh` as `5777e78c20655605fa4138dba81a1009`. **All three are SUPERSEDED and name nothing.**

**THE CORRECT VALUES.** This table is in the same two-column shape as §7's, deliberately, so that `d19m_repin.sh --verify` reads it as a **superseding record** rather than as a second claim — the checker keeps the LAST hash recorded for each file, which is what "carry the value from the amendment" means expressed as code.

| file | md5 |
|---|---|
| `d19m_grade.py` | `94b72950d795c28bfa3a2a7ca17febb5` |
| `d19m_chain_driver.sh` | `4d7ebd5b660d2ea27e6d681d5c3f7e58` |
| `d19m_repin.sh` | `ba8bd537d2ec78370d34fbecc3bf15ab` |

**`d19m_grade.py` `94b72950d795c28bfa3a2a7ca17febb5` IS THE GRADING PATH.** §15's FREEZE sentence is superseded as to that value only; everything else it says stands.

**Every other §7 row was re-derived from disk at this amendment and is UNCHANGED** — `d19m_run_arm.sh`, `d19m_xf.py`, `d19m_runScript.py`, `d19m_aggregate_memory.py`, `d19m_stall.py`, `d19m_age_guard.py`, `d19m_stop_marker.sh`, `d19m_decomposeParDict`, and the four selftests.

**The driver's own executable pin was never wrong.** `d19m_chain_driver.sh:MD5_GRADER` has carried `94b72950…` since the repin fixpoint, so **no executable path could ever have reached a struck value** — the defect was confined to this document. That is smaller than it looks in one direction and exactly as large as it looks in the other: **a reader taking the pin from §7 would have taken a hash that names nothing.**

**A SECOND DEFECT, IN THE CHECK ITSELF, FOUND BY DRIVING IT AND FIXED BEFORE IT COULD MISLEAD.** The first version of the new prereg check paired a filename with any hash on the same LINE, and §7.1 names `d19m_xf.py` and the **physics-block** md5 `c66504acc57bd9ef009599e883d2ef3b` in one sentence — **two different claims about two different byte ranges.** It reported a false drift. The check now pairs **by adjacency**: the hash must follow the filename with nothing between but table and emphasis markup. **A checker that cannot tell two claims apart is worse than no checker, because it trains its reader to ignore it.**

### A1.4 SUPERSEDED-HASH INDEX

Rule 6 forbids editing above an amendment, so the struck values still stand in §7 and §15. **Swept, not assumed — FOUR occurrences above this section:** §7 row 1 (`c4af7e13…`), §7 row 5 (`f1f78bf4…`), §7's suite line (`5777e78c…`), and §15's FREEZE sentence (`f1f78bf4…`). **A reader of §7 or §15 must carry the values from §A1.3, not from there.** The occurrences inside this amendment are correct in context — they are the landing point for that grep.

### A1.5 STATUS

**Still not cleared to launch.** This amendment corrects three recorded hashes and adds one check; it authorises nothing. The run root is absent and the freeze window closes at the first arm.
