# SO-3 (MULTIPOINT, WEIGHTED OBJECTIVE) — SCOPE MEMO. NOT A PRE-REGISTRATION.

**Dated 2026-08-28. Lane: dafoam `lab-lane` (Z). Supervisor: `dafoam-supervisor`.**
**Nothing here is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

> **THIS DOCUMENT PROMISES NOTHING AND PREDICTS NOTHING.** It freezes no gate, no threshold, no band, no label and no cap, and it registers no run. It exists because Sanaa's 2026-08-28T17:01Z directive said to pull SO-2 and SO-3 forward, and because SO-3 turns out to carry a scoping question that must be answered by a human before any registration is possible. **Nothing here may be cited as a prediction, and no number below is a registered cost.**

Sanaa's SO-3, verbatim (standing directives 2026-08-27T16:54Z §4): *"SO-3 Multipoint (2-3 Mach/alpha) weighted objective."*

---

## 1. THE SCOPING QUESTION THAT HAS TO BE ANSWERED FIRST, AND IT IS NOT A DETAIL

**SO-1's case cannot deliver a Mach sweep, because Mach is not one of its parameters.** `curriculum_SO2a/so2a_runScript.py` (byte copy of the tutorial's own) runs `solverName = "DASimpleFoam"` — the **incompressible** solver — at `U0 = 10.0`, M ≈ 0.03, with `primalBC` carrying `U0`, `p0` and `nuTilda0` and no thermodynamic state at all. On that case a "multipoint" can only be an **angle-of-attack (or lift-coefficient) sweep**; asking it for two or three Mach numbers is asking a solver with no density equation for a compressibility effect it does not model.

Three routes exist and **the choice is Sanaa's or the supervisor's, not this lane's**:

| route | case | what "2–3 points" means there | what it costs the ladder |
|---|---|---|---|
| **A. alpha-only on SO-1's own case** | A1 incompressible, `DASimpleFoam` | 2–3 angles of attack (or 2–3 `CL` targets) at one Mach | cheapest and most continuous with SO-1a/SO-2a; but it answers **half** of Sanaa's sentence and the record would have to say so in its title |
| **B. the subsonic compressible A1 case** | `curriculum_D15`, `DARhoSimpleFoam`, **same 4,032-cell mesh, byte-identical `genAirFoilMesh.py`, profiles and FFD box** (`curriculum_SO1a/PREREGISTRATION.md:40`, `cmp` silent four of four) | 2–3 genuine Mach numbers **and** alpha | answers Sanaa's sentence in full on a mesh the lab already knows; costs a new gradient rung, because a gradient verified on `DASimpleFoam` is not a statement about `DARhoSimpleFoam` |
| **C. the transonic half of SO-1** | `curriculum_D16` / RAE2822 | Mach either side of the drag-rise | Sanaa's own SO-1 sentence puts RAE2822 transonic *after* NACA0012; taking SO-3 there first reorders her ladder |

**This lane's reading, offered as a reading and not a decision:** route **B** answers the directive literally on a mesh, FFD and toolchain the lab has already exercised, and it inherits SO-2a's constraint-Jacobian work unchanged (the geometric constraints are pyGeo's and do not depend on the flow solver at all — which, if SO-2a's `G-STRUCT` passes, will have been **measured** rather than assumed). Route A is cheaper and can be frozen sooner but delivers a partial answer.

## 2. HOW THE WEIGHTED OBJECTIVE WOULD BE FORMED

The mechanism is already in the lab: D6 (`cases/dafoam/ladder-a/A2/curriculum_D6`) is a **3-scenario multipoint wing optimisation** and is the family's only multipoint precedent. The mphys shape is one `Multipoint` model carrying N `ScenarioAerodynamic` instances built from N `DAFoamBuilder`s (one per operating point), all fed by **one** `OM_DVGEOCOMP` geometry component, so the shape DVs are shared and each scenario carries its own `patchV`/boundary state. The weighted objective is an `om.ExecComp` forming `J = Σ wᵢ · CDᵢ` with the weights as fixed inputs, and `add_objective` on that component's output; the lift equality and the geometric constraints attach per scenario and once, respectively.

**Three things about that shape would have to be registered, and none is settled here:**

* **The weights.** Equal weights are a choice, not a default; a registration must name them, name why, and name what a different weighting would change. Sanaa's phrase "weighted objective" does not fix them.
* **Whether `CL` is trimmed per point.** SO-1's `findFeasibleDesign` trims `aoa` to `CL_target` before the optimisation. With N points, either each carries its own `aoa` DV and its own `CL` equality (N constraints, N extra DVs), or the points are specified at fixed `aoa` and `CL` floats. **These are different problems** and the choice changes the objective's meaning.
* **Whose gradient is being verified.** The multipoint objective's gradient is a **new quantity** — it is not the single-point `dCD/dx` SO-1a verified. `DAFOAM_CHARTER.md` §2 requires an FD table beside it before it drives an optimisation, and §5 requires that verification at the np the optimisation runs at. **That is a gradient rung of its own and it is not optional.**

## 3. MEMORY — MULTIPOINT IS FEASIBLE ON THIS BOX, AND THAT IS MEASURED, NOT ASSUMED

**D6's own run answers this and it is the load-bearing fact of this memo.** `docs/COST_CALIBRATION.md` C-188: D6's `O_mp` arm — **3 scenarios, np = 4, in a 20 g cgroup** on a 3-D wing — ran **8 h 20 m** and was stopped by its own registered deadline with `rc = 124` and **`OOMKilled = false`**. The D6R queue entry states the consequence in the same words: *"P7 (multipoint memory-feasible at np=4 in 20g) is ALREADY ANSWERED by D6 — OOMKilled=false after 8 h 20 m, C-188 — and is scored here only as a regression check, never re-bought."*

**SO-3 on A1 would be far smaller than that.** D13 measured peak RSS **1.70 GiB** for this 4,032-cell 2-D case at np = 1. Three DASolver instances in one process is bounded above, crudely, by `3 × 1.70 ≈ 5.1 GiB` plus one shared mesh/FFD/IDWarp footprint — comfortably inside the family's 4 g-per-arm convention only if the cap is raised, and comfortably inside a 12 g or 20 g cap. **A registration would still have to measure it rather than inherit this arithmetic**, and the H5 windowed floor and the 30.64 GiB aggregate bound apply as they do everywhere.

## 4. WHAT IT WOULD COST — SCOPING ARITHMETIC, EXPLICITLY NOT A REGISTERED ESTIMATE

Two measured anchors exist and they disagree in an instructive way:

* **`C-24`, D1 arm `O`, on THIS A1 case at np = 1: 0.42127 core-min/major MEASURED** (11 majors). This is the right single-point anchor for A1.
* **`C-188`, D6, 3-scenario multipoint at np = 4: 31.258 core-min/major MEASURED** against **19.167 registered** (a naive 3 × single-point) — **1.6308×**. The row's own conclusion: *"the ×3 model is short by 63 %."* It also records that the optimiser **stalled** rather than ran slow (545 line-search cutbacks, 7 restoration majors, dual infeasibility worsening), and that *"a rate calibrated on a converging optimiser does not price one that is backtracking, and the successor's estimate must carry a stall branch."*

Applying D6's measured multipoint correction to A1's measured single-point rate gives, **as scoping arithmetic only**: `0.42127 × 3 × 1.6308 ≈ 2.06 core-min/major` at np = 1, so **20–40 majors would land somewhere around 40–85 core-min**, plus a multipoint FD arm. That is a small item by this lab's standards and well inside the $25 pre-authorisation at $0.0513/core-h. **It is written here to show the order of magnitude and to show which anchors a real registration would use. It is not a cost, it is not a band, and a registration must derive its own with a stall branch.**

## 5. WHAT WOULD HAVE TO BE TRUE BEFORE SO-3 CAN BE FROZEN

1. **The route in §1 is chosen** — by Sanaa or the supervisor. Everything else depends on it, and this lane will not choose it.
2. **The multipoint objective's own gradient carries an FD table**, at the np the optimisation will run at (`DAFOAM_CHARTER.md` §2 and §5). On present evidence that is a **separate rung** — call it SO-3a — and SO-3 proper is its optimisation rung.
3. **SO-2a has an answer**, if the multipoint problem carries the geometric constraints — which it should, since a multipoint drag-min that may thin the section without a thickness floor is not the problem Sanaa described. The charter bars an unverified gradient from entering an optimisation.
4. **A per-major anchor measured on a 2-D multipoint exists, or the registration states plainly that it does not** and prices from D6's 3-D correction with the misprediction named as an exposure. C-188's lesson is that the ×3 model is the thing that breaks.
5. **The trivial baseline is decided for a multipoint objective**, which is not obvious: the weighted objective's gradient is a linear combination, so a shuffled-weight baseline (score against the wrong weights) is the natural candidate, and a step-based one is available here because the objective IS flow-dependent and noisy — unlike SO-2a's geometric constraints (`curriculum_SO2a/PREREGISTRATION.md` §3, `G-TB`).
6. **The C5 repair is carried forward**, not re-derived from an SO-1 ancestor. Any comparator descended from `so1a_grade.py` inherits the bare-substring token scan that published `NOT A RESULT` on a clean five-arm run; the repaired form lives in `curriculum_SO1c/so1c_grade.py` @ `42c7c8c3` and in `curriculum_SO2a/so2a_grade.py`.

## 6. STATUS

**`PENDING`** — scoped, not frozen, not registered, not enqueued, no compute. The supervisor reads this before anything is registered.
