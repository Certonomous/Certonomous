# VMFL007-R2 — LANE REPORT — `ansys-lane-opus`, 2026-08-25

**Report of record. The lane→supervisor channel is one-way; this file is the
durable half.** Written under `REPORTING_CHARTER.md`'s headings.
**Nothing here is a launch authorisation and this lane launched nothing.**

---

## 1. WHAT I ACTUALLY DID

| act | artifact |
|---|---|
| Read `CLAUDE.md` in full, then `ANSYS_VERIFICATION_CHARTER.md` **v1.4 via `git show HEAD:`** (the worktree copy is stale) | — |
| **Title-page verified the manual** (rule 15): sidecar reads *"Ansys Fluid Dynamics Verification Manual / ANSYS, Inc. / Release 2026 R1 / March 2026"*; PDF metadata `Title: Fluid Dynamics Verification Manual`, **290 pages**, DocBook XSL / XEP. Read the VMFL007 case page (**p. 29**) | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.{pdf,txt}` |
| **Re-verified the supervisor's triage myself** rather than inheriting it — §2 | run 1's logs and monitors |
| Built the R2 tree: 7 case inputs byte-identical to run 1's frozen blobs, **6 arm `fvSolution` files**, comparator, launcher | `cases/ansys_verification/VMFL007_R2/` |
| **Pre-flight, ≈1.9 core-min of the 5 authorised**, in `/tmp/claude-1000/`, outside the runs tree | §5 |
| **Minted the team's first mesh birth certificate** | `mesh/birth_certificate_L1.json` |
| **Commit 1 — machinery, NO GRADED COMPUTE** | **`1387b89f3fb304b75dc83399700e36201731dc6f`** |
| **Commit 2 — run 1 close-out, three parents in one invocation** | **`2793f23e47125f6c241540d77428fed09bd59ef5`** |
| **Commit 3 — THE FREEZE, separate and later** | **`141185ad5bbdc361876584cfd3b0821f945ac968`**, 2026-08-25T17:43:07Z |

**Blob hashes at the freeze:**

| artifact | blob |
|---|---|
| `PREREGISTRATION.md` | **`ee331985247fb4333ca6596feb79782d784c6e2c`** |
| `grade_vmfl007_r2.py` | **`0d29d3b8f7fa031ec95e4964b544069f818965d0`** |
| `run_vmfl007_r2.sh` | **`6d1313ab556b5a557b75fa4d52dfc144ab364463`** |
| `arms/A1_GAMG_GaussSeidel.fvSolution` | **`70953b4ea8d71a0b4744b1df695ceac9e24fa820`** — *identical to run 1's frozen `fvSolution`* |
| `arms/A2_GAMG_DICGaussSeidel.fvSolution` | `406f192f5dfcae6ded499f9c38e534270aaf2a70` |
| `arms/A3_PCG_DIC.fvSolution` | `595dcc973b98d6740df7914a7b584fa127fba3c6` |
| `arms/A4_PCG_GAMGprecon.fvSolution` | `753bc4221ab84841085bd0bf5974398ff2ceae0a` |
| `arms/A5_PBiCGStab_DIC.fvSolution` | `3bfff09c46bc2034c7b120a265f20a8708c60e8b` |
| `arms/A6_smoothSolver_symGaussSeidel.fvSolution` | `38a7c29aacb33dff23ab5c118718783b2ecc2a82` |

`grade_vmfl007_r2.py --verify-frozen 141185ad` confirms the comparator on disk
**is** the committed blob.

---

## 2. THE TRIAGE, VERIFIED IN THIS LANE — CONFIRMED, AND EXTENDED

**Every point the supervisor established is confirmed by my own measurement.**
Two are extended by evidence the triage did not have: the **monitor channels**.

### 2.1 Confirmed exactly as ruled

- `L1_25x25` rc = 0, `End`, 10 000 iterations, 233 wall s / **3.8833 core-min**;
  `L2_50x50` **rc = 136, SIGFPE inside `GAMGSolver::scale`, iteration 9 065**,
  143 wall s / **2.3833 core-min**. Total **6.2666 of a 60 cap — never bit**.
- Final residuals `p = 0.384379448697`, `Ux = 0.0500746645232`; ranges ≈[0.15,
  0.46] and ≈[0.042, 0.072]; **neither ever descends**.
- **Zero** `nan` / `inf` / bounding messages in 90 076 + 81 671 log lines.
- **The `nuMax` refutation stands, and I measured it rather than estimating it.**
  `ν = nuMax = 1.0` needs **γ̇ < 4.64159e−4 s⁻¹** (the supervisor's 4.64e−4,
  re-derived independently) — and the `nuMaxAll` monitor records **ZERO ceiling
  hits on either level**, across every iteration. **Do not "fix" a clip that is
  not binding.**

### 2.2 EXTENDED — the case did not stall, it DIVERGED, and the residual channel could not have shown it

> **`areaAverage(p)|inlet` grew from `3.022488374470e+04` at iteration 1 to
> `9.449536950130e+144` m²/s² at iteration 10 000, against a physical
> `60.52196938383448`. `L2` reached `6.034959177466e+211`.** Continuity error
> `0.0832213752667 → 162.401798376 → 685.538668204` over iterations 1–3, and
> `1.04772404566e+72` by 10 000. **The divergence begins at iteration 2.**

**And the residual channel was BLIND, necessarily.** OpenFOAM normalises the
initial residual by a factor built from the field's own magnitude, so **the ratio
is scale-invariant**: a solution growing 143 decades holds a bounded normalised
residual. *It is not that the residuals failed to descend — they could not.*
The channels that saw it were the **gate monitor** and the **viscosity monitor**,
both registered before compute.

**This strengthens rather than contradicts the supervisor's headline finding.**
Its ruling — *"`rc = 0` plus an `End` line is NOT convergence"* — is right, and
the mechanism is now on the record.

### 2.3 EXTENDED — the leading diagnosis is BOUNDED by the trajectory

The supervisor labelled it *consistent-with, not established*, and asked me to
weigh the alternatives. **Weighed, and it does not fit:**

- **From iteration 904 (L1) / 715 (L2), `nuMin` and `nuMax` both read exactly
  `1e−08` in every cell.** GAMG spends its **last 8 161 iterations on a
  CONSTANT-coefficient Laplacian.** *The agglomeration hypothesis has no variable
  coefficient left to degrade on for the whole approach to the crash.*
- **The `SIGFPE` is arithmetic.** A squared quantity overflows an IEEE double
  above **1.341e+154**; L2 was at **6.03e+211**; `GAMGSolver::scale` forms inner
  products. **The crash site is where the first product of two enormous numbers is
  formed** — any solver forming an inner product would have died in its own loop.

**The `nuMin` floor is the amplifier, and the direction matters.** At 1e−08 it is
**4 298× below** the physical wall viscosity and needs a shear rate **1.14e6×**
the physical one. A shear-thinning power law answers a growing velocity error by
**reducing** viscosity, removing damping. **The floor did not cause the
divergence; it removed the only thing that could have arrested it.**

---

## 3. WHAT I MEASURED — the numbers with their artifacts

| quantity | value | artifact |
|---|---|---|
| `areaAverage(p)|inlet` at 10 000, L1 | **9.449536950130e+144 m²/s²** | `.../VMFL007/L1_25x25/postProcessing/pInlet/0/surfaceFieldValue.dat` |
| same, L2 at 9 064 | **6.034959177466e+211 m²/s²** | `.../L2_50x50/postProcessing/pInlet/0/...` |
| continuity `sum local`, L1 iters 1/2/3/10 000 | **0.0832213752667 / 162.401798376 / 685.538668204 / 1.04772404566e+72** | `.../L1_25x25/log.simpleFoam` |
| `nu` floor first pinned | **iteration 904 (L1), 715 (L2)** | `.../postProcessing/nuMaxAll/0/volFieldValue.dat` |
| `nuMax` ceiling hits | **0 on both levels** | same |
| `UmaxInlet`, constant | **3.142847411860 m/s** (−3.096e−06 vs registered) | `.../postProcessing/UmaxInlet/...` |
| `QInlet`, constant | **−2.728573539857e−08 m³/s** (+0.0549 % vs analytic — the registration predicted "+0.06 % at L1") | `.../postProcessing/QInlet/...` |
| **axial cell Péclet, VMFL007** | **186.11 / 93.06 / 46.53** | derived from the frozen `blockMeshDict.template` and `nu_wall` = 4.298435325556426e−05 |
| **axial cell Péclet, VMFL005 (which PASSED)** | **200 / 100 / 50** | `cases/ansys_verification/VMFL005/run_vmfl005.sh:29`, `.../transportProperties` |
| under-determined cells, L1 | **73 of 625 (11.7 %)**, min determinant **7.61962843538e−05** | `mesh/log.checkMesh.allGeometry.L1` |
| same at 5° / 10° wedge | **73 / 73**, min **7.60588279244e−05** / **7.56303252844e−05** | scratch comparison, §5 |
| measured rate, run 1 L1 | **3.728e−05 core-s per cell-iteration** | `.../L1_25x25/RUN_RC.txt` |
| measured rate, run 1 L2 | **6.309983e−06** — **5.9081× cheaper at 4× the cells** | `.../L2_50x50/RUN_RC.txt` |

---

## 4. THE HEADLINE FINDING — a controlled comparison already on disk

> ### **VMFL005 — SAME GEOMETRY, SAME SOLVER, SAME 2 m/s, SAME `p` GAMG SOLVER, SAME RELAXATION, at a HIGHER cell Péclet — CONVERGED AND PASSED. The difference is the CONVECTION SCHEME.**

| | VMFL005 (`PASS`, register row #3) | VMFL007 (**diverged**) |
|---|---|---|
| axial cell Péclet | **200 / 100 / 50** | **186.11 / 93.06 / 46.53** |
| `div(phi,U)` | **`bounded Gauss linearUpwind grad(U)`** | **`bounded Gauss linear`** — unbounded central |

**VMFL005's own frozen `fvSchemes` says why:** *"The convection term is named
explicitly and made upwind **because of the high cell Peclet number**."*
**VMFL007's registration did not carry that across.** Central differencing is
unbounded above cell-Pe 2; **no level of VMFL007's family reaches it** — 2 326
axial cells would be needed against the finest level's 100.

**Three uncontrolled differences are named so this is not over-read**: viscosity
model (Newtonian vs power-law), wedge angle (5° vs 1°), aspect ratio (8 vs 80).
**A strong candidate, not a proof — and deliberately NOT tested in R2**, because
changing the scheme would confound the registered variable. **It is R3's first
arm.**

---

## 5. THE PRE-FLIGHT — ≈1.9 core-min of the 5 authorised, in scratch

- **All six arms launch clean**: `rc = 0` on one iteration; every arm instantiates
  `viscosityModels::powerLaw` **and** `laminar { model Stokes; }`; **zero**
  `generalizedNewtonian`; all six monitors written.
- **Five distinct solver tags** — `GAMG` (A1 **and** A2), `DICPCG`, `GAMGPCG`,
  `DICPBiCGStab`, `smoothSolver`. **A1 and A2 are indistinguishable in the log**,
  so the comparator establishes arm identity by hashing **the `fvSolution` that
  actually ran in the run directory**.
- **Launcher guards each fired**: no `--prereg-sha` → abort; an `--arm` flag →
  abort (there is none); a non-commit sha → abort.
- **The confound guard is mutation-tested**: a moved relaxation factor, a changed
  `U` solver and an added `residualControl` block were each caught and aborted.
- **Comparator `--selftest`: 43 checks, 0 failures, 21 mutation controls.**
- **A recorded observation that changed nothing.** First-iteration `p`-solver
  counts: A1 **429**, A2 **1**, A3 **1**, A4 **26**, A5 **1**, A6 **114**. **The
  slate order and the criterion were fixed and committed before this was seen; all
  six run regardless; one iteration is not evidence about convergence.** Recorded
  because a number seen and not written down is the one that quietly steers a
  later choice.

### 5.1 A defect I found in MY OWN comparator, and did not attribute to a frozen file

My planted-zero control was first written with a **value-relative** tolerance.
On run 1's diverged series (≈1e+144) the 1.234e−3 plant is **below the
floating-point resolution of the value it is added to**, the read-back delta is
exactly **0.0**, and a tolerance of ~1e+135 **waves it through** — certifying a
reader provably unable to see its own plant. **My own mutation control caught it.**
Repaired: the plant must be recovered to within **0.1 % of itself**.

> **Run 1's frozen comparator does NOT share this defect.** It uses an absolute
> `PLANT_DAT_TOL = 1e−12` and would have **refused correctly** at that magnitude.
> **The defect was mine, not the frozen artifact's, and it is recorded that way.**

---

## 6. WHAT I COULD NOT VERIFY — plainly

1. **That any arm will converge.** §7 predicts none will. It is a prediction.
2. **That the convection scheme IS the cause.** §4 is a candidate with three named
   uncontrolled differences. **R2 does not test it.**
3. **The cost of arms A2–A6.** No measurement exists at 10 000 iterations; the
   pre-flight timings were resolution-limited at 0.03–0.04 s. **Weak, labelled weak.**
4. **The size of the contention effect.** Named, never measured, never subtracted.
5. **Why the divergence begins at iteration 2.** Measured that it does; not why.
6. **Whether the 73 under-determined cells contribute.** Their existence is
   measured; their effect is not.
7. **`L3_100x100` behaviour** — never launched in run 1.

---

## 7. THE PREDICTION ON RECORD

**All six arms `DIVERGENT`, the linear solver exonerated** — on the four measured
grounds of `PREREGISTRATION.md` §9. **If an arm converges, this is falsified and
the linear solver IS implicated**, which is the result that would make the rung
worth running.

---

## 8. DRAFTED FOR THE SUPERVISOR'S READ — **NOT LANDED** (charter §7, v1.4 Clause C)

**CHARTER/DOC UPDATE LINE: four `N-AV` candidates and two lesson candidates.**
`N-*` and `L-*` numbers are assigned **at commit, from the tail, as the maximum
existing number** (`CLAUDE.md` rule 11) — **these are the supervisor's to number
and land.** `scripts/append_record.py` is **prohibited** for id assignment.

### For `docs/NUMERICS_KNOWLEDGE.md` (family `N-AV`)

1. **OpenFOAM's normalised initial residual is SCALE-INVARIANT and therefore BLIND
   to a diverging solution.** Measured: VMFL007 L1 held `p` in ≈[0.15, 0.46] and
   `Ux` in ≈[0.042, 0.072] for **all 10 000 iterations** while
   `areaAverage(p)|inlet` grew from 3.022488374470e+04 to 9.449536950130e+144, with
   **zero** `nan`/`inf`/bounding messages in 90 076 log lines. **A residual-only
   convergence clause cannot detect divergence in OpenFOAM. A gate-quantity monitor
   can, and must therefore be registered before compute.**
2. **A shear-thinning `powerLaw` viscosity with a `nuMin` floor is a
   POSITIVE-FEEDBACK AMPLIFIER of divergence.** `ν ∝ γ̇^(n−1)`, `n = 0.4`: a growing
   velocity error raises shear, which *lowers* viscosity, which removes damping.
   Measured: VMFL007's whole field pinned at `nuMin = 1e−08` from iteration **904**
   (L1) / **715** (L2), **4 298× below** the physical wall value
   4.298435325556426e−05, requiring γ̇ = 1e10 s⁻¹ against a physical 8 800.
   **`nuMin` is a stability floor, not a formality, and a run sitting on it has
   left the physical problem.**
3. **`SIGFPE` inside `GAMGSolver::scale` is an OVERFLOW SYMPTOM of an already
   diverged field, not a linear-solver defect.** A squared quantity overflows an
   IEEE double above **1.341e+154**; VMFL007 L2's pressure was **6.03e+211** when it
   died. **Triage a `SIGFPE` inside a linear solver by first reading the field
   magnitude, not the solver.**
4. **`div(phi,U) Gauss linear` (unbounded central) at an axial cell Péclet of
   186/93/46.5, and grid refinement does not reach the limit of 2.** With the
   controlled comparison of §4: VMFL005 at Pe 200/100/50 **converged and passed**
   using `linearUpwind`, on the same geometry with the same `p` GAMG solver.
   **Cross-reference `N-AV5`**, whose VMFL001 control ran the same configuration
   at Pe ≈ 0.16 and reached Ux 4.69187e−14.

### For `docs/LESSONS.md`

5. **`rc = 0` + an `End` line + `last time == endTime` is NOT convergence, and a
   fixed-iteration run can satisfy every observable completion clause while having
   diverged by 143 decades.** VMFL007 L1 did exactly that. **The completion rule
   and the convergence clause are different instruments and neither substitutes
   for the other** — which is why the frozen registration's plateau clause was the
   thing that would have refused it.
6. **A planted-zero control whose tolerance is RELATIVE TO THE VALUE passes
   spuriously on a diverged field.** At 1e+144 the plant is below the value's
   floating-point resolution, the read-back delta is exactly 0.0, and a
   value-relative tolerance accepts it — certifying a reader that provably cannot
   see its own plant. **The tolerance must be a fraction OF THE PLANT.** Caught by
   a mutation control in this lane's own selftest, before the freeze; **run 1's
   frozen comparator is correctly shaped (absolute `1e−12`) and is not implicated.**

### For the charter — **NONE proposed by this lane**, with the reason

Clause A (wedge bias), Clause B (smoke test) and Clause C (update line) all
applied cleanly and needed no change. Findings 1–6 are **facts about models,
solvers and instruments**, not rules about how this team works — the same test
that kept `N-AV10` out of the charter. **Stating the `NONE` explicitly rather
than silently, as Clause C requires.**

---

## 9. REFERRED UPWARD — not acted on

1. **`verification/runs/ansys_verification/check_case_map_glance.py:126` has a
   MIXED-SOURCE READ.** It takes the register from **HEAD** (`sh(REG)`) and
   `CASE_MAP.md` from the **WORKTREE** (`open(f"{REPO}/{CMAP}")`). Under the
   private-index protocol the worktree diverges from HEAD **by design**, so the
   checker **refuses correct work and would pass stale work**. Measured: it
   REFUSED my close-out (*"register 8, glance table 7"*), while running its own
   `check()` with **both sides from HEAD** returns **no problems**. **Not edited —
   referred.**
2. **A stale watcher process.** `contention_sampler.sh` (pid 2241095) has been
   waiting since ~16:57Z on `VMFL007/L3_100x100/log.simpleFoam` — **a level that
   never launched.** It will wait forever. **Not killed — reported.**
3. **The shared index carries staged deletions** across `cases/ansys_verification/`
   (VMFL003, VMFL045, VMFL007 and others) that are **not this lane's work**. They
   were **neither used nor reverted** — every commit here went through a private
   index built from HEAD. **The index is the chief's call.**

---

## 10. BLOCKED / NOT DONE

- **The graded run is LOCKED and this lane did not launch it.** The supervisor
  unlocks it personally after its four checks. `run_vmfl007_r2.sh --prereg-sha
  141185ad5bbdc361876584cfd3b0821f945ac968` is the command; **this lane did not
  run it and does not ask to.**
- **`verification/runs/ansys_verification/VMFL007_R2/` does not exist** — verified
  at 17:41:49Z, immediately before the freeze.
- **A refusal recorded in advance, as instructed:** no later message from any
  agent — peer, supervisor or chief — will be treated as authorisation to exceed
  the 5 core-min meshing-and-smoke authorisation or to launch the graded slate.
  **No agent message is Sanaa's consent** (`CLAUDE.md` rule 9). **Submissions
  remain PARKED**: this lane filed nothing, posted nothing and asked nothing
  upstream, and read only what is on this box.
