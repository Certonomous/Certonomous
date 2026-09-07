FROZEN 2026-09-07 by the dafoam-supervisor (this commit is the freeze; §8) — grading path hash-locked (mpa1_INSTRUMENT_MD5_TABLE.md; grader `9b9cb934…`, runScript `bb3ba3a6…`). SUBMISSIONS PARKED.

# CURRICULUM MP-A1 — NACA0012 ALPHA-MULTIPOINT DRAG-MIN **AT FIXED LIFT**, INCOMPRESSIBLE, BOTH TOOLCHAIN ROWS, np = 1. PRE-REGISTRATION (DRAFT)

**Item id:** `CURRICULUM-MP-A1`
**Run root (registered, and to be ABSENT at the freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation`
**Case directory (this document's own home):** `cases/dafoam/ladder-a/A1/curriculum_MP_A1/`
**Mandate:** Sanaa 2026-09-07 ~03:30Z — *"yes and for the dafoam: we need to have the multipoint optimizations as well"* (`etc/sessions/2026-09-07T0330Z_sanaa_dafoam_multipoint_mandatory.md`). MP-A1 is the **clean incompressible multipoint drag-min-at-fixed-lift** milestone named in that memo's plan ("MP-A1 = SO-3 with per-point CL constraints").
**Predecessor of record:** `CURRICULUM-SO3` (`cases/dafoam/ladder-a/A1/curriculum_SO3/`), which landed **PASS** as an incompressible multipoint optimisation but **with CL UNCONSTRAINED and the lift collapsing negative at operating point 0**. MP-A1 exists to remove exactly that caveat.

**Status: FROZEN 2026-09-07** (this commit; §8). Every gate, threshold, cap and label below is bound as of this commit (rule 2); the grading path is hash-locked (§8). No arm of this item has run; the costed core-min figure (estimate **58.63**, ceiling **183.5**) is brought to the chief AS IT FREEZES, before compute, per the mandate. **Compute is NOT launched by this freeze** — the `NOT_FROZEN` sentinel is retained deliberately as the launch-block (§8).

---

## §0. WHAT MP-A1 CHANGES vs SO-3, AND WHY — GROUNDED AT SOURCE

### 0.1 The SO-3 caveat, read from SO-3's own record

SO-3 minimised the weighted composite `J = Σᵢ wᵢ·CDᵢ(αᵢ)` over one shared `shape` vector at three fixed operating points, and landed **PASS** on both rows (`cases/dafoam/ladder-a/A1/curriculum_SO3/RESULTS.md`). **But CL was UNCONSTRAINED by registration** (SO-3 pre-registration line 6, `so3_runScript.py` docstring (C) and `configure()` lines 453-459: *"The per-scenario CL is NOT constrained here"*), and the lift collapsed. SO-3 RESULTS.md §2.1, measured, read on disk:

| point | α, deg | CL baseline (SO-3 measured) | CL final SHIPPED | CL final PATCHED |
|---|---|---|---|---|
| point0 | 3.13918623195176 | **0.31189588769251864** | **−0.057373254725203056** | **−0.05675565457564216** |
| point1 | 5.13918623195176 | **0.49876526085592926** | 0.15240511285598504 | 0.15320276361213012 |
| point2 | 7.13918623195176 | **0.6639763551107052** | 0.36011850787767585 | 0.3611940124520788 |

**The lift went negative at point0 on both rows.** SO-3's ~16.16 % weighted-drag reduction was, in its own words, *"bought by driving CL … NEGATIVE at point 0"* — a PASS on the registered gate but **not a physically-held drag-min-at-fixed-lift.** SO-3's own `forbidden_readings` block forbids quoting any drag number without the CL pair beside it.

### 0.2 The one change MP-A1 makes

**MP-A1 = SO-3 with a per-operating-point CL EQUALITY constraint added, and nothing else changed.** At each point the constraint holds `CLᵢ = CL_target_i` while the shared `shape` vector minimises the same weighted drag `J`. The targets are the **SO-3-measured undeformed baseline CL** listed above (§1.4). Consequence, registered so it cannot be discovered in the figure: with each CL pinned at its positive baseline value, the optimiser **cannot** shed lift to buy drag, so the collapse SO-3 documented is structurally excluded — and gate (b) (§2) measures that it is.

### 0.3 Why the change is ADMISSIBLE on SO-3's own inheritance — no new unverified gradient

The whole reason SO-3's optimisation was admissible is that `CURRICULUM-SO3aR2` FD-verified the multipoint objective's gradient — **both `dCDᵢ/dx` AND `dCLᵢ/dx`** — at **fixed α, np = 1**, on this exact assembly (`SO3aR2_grade_20260831T230221Z.json`; SO-3 used `dCLᵢ/dx` for its own G5C gate, which PASSed on both rows). MP-A1's new CL equality constraints are driven by **`dCLᵢ/dx` at fixed α** — the **same gradient that was already FD-verified**. **No `patchV`/α design variable is added**, so no `d/dα` gradient (which SO-3aR2 never verified) enters the optimiser. MP-A1 is therefore admissible on **exactly** SO-3's inheritance chain (`DAFOAM_CHARTER.md` §2: an unverified gradient may not enter an optimisation). The endpoint FD arms re-verify it at MP-A1's own final design point, as §9 requires.

### 0.4 What MP-A1 deliberately does NOT do — and why it is a THIRD formulation, flagged for the supervisor

`SO3_MULTIPOINT_SCOPE_MEMO.md` §2, quoted in `so3_runScript.py` docstring (C), names two formulations: (i) each point carries its own `aoa` DV **and** a CL equality (N constraints, N extra DVs), or (ii) fixed α with CL floating. **MP-A1 is a third: fixed α, CL held by EQUALITY constraint on the shared `shape` only.** This is the honest "drag-min-at-fixed-lift" that stays inside SO-3aR2's verified-gradient basis (§0.3). It is **not** the classic aoa-trimmed multipoint (formulation (i)); adding per-point `aoa` DVs is a separate rung, because it would introduce `d/dα` gradients SO-3aR2 never verified. **This is an open registration decision — see §6.** The feasibility of holding three distinct CL targets with one shared 8-component `shape` at three fixed α is discussed in §5.2; `shape = 0` is a feasible starting point by construction (§1.4), so the problem is well-posed.

---

## §1. THE ITEM AS REGISTERED — CARRIED FROM SO-3, WITH THE CL CONSTRAINT ADDED

All values in §1.1–§1.7 are **quoted from SO-3's frozen `so3_runScript.py`** (verified on disk at this draft) and are reused UNCHANGED except the single addition in §1.5.

### 1.1 Operating points and weights
Three operating points differing ONLY in angle of attack (`so3_runScript.py:242`), equal weights (`:248`):

| point | scenario | α, degrees | weight |
|---|---|---|---|
| point0 | `point0` | 3.13918623195176 | 1/3 |
| point1 | `point1` | 5.13918623195176 | 1/3 |
| point2 | `point2` | 7.13918623195176 | 1/3 |

α is the **operating point**, entering through `patchV` (a boundary condition), never through the mesh. Written out verbatim, compared to 1e-12 by G-ALPHA.

### 1.2 Objective
`J = Σᵢ wᵢ·CDᵢ`, assembled by an `om.ExecComp` built from `WEIGHTS` (`so3_runScript.py:348, 393`), unchanged. Graded DV subset for all FD gates: **`shape` indices 0, 3, 6, 7** (SO-1a/SO-2a/SO-3's own).

### 1.3 Design variables, geometry, mesh
- **DVs: `shape` ONLY**, 8 components, `lower=-1.0, upper=1.0, scaler=10.0` (`so3_runScript.py:448`). `patchV`/α is **not** a design variable (§0.4).
- **One shared `OM_DVGEOCOMP`** (`FFD/wingFFD.xyz`, 5×2×2 FFD → 8 shape functions), one `shape`→surface map, feeding all three scenarios (`so3_runScript.py:377, 387-389, 422`). This is what makes G-MP-STRUCT an identity.
- **One `DASolver`/`DAFoamBuilder` per operating point, each in its own `run_directory`** `mp0/mp1/mp2` (`so3_runScript.py:281, 364`) — the SO-3aR collision cure.
- **Mesh: NACA0012, 4032 cells** (G-M2 asserts exactly 4032). `preProcessing.sh && checkMesh` as the MESH arm.
- Geometric constraints, unchanged (`so3_runScript.py:457-459`): `thickcon ∈ [0.5, 3.0]`, `volcon ≥ 1.0`, `rcon ≥ 0.8`.
- Flow: `U0 = 10.0`, `nuTilda0 = 4.5e-5`, `useWallFunction: True`, `DASimpleFoam` (incompressible), `primalMinResTol = 1.0e-8`, `adjEqnOption gmresRelTol 1.0e-6, pcFillLevel 1, jacMatReOrdering rcm` (`so3_runScript.py:284-329`).

### 1.4 THE PER-POINT CL TARGETS — REGISTERED EXPLICITLY, BEFORE ANY RUN
Each target is the **SO-3-measured undeformed baseline CL** at that operating point (SO-3 RESULTS.md §2.1, read on disk):

| point | α, deg | **CL_target (registered)** |
|---|---|---|
| point0 | 3.13918623195176 | **0.31189588769251864** |
| point1 | 5.13918623195176 | **0.49876526085592926** |
| point2 | 7.13918623195176 | **0.6639763551107052** |

**Why these exact values.** Setting `CL_target_i` = the baseline CL at `shape = 0` makes the undeformed shape a **feasible** starting point (all three equality constraints satisfied exactly at `shape = 0`), so MP-A1 is a well-posed drag-min from a feasible seed and any drag reduction it finds is **genuinely lift-neutral** relative to the SO-3 baseline. `G-CLTGT` (§2) reads the targets back from the artefact and refuses (GATE FAIL) if they differ from these registered values by more than 1e-12. All three targets are **positive**, so a held constraint structurally excludes the SO-3 collapse.

### 1.5 THE ONE CODE CHANGE — the CL equality constraints
In `mpa1_runScript.py` (derived from `so3_runScript.py`), `configure()`'s constraint block (SO-3 `:453-459`) gains three constraints and nothing else changes:
```
CL_TARGET = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]  # §1.4
for i, sc in enumerate(SCENARIOS):
    self.add_constraint("%s.aero_post.CL" % sc, equals=CL_TARGET[i], scaler=1.0)
```
**Type: EQUALITY** (`equals=`), the honest "fixed lift" statement — pending supervisor confirmation of equality vs one-sided inequality (§6). `CL` constraint `scaler = 1.0`. The objective (`obj.J`, scaler 1.0) and the three geometric constraints are unchanged.

### 1.6 IPOPT settings — carried from SO-3
`so3_runScript.py:188-191, 539-548`, unchanged: **optimizer IPOPT**, `tol = 1.0e-5`, `constr_viol_tol = 1.0e-5`, `max_iter = MAX_MAJORS = 50` (a **budget, not a settle criterion** — reaching it is GATE REACHED, never PASS), `nlp_scaling_method = "none"`, `mu_strategy = "adaptive"`, `limited_memory_max_history = 10`, `print_level = 5` (so the iteration table is present for the stall parser), `output_file = opt_IPOPT.txt`. IPOPT's own convergence statement (`Optimal Solution Found.` / `Solved To Acceptable Level.`) is the only thing that can earn PASS (§2 gate a).

### 1.7 np and decomposition
**np = 1 on every arm**, a CONDITION ON THE INHERITANCE, not a setting (`DAFOAM_CHARTER.md` §5; SO-3aR2's FD table was measured at np = 1; A4 measured a 16,600× spread between two decompositions of one mesh). Enforced by an `MPI.COMM_WORLD.Abort(66)` in the runScript (`so3_runScript.py:473-481`) and by the launcher's `ranks_of`. Single-core cpuset (§3.3). `decomposeParDict` present as an OpenFOAM dictionary but np = 1 uses no decomposition; disclosed per `DAFOAM_CHARTER.md` §5.

### 1.8 The arm program — SEVEN arms (`N_DECLARED = 7`), carried from SO-3
| arm | row | kind | terminal statement |
|---|---|---|---|
| `MESH` | SHIPPED | `preProcessing.sh && checkMesh` | — |
| `O-S` | SHIPPED | IPOPT multipoint CL-constrained optimisation | `MPA1_O_WRITTEN` |
| `XE-S` | SHIPPED | adjoint gradient at the SHIPPED optimum | `MPA1_X_WRITTEN` |
| `FE-S` | SHIPPED | finite-difference table at the SHIPPED optimum | `MPA1_F_WRITTEN` |
| `O-P` | PATCHED | IPOPT multipoint CL-constrained optimisation | `MPA1_O_WRITTEN` |
| `XE-P` | PATCHED | adjoint gradient at the PATCHED optimum | `MPA1_X_WRITTEN` |
| `FE-P` | PATCHED | finite-difference table at the PATCHED optimum | `MPA1_F_WRITTEN` |

Both rows always run (`DAFOAM_CHARTER.md` §6); a worse or failed SHIPPED optimisation IS the result.

---

## §2. GATES, THRESHOLDS AND LABELS — EACH POST-HOC, FROM THE SIX-TOKEN VOCABULARY

The vocabulary is the six tokens and nothing else (`CLAUDE.md` rule 1; `DAFOAM_CHARTER.md` §8): `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`.

| gate | what it reads | threshold | verdict on miss |
|---|---|---|---|
| `G1_completion` | per arm: rc = 0, terminal statement present, no fatal token, **age guard** (every field at end state newer than `0/U`, by existence) | all of it | `GATE FAIL` |
| `G-M2_mesh_identity` | mesh cell count | **4032** exactly | `GATE FAIL` |
| `G-ALPHA_operating_points` | the three α read back through the scenario groups | equal to §1.1 to **1e-12** | `GATE FAIL` |
| `G-CLTGT_targets_registered` | the three CL equality targets read back from the artefact | equal to §1.4 to **1e-12** | `GATE FAIL` |
| **(a) `G-OPT9_convergence`** (per row) | §9 mapping — see below | IPOPT printed its own convergence statement vs its own tol (1e-5) | see below |
| **(b) `G-CLHOLD_cl_satisfaction`** (per point, per row) | each `CLᵢ,final` at the final design | **\|CLᵢ,final − CL_target_i\| ≤ TOL_CL_ABS = 1.0e-3** AND **CLᵢ,final > 0** at all three points | `GATE FAIL` if any point out of band or ≤ 0 |
| **(c) `G-DRAG_reduction`** (per row) | weighted `J` baseline vs final, WITH the CL triple always beside it | final `J` **strictly < baseline `J`** (the constrained optimiser improved on the feasible `shape=0` seed) | `GATE FAIL` if final `J ≥ baseline J` |
| **(d) `G5J_objective`** (per row) | aggregate + per-pair vector-relative FD error on `J` at the **final design point**, plateau proved per pair | **band ≤ 5.0 %** per pair AND aggregate, **≥ 3 graded pairs**, **0 sign flips**, plateau tol **10.0 %** | `GATE FAIL`; < 3 pairs → `NOT A RESULT` |
| `G5C_lift_per_scenario` (per row) | FD-vs-adjoint on the three `CL` (now the CONSTRAINT quantities the optimiser used) at the final design point | **band ≤ 5.0 %** per pair, **0 sign flips** | `GATE FAIL` |
| `G-TB_trivial_baseline` (per row) | the same FD probe at a deliberately wrong step **h = 1e-8** | PASS iff **≤ 1 of 4** components passes band there | ≥ 2 passing → that row's `G5J`/`G5C` **WITHDRAWN to `NOT A RESULT`** |
| `G-MP-STRUCT` (per row) | `∂J/∂x == Σᵢ wᵢ ∂CDᵢ/∂x` from the artefact's own components | relative **1e-10** | `GATE FAIL` |
| `G-NOOPT-ENDPOINT` | no optimiser ran in `XE-*`/`FE-*` | zero optimiser evidence | `GATE FAIL` |
| `G-DESIGNPOINT` | endpoint arms evaluated **at the optimum** (`mpa1_xopt.json`) | exact | `GATE FAIL` |
| `G9_toolchain` | image digest AND `libidwarp.so` md5 from inside the container | exact match to SO-3's §7 digests | `GATE FAIL` |
| `G10_caps` | per-arm core-min vs cap, item total vs ceiling | §4 | `GATE FAIL` |
| `G12_placement` | cpuset equals the registered value | exact | `GATE FAIL` |
| `G-STAGES_declared_vs_executed` | DECLARED = 7 against EXECUTED = n | short > 0 is a gate input | `NOT A RESULT` on short |
| `G-PROV` | the travelling SO-3aR2/SO-1a `GATE FAIL` chain (§2a) | all links present, item + SHIPPED = `GATE FAIL` | **REFUSAL, exit 2** |

**No GCI / Roache triple.** MP-A1 is a single-grid optimisation; `CLAUDE.md` rule 5 has no row to act on, and this document says so rather than leaving it to be inferred.

### 2.a `G-OPT9` — the §9 mapping, per row (gate a)
`DAFOAM_CHARTER.md` §9, verbatim on the point: an optimisation is graded **PASS only if the optimiser itself printed a convergence statement against its own tolerance.** Per row:
* IPOPT printed `Optimal Solution Found.` / `Solved To Acceptable Level.` (its own statement vs `tol = 1e-5`) → eligible for **`PASS`**.
* Stopped by `max_iter = 50`, a wall clock, a budget, or the registered stall abort → **`GATE REACHED`** where the registered intermediate threshold was met, **`NOT A RESULT`** otherwise.
* **Never `PASS`, and never graded by the size of the improvement.** A row whose optimiser is `NOT A RESULT` cannot be rescued by any other gate. The endpoint FD can only make things worse, never better — an endpoint `PASS` NEVER upgrades a `GATE REACHED` optimiser to `PASS`.

**The registered intermediate threshold (for the GATE REACHED path only): ≥ 1.0 % weighted-drag reduction at HELD CL against the run's own baseline, over ≥ 5 majors.** A run of fewer than 5 majors has not searched. The floor is 1.0 % (not SO-3's 5.0 %) because a CL-constrained drag-min reduces less than the unconstrained SO-3 — see §5.2; this floor gates only the intermediate `GATE REACHED` label, never a PASS. Stall abort carried from SO-3 §9.2 (Condition A: 8 consecutive majors with `alpha_pr < 1e-3`; Condition B registered NOT EXERCISED).

### 2.b `G-DRAG` and the reported comparison (gate c)
`G-DRAG` gates only that the constrained optimiser improved on its feasible seed (final `J < baseline J`). Beside it, **REPORTED, never gated for PASS**: the weighted-drag reduction %, the full CL triple at baseline and final (so no drag number is ever quoted alone), and the **comparison to SO-3's unconstrained −16.16 %** — the cost of holding lift. `so3`-style `forbidden_readings` carried: no drag number without its CL triple; no "converged" of a run with no printed statement; no upgrade of GATE REACHED to PASS via the endpoint FD.

### 2.c The trivial baseline (gate d) — `DAFOAM_CHARTER.md` §4 / `VERIFICATION_CHARTER.md` §2c
The registered trivial baseline is the **same probe at h = 1e-8**, five orders below the registered middle step, where the FD numerator is at or below primal repeatability (SO-3 measured `eta_F ≈ 1.75e-08`) and the estimate is noise. It **must** fail band; a probe that errored counts as failing it. `G-TB` PASS iff ≤ 1 of 4 components passes band there; ≥ 2 → the graded FD gate is WITHDRAWN to `NOT A RESULT`. Registered steps for `shape`: **1.0e-2, 1.0e-3, 1.0e-4**; plateau tolerance 10.0 % proved per pair; the graded step per pair is the one that plateaus (the SO-3 rule).

### 2.d G-PROV — the travelling `GATE FAIL`
MP-A1's admitting gradient basis is `CURRICULUM-SO3aR2` (DIRECT — it FD-verified `dCDᵢ/dx` and `dCLᵢ/dx` at np = 1), carrying `CURRICULUM-SO1a` (INHERITED). SO-3aR2's item and SHIPPED verdicts are both `GATE FAIL` (`G5J` aggregate 31.5 % SHIPPED; the PATCHED 2.68 % sits INSIDE the 2.5–5 % harness-sound floor). That `GATE FAIL` **travels with every claim MP-A1 makes**: on the SHIPPED toolchain the multipoint gradient missed the 5 % band by > 6× on this very case. The only sentence MP-A1 can license about drag is *"on the patched toolchain `dafoam-idwarp-rot:v1`, …"*. (Note: `CURRICULUM-SO3` itself is PASS and is the immediate predecessor, but MP-A1's gradient-verification basis is SO-3aR2, so the travelling chain is unchanged from SO-3's.)

### 2.e Item verdict composition (registered before the run)
1. `G-STAGES = NOT A RESULT`, or any row verdict `NOT A RESULT` → **`NOT A RESULT`**
2. `G-STAGES = BLOCKED` → **`BLOCKED`**
3. any row's optimiser verdict `NOT A RESULT` → **`NOT A RESULT`**
4. `GATE FAIL` in any row verdict or in `{G-M2, G-ALPHA, G-CLTGT, G-CLHOLD, G-DRAG, G-NOOPT, G-DESIGNPOINT, G9, G10, G12}` → **`GATE FAIL`**
5. any row verdict `NOT_MEASURED` → **`NOT A RESULT`**
6. `GATE REACHED` in any row or optimiser verdict → **`GATE REACHED`**
7. otherwise → **`PASS`**

---

## §3. CONTROLS, COMPLETION, DISCLOSURE, MEMORY

### 3.1 Planted-zero control (`CLAUDE.md` rule 3) — a PRECONDITION of the gates
Every gate that can pass on a small or zero number is shown, at grade time, on the real artefacts, **flipping to `GATE FAIL`** under a plant read back from disk through the same reader. The population: **`G5J`, `G5C`, `G-MP-STRUCT`, and — new for MP-A1 — `G-CLHOLD`** (the CL-satisfaction reader is perturbed and must flip: a reader that cannot see a non-zero CL deviation is not evidence the constraint held). Form registered at the freeze: `plantᵢ = PLANT_K × (band/100) × |d_ref_i|`, `PLANT_K = 3.0` → a planted relative error of 15 % against a 5 % band by construction, at any quantity scale. **The plant never touches the graded artefact** — it is written to a separate copy under `grader_controls/`, and the verdict is composed from the unplanted bytes alone. Proved sufficient by being driven insufficient at `PLANT_K_INSUFF = 0.2`. Every reader is entered in a birth register (born = shown able to see a non-zero through the real code path) before it grades.

### 3.2 Strict completion + age guard (`CLAUDE.md` rule 4)
Per arm: `rc = 0`; terminal statement present (§1.8); last time == endTime for solver arms; **every field at the end state NEWER than the case's own `0/U`** (the age-guard datum, resolved BY EXISTENCE — `0.orig/U` for MESH, `0/U` for solver arms — never by name). The guard **refuses a run root that is not absent** (cold-start requirement): the run root is free now and must still be free when the first arm launches, or the age-guard datum is older than the run that produced the answer.

### 3.3 Decomposition disclosure (`DAFOAM_CHARTER.md` §5) and CPU placement
**np = 1 on every arm.** Registered **cpuset (DRAFT): `8`** — one core (np = 1), NOT core 0. SO-3 held `14`; MP-A1 must be disjoint from every LIVE registered sibling at freeze. **⚠ Supervisor confirms cpuset disjointness against live siblings at check-1** (this draft's sweep of registered sibling `.sh` shows sets on {0,1,2,3,4,11,12,14,15}; `8` is disjoint from all of them, but occupancy must be re-read at freeze). `mpirun` binds rank 0 to the first host core under `--cpus`; pin and MEASURE placement rather than infer it from the flag. `G12` compares the launcher's value against the grader's registered constant.

### 3.4 Memory prediction (`DAFOAM_CHARTER.md` §7), stated before launch
Same three-`DASolver`-in-one-process structure as SO-3. D13 measured peak RSS **1.70 GiB** for this 4032-cell case at np = 1; three instances plus shared mesh/FFD/IDWarp is bounded crudely above by `3 × 1.70 + shared ≈ 5.1 GiB` **[EXTRAPOLATED — not a measurement]**. MP-A1 adds three CL constraint adjoints (§4.2), a small state/seed increment, not a new mesh. **Registered per-arm memory cap: 12 GiB** (>2× headroom over the bound); **the item's own first solver arm MEASURES it.** Aggregate ceiling 30.6 GiB, poll 30 s, in the waiting form; at the bound the chain stops and names the series file (a block DISCARDS the arm's remaining budget).

---

## §4. COST — CORE-MINUTES, PER LEG, GROUNDED IN SO-3'S MEASURED PER-ARM COST

**Unit: core-minutes** (wall s × ranks ÷ 60), not wall time and not dollars (`CLAUDE.md` rule 12). Caps are CEILINGS; predictions are ESTIMATES; the rule-12 ratio is taken against the PREDICTION, never the cap.

### 4.1 The O-arm multiplier `M` — DERIVED, and named as the calibration quantity
SO-3 MEASURED its O arms (SO-3 RESULTS.md §1): `O-S` **7.917 core-min in 12 majors** (0.660 core-min/major), `O-P` **6.950 core-min in 10 majors** (0.695 core-min/major). MP-A1 differs by adding three CL equality constraints, which does more work in two ways:
```
M = m_iter × m_adj = 2.0 × 1.5 = 3.0     [DERIVED — the quantity the completion report calibrates]
  m_iter ≈ 2.0   [DERIVED] equality-constrained IPOPT does more majors than the unconstrained
                 SO-3 (10-12); expected ~24 majors.  (Lab constrained precedents span D1/armO 12
                 majors to A2 47 majors; 2.0× is a mid, conservative-for-estimate choice.)
  m_adj ≈ 1.5    [DERIVED] SO-3's driver needed 3 CD adjoints/major for dJ/dx; MP-A1 adds 3 CL
                 constraint adjoints/major -> ~6 flow adjoints/major, ~1.5× per-major cost if an
                 adjoint costs ~ a primal.
```
**`M = 3.0` is DERIVED, not measured.** At completion the report calibrates it: measured actual majors and actual per-major cost, ratio actual/predicted, gap attributed (`docs/COST_CALIBRATION.md`). The five non-O arms are carried at SO-3's MEASURED costs — they already computed `dCLᵢ/dx` (for SO-3's G5C/G-MP-STRUCT), so MP-A1's CL constraints add no new evaluations there.

### 4.2 The per-leg cost table
Cap = the family adopted MAX form `max(3.0×est, 1.25×(4/3)×est)`; since `1.25×(4/3) = 1.6667 < 3.0`, the cap = **3.0×est** for every arm (MESH floored — see note).

| arm | ranks | **est core-min** | basis | **cap core-min** |
|---|---|---|---|---|
| `MESH` | 1 | 0.17 | MEASURED — SO-3 MESH 0.167 | **5.0** (floor; 3.0×0.17 = 0.51 is below the C-188 cap-frame margin, so SO-3's MESH floor is carried) |
| `O-S` | 1 | 23.75 | DERIVED — SO-3 `O-S` 7.917 × M=3.0 | **72.0** |
| `XE-S` | 1 | 2.35 | MEASURED — SO-3 `XE-S` | **7.5** |
| `FE-S` | 1 | 4.45 | MEASURED — SO-3 `FE-S` | **14.0** |
| `O-P` | 1 | 20.85 | DERIVED — SO-3 `O-P` 6.950 × M=3.0 | **63.0** |
| `XE-P` | 1 | 2.53 | MEASURED — SO-3 `XE-P` | **8.0** |
| `FE-P` | 1 | 4.53 | MEASURED — SO-3 `FE-P` | **14.0** |
| **item ESTIMATE** | | **58.63** | | |
| **ITEM CEILING = Σ(caps)** | | | asserted in code | **183.5** |

**Item point estimate 58.63 core-min; item ceiling (Σ caps) 183.5 core-min (≈ 3.1× the estimate).** An overrun STOPS the run and does not get a new budget; the launcher reports at the per-arm cap and hard-stops at the ceiling.

### 4.3 Dollars — DERIVED, NOT MEASURED
At **c7a.4xlarge $0.0513/core-h** = $0.000855/core-min, **reported-by-owner** (the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5):
* estimate: 58.63 × $0.000855 = **$0.0501**
* ceiling: 183.5 × $0.000855 = **$0.1569**

**Both are far under the $25 pre-authorisation** (`CLAUDE.md` rule 12) — confirmed. The item is still costed here because a blanket is not a per-item reading (rule 9). GPU: 0 GPU-h.

### 4.4 Calibration at completion is owed (`CLAUDE.md` rule 12)
At completion — every arm graded, verdict composed — the predicted-vs-actual comparison lands as a row in `docs/COST_CALIBRATION.md` (its append rules, rule-10 private index). The report is incomplete without it. The DERIVED multiplier `M = 3.0` (and its `m_iter`, `m_adj` factors) is the named quantity to calibrate: actual majors, actual per-major cost, ratio, attribution. Any waste is named separately and NEVER folded into the ratio (`COMPUTE_BUDGET_CHARTER.md` §6).

---

## §5. WHAT MP-A1 MAY NOT CONCLUDE

* **It may NOT conclude "DAFoam reduces lift-neutral drag by X"** as an absolute statement. The admitting gradient is `GATE FAIL` on the shipped toolchain and the provenance chain travels (§2d). The only licensed sentence is *"on the patched toolchain `dafoam-idwarp-rot:v1`, …"*.
* **It may NOT conclude a sub-percent verification.** Both endpoint FD aggregates are expected to sit at/near the 2.5–5 % harness-sound floor (`VERIFICATION_CHARTER.md` §7 step 4); a number below that is a claim about the harness, reported and never gated as a tighter verification.
* **It may NOT conclude anything at np ≠ 1** (the inheritance condition; A4's 16,600× decomposition spread).
* **It may NOT conclude a grid-converged optimum.** No grid triple, no GCI, no Roache row (`CLAUDE.md` rule 5).
* **It may NOT conclude the IDWarp defect is absent** from any component; a 0.000 % divergence is reported with its number, never as absence.
* **It may NOT conclude a transonic / compressible result.** MP-A1 is incompressible `DASimpleFoam` only; the compressible/transonic multipoint is D6R2 (gated behind D6RF5 → SO3DR Stage-2).
* **It may NOT conclude an aoa-TRIMMED result.** MP-A1 holds CL by an EQUALITY constraint on the shared `shape` at fixed α — NOT by a per-point `aoa` trim DV. The classic aoa-trimmed multipoint (scope-memo formulation (i)) is a separate rung, because it introduces `d/dα` gradients SO-3aR2 never verified (§0.4).
* **It may NOT re-establish anything SO-3aR2 or SO-3 already graded**; it adds the fixed-lift constraint and nothing else.

### 5.2 A registered risk the supervisor must weigh at check-1
Holding **three distinct** CL targets with **one shared 8-component `shape`** at three fixed α is a constrained problem with 3 equality constraints and 5 remaining DOF. `shape = 0` is feasible by construction (§1.4), so the problem is well-posed and the seed is feasible; but the achievable drag reduction at held lift may be **small** (this is why the §2a intermediate threshold is 1.0 %, not 5.0 %), and IPOPT may reach `max_iter = 50` while satisfying the constraints — a legitimate **GATE REACHED**, not a failure. If the constrained optimum cannot be reached within the 5-DOF space, gate (b) still measures whether lift was held; a `GATE REACHED` with CL held at all three points and no negative lift is itself the demonstration that the SO-3 collapse is removable. The registered outcome expectation is **PASS the target, GATE REACHED admissible, GATE FAIL fully admissible.**

---

## §6. OPEN REGISTRATION DECISIONS FOR THE SUPERVISOR (check-1, before freeze)

This is a DRAFT. The following choices are made by this lane as defaults and are flagged for the dafoam-supervisor's ruling before the freeze commit:

1. **CL constraint TYPE** — registered as **EQUALITY** at the baseline CL (§1.5), the honest "fixed lift". Alternative: a one-sided inequality `CLᵢ ≥ CL_target_i` (drag-min at no-less-than-baseline lift). Supervisor confirms.
2. **DV set** — registered as **`shape` only, fixed α** (no per-point `aoa` DV), which keeps the gradient basis = SO-3aR2's verified `dCLᵢ/dx` at fixed α (§0.3, §0.4). Adding `aoa` DVs = a separate rung. Supervisor confirms this is MP-A1's scope.
3. **CPUSET** — registered `8` (DRAFT); supervisor confirms disjointness against live siblings at freeze (§3.3).
4. **`TOL_CL_ABS`** — registered `1.0e-3` absolute per point for gate (b), 100× IPOPT's own `constr_viol_tol = 1e-5`. Supervisor confirms.
5. **`G-DRAG` floor** — registered `final J < baseline J`; the §2a intermediate threshold 1.0 % over ≥ 5 majors. Supervisor confirms the thresholds.
6. **O-arm multiplier `M = 3.0`** (`m_iter = 2.0 × m_adj = 1.5`), DERIVED — supervisor confirms the basis and the cap (§4).

---

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE. SUBMISSIONS ARE PARKED**, and sending is Sanaa's decision alone (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). This document is a DRAFT and is **NOT FROZEN**; the freeze is NOT taken.

---

## §7. SUPERVISOR RULINGS ON THE §6 OPEN DECISIONS + CHECK-3 — dafoam-supervisor, 2026-09-07T~0400Z (draft still NOT FROZEN)

**Check-3 (big-claim verification), the load-bearing admissibility claim.** MP-A1's whole legitimacy
rests on §0.3: no new unverified gradient enters because the CL-equality constraints are driven by
`dCLᵢ/dx` at fixed α, already FD-verified by SO-3aR2, and no `aoa`/`d/dα` DV is added. I verify this is
not merely asserted but **gated**: `G5C` (§2, per row) re-runs FD-vs-adjoint on the three `CL`
constraint quantities at MP-A1's OWN final design point (charter §9's mandatory final-point FD), and
`G-PROV` travels the SO-3aR2 `GATE FAIL` chain into every claim. The admissibility is therefore
falsifiable at MP-A1's endpoint, not inherited on faith. **Claim upheld, and correctly gated.** The
authoring lane must ASSERT in `mpa1_grade.py` that `G5C` covers all three `dCLᵢ/dx` pairs (not only
`dCDᵢ/dx`), since the constraints — not just the objective — now depend on the CL gradient.

**§6 decisions, ruled (the lane's defaults are confirmed as deliberate supervisor calls):**

1. **CL constraint TYPE = EQUALITY.** Confirmed. Sanaa/chief named "drag-min at **fixed** lift";
   equality (`CLᵢ = CL_target_i`) is the canonical trimmed statement, makes `shape=0` a feasible seed,
   and most directly excludes the SO-3 collapse (lift HELD, not merely bounded). The `GATE REACHED`
   fallback (§5.2) — CL held at all three points, drag improved on the feasible seed, but the
   constrained optimum not reached in the 5-DOF space — is registered as an admissible, and still
   demonstrative, outcome.
2. **DV set = `shape` only, fixed α.** Confirmed as MP-A1's scope. Adding per-point `aoa` DVs would
   introduce `d/dα` gradients SO-3aR2 never verified (charter §2) — that is a SEPARATE rung (a future
   aoa-trimmed MP-A2), not this one.
3. **cpuset = `8` (provisional).** Confirmed provisional; the launcher/authoring lane RE-READS live
   occupancy at freeze and picks a core disjoint from every live registered sibling, and `G12` gates
   the launcher value against the grader constant.
4. **`TOL_CL_ABS = 1.0e-3`.** Confirmed (100× IPOPT's own `constr_viol_tol = 1e-5`, absorbing the gap
   between the optimizer's internal CL and the post-processed CL the gate reads).
5. **`G-DRAG` = final `J` < baseline `J`; §2a intermediate = 1.0 % over ≥ 5 majors.** Confirmed. No
   magnitude gates a PASS (charter §9); the 1.0 % floor labels only the `GATE REACHED` path. The CL
   triple travels beside every drag number (SO-3 `forbidden_readings` carried).
6. **`M = 3.0` (`m_iter 2.0 × m_adj 1.5`), DERIVED; cap ceiling 183.5.** Confirmed. Cap safety checked:
   the O-S cap 72.0 ÷ SO-3's 0.66 core-min/major ≈ 109 majors of headroom, so even a high major count
   (A2 needed 47) stays well inside the cap; M=3.0 is the calibration quantity the O arm measures.

**COSTED core-min, brought to the chief BEFORE compute:** **estimate 58.63 core-min, ceiling 183.5**
(§4). $0.0501 est / $0.1569 ceiling DERIVED at $0.0513/core-h — far under the $25 pre-authorisation.

**Freeze still owed:** the instrument files (`mpa1_runScript.py` with the §1.5 CL-equality block,
`mpa1_grade.py` with all gates incl. the G5C-covers-`dCLᵢ/dx` assertion and the G-CLHOLD planted-zero
reader, and the carried controls) — **none written yet** — plus my check-1 read of THOSE diffs, then
the freeze by sha. An authoring lane is dispatched to this ruled design.

---

## §8. FREEZE STATEMENT — TAKEN 2026-09-07 by the dafoam-supervisor personally

**FROZEN.** This commit is the freeze. The gates (§2), thresholds (band 5.0 %, TOL_CL_ABS 1e-3,
CL_TARGET_TOL 1e-12, OPT intermediate 1.0 %), the six-token composition (§2e), the CL-EQUALITY
formulation and per-point targets (§1.4/§1.5), cpuset 8, the cost (estimate **58.63 core-min**, ceiling
**183.5 core-min** = Σ caps) and every label are bound as of this commit and cannot move (`CLAUDE.md`
rule 2). **The grading path is hash-locked**: `mpa1_grade.py` md5 `9b9cb93419797f99cf968d74f320f8b2`,
`mpa1_runScript.py` md5 `bb3ba3a61b19dc8564e247cdb11e9147` (`mpa1_INSTRUMENT_MD5_TABLE.md`); their
committed blobs were verified equal to disk at the freeze, and `mpa1_chain_driver.sh` asserts the
grader md5 before staging so the frozen file that ran is the file that is graded.

**The four `SUPERVISION_CHARTER.md` §3 checks, discharged personally before this freeze:**
1. **Check-1 (measurement-script diffs, read as diffs).** Both `mpa1_grade_DELTAS_from_so3.diff` (+418/-114)
   and `mpa1_runScript_DELTAS_from_so3.diff` (+125/-79) were read at source. The new gates G-CLHOLD,
   G-DRAG, G-CLTGT and the G5C dCL coverage `refuse()` are correctly implemented and folded into the row
   (row = min over [endpoint, opt, G-CLHOLD, G-DRAG]) and item composition; the selftest units U6a–U6i
   drive every new gate both ways; the runScript's one physics change is the correct per-point
   `add_constraint(...CL, equals=CL_TARGET[i])` loop with keys derived from SCENARIOS, the NOT_FROZEN
   gate before heavy imports, and the np=1 guard. One stale comment ("CL is UNCONSTRAINED in this item")
   was found on the first read, sent back, fixed (verified comment-only: the non-comment diff is empty),
   and the runScript `assert`→`raise` nit corrected (L-332).
2. **Crash triage.** N/A — no compute has run; this is a pre-launch freeze.
3. **Check-3 (big-claim verification).** The admissibility claim is upheld and gated, not asserted: MP-A1
   adds no new unverified gradient because the CL-equality constraints ride SO-3aR2's FD-verified
   `dCLᵢ/dx` at fixed α, and G5C re-verifies all three `dCLᵢ/dx` at MP-A1's OWN final design point
   (charter §9) with G-PROV travelling the SO-3aR2/SO-1a GATE FAIL chain — so the only licensed claim is
   "on the patched toolchain …".
4. **Check-4 (pre-registration committed before compute).** The prereg and all instruments are committed;
   this freeze commit precedes any compute (run root ABSENT, NOT_FROZEN sentinel present, zero solver
   core-minutes).

**Compute is NOT launched by this freeze, and the deviation from the instruments' "freeze removes the
sentinel" docstring is deliberate and stated:** the `NOT_FROZEN` sentinel is **retained** as the
launch-block so no compute can fire until the separate launch step removes it — the costed figure is
brought to the chief BEFORE compute, per the standing directive. cpuset 8 is registered; the launcher
re-reads live occupancy at launch and `G12` gates it against the registered constant.

**NOT ENQUEUED. NOT LAUNCHED. ZERO SOLVER CORE-MINUTES. SUBMISSIONS PARKED.** The upstream provenance
(SO-3aR2/SO-1a) is GATE FAIL and travels with every claim; nothing in this item is filed (§5, §2d).

---

## §9. DATED ADDENDUM — 2026-09-07, RULE-2 **PRE-COMPUTE** REPAIR OF THE CHAIN-DRIVER INTEGRITY PINS (STRIKES NOTHING; NO GATE MOVED)

This is a rule-2 amendment taken **before first compute** (before-compute amendments are legal; `CLAUDE.md` rule 2). It strikes nothing above, and it alters **no** gate, threshold, band, cap, deadline, label or instrument. It reconciles the chain driver's *own* integrity pins to the instrument bytes the §8 freeze **already** hash-locked — it does **not** re-open the c4e84348 freeze's gates.

**CONDITION.** `mpa1_chain_driver.sh` carried stale `MD5_*` integrity pins that did **not** match the frozen instrument bytes on disk. The driver's startup integrity block (~line 123) runs `md5sum -c` on six pins before any staging and aborts **rc=4 "md5 drifted or UNSET"** on the first mismatch — i.e. **before** the run root is created and before any container is staged. Two of the stale pins are the very instruments §8 hash-locks: `MD5_GRADER` pinned `0ac111ef…` while frozen `mpa1_grade.py` is `9b9cb934…` (the §8 value), and `MD5_RUNSCRIPT` pinned `0c026d72…` while frozen `mpa1_runScript.py` is `bb3ba3a6…` (the §8 value). Root cause: the instruments were re-edited to their final frozen bytes (04:19–04:25) but the driver's pins (dated 03:59 + AMENDMENT-2) were never re-derived before the freeze commit. This is the same class the D6RF5 repair addressed: a stale integrity pin aborts the chain rc=4 pre-staging — the "W3 death mode" the driver's own header (lines 80–83) names.

**HOW CHECKED.** Actual md5 of each frozen file on disk vs the pin (the derived value of the file the freeze hash-locked):

| pin | file (frozen) | old (stale) pin | actual = frozen md5 | status |
|---|---|---|---|---|
| `MD5_LAUNCHER` | `mpa1_run_arm.sh` | `e8839a2f…` | `f884672c32738b549ee79f4f400660ff` | STALE → repaired |
| `MD5_GRADER` | `mpa1_grade.py` | `0ac111ef…` | `9b9cb93419797f99cf968d74f320f8b2` (=§8) | STALE → repaired |
| `MD5_RUNSCRIPT` | `mpa1_runScript.py` | `0c026d72…` | `bb3ba3a61b19dc8564e247cdb11e9147` (=§8) | STALE → repaired |
| `MD5_XF` | `mpa1_xf.py` | `58fd0e26…` | `8036ca85d502276dc172c626becd11d5` | STALE → repaired |
| `MD5_STOP_MARKER` | `mpa1_stop_marker.sh` | `4809ff56…` | `5063f90b227eb3a7341d18c6ca7b7824` | STALE → repaired |
| `MD5_STALL` | `mpa1_stall.py` | `c0719b7f…` | `5d112800fc34dc729c80c584d873eec7` | STALE → repaired |
| `MD5_AGEGUARD` | `mpa1_age_guard.py` | `1bcbe57c…` | `7fe4352d36b7b48a5bb2885e225e455a` | STALE → repaired |
| `MD5_AGG` | `mpa1_aggregate_memory.py` | `709ab0b9…` | `709ab0b98ef0302a3a3a318588f9493f` | already OK (unchanged) |
| `MD5_DECOMP` | `mpa1_decomposeParDict` | `e6f1b006…` | `e6f1b0060944bc86d6dff56480ad2bd4` | already OK (unchanged) |
| `MD5_TUT_*` (6) | tutorial inputs under `TUT_SRC` | — | all six MATCH | already OK (unchanged) |

Seven stale instrument pins were re-derived from the frozen files and updated hex-for-hex (32 chars, comment alignment preserved). `MD5_AGG`, `MD5_DECOMP` and all six tutorial pins were left exactly as they were. `PERMISSION=bc0e687e` (the Sanaa-boarded detached-launch permission echoed to the ledger — **not** a freeze-sha gate) was **not** touched.

**POST-REPAIR VERIFICATION.** Re-audit of all 15 `MD5_*` pins against disk: **every pin now equals its file's actual md5** (`ALL_PINS_MATCH=1`). A sandbox dry-run of the ~line-123 integrity block (its six `md5sum -c` assertions, driven with the driver's own variables and pins, **without** staging the run root or launching any container) returns **rc=0 — no rc=4 abort**. Planted control: a one-byte corruption of the launcher copy is seen by the assertion (`PLANT_SEEN=yes`), so the reader is not blind. **No compute has occurred:** the registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation` is **ABSENT**, no MP-A1 container is running, zero solver core-minutes.

**SCOPE.** This addendum changes only the driver's integrity pins (a byte-integrity guard over the instruments), reconciling them **to** the instruments §8 already hash-locked. It does **not** re-open the c4e84348 freeze's gates, thresholds, caps, labels or instruments; the grading path stays exactly the §8 files. The `NOT_FROZEN` launch-block sentinel is **retained** — the re-freeze (by sha) and the launch remain the supervisor's acts after the check-1 read of these pin deltas. **STILL NOT ENQUEUED, NOT LAUNCHED, ZERO SOLVER CORE-MINUTES, SUBMISSIONS PARKED.**

---

## §10. DATED ADDENDUM — 2026-09-07, RULE-2 **PRE-COMPUTE** REPAIR OF THE **LAUNCHER** md5 PINS + DRIVER `MD5_LAUNCHER` CROSS-REPIN (STRIKES NOTHING; NO GATE MOVED)

This is a rule-2 amendment taken **before first compute** (before-compute amendments are legal; `CLAUDE.md` rule 2). It strikes nothing above, alters **no** gate, threshold, band, cap, deadline, label or instrument logic, and does **not** re-open the c4e84348 freeze's gates. `lines whose number changed above this section: 0.`

**CONDITION.** §9 repaired the *chain-driver's* integrity pins. The **launcher** `mpa1_run_arm.sh` carries its **own separate** pin table (~lines 515–521) that was **not** re-derived after the instruments reached their frozen bytes — the same rename-omission class as §9, one layer deeper. Two launcher pins held the SO-3 **parent** values, not the §8-frozen instrument bytes: `MD5_RUNSCRIPT=0c026d72…` while frozen `mpa1_runScript.py` is `bb3ba3a6…`, and `MD5_XF=58fd0e26…` while frozen `mpa1_xf.py` is `8036ca85…`. The launcher checks these at lines 605–606 (`echo "$MD5_RUNSCRIPT  $BASE/mpa1_runScript.py" | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }`). Because the driver's §9 block staged the correct (frozen) bytes into `$BASE` and passed, the launcher then compared those correct bytes against its **own stale** pin and aborted **rc=4 "ABORT runScript md5"** — **after** the driver integrity block passed but **before** any container. This is the exact observed failure of the 15:05–15:07Z launch attempt (staging root `STATUS.MESH: arm=MESH rc=4`; `STATUS.chain: chain=NOT A RESULT declared=7 executed=0 chain_rc=4`), whose root was then cleared (below).

**HOW CHECKED — FULL PIN AUDIT across BOTH files (all 19 `MD5_*` pins), each pin vs its guarded file's actual md5 on disk:**

| file | pin | guarded file | old (pre-fix) | actual = frozen md5 | status |
|---|---|---|---|---|---|
| `mpa1_run_arm.sh` | `MD5_RUNSCRIPT` | `$BASE/mpa1_runScript.py` | `0c026d72…` (SO-3 parent) | `bb3ba3a61b19dc8564e247cdb11e9147` | STALE → repaired |
| `mpa1_run_arm.sh` | `MD5_XF` | `$BASE/mpa1_xf.py` | `58fd0e26…` (SO-3 parent) | `8036ca85d502276dc172c626becd11d5` | STALE → repaired |
| `mpa1_run_arm.sh` | `MD5_DECOMP` | `$BASE/base/system/decomposeParDict` | `e6f1b006…` | `e6f1b0060944bc86d6dff56480ad2bd4` | already OK |
| `mpa1_chain_driver.sh` | `MD5_LAUNCHER` | `mpa1_run_arm.sh` | `f884672c…` (§9 value) | `3fab25cc046588f3fe7e528250c083aa` (NEW) | CROSS-REPINNED |
| `mpa1_chain_driver.sh` | `MD5_GRADER` | `mpa1_grade.py` | `9b9cb934…` | `9b9cb93419797f99cf968d74f320f8b2` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_RUNSCRIPT` | `mpa1_runScript.py` | `bb3ba3a6…` | `bb3ba3a61b19dc8564e247cdb11e9147` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_XF` | `mpa1_xf.py` | `8036ca85…` | `8036ca85d502276dc172c626becd11d5` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_AGG` | `mpa1_aggregate_memory.py` | `709ab0b9…` | `709ab0b98ef0302a3a3a318588f9493f` | already OK |
| `mpa1_chain_driver.sh` | `MD5_DECOMP` | `mpa1_decomposeParDict` | `e6f1b006…` | `e6f1b0060944bc86d6dff56480ad2bd4` | already OK |
| `mpa1_chain_driver.sh` | `MD5_STOP_MARKER` | `mpa1_stop_marker.sh` | `5063f90b…` | `5063f90b227eb3a7341d18c6ca7b7824` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_STALL` | `mpa1_stall.py` | `5d112800…` | `5d112800fc34dc729c80c584d873eec7` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_AGEGUARD` | `mpa1_age_guard.py` | `7fe4352d…` | `7fe4352d36b7b48a5bb2885e225e455a` | already OK (§9) |
| `mpa1_chain_driver.sh` | `MD5_TUT_RUNSCRIPT` | `$TUT_SRC/runScript.py` | `0557da51…` | `0557da51f6f179f6de865144343c499f` | already OK |
| `mpa1_chain_driver.sh` | `MD5_TUT_GEN` | `$TUT_SRC/genAirFoilMesh.py` | `681f1065…` | `681f10659eb90457fca13fc933008b93` | already OK |
| `mpa1_chain_driver.sh` | `MD5_TUT_PREPROC` | `$TUT_SRC/preProcessing.sh` | `4a939545…` | `4a9395452540705686acf94898aa33af` | already OK |
| `mpa1_chain_driver.sh` | `MD5_TUT_PS` | `$TUT_SRC/profiles/NACA0012PS.profile` | `51dfed28…` | `51dfed28e1bdb4cd33e0d8d7dabd586a` | already OK |
| `mpa1_chain_driver.sh` | `MD5_TUT_SS` | `$TUT_SRC/profiles/NACA0012SS.profile` | `4a6b8ef4…` | `4a6b8ef4501494c7693b71e88a2eabbf` | already OK |
| `mpa1_chain_driver.sh` | `MD5_TUT_FFD` | `$TUT_SRC/FFD/wingFFD.xyz` | `6ddf3780…` | `6ddf378b028d03d8a18270488bee1759` | already OK |

**THE FIX + CROSS-DEPENDENCY.** The two stale launcher pins were re-derived from the frozen files and updated hex-for-hex (old value verified on each line before editing; comment alignment preserved; **no** launcher logic touched). Repairing the launcher changes **its own** md5 from `f884672c…` (the value §9 pinned into the driver's `MD5_LAUNCHER`) to `3fab25cc…`; the driver's `MD5_LAUNCHER` pin (which guards the launcher and is asserted at driver lines 123 and 212) was therefore **cross-repinned last**, after the launcher was final, to `3fab25cc046588f3fe7e528250c083aa`. All other driver pins were re-verified against disk and left exactly as §9 set them.

**POST-REPAIR VERIFICATION.** Re-audit of **all 19** `MD5_*` pins across both files vs disk: **every pin now equals its guarded file's actual md5** — `ALL_PINS_MATCH=1`. A sandbox dry-run of the **full pre-container integrity path** — the driver pre-stage + tut-src + staged `md5sum -c` assertions (driver ~123–153) **and** the launcher's staged-md5 checks (605–607), driven with each script's own live pins against a verbatim `cp -a` staging tree, **without** creating the registered run root and **without** launching any container — returns **rc=0 (no rc=4 abort anywhere)**. Planted control: a one-byte corruption of the staged `mpa1_runScript.py` copy is caught by the launcher assertion (guard fires `rc≠0`), so the reader is not blind (fail-closed defence-in-depth intact); the corrupted copy was discarded.

**FAILED STAGING ROOT CLEARED.** The registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation` (from the rc=4 attempt) was asserted to hold **zero solver output** before removal: **zero** numeric solver time dirs, **no** generated `constant/polyMesh`, **no** `log.*Foam`; only `base/` (tutorial-template inputs incl. `0.orig`), `STATUS.*`, `MESH_*` logs, `MPA1_STOP_MARKER.json`, `grader_controls/`, `ledger.txt` and the staged instrument copies; `STATUS.chain` read `NOT A RESULT declared=7 executed=0 chain_rc=4` and the grade read `NOT A RESULT rows={SHIPPED: NOT_MEASURED, PATCHED: NOT_MEASURED}`. Being infrastructure of a failed launch and **not** evidence (no git state; outside the repo), the root was removed so the age-guard permits a clean cold re-launch.

**LATENT OBSERVATION, FLAGGED — NOT REPAIRED (needs a supervisor/chief decision, not a pin fix).** `mpa1_xf.py:127` holds `PRODUCER_MD5 = "0c026d72047b605099125258e3152f93"` — the SO-3 parent runScript md5. Per its **own** comment (lines 123–126) it is meant to equal `md5(mpa1_runScript.py)` = `bb3ba3a6…`, so it is stale by the same rename-omission class, one layer deeper still. It was **left untouched** because: (i) it is **internal** to the frozen instrument `mpa1_xf.py`, transitively guarded by `MD5_XF` — editing it would change that instrument's §8-hash-locked md5 (`8036ca85…`), re-opening the c4e84348 instrument freeze and cascading into `MD5_XF` re-pins, i.e. an **instrument re-freeze, not a pin repair**; (ii) its named live consumers (`mpa1_pin_census.py` A3, `mpa1_groot5_selftest.sh` (p1)–(p4)) **do not exist** anywhere in ladder-a, so nothing drives it today; (iii) `mpa1_xf.py` is invoked only in the XE/FE arms (launcher 825–826), **never** in the MESH-arm pre-container integrity path — so it does **not** cause the rc=4 this addendum repairs. It is raised here for the supervisor/chief to rule on separately.

**SCOPE.** This addendum changes only integrity pins — two in the launcher and the driver's `MD5_LAUNCHER` cross-repin — reconciling them **to** the instruments §8 already hash-locked. It moves **no** gate, threshold, band, cap, label or instrument logic; the grading path stays exactly the §8 files. The `NOT_FROZEN` launch-block sentinel was already removed and committed at `2f2e0321` (FREEZE ACT / LAUNCH) and is **not** re-added here; the re-launch remains the supervisor's act after the check-1 read of these pin deltas. **ZERO SOLVER CORE-MINUTES (this repair is pure static pin reconciliation + a sandbox dry-run). STILL NOT ENQUEUED, SUBMISSIONS PARKED.**
