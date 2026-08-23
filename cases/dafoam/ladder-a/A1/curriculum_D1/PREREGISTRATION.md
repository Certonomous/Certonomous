# Curriculum item D1 — A1 NACA0012, lift-constrained drag minimisation: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the item it registers is filed, sent,
emailed, uploaded, posted, registered or commented outside this box, now or on completion**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**NOT FILED — and not yet launched.** This file is frozen **before any container starts**
(`CLAUDE.md` rule 2; `SUPERVISION_CHARTER.md` §3 check 4). Phase 1 of this item is this document
and nothing else. **Launch authorisation comes from the dafoam-supervisor after its own personal
freeze verification, and no agent message is Sanaa's consent** (`CLAUDE.md` rule 9).

**Filed 2026-08-23 by Lane Y (Opus), DAFoam team, for curriculum item D1
(`cases/dafoam/EXPERTISE_CURRICULUM.md` §3 Tier 1, RATIFIED 2026-08-23 under the conservative
reading of its §7).** `RESULTS.md` is written afterwards, in this directory, and **does not revise
this file**; departures land as dated amendments at the foot, never by editing above.

---

## 0. What this item is, in three lines

1. **Minimise `CD` on the A1 NACA0012 case (`DASimpleFoam`, 4,032 cells, np=1) subject to the
   equality constraint `CL = CL* = 0.500000` and the case's own DVGeo/DVConstraints geometric
   constraints — thickness ≥ 0.5× baseline, volume ≥ 1.0× baseline, LE radius ≥ 0.8× baseline.**
2. **Design variables are the 8 FFD shape-function modes (`shape`) plus angle of attack, carried
   as `patchV[1]`; `patchV[0]` (freestream speed `U0`) is pinned `lower = upper = 10.0` and is
   inert. This 2D case has no twist DV — §2.3 shows why, from the case's own source.**
3. **The claim graded is the optimiser's, not aerodynamics': did a constrained optimisation
   converge on its own statement, at a feasible design, with its gradient re-verified against
   finite differences at the design point it actually reached.**

---

## 1. Provenance of every input, and the one record this item declines to use

Every number below is read from a committed record or from a file already on disk. **No solver was
run to write this document.** The only arithmetic performed here is on stored values and is shown
so it can be checked.

| what | value | source |
|---|---|---|
| case | NACA0012 official DAFoam tutorial, `incompressible` | `../../A1_naca0012_incompressible.md` |
| cells | **4,032** (`nPoints:8316 nCells:4032 nFaces:16254`) | same, mesh section |
| solver / tolerance | `DASimpleFoam`, `primalMinResTol = 1.0e-8` | `runScript.py:44` of the staged case |
| baseline `CD` (cold, np=2, and reproduced bit-identically np=1) | **`0.0209105098587985`** | `../../A1_naca0012_incompressible.md` primal-convergence block |
| baseline `CL` at the shipped `aoa0` | **`0.4987652667308054`** | same |
| shipped `aoa0` | **`5.13918623195176`** deg | `runScript.py:35` |
| **`CL_target`** | **`0.5`** | `runScript.py:34` — **this is `CL*`, registered from the case's own setup, zero compute** |
| shipped-toolchain A1 gradient verdict | **GATE FAIL**, `CD wrt shape` **11.4274%**, one sign flip at **idx6, 640.3696%** | `../reverify_patched_idwarp_np1/RESULTS.md` §2, §4.1 |
| patched-toolchain A1 gradient verdict | **PASS**, `CD wrt shape` **0.03796%**, zero flips, idx6 **1.1888%** right-signed | same, §2, §4.2 |
| A1 measured FD plateau | dead flat **2.5–3.0%** from **1e-4 to 3e-2** excluding the flagged components, cosine 0.99998; roundoff branch **94.95% at 1e-8**; **primal FAILS at 5e-2 and 1e-1** | `DAFOAM_CHARTER.md` §3 quoting `../../A_stepsize_study.md` |
| A1 np=1 whole-`check_totals` cost | **1.633 core-min / 98 s** at np=1 (1 cold primal + the CD/CL/volcon/thickcon/rcon adjoint set + 20 warm perturbed primals) | `../reverify_patched_idwarp_np1/RESULTS.md` §6, §8 |
| lab's only measured optimisation | **13.616 core-min, 6 majors, `EXIT: Optimal Solution Found.`, CD −7.47753%**, peak RSS 1.007 GiB, np=1, 2,777 cells | `../../A4/shipped_optimisation_np1/RESULTS.md` §2, §6 |
| mechanical noise-sized step rule | `η/(2s)` noise floor; clearance `C(s) = |J|·2s/η`; `s_lo` = smallest rung with `C ≥ 5`; `s_hi` = smallest rung at the registered ratio; **graded step is `s_hi`, never selected on agreement** | `../../A6/rung_n16_remaining_components/PREREGISTRATION.md` §4.1–4.2, scored in its `RESULTS.md` **§3.1** |

**The declined record, named rather than silently avoided.** `../../A1_naca0012_incompressible.md`
carries an **⚠ integrity flag on lines 167–172**. **Nothing in this pre-registration quotes,
paraphrases or relies on that span.** In particular, the identification of `shape` **idx6** as the
leading-edge combo mode is taken **not** from that span but from two independent primary sources:
the case's own `runScript.py:141-149`, where the interior shapes are appended first (`for i in
range(1, pts.shape[0]-1)`) and the two LE/TE combo modes are appended **after** them (`for i in [0,
pts.shape[0]-1]`), making them indices 6 and 7 of an 8-element list; and the per-component tables of
`../reverify_patched_idwarp_np1/RESULTS.md` §4.1–4.2, which print all eight components by index.

---

## 2. The problem, exactly as the case defines it

### 2.1 Objective, constraints and their registered numbers

Taken verbatim from the staged case's `runScript.py:172-177` — **this item changes none of them**:

| role | quantity | registered bound | notes |
|---|---|---|---|
| objective | `scenario1.aero_post.CD` | minimise, `scaler = 1.0` | |
| **equality constraint** | `scenario1.aero_post.CL` | **`equals = 0.5`**, `scaler = 1.0` | **`CL* = 0.500000`** |
| thickness | `geometry.thickcon` | **`lower = 0.5`**, `upper = 3.0` | `nom_addThicknessConstraints2D`, `nSpan=2`, `nChord=10` → **20 rows**; DVGeo normalises to the baseline, so **t_min = 0.5 × baseline thickness** |
| volume | `geometry.volcon` | **`lower = 1.0`** | `nom_addVolumeConstraint`, same lists → **1 row**; **V_min = 1.0 × baseline volume**, i.e. the section may not lose volume |
| LE radius | `geometry.rcon` | **`lower = 0.8`** | `nom_addLERadiusConstraints`, **2 rows** |

**24 constraint rows in total** (1 + 20 + 1 + 2).

**The normalisation is asserted, not assumed.** DVGeo's `thickcon`/`volcon`/`rcon` are conventionally
scaled by their own baseline value, which is what makes `lower = 1.0` on `volcon` mean "no volume
loss". Arm E prints the baseline values of all 24 rows; **if `volcon` at the undeformed baseline does
not read `1.0 ± 1e-9` and every `thickcon` row does not read `1.0 ± 1e-9`, the normalisation
assumption is wrong, this section's `t_min`/`V_min` statements are withdrawn, and the item is
reported `NOT A RESULT` about the constrained problem rather than re-interpreted after the fact.**

**Evidence the constraint chain itself is sound, already on record and costing nothing:** the
geometric-constraint Jacobians on this exact case verify at machine precision —
`volcon` **4.366597e-14**, `thickcon` **1.265004e-13**, `rcon` **1.363491e-10**, and they are
**identical to every printed digit across the shipped and patched images**
(`../reverify_patched_idwarp_np1/RESULTS.md` §2, §3). The DVGeo/DVConstraints chain this
optimisation leans on is therefore verified before the optimiser is allowed to lean on it.

### 2.2 Design variables

From `runScript.py:137-170`:

* **`shape`** — **8** shape-function DVs from `nom_addShapeFunctionDV`, all in `dir_y`:
  6 interior FFD stations (`k=0` and `k=1` moved together to enforce 2D symmetry) and 2 LE/TE combo
  modes (`j=0` and `j=1` moved in opposite directions so the LE/TE points stay fixed).
  Bounds `lower = -1.0`, `upper = 1.0`, `scaler = 10.0`.
* **`patchV`** — 2 components `[U0, aoa]`, bounds `lower = [10.0, 0.0]`, `upper = [10.0, 10.0]`,
  `scaler = 0.1`. **`patchV[0]` has `lower == upper == U0 == 10.0` and is therefore an inert DV**;
  **`patchV[1]` is the angle of attack in degrees and is the live one.**

**9 live design variables.** The count is corroborated by the frozen record's own instrument reading:
`check_totals` performs **21 primal solves** = 1 baseline + 2 × 10 central-difference perturbations,
i.e. **10 DVs** total, of which one (`patchV[0]`) is pinned.

### 2.3 AoA, not twist — derived from what the case supports

The brief permits "AoA (or twist equivalent for this 2D case)". **A1's setup supports AoA and does
not define any twist DV.** The rotation is applied to the **freestream**, not to the geometry:
`daOptions["inputInfo"]["patchV"]` is `{"type": "patchVelocity", "patches": ["inout"], "flowAxis":
"x", "normalAxis": "y"}` (`runScript.py:78-84`), and the `CD`/`CL` functions use
`directionMode: parallelToFlow` / `normalToFlow` with `patchVelocityInputName: "patchV"`
(`runScript.py:51-67`). There is **no** `nom_addGlobalDV`, no twist callback and no rotation
parametrisation anywhere in the file. **The registered DV set is FFD shape points + AoA via
`patchV[1]`.** This matters for the FD gate: `patchV` is the one DV in this case that **does not
cross `warpDeriv`**, which is why §6 names it as a component of the endpoint check.

### 2.4 The feasibility step, and what it does to the registered baseline

`run_driver` first calls
`optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[0.5],
designVarsComp=[1])` (`runScript.py:234`) — it solves for AoA so `CL = 0.5` **before** the optimiser
starts. **The reduction percentage is therefore registered against the post-feasibility CD, not
against the frozen `0.0209105098587985`**, and both figures are reported.

**Derived here, zero compute, from stored values** — labelled DERIVED, not measured. The frozen
record's `CL wrt patchV` and `CD wrt patchV` analytic magnitudes are **`1.345505e-01`** and
**`4.601100e-03`** per degree; both are 2-vector norms over `[U0, aoa]`, and for an incompressible
case whose `CD`/`CL` are normalised by `U0²` the `U0` component is expected to be negligible, so the
norms are taken as `|dCL/dAoA|` and `|dCD/dAoA|`. **This is an inference, and it is labelled as one.**

```
ΔCL required   = 0.5 − 0.4987652667308054      = 1.234733e-03
ΔAoA           = 1.234733e-03 / 1.345505e-01   = 9.176e-03 deg
AoA_feasible   = 5.13918623195176 + 9.176e-03  = 5.148362 deg      (DERIVED)
ΔCD            = 9.176e-03 × 4.601100e-03      = 4.222e-05
CD_feasible    = 0.0209105098587985 + 4.222e-05 = 0.02095273       (DERIVED)
```

---

## 3. Toolchain, registered by image hash (`DAFOAM_CHARTER.md` §6)

**Two rows, always. A patched row never replaces a shipped row (R11).**

| row | image | image ID / digest | `libidwarp.so` md5 | what runs on it |
|---|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | **`2927768a16ac`**, `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** | arms **E**, **O** — the η probe, the optimisation, and its endpoint gradient |
| **SHIPPED** | `dafoam/opt-packages:latest` | **`9d45679d55fd`**, `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** | arm **C** — the shipped endpoint-gradient companion |

Both digests were read from `docker images --no-trunc` on this box on 2026-08-23; the shipped digest
matches the one `../../ROOTCAUSE_getRotationMatrix3d.md` §1 records for IDWarp 2.6.2. **Every arm
prints the md5 of the `libidwarp.so` it actually loaded, from inside the process that loaded it**, and
an arm whose printed hash does not match the row above is **void** (gate G7). The version string reads
`2.6.2` on both stacks and the two `.so` files are the same size — the hash is the only identity.

### 3.1 Why the patched image for the optimisation row — from A1's own measured pair, not a global rule

`N-D18` records that the rotation patch is **not** monotonically beneficial: on A3 rung 2, where the
shipped gradient was already right to ~1 part in 5,800, the patch made every warp-crossing row
**worse** (`CD/shape[115]` 0.0172% → 0.1586%). **Adoption is case-dependent and is an owner's
decision, not a lane's.** The justification here is therefore A1's own A/B pair and nothing else:

| A1, np=1, same case, same mesh, same script, FD column bit-identical | shipped | patched |
|---|---|---|
| `CD wrt shape` aggregate | **11.4274%** | **0.03796%** — 301× |
| sign flips | **1 (idx6, 640.3696%)** | **0** (idx6 1.1888%, right-signed) |
| all 8 raw `Jfd` components | — | **8 of 8 bit-identical to the shipped arm** |

The last row is what makes the first two readable: because the **FD reference did not move on any of
the eight components**, the 301× improvement is a property of the derivative and not of a moved
reference (`../reverify_patched_idwarp_np1/RESULTS.md` §3). And the direction is the one only a
genuine fix can take — the analytic moved **toward** the pre-existing, unchanged FD on every
component (§4.2 of that file). **On A1, unlike A3 rung 2, there was a large error for the patch to
remove and it removed it.** An optimiser driven by the shipped gradient on this case would be driven
by a component whose **sign is wrong**; that is the reason the optimisation row is patched.

**This is not an adoption of a forked toolchain.** R11 stands: the patched row sits beside the
shipped row, and whether the lab grades against a fork is Sanaa's call.

### 3.2 `dafoam-team:v1` is rejected by name, with the reason

The brief names `dafoam-team:v1` (`0b3c94c33a15`) as a candidate. **It does not carry the IDWarp
rotation patch.** `docs/dafoam/README.md:153` and `cases/dafoam/patched_build/team/BUILD.md` record it
as `opt-packages` + the **two DAFoam `DALinearEqn.C` patches** (`subpclu:v2` + `kspopts`), both off by
default; `docs/LAB_STATE.md:309` records `dafoam-idwarp-rot:v1` as *the only image carrying the
rotation patch*. Using `dafoam-team:v1` here would produce **stock IDWarp numbers under a patched
label** — the exact failure `patched_build/idwarp_rot/BUILD.md` §1 warns about. It is also the one
lab image that ends `USER dafoamuser`, which would collide with §8's uid pinning. **Rejected.**

### 3.3 The shipped-row companion: what is bought and what is deferred, both priced

* **BOUGHT — arm C, the shipped endpoint gradient at the patched run's own final design point,
  priced at 2.0 core-min** (§7). It is bought because it closes, on this case, the exact hole
  `../../A4/shipped_optimisation_np1/RESULTS.md` §8 limit 3 names: *"A clean toolchain comparison at
  a deformed design would require running both images' `check_totals` at the same design point
  reached by the same path — an arm this item did not register and did not buy."* Arm C runs at the
  **same design point reached by the same path**, so its comparison against arm O's endpoint is a
  toolchain comparison and not two FD references disagreeing about two different optima.
* **DEFERRED — a shipped-image *optimisation* twin, priced at ~19.8 core-min** (the same as arm O).
  Reason, registered: A4 bought exactly this and the answer it returned was *"the rotation patch did
  not matter to this optimisation"*, driven by regime 1 decaying ≈2,000× between baseline and optimum
  on **one** DV — and that record states in its own §8 that nothing there transfers to an 8-DV case.
  **A1 is the case where the shipped gradient has a sign-flipped component at the baseline, so a
  shipped optimisation twin is a genuinely interesting run and it is deferred for cost, not
  dismissed.** It is listed for the supervisor's desk at 19.8 core-min / $0.0169 with its
  discriminating outcome: *does an 8-DV optimiser driven by a sign-flipped LE component reach a
  different optimum, or does the constraint set dominate?* **Not run under this pre-registration.**

---

## 4. Arms

Three arms, all np=1 (`DAFOAM_CHARTER.md` §5, serial before parallel; A1 has no decomposition axis
at np=1 and every A1 number this item leans on was measured at np=1).

| arm | image | task | why |
|---|---|---|---|
| **E** | patched | cold baseline primal, `printInterval 10`, constraint dump | measures **η** on THIS case; asserts cold start, mesh and setup identity; prints the 24 baseline constraint values |
| **O** | patched | `findFeasibleDesign` → `run_driver` (IPOPT) → **in the same process**: endpoint adjoint, per-component endpoint FD, trivial-baseline probe | the item |
| **C** | shipped | set DVs to arm O's final design vector → primal → adjoint → the same per-component FD | the shipped row (§3.3) |

**Arm O's endpoint work runs in the same process as `run_driver()`, immediately after it returns,
with the design vector already at the optimum — no reload, no restart, no directory reuse.** This is
the A4 pattern (`../../A4/shipped_optimisation_np1/PREREGISTRATION.md` §3.2, executed in its
`RESULTS.md` §3) and it is what makes the endpoint check a check *at the design point the optimiser
reached* rather than at a point re-derived from a file.

### 4.1 Optimiser and invocation pattern — reused from A4, disclosed

**Optimiser: IPOPT via `om.pyOptSparseDriver()`, `prob.driver.options["optimizer"] = "IPOPT"`** —
the same optimiser and the same driver A4's measured optimisation used
(`../../A4/shipped_optimisation_np1/RESULTS.md` §2: `opt_IPOPT.txt`, the `lg(mu)` barrier column,
`EXIT: Optimal Solution Found.`), and the case's own default (`runScript.py:23`). **The invocation
pattern is A4's `run_arm.sh` pattern, disclosed as reused:** `timeout <T> sudo -n docker run
--user 0:0 --cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500 -v $BASE:/mnt -w /mnt/<arm>
<IMG> bash -lc "source loadDAFoam.sh && <print IDWARP_SO_MD5 from inside the loading process> &&
mpirun --allow-run-as-root -np 1 -x PYTHONPATH python <script> -task <task>"`.
**Two deliberate departures from A4's script, both registered here:** `--rm` is **dropped** (§8.2) and
the **record-only RSS watcher subshell is removed** (§8.1).

**IPOPT settings: the case's own, unchanged** (`runScript.py:206-217`) — `tol 1e-5`,
`constr_viol_tol 1e-5`, `print_level 5`, `mu_strategy adaptive`,
`limited_memory_max_history 10`, `nlp_scaling_method none`, `alpha_for_y full`, `recalc_y yes` —
**with one registered change: `max_iter 100 → 40`.** The cap is registered so that a cap-stop is
legible under `DAFOAM_CHARTER.md` §9 and so the prediction band of §5 P2 ([8, 30]) **cannot be
satisfied by the cap itself**. `output_file` stays `opt_IPOPT.txt`.

### 4.2 The endpoint FD driver

`check_totals` cannot be restricted to individual DV indices, so the endpoint FD is taken by a
**hand-written per-index central-difference driver**, `d1_fd_endpoint.py`, the A6 `fdsub` pattern
(`../../A6/rung_n16_remaining_components/PREREGISTRATION.md` §4). Its formula is fixed here:
`J_fd(i, s) = (f(x + s·e_i) − f(x − s·e_i)) / (2s)`, `f = CD`, `x` = the endpoint design vector held
in memory.

**The grading path is fixed at this commit** (`CLAUDE.md` rule 2). Since the driver file cannot be
hashed before it exists, the binding registration is: **(a)** its algorithm, ladder and step rule are
fully specified in this document and in §6; **(b)** it is written **before any container starts**, its
md5 is written into `ledger.txt` **before the first launch**, and that md5 is quoted in `RESULTS.md`;
**(c)** it is **not edited after the first launch — an edit voids every arm that ran before it**, and
that voiding is reported, not repaired.

**Two zero-compute instrument controls on the driver, run before any container starts:**

* **FD-arithmetic plant.** The driver's difference kernel is exercised on `f(x) = x³` at `x = 2`,
  `s = 1e-4`: it must return `12.000000` to ≥ 8 significant figures. A kernel that cannot
  differentiate a cubic is not permitted to differentiate a solver.
* **Planted-zero control (`CLAUDE.md` rule 3) — gate G5.** The comparator that reads the endpoint
  design vector, `CD` and `CL` from disk (arm O writes `endpoint.json`; arm C reads it) plants
  `PLANT = 1.234e-03` into a **copy** of that file, re-reads it through the same reader, and asserts
  the read-back value moved by exactly the plant. **If the reader cannot see the plant, the
  comparator exits 2 and refuses** — it does not degrade to a warning.

---

## 5. Predictions, with HIT/MISS bands and the basis of each

**Every band below is committed before any compute. Bands are scored as HIT or MISS in `RESULTS.md`,
and a MISS is reported as a MISS with its reason named, never explained away.** Where A1 carries no
basis the figure is **SCALED** from A4 and labelled.

| id | prediction | HIT band | basis |
|---|---|---|---|
| **P1** | **termination class** | `EXIT: Optimal Solution Found.` present in `opt_IPOPT.txt` with `Overall NLP error < 1e-5` | **MEASURED anchor:** A4's shipped and patched arms both printed it on this optimiser and driver (`../../A4/shipped_optimisation_np1/RESULTS.md` §2). **Counter-anchor, which is why this is not free:** A2's 47-major IPOPT run printed **no EXIT line and no convergence statement at all** (`DAFOAM_CHARTER.md` §9) |
| **P2** | **major iterations** — point **18** | **[8, 30]** | **ESTIMATED-BY-ANALOGY, labelled.** Lower anchor MEASURED: A4 took **6** (shipped) / **9** (patched) on a **1-DV** bounded problem. Upper anchor: A2's **47** majors on a ~100-DV wing, itself NOT A RESULT. A1 has **9 live DVs and 24 constraint rows**; no A1 optimisation has ever been run in this lab, and per-DV extrapolation from a 1-DV case is not defensible — **the band is wide on purpose and its width is the honest content** |
| **P3** | **CD reduction** vs `CD_feasible` — point **5.0%** | **[2.0%, 12.0%]** | **ESTIMATED-BY-ANALOGY, labelled.** A4 MEASURED **−7.47753%** (1 DV, bluff body). A2's historical run reached **−28.275%** at matched `CL ≈ 0.5` but is NOT A RESULT and is quoted as an upper anchor only. The constraint set here is tight — `volcon ≥ 1.0` forbids net volume loss, `thickcon ≥ 0.5`, `rcon ≥ 0.8` — so a large reduction is not available at fixed `CL` |
| **P3b** | **`CD_feasible`** after `findFeasibleDesign` — point **`0.020953`**; **`AoA_feasible`** — point **`5.1484`** deg | `CD_feasible ∈ [0.02090, 0.02100]`; `AoA ∈ [5.13, 5.17]` | **DERIVED zero-compute in §2.4** from the frozen `CD`/`CL` and the stored `CD`/`CL wrt patchV` magnitudes; the `U0`-component-negligible step is an inference and is labelled |
| **P4** | **final `|CL − CL*|`** — point **≈1e-8** | **≤ 1.0e-6** (prediction); **gate G1 threshold is the looser ≤ 1.0e-5** | A4's IPOPT reported `Constraint violation....: 0.0000000000000000e+00` at its optimum on this driver; `constr_viol_tol` is `1e-5` as shipped and `scaler = 1.0`, so the constraint is unscaled |
| **P5** | **per-major cost** — point **1.0 core-min/major** | **[0.4, 3.5] core-min/major** | **A1's own MEASURED anchor:** 1.633 core-min for 1 cold primal + the full CD/CL/volcon/thickcon/rcon adjoint set + 20 warm perturbed primals at np=1 (`../reverify_patched_idwarp_np1/RESULTS.md` §6). A major ≈ 1 deformed primal + the CD and CL adjoints + ~1 line-search primal. **SCALED cross-check, labelled:** A4 measured **2.27 core-min/major** at 2,777 cells; A1 has 1.45× the cells, so the A4-scaled figure is ≈3.3 — **the band's top is set to 3.5 to cover it while the point estimate deliberately does not, because A1's own primal is measured to be cheap. If the A4 scaling wins, P5 is a MISS and is reported as one** |
| **P6** | **endpoint FD agreement, patched**, per component on the ≥3 named components — point **≤ 1.5%** | **every graded component ≤ 5.0% AND zero sign flips** | A1's patched **baseline** per-component errors are **0.0104%–1.1888%** at step 1e-3, worst at idx6 (`../reverify_patched_idwarp_np1/RESULTS.md` §4.2). A4's endpoint read **0.4936%** patched, better than its baseline. **The named risk, registered:** `DAFOAM_CHARTER.md` §9 — *a gradient verified at iteration 0 is not verified at iteration 47* — and A1's own record §7.3 states regime 2 *"would govern any optimisation run from iteration 1"*. **This gate exists precisely because P6 may fail** |
| **P7** | **η on this case** — point **2e-9** | **[2e-10, 5e-8]** | A1's own frozen primal tail: `CD` reads `0.02091052898117485` at Time 400 and `0.0209105098587985` at Time 435 — a change of **1.91e-9** over the final 35 iterations at `primalMinResTol 1e-8`. And δ_repeat is **exactly zero**: the run-2 baseline primal reconverged **bit-identically to all 16 digits** from a cold start (`../../A1_naca0012_incompressible.md`). For comparison A6's η is **1.0910e-05** — four orders larger — which is why §6 registers a floor the clearance test cannot undercut |
| **P8** | **trivial baseline** (gate G4), `shape` idx6 at `step = 1e-8` | **> 50%** | A1's own sweep: **94.95%** at 1e-8 (shipped, baseline, full 8-vector); and **132.75%** at 1e-8 on the **patched** stack that passes at 0.03796% (`../reverify_patched_idwarp_np1/RESULTS.md` §4.3) |
| **P9** | **peak memory** — point **1.2 GiB** | **≤ 2.0 GiB** | A4 MEASURED **1.007 GiB** (optimisation) and **1.331 GiB** (`check_totals`) at 2,777 cells, np=1, against an 8 GiB cap; A6 N=16 measured 0.657 GiB at 41,760 cells for a primal-only arm. Most of the RSS is the image's Python/OpenFOAM/PETSc base and does not scale with 4,032 vs 2,777 cells |
| **P10** | **total cost** — point **23.0 core-min** | **≤ 46.0 core-min** (point + 100% contingency) | §7 |

**Falsifiers — each stops or re-labels the item rather than being absorbed.**

* **F1.** Arm E's baseline `CD` is not **`0.0209105098587985`** to all 16 digits → the staged case is
  not the case these records describe (warm start, wrong mesh, or wrong setup). **Stop; nothing else
  in the run means anything.** *(This single assertion proves cold start, mesh identity and setup
  identity at once — the A6 `FD_BASELINE_CD` construction.)*
* **F2.** Any arm's printed `IDWARP_SO_MD5` differs from §3's row → that arm is **void** (G7).
* **F3.** The reduction is **≤ 0%** → the optimiser did not improve the objective; the design claim is
  **NOT A RESULT**, whatever the exit line says.
* **F4.** The objective column is **non-monotone on an accepted step** → reported, and the optimiser's
  own line-search behaviour is quoted rather than the endpoint alone (A4's falsifier P3(a)).
* **F5.** Any endpoint component shows a **sign flip** → gate G3 is **GATE FAIL** and the design is
  **not validated**, regardless of the aggregate (`DAFOAM_CHARTER.md` §2).
* **F6.** The trivial baseline at `1e-8` returns **≤ 5%** → the instrument cannot fail, and **G3's
  verdict is WITHDRAWN** (`DAFOAM_CHARTER.md` §4).
* **F7.** The planted-zero comparator cannot see its plant → **exit 2**, no comparator number is
  reported (`CLAUDE.md` rule 3).
* **F8.** `volcon` or any `thickcon` row does not read `1.0 ± 1e-9` at the undeformed baseline →
  §2.1's `t_min`/`V_min` statements are **withdrawn** and the item is **NOT A RESULT** about the
  constrained problem.

---

## 6. Gates — every one with its number

**Grading band (`DAFOAM_CHARTER.md` §2, `VERIFICATION_CHARTER.md` §7):** PASS ≤ 5% with zero flagged
components; CONDITIONAL 5–15% with a per-component breakdown; **> 15% or any sign flip → FAIL**,
whatever the aggregate.

### G1 — constraint satisfaction at the accepted design

**`|CL − 0.500000| ≤ 1.0e-5`** at the accepted design, **AND** IPOPT's own
`Constraint violation....:` ≤ `1.0e-5`, **AND** every geometric row inside its registered bound:
`thickcon ∈ [0.5 − 1e-6, 3.0 + 1e-6]` on all 20 rows, `volcon ≥ 1.0 − 1e-6`, `rcon ≥ 0.8 − 1e-6`.
**Any row outside → the design is not accepted and the optimisation claim is `NOT A RESULT`.**
The tolerance is `constr_viol_tol` as the case ships it — registered, not chosen after the fact.

### G2 — termination (`DAFOAM_CHARTER.md` §9)

| what the optimiser did | verdict |
|---|---|
| `EXIT: Optimal Solution Found.` with `Overall NLP error < tol 1e-5` | **gradeable** — PASS if G1 and G3 also hold |
| stopped at **`max_iter 40`**, or at the stage **`timeout`**, or at the **120.0 core-min ceiling** | **`GATE REACHED`** *if and only if* G1 holds at the last accepted design **and** G3 holds **and** the reduction is ≥ the registered intermediate threshold of **2.0%**; otherwise **`NOT A RESULT`** |
| any infeasible / restoration-failure / error exit | **`NOT A RESULT`** |

**Never `PASS`, and never described by the size of the improvement it reached.** The intermediate
threshold (2.0%) is the floor of P3's band and is registered here, before the run, precisely so that
`GATE REACHED` cannot be chosen after the number is seen (`DAFOAM_CHARTER.md` §8's D383 failure).

### G3 — endpoint FD spot-check on the named components

**Four components, named now:**

| # | component | why this one |
|---|---|---|
| 1 | **`shape` idx6** | the LE combo mode — the defect's own component; **640.3696% and sign-flipped** on the shipped image at baseline, **1.1888%** patched. Mandatory |
| 2 | **`shape` idx1** | the largest baseline shipped error that is *not* a flip (**11.6625%**), `|J| = 1.99e-2` |
| 3 | **`shape` idx5** | the largest `|J|` (**4.34e-2**) and the best-behaved patched component (**0.0104%**) — the component that should agree if anything does |
| 4 | **`patchV` idx1 (AoA)** | the only live DV that **does not cross `warpDeriv`** — the IG-2 analogue, and the row `N-D18` measured bit-identical across images |

**The registered step rule — mechanical, and a function of `|J_adj|` and `η` only.**

> **Ladder.** `shape` (FFD y-displacement, length units): **`{1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2}`**.
> `patchV[1]` (degrees): **`{1e-3, 3e-3, 1e-2, 3e-2, 1e-1}`**.
> **Noise floor** at step `s` := `η / (2s)` (central difference). **Clearance** `C(s) := |J_adj|·2s/η`.
> **`s_lo`** := the **smallest** rung satisfying **both** (a) `C(s) ≥ 5` and (b) `s ≥ 1e-4` for
> `shape` / `s ≥ 1e-3` for `patchV[1]`. **`s_hi`** := the smallest rung with `s_hi ≥ 3·s_lo`.
> **The graded step is `s_hi`, and it is NOT selected on agreement.**
> **A component is GRADED only where `C ≥ 5` at the graded step AND its two steps agree within the
> plateau tolerance of 10%.** A component failing either test is **FLAGGED and excluded BY NAME** from
> every aggregate (`DAFOAM_CHARTER.md` §3) — never rescued by a step at which it happens to cross.

**Three things about this rule are registered because they are departures or choices:**

1. **`|J_adj|` is the endpoint adjoint, computed by arm O itself before any FD is taken.** A6's rule
   used a *stored* `|J_adj|` because its design point existed in advance; **an endpoint design point
   does not exist until the optimiser produces it.** The anti-fitting property that matters is
   preserved exactly: **no FD value ever enters the choice of step.** The arithmetic, the ladder, the
   ratio and the thresholds are frozen here; only the two inputs are read at run time, and both are
   read before the first FD perturbation.
2. **Ratio 3, not A6's 2.** The `shape` ladder's rungs are spaced ≈3.16×, so a ratio of 2 would land
   on the same rung as 3 for most components while allowing a degenerate 1.25×-style pair on a denser
   ladder. A6's reasoning (*"a plateau read across two steps a factor 1.25 apart is satisfied by
   construction and measures nothing"*) is preserved a fortiori.
3. **The floor (b) exists because on A1 the clearance test is expected not to bind, and saying so in
   advance is the point.** With P7's `η = 2e-9`, the smallest component (`shape` idx6,
   `|J| = 1.07e-3`) clears **C(1e-4) ≈ 107**, and every other component clears by more. **The step is
   therefore expected to be set by A1's own measured roundoff branch, not by the noise rule** —
   94.95% at 1e-8, 52.88% at 1e-7, 17.64% at 1e-6, 12.27% at 1e-5, with the measured plateau running
   **1e-4 to 3e-2** (`DAFOAM_CHARTER.md` §3 quoting `../../A_stepsize_study.md`). The ceiling 3e-2 is
   the largest step in that measured plateau; the study measured genuine **primal failures at 5e-2
   and 1e-1**, so no rung above 3e-2 is offered. **Predicted registered pair for every `shape`
   component: `{1e-4, 3e-4}`, graded at `3e-4`. Predicted for `patchV[1]`: `{1e-3, 3e-3}`, graded at
   `3e-3`.** If the measured `η` moves the pairs, the **rule** — not the number — is what was frozen,
   and every clearance is re-stated at both η values in `RESULTS.md`.

**G3 verdict:** PASS if every graded component ≤ 5% with zero sign flips; CONDITIONAL 5–15% with the
per-component table printed; **GATE FAIL** above 15% **or on any sign flip**. The aggregate statistic,
if one is quoted, is named as **the vector-relative error `‖J_an − J_fd‖/‖J_fd‖` over the graded
components only, with the flagged ones listed by name beside it, never instead of it**
(`DAFOAM_CHARTER.md` §2). **A vector norm and a per-component average are different statistics and
are never compared** — the per-component table is the primary report here, the aggregate secondary.

**Registered limitation, stated in advance.** `η` is measured at the **baseline** design (arm E);
the endpoint's own noise floor is not measured, and
`../../A4/shipped_optimisation_np1/RESULTS.md` §3.2 found the FD reference at a deformed design point
to be **path-dependent** (two runs, same optimum to 1.8e-07, FD references 0.183% apart). The
mitigation registered here is the **two-step plateau test at the endpoint**, which detects a
noise-dominated estimate without needing an endpoint η. It is a mitigation, not a measurement, and
`RESULTS.md` says so.

### G4 — trivial baseline (`DAFOAM_CHARTER.md` §4)

**The same probe at a deliberately wrong step: `shape` idx6 at `step = 1e-8`, on the patched stack —
the one predicted to pass at the registered step.** Registered prediction **> 50%** (P8).
**If the wrong step also passes (≤ 5%), G3's verdict is WITHDRAWN and the item reports that the gate
was not measuring what it claimed.**

**Why 1e-8 and not one order off the registered step.** One order off `3e-4` is `3e-3` and `3e-5`;
`3e-3` sits **inside A1's measured plateau** and `3e-5` sits on its shoulder. A step inside the
plateau is not a wrong step on this case, and using one would build a control that passes for the
same reason the real arm does. **The measured roundoff branch is severe by 1e-8 and this is A1's own
registered precedent, executed and scored** (`../reverify_patched_idwarp_np1/PREREGISTRATION.md`
§ Arm 3; measured 132.75% in its `RESULTS.md` §4.3).

### G5 — planted-zero control (`CLAUDE.md` rule 3)

Every comparator that reads a value from disk plants `PLANT = 1.234e-03`, reads it back through the
same reader, and **refuses (exit 2)** unless the read-back moved by the plant. This binds the
`endpoint.json` reader that hands arm O's design vector to arm C, and any reduction/agreement figure
computed from a file rather than in-process. **A zero from a reader not shown able to see a non-zero
is not evidence.**

### G6 — launch gate, re-run immediately before each of the three launches

**`free_cores ≥ 4` AND `MemAvailable ≥ 12 GiB`**, where `free_cores := nproc − load1`
(`/proc/loadavg` field 1, `/proc/meminfo MemAvailable`). **The 12 GiB floor is the lab's standing
floor: this item neither touches it nor argues with it.** The gate is run as its **own command**
whose output is appended to `preflight_history.txt` with a UTC timestamp, and **its result is read
before the launch command is issued** — not polled by a background process. If the gate is not open,
the arm **waits and the gate is re-run**; it is not launched under a departure on this lane's own
authority. Any departure must be directed in writing by the supervisor and is recorded as a dated
amendment **before** the launch, never after (the A4 Amendment-1 precedent).

### G7 — image identity

`IDWARP_SO_MD5`, printed from inside the process that loaded the library, must equal
`85f59e87253e0a71a813f64ca6e4c425` (arms E, O) or `f0fcb488e0e98156575cd19548e91663` (arm C).
A mismatch **voids that arm**. `nProcs : 1` is asserted in every arm's log.

### G8 — cold start

Before **every** launch, verified **before, not after**: no `processor*` directory, no `0.0001` or
other numeric time directory, `0/` restored from `0.orig/`, no `reports/` carried over. A1's own
Lesson records the failure this prevents — `check_totals` run 1 died because `compute_totals` had left
`processor0/0.0001` populated — and `DAFOAM_CHARTER.md` §6 records the subtler one: **pyDAFoam writes
the primal end state back into the time-0 directory at run end, so the second run of a case directory
silently warm-starts.** F1's bit-identical baseline `CD` is the check that this held.

### G9 — memory envelope (`DAFOAM_CHARTER.md` §7)

Predicted peak **1.2 GiB**, ceiling **2.0 GiB** (P9). **Kernel cap `--memory=6g --memory-swap=6g`** —
equal, so there is no swap escape — plus **`--oom-score-adj=500`** and the per-stage `timeout`.
**A container the kernel OOM-killed (`docker inspect` `.State.OOMKilled == true`, or exit 137) is
recorded as stopped by memory and is `NOT A RESULT` about convergence** — it is not re-labelled as a
solver finding. Equally, and because L-15 is the opposite error: **a failure with headroom unused is
not a memory finding either**, and the peak figure is reported beside the cap so a reader can tell.

### G10 — cost ceiling

**HARD ceiling 120.0 core-min = $0.1026 derived.** An overrun **stops the run**; it does not get a new
budget (`CLAUDE.md` rule 12). §7.

---

## 7. Cost (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); every dollar figure
here is **DERIVED**. Core-minutes are **wall seconds × ranks ÷ 60**, billed as **cores × wall for the
whole clock** — the lab convention for DAFoam, because `docker run` holds its cpu allocation whether
the solver saturates it or not.

| stage | ranks | predicted wall | predicted core-min | basis |
|---|---|---|---|---|
| zero-compute reads, staging, driver self-tests | — | — | **0.000** | no container is started |
| **arm E** — cold baseline primal, `printInterval 10`, η + constraint dump | 1 | ~70 s | **1.2** | A1 np=1 measured: a whole `check_totals` (cold primal + full adjoint set + 20 warm primals) = 98 s |
| **arm O** — `findFeasibleDesign` + 18 majors + endpoint adjoint + 16 FD primals + 2 trivial-baseline primals | 1 | ~1,190 s | **19.8** | 18 majors × **1.0 core-min/major** (P5) + ~110 s of endpoint work |
| **arm C** — shipped endpoint gradient at arm O's design point (cold primal + adjoint + 18 perturbed primals) | 1 | ~120 s | **2.0** | A1's measured 98 s `check_totals` shape, plus a cold primal |
| **REGISTERED PRICE (point)** | | | **23.0** | **$0.01967 DERIVED** |
| **with 100% contingency** | | | **46.0** | **$0.0393 DERIVED** |
| **HARD CEILING** | | | **120.0** | **$0.1026 DERIVED — overrun STOPS the run** |

**The curriculum's own estimate was ~70 core-min; this lane re-derives 23.0 and discloses the gap.**
`EXPERTISE_CURRICULUM.md` §3 priced D1 at ~70 core-min by scaling A4's **2.27 core-min/major** across
an assumed major count. **A1 carries its own np=1 timing anchor** — 1.633 core-min for a full
`check_totals` — and that anchor is nearer the work than A4's is, so it is used and the A4 figure is
kept as the labelled cross-check inside P5's band. **The 120.0 hard ceiling is unchanged**: it is
registered by the brief and is not this lane's to move.

### 7.1 L-250 — `timeout` at the predicted-run envelope plus a stated margin, never at the budget's edge

*"A per-stage timeout cap is both the bound on a hang and the size of the loss."* The budget ceiling
is a different number with a different job; a `timeout` at 120 core-min would legalise ~97 core-min of
hang.

| stage | predicted wall | **registered `timeout`** | stated margin | loss bound if it hangs |
|---|---|---|---|---|
| arm E | ~70 s | **300 s** | **4.3×** | 5.0 core-min |
| arm O | ~1,190 s | **2,700 s** | **2.3×** | 45.0 core-min |
| arm C | ~120 s | **400 s** | **3.3×** | 6.7 core-min |
| **sum of caps** | | **3,400 s** | | **56.7 core-min — 47% of the ceiling** |

**Every arm runs foreground-or-polled under its `timeout`; no unbounded process is started.**
**The timeout, not the ceiling, is the binding instrument** — if P5's per-major cost lands at the top
of its [0.4, 3.5] band and P2's majors at the top of [8, 30], arm O would need ~105 core-min and
**the `timeout` fires first**, at 45 core-min, and the run is recorded as stopped by the wall clock →
`GATE REACHED` or `NOT A RESULT` under G2. That is a registered outcome, not a surprise.

### 7.2 Predicted-versus-actual cost comparison — a registered deliverable

**Relay, recorded as a relay** (`CLAUDE.md` rule 9): a peer session relayed Sanaa's standing directive
of 2026-08-23, verbatim — *"for all teams involved once a process is completed, the estimated costs
must be compared with the actual incurred costs so we can improve the lab's estimates."* It reached
this lane as an agent message, is treated as a **reporting duty within this item's existing scope**,
and grants nothing else.

`RESULTS.md` **must** carry, and this pre-registration registers as a deliverable:

1. **Core-minutes measured from the run's own logs and `ledger.txt`**, per arm and in total, stated
   **gross** and **cleaned** (cleaned = gross minus any row the 3,600-s stall rule matches; if no row
   matches, the record says so rather than leaving the column blank).
2. **Dollars DERIVED at $0.0513/core-h and labelled derived, never measured.**
3. **The ratio actual/predicted**, on the total **and per-major** — which is why P5 registers a
   per-major figure and not only a total, so the comparison is meaningful rather than an artefact of
   the major count.
4. **Gap attribution split three ways — contention / waste / misprediction — with waste separately
   named and never laundered into either of the other two**, nor into the ratio's explanation.
   Contention is measured against a like-for-like work marker in both logs where one exists (the A4
   §6.1 method), not asserted from the whole-arm wall clock.
5. **The row appended to `docs/COST_CALIBRATION.md`** in that file's registered format
   (`date | team | process/rung | predicted | actual gross | actual cleaned | ratio | gap attribution
   | record ref`), landed via the private-index protocol with the table tail re-derived **in the same
   shell invocation as the commit** (its append rule 5). **That file exists at HEAD as of this
   freeze**; if it has been moved or removed by completion, the row is **drafted inside `RESULTS.md`
   for the supervisor to land** rather than written to a new location.

---

## 8. Memory envelope, and the mechanism this item will NOT use

### 8.1 The wired stop is kernel-enforced only — no watcher, and the reason is on the record

**`DAFOAM_CHARTER.md` §13's dated note is a PROPOSAL and is unratified; this item does not enforce
it. It does, however, register the thing that note is about, because the failure it describes is
real:** A3 rung 2 registered a host-memory floor, armed a **record-only** watcher, and had **nothing
connecting them** — the floor was breached for 52.6% of the graded arm's samples by the arm's own
container, and **no stop fired because none could** (L-239, D462).

**So this item registers, in one sentence, which of its guards can execute and which cannot:**

* **CAN execute — the kernel.** `--memory=6g --memory-swap=6g` (equal: no swap escape) and
  `--oom-score-adj=500` are enforced by the cgroup, not by any process this lane starts; a breach ends
  the container and G9 grades it.
* **CAN execute — `timeout`.** Per stage, §7.1, enforced by the kernel's signal delivery.
* **CANNOT execute — the host `MemAvailable` floor.** G6's 12 GiB floor is a **launch condition**,
  checked immediately before each launch and **not** re-checked during a run. **It is record-only in
  flight, it is stated as record-only here, and nothing in this item claims it stops anything.**

**No watcher-script mechanism is used, and this is not a preference.** A watcher start command is
under a **permission denial in a peer context**. This lane does **not** re-attempt it, does **not**
route around it, and does **not** treat any agent's message as authority to do either
(`CLAUDE.md` rule 9). **A6's and A4's record-only RSS polling subshell is therefore deliberately
removed from the reused `run_arm.sh` pattern** (§4.1).

**Consequence, accepted rather than worked around:** peak RSS is reported from
`/usr/bin/time -v`'s `Maximum resident set size` if that binary is present in the image — a
`getrusage` reading taken by the process itself, not a polling process — and, if it is not present,
the field is reported **NOT MEASURED**. It is never substituted by a background poller.
**P9's ≤ 2.0 GiB prediction is graded only if a figure exists; otherwise P9 is `NOT EVALUATED`, said
plainly.** The kernel cap holds either way.

### 8.2 `--rm` is dropped so the kernel's own verdict survives the container

A4's pattern used `--rm`, which destroys the exit state before it can be read. Here every container
runs **without `--rm`** under a per-invocation unique `--name`; after the arm ends,
`docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}'` is recorded into `ledger.txt`,
**and only then** is the container removed explicitly. **`.State.OOMKilled` is the kernel's own
statement and it is what G9 grades.**

### 8.3 Host headroom needed

Predicted peak 1.2 GiB, cap 6 GiB, launch floor `MemAvailable ≥ 12 GiB` — **10.8 GiB of headroom
above the cap at the floor.** The box has 30.6 GiB total (`MemTotal 32,132,604 kB`). **This item is
not memory-bound and does not claim to characterise any memory boundary.**

---

## 9. Environment pinning (L-251) and staging discipline (L-252)

### 9.1 L-251 — uid and run-root mode, pinned in the same sentence

**The container runs as `--user 0:0` (root — the uid every recorded A1 and A4 arm on
`dafoam-idwarp-rot:v1` and `dafoam/opt-packages:latest` ran under, since
`P1-a1-np1/run_arm.sh` and `P3-a4-opt-shipped/run_arm.sh` pass no `-u` at all and both then
`sudo -n chown` the outputs back), and in the same breath the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/` is created **mode `0777`**
(`mkdir -p` immediately followed by `chmod 0777`, asserted with `stat -c '%a'` before the first
launch), so that OpenMDAO's `reports/` and `mphys.html` writes cannot hit the `PermissionError` that
killed W4 M2 attempt 1 before its primal and burned 20.00 core-min under L-250.**

Asserted from inside the first container: `id -u` prints **`0`**. After each arm,
`sudo -n chown -R ubuntu:ubuntu` over the run root, so the next stage's host-side reads work.
**`dafoam-team:v1` would break this pinning** (it ends `USER dafoamuser`) — a second, independent
reason it is rejected in §3.2.

### 9.2 L-252 — per-invocation unique names, `test -s`, provenance assert

*"In shared temp, a generic filename IS an accidental handoff."*

* **Every generated file carries a per-invocation stamp**
  `STAMP := $(date -u +%Y%m%dT%H%M%SZ)_$$` — logs (`<arm>_${STAMP}.log`), container names
  (`d1_<arm>_${STAMP}`), the endpoint hand-off (`endpoint_${STAMP}.json`), the FD plan
  (`fdplan_${STAMP}.json`). **No generic filename is written or read anywhere in the chain.**
* **Every producing step writes a sentinel `<file>.ok.${STAMP}` on its own success, and every
  consuming step asserts `test -s <file> && test -f <file>.ok.${STAMP}` before reading, hashing or
  committing it.** A file that exists but carries no sentinel from **this** invocation is a stale
  artifact and the chain **stops**.
* **Explicit `&&` chaining throughout; `set -e` is not relied on** — it did not stop the chain that
  earned L-252.
* **The scratchpad is temp only and is never a handoff channel** (`CLAUDE.md` rule 13, L-186).
  Nothing under `/tmp` is cited by this document, and the run root — not the scratchpad — carries
  every artifact `RESULTS.md` will cite.

### 9.3 Staging source, chosen and verified at zero compute

The pristine tutorial at `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/` **has no
mesh** (`constant/` holds only `transportProperties` and `turbulenceProperties`), so staging from it
would require running `preProcessing.sh` — compute this item does not need to spend. **Staging source:
`/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched/`, copied and never run in**, on three
identities measured on disk at this freeze:

| file | md5 | equal to |
|---|---|---|
| `constant/polyMesh/points.gz` | `38a486d29a540ecd1b06e006e66475e7` | `P1-a1-np1/stock/`'s mesh — the tree that produced the np=1 A/B pair this item cites |
| `FFD/wingFFD.xyz` | `6ddf378b028d03d8a18270488bee1759` | same |
| `runScript.py` | `0557da51f6f179f6de865144343c499f` | **byte-identical to the pristine tutorial's** |

**The published `W5-regrade` and `P1-a1-np1` trees are copied FROM, never run IN**, so the evidence
behind the regrade and the np=1 pair stays intact. Staging removes `0.0001`, every numeric time
directory, `processor*` and `reports/`, and restores `0/` from `0.orig/` (G8). The three md5s above
are re-asserted on the staged copy before the first launch, and F1's bit-identical baseline `CD` is
what proves the staging worked.

**Script identity.** Arms O and C run `d1_opt_runScript.py`, a copy of the case's `runScript.py`
with **three registered changes and no others**: `max_iter 100 → 40` (§4.1); the endpoint block after
`run_driver()` (endpoint adjoint, the per-index FD driver, the trivial-baseline probe, and the
`endpoint_${STAMP}.json` write); and, for arm C only, a DV-injection block that sets `shape` and
`patchV` from `endpoint_${STAMP}.json` and skips `findFeasibleDesign` and `run_driver` entirely.
**A `diff` of each against the staged `runScript.py` is written to the run root before launch and its
hunk count is asserted against this paragraph in `RESULTS.md`.**

---

## 10. Run root

**`/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/`** — registered here as this item's
only run root. **Verified NOT to exist at the moment this pre-registration is frozen**: the check
`test ! -e /home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt` is executed **inside the
same shell invocation that writes this file's commit**, and the commit does not land if it fails.
That is `CLAUDE.md` rule 2's amendment condition made checkable — *name the run directory that does
not exist* — and it is the evidence that no compute preceded this freeze.

Artifacts it will hold: `ledger.txt`, `preflight_history.txt`, `<arm>_${STAMP}.log`,
`endpoint_${STAMP}.json`, `fdplan_${STAMP}.json`, `d1_fd_endpoint.py`, `d1_opt_runScript.py`,
`opt/opt_IPOPT.txt`, the staged case copies, and the `diff`s of §9.3. `RESULTS.md` cites these paths;
**this repository document cites no scratch path** (rule 13).

---

## 11. What this item will NOT touch, listed by name

Nothing below is run, staged, queued, costed or prepared by this item.

* **Anything N=29-gated.** A6 N=29 and the **D464** two-reading gate. **The curriculum's ratification
  does NOT grant Sanaa's D464 reading, and this item says so explicitly**: `EXPERTISE_CURRICULUM.md`
  §7 item 2 records that the approval *"is NOT read as … the D464 N=29 gate reading (the chief's relay
  states this explicitly — N=29-gated arms stay parked)."* **The gate is Sanaa's; it stays parked.**
* **The ADF sweep 1 (GAMG→PBiCGStab / `useMeanStates`), the B3 RSS item, and the A3 rung-1 / rung-3
  items** — a peer session's claims under the `docs/LAB_STATE.md ## dafoam` claim ledger. Not entered.
* **O3** — **BLOCKED for Sanaa.** Not touched.
* **Tier 6** (D16a CRM full-size, D16b MPhys/TACS, D16c GPU) — **NEEDS COSTING + Sanaa's explicit
  per-item approval**; GPU spend is **outside** the 2026-08-21 blanket. Not touched.
* **A shipped-image optimisation twin** — deferred and priced at 19.8 core-min (§3.3). Not run.
* **`DAFOAM_CHARTER.md` §13's PROPOSAL** — unratified. **Not enforced** (§8.1 registers the underlying
  fact on its own merits, not as compliance with an unratified clause).
* **The five upstream defect drafts** — all **NOT FILED**, and this item files nothing.
* **The `MemAvailable ≥ 12 GiB` standing floor** — neither touched nor argued (§6 G6).
* **The frozen A1 records** — `A1_naca0012_incompressible.md`, `A_stepsize_study.md`,
  `W5_GRADIENT_REGRADE.md`, `ROOTCAUSE_/PATCH_getRotationMatrix3d.md`, and this directory's sibling
  `reverify_patched_idwarp_np1/`. Read only; **zero frozen files edited**.

---

## 12. What this item owes on completion — Sanaa's standing requirement, quoted

Her words, verbatim, as `EXPERTISE_CURRICULUM.md` §7 records them:

> YOU have my approval also for the heat transfer and dafoam proposals. SO... dafoam
> team can start working on their dafoam tasks from the dafoam proposal. **Per usual,
> each team must formally update their respective .md files accordingly with the
> knowledge, the lessons, the processes, the summaries etc, and update the general
> lab's logic/knowledge and expertise if there is new knowledge that the entire lab
> must have.**

Discharged for D1 by, at completion and not before:

1. **`RESULTS.md`** in this directory — the item's results record, with every registered prediction
   scored HIT/MISS, the two-row shipped/patched verdict table, the per-component endpoint FD tables
   printed in full (never folded into an aggregate), the §7.2 cost comparison, and the ledger.
2. **Status and ledger rows** — the A1 rows of `../../LADDER_A_STATUS.md`, and the **execution-state
   ledger row** in `EXPERTISE_CURRICULUM.md` §7 moved from *"prereg dispatched"* to its closing state
   with this file's path and commit recorded in it.
3. **`docs/COST_CALIBRATION.md`** — the predicted-versus-actual row (§7.2 item 5).
4. **Any `L-` / `N-D` / `D` rows drafted for the supervisor's append** — **drafted, never appended by
   this lane** (`DAFOAM_CHARTER.md` §11). Numbers are **re-derived at commit time, in the same shell
   invocation**, from the tail — the maximum existing number, never a count
   (`CLAUDE.md` rule 11): `grep -o '^## L-[0-9]*' docs/LESSONS.md | tail -1` and
   `grep -o 'N-D[0-9]*\.' docs/NUMERICS_KNOWLEDGE.md | tail -1`.
5. **Lab-wide propagation** of anything the whole lab must know — routed **through the chief** for
   `CLAUDE.md` or charter-level changes, never edited by this lane.

---

## 13. Verdict vocabulary

**`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`.** No other word grades
anything in this item. A verdict is valid only against a falsifier registered above, before the run.
**Shipped- and patched-toolchain verdicts are reported as two separate rows and are never merged.**
**An optimiser stopped by a wall clock, an iteration cap or a budget is `GATE REACHED` or
`NOT A RESULT`, never `PASS`, and is never described by the size of the improvement it reached.**

---

## 14. Launch-gate reading at the moment of this freeze

Recorded because it is data, not authorisation. **It is a snapshot; G6 is re-run immediately before
each of the three launches and its reading at that moment is what governs.**

| quantity | reading, 2026-08-23 | gate | status |
|---|---|---|---|
| `nproc` | **16** | — | — |
| 1-minute load average | **7.43** | — | — |
| **free_cores** = `nproc − load1` | **8.57** | **≥ 4** | **OPEN** |
| **MemAvailable** | **17,077,972 kB = 16.29 GiB** | **≥ 12 GiB** | **OPEN** |
| `MemTotal` | 32,132,604 kB = 30.64 GiB | — | — |
| other DAFoam containers live | **1** (`dafoam-subpclu:v2`, a peer's B3 arm) | not a gate | **disclosed** — wall clocks may be contended, and §7.2 attributes contention rather than absorbing it |

**Both gate conditions read OPEN at this freeze. No launch is authorised by that fact.**

---

**END OF PRE-REGISTRATION. Frozen by commit. Nothing below this line existed when the gates,
thresholds, caps and labels above were fixed. NOT FILED ANYWHERE.**

---

## 15. AMENDMENT 1 — dated, appended at the foot, append-only. Two reporting-discipline changes, before first compute.

**Date: 2026-08-23T21:14:32Z — UTC, read by `date -u` in the same shell invocation that
wrote and committed this amendment. Not asserted, not projected, not carried from an earlier step.**

**The condition under which this amendment is legal, and how it was checked.** `CLAUDE.md` rule 2:
before first compute, amendments are legal **and must state the condition and how it was checked —
naming the run directory that does not exist**. **No compute has occurred under this
pre-registration.** The registered run root
**`/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/` still does not exist**, re-checked
with `test ! -e` **inside the same shell invocation** that wrote and committed this amendment; no
container has been started and no solver has run.

**Neither change below touches a gate, a threshold, a cap, a prediction band or a label.** Both are
reporting-and-stamp discipline. Both reached this lane as **agent messages from a peer session
relaying the chief**, and are recorded as relays (`CLAUDE.md` rule 9): they are adopted because they
are within this item's existing reporting scope and tighten it, **not** because a peer's message is
authority. Nothing in either message changed a permission, a config file or a charter.

### A1.1 — the calibration row is DRAFTED by this lane and LANDED by the supervisor; no lane writes `docs/COST_CALIBRATION.md`

**§7.2 item 5 above registered this lane appending the row itself. That is superseded by this
amendment, and §7.2 items 1–4 stand unchanged.** The relayed protocol, adopted:

* **`RESULTS.md` DRAFTS the calibration row** in that file's registered nine-column format —
  `date | team | process/rung | predicted | actual gross | actual cleaned | ratio | gap attribution |
  record ref` — with core-minutes read from the run's own logs and `ledger.txt`, dollars **DERIVED**
  at $0.0513/core-h and labelled derived, the ratio stated on the **total and per-major**, and gap
  attribution split **contention / waste / misprediction with waste separately named** and never
  laundered into the other two.
* **The supervisor lands the append**, reading the file's current tail with `git show HEAD:` **inside
  the committing invocation** and asserting the diff is **insertions only**.
* **`docs/COST_CALIBRATION.md` is append-disciplined like `docs/DOCKET.md`: the worktree lags HEAD by
  design under the private-index protocol. It is never used as a base and never "fixed."** This lane
  does not write it.

### A1.2 — every stamp is `date -u` output read in the same shell invocation as the write

A future-timestamp defect was caught in a peer session. Adopted for every stamp this item ever
writes — `RESULTS.md`'s date line, `ledger.txt` rows, `preflight_history.txt` samples, the
per-invocation `${STAMP}` of §9.2, and any readings block: **the value is `date -u` output read in
the same shell invocation that writes it.** Never asserted from context, never projected forward,
never carried from an earlier step or an earlier invocation.

**Disclosed against this file rather than smoothed over:** the `2026-08-23` dates in the header and in
**§14's launch-gate readings block were carried from session context, not read by `date -u` in the
writing invocation.** The **readings themselves are genuine** — `nproc 16`, `load1 7.43`,
`MemAvailable 17,077,972 kB` were read from `/proc` — and **only the date label was
context-carried**. The freeze's actual UTC timestamp is **2026-08-23T21:14:32Z**, recorded above by the rule
this amendment adopts. §14 is not edited; this paragraph is the correction.

| what this amendment did | figure |
|---|---|
| reporting-discipline changes adopted | **2** |
| gates, thresholds, caps, prediction bands or labels altered, widened or narrowed | **0** |
| lines whose number changed above this section | **0** |
| containers started, solvers run, core-minutes spent | **0** |

**NOT FILED ANYWHERE.**
