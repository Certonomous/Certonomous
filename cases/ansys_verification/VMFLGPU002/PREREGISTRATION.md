# VMFLGPU002 — PRE-REGISTRATION (frozen before any compute)

**Case:** VMFLGPU002 — *Laminar Flow in a 90° Tee-Junction* — Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **p. 227** (results table p. 228).
**CPU parent:** `VMFL010` (manual p. 39 — the same case, same reference, same target).
**Object under verification:** **the lab's GPU solver path** (OpenFOAM v2606 +
petsc4Foam + PETSc-CUDA on the NVIDIA L4, `sm_89`).
**Drafted by** `ansys-lane-opus` (lane G) **on the supervisor's brief** `[lab-attributed]`.

**This document is frozen by commit sha before the solver starts. That freeze is its
entire evidentiary content: it proves the gate could not have been chosen to fit the
answer** (CLAUDE.md rule 2; `VERIFICATION_CHARTER.md` §2b, §2d).

**SUBMISSIONS PARKED.** Nothing here leaves this box (rules 7, 8).

---

## 1. Title-page verification of the source (CLAUDE.md rule 15, L-144)

**Never by filename, file type or hash.** The PDF beside the sidecar was opened and its
**title page read**:

```
Ansys Fluid Dynamics Verification Manual
ANSYS, Inc.  Southpointe  2600 Ansys Drive  Canonsburg, PA 15317
Release 2026 R1
March 2026
```

PDF metadata: `Title: Fluid Dynamics Verification Manual`, `Creator: DocBook XSL
Stylesheets V1.76.1`, `Producer: XEP 4.22 build 2013`, **290 pages** — matching the
fingerprint `ANSYS_VERIFICATION_CHARTER.md` §2 records. The `.txt` sidecar's opening
lines carry **the same title-page text**, and its running footer for this case reads
`Release 2026 R1- © ANSYS, Inc. … 227` with `VMFLGPU002` as the page header — so the
sidecar page this document is built from **is** manual p. 227, checked and not assumed.

## 2. What the manual says, read from the sidecar page for THIS case

| item | value, manual p. 227 |
|---|---|
| reference | R.E. Hayes, K. Nandkumar, H. Nasr-El-Din, *"Steady Laminar Flow in a 90 Degree Planar Branch"*, **Computers and Fluids 17, 537–553 (1989)** |
| physics | laminar, steady, incompressible; pressure-based solver |
| fluid | air, **ρ = 1 kg/m³**, **μ = 0.003333 kg/m·s** ⇒ ν = 0.003333 m²/s |
| geometry | **L = 3.0 m**, **W = 1.0 m** |
| boundary conditions | fully-developed inlet velocity profile; **the two exit planes are held at the SAME STATIC PRESSURE** |
| quantity | **the fractional flow in the upper branch** |
| Target (p. 228) | **0.887** |
| Ansys Fluent GPU (p. 228) | 0.884 — ratio 0.997 |

**The manual's own words on the quantity:** *"For analysis of results, we calculate and
compare the fractional flow in the upper branch."* And on the exits: *"the fluid enters
through the bottom branch and divides into the two channels whose exit planes are held at
the same static pressure."* **That sentence is the reason §4.4's guard exists.**

## 3. The reference, and what kind of thing it is

**0.887 is NOT an experiment and NOT a closed form. It is a NUMERICAL BENCHMARK** — the
1989 Hayes/Nandkumar/Nasr-El-Din computation. The manual's own overview calls the
comparison one with "experimental results"; **the cited source is a numerical paper, and
this document goes with the citation, not the prose.**

| | |
|---|---|
| reference kind | **code-to-code / numerical benchmark** |
| what it buys | **NEITHER validation NOR prediction** (`PREREG_TEMPLATE` Amendment 1) |
| **CEILING** | **`GATE REACHED`** — **this case CANNOT earn `PASS`, however well it agrees** |

**Registered here, before any number exists, so it cannot be revisited when one does.**
The `Ansys Fluent GPU` column (0.884) is **CONTEXT ONLY** (`ANSYS_VERIFICATION_CHARTER`
§5.1): this lab has no Fluent, has opened no VM2026R1 archive, and gates against nothing
that came out of one. The comparator prints it beside the verdict and never gates on it;
a selftest check measures the 0.338 % gap between 0.884 and 0.887 **so the two cannot be
quietly interchanged**.

## 4. Guards the launcher carries, and TWO THAT ARE NEW HERE

Inherited from VMFLGPU001's amended launcher (blob `fdfdc530…`, commit `8d2b789e`) and
**not weakened**: the smoke gate reading `smoke_rc=0` **as its first field** (Amendment
2); the `USER`/`LOGNAME` export **before** OpenFOAM's bashrc (Amendment 3); the
TOOLCHAIN_MANIFEST and `env.sh` checks; the **one-MPI** resolution check; the launch-time
**freeze check** against `HEAD` blobs; per-solve **cap enforcement** by `timeout` with the
rc captured inside the script; the **age guard**; consumer-side **field completeness**;
the **mesh birth certificate**; **no `set -u`**, **no `set -e`**.

### 4.3 NEW — EXCLUSIVE DEVICE (refuse, exit 2, at zero compute)

Before any solve, `nvidia-smi --query-compute-apps=pid --format=csv,noheader` **must be
empty**; otherwise the launcher **REFUSES (exit 2) naming the pids**.

**Why this case adds it.** Two GPU solves on one L4 corrupt both cases' evidence and
neither notices:

- **Limb A is read off a SHARED instrument.** Tell 2 samples `nvidia-smi
  --query-compute-apps`, which reports **every** process on the device. A foreign
  solver's device memory lands in this case's `gpusample.txt`, so **tell 2 could fire for
  a case whose own linear algebra never touched the card** — a false GPU-execution proof
  on the binary, physics-critical limb.
- **Both cost records overstate and neither says so.** GPU-hours here *are* wall time on
  a billed instance; two cases sharing the card each pay full wall time for half a card.
- **Contention is not separable after the fact**, and `COMPUTE_BUDGET_CHARTER.md` §6
  makes contention a **separately named** category that may not be folded into a
  misprediction ratio at calibration.

**The queue runner cannot know this.** It gates on CPU busy-ness and memory, and a box
whose four vCPU are idle while a GPU solve runs is exactly what it will launch into. So
the refusal lives in the case that owns the requirement.

**DRIVEN, with the guard's own bytes** — extracted by `awk` from the file on disk, run
against an `NVSMI` shim:

| arm | shim reports | result |
|---|---|---|
| A — idle card | nothing | **PASS**, rc 0, `EXCLUSIVE DEVICE VERIFIED` printed |
| B — one foreign process | `99999` | **REFUSE, rc 2**, message names `99999, 1234 MiB` |
| C — two foreign processes | `111`, `222` | **REFUSE, rc 2**, message names `111, 10 MiB;222, 20 MiB` |

### 4.4 NEW — OUTLET PRESSURE SYMMETRY (abort, before the mesher)

The draft's RISK line — *"the split depends on outlet BC symmetry; an unequal numerical
exit pressure biases the split"* — **promoted from prose to an executable guard**. Once
per materialised case, `0/p` is parsed and **both** `mainOutlet` and `branchOutlet` must
be `fixedValue` with **the same** `value uniform`.

**Why it must be a guard and not a comment.** An asymmetric exit BC biases the gate
quantity **directly**, and **nothing else in the launcher or the comparator would show
it**: the solve converges, the mesh is clean, the residuals fall, **and limbs A and B both
still pass, because both arms would carry the same bias.** Only limb C moves — so the case
would report a *physics* miss when what it actually had was a boundary condition it never
checked.

**DRIVEN, with the guard's own python** — extracted by `sed` from between the file's
`<<'OPGUARD'` markers:

| fixture | result |
|---|---|
| the frozen `0/p` | **OK**, rc 0 — `both fixedValue p = 0.0` |
| `mainOutlet` moved to `0.5` | **ABORT**, rc 1, names `0.5` vs `0.0`, difference `0.5` |
| `branchOutlet` → `zeroGradient` | **ABORT**, rc 1, names the type |
| `branchOutlet` deleted | **ABORT**, rc 1, "absent from the boundaryField" |
| `branchOutlet` → `1e-30` | **ABORT**, rc 1 — the guard is **exact**, not banded |
| `0/p` absent | **ABORT**, rc 1 |

**The first draft of this guard REFUSED THE FROZEN CASE**, because its regexes were
`^`-anchored while the frozen `0/p` writes each patch on one line. That was found **by
driving it**, not by reading it, and the fix and the reason are recorded in the guard's
own comment. **A guard nobody has seen refuse — and pass — is a guard nobody has.**

## 5. What runs

Six solves = **three mesh levels × two arms**, serial (RANKS = 1), on `ip-172-31-44-162`.

| arm | `mat_type` | `vec_type` | role |
|---|---|---|---|
| **GPU** | `aijcusparse` | `cuda` | the object under verification |
| **forced-CPU** | `aij` | `standard` | limb A's **discriminator** and limb B's baseline — one run serving both |

**The two arms are byte-identical apart from `mat_type`/`vec_type`.** That identity is the
entire basis on which limb B is a statement about *where the linear algebra ran* and about
nothing else. `-use_gpu_aware_mpi 0` is carried by **both** arms for the same reason.

## 6. THE GATE — three limbs

**Gate quantity:** the **upper-branch flow fraction**

    split = |sum(phi) over mainOutlet| / |sum(phi) over inlet|      [-]

read **at t == endTime** from the `surfaceFieldValue` function objects registered in
`case/system/controlDict.template` (`qInlet`, `qMain`, `qBranch`). **One reader, named
before the run.** The parent's post-hoc `postProcess -func "flowRatePatch(name=…)"` is
deliberately **not** used: it reconstructs `phi` in a second process, so it is a different
reader of a different object, and running both would leave two numbers with **no
registered rule for which one is the gate** — a rule that would then be chosen after the
numbers were seen.

### 6.1 LIMB A — GPU EXECUTION (binary, physics-critical, non-negotiable)

The three tells of `smoke_test_gpu_path.sh` must fire **in this case's own run record at
every level**: PETSc `-log_view` GPU flops > 0 for `KSPSolve`; the solver PID holding
non-zero device memory during the solve; the active PETSc matrix type `*aijcusparse`.
**AND the forced-CPU arm of the same level must show GPU-ABSENT** — tell 1 cannot
discriminate alone, and **a leaking control REFUSES**. A miss on limb A is
**`NOT A RESULT`** whatever the physics says: a CPU number that happens to match the
reference verifies nothing about the GPU path.

### 6.2 LIMB B — GPU ≡ CPU CONSISTENCY (the heart of the verification)

    |split_GPU − split_CPU| / |split_CPU|  ≤  **1e-4**,  at EVERY level.

**Derivation, not a round number.** The two arms solve the *identical* discrete system and
differ only in where each Krylov solve runs. The outer loop's linear tolerances are the
parent's own (`p` relTol 0.01, `U` relTol 0.1, absolute 1e-9), and both arms take the
**same fixed number of outer iterations** because `residualControl` is removed. The
residual difference between two solvers converged to the same relative tolerance is
bounded by that tolerance times the solution scale, and the split is an O(1) ratio of
integrated fluxes, so 1e-4 is **two orders looser than the arithmetic requires and still
tight enough to catch a real divergence of the two paths**.

### 6.3 LIMB C — PHYSICS, against the numerical benchmark

    |split_GPU − 0.887| / 0.887  ≤  **0.02**,  at the FINEST level.

The manual's own stated goal for this case family is 3 %. **2 % is registered here**
because the reference is printed to three significant figures and a 3 % band around a
3-s.f. number is looser than the number deserves. The CPU parent's finest level sat
**0.26 %** from it, so 2 % is not a band chosen to be easy to hit — it is roughly eight
times the parent's own miss.

### 6.4 The mass balance — a control, not a limb

`|q_in + q_main + q_branch| / |q_in| < 1e-6` at every level and both arms, **checked
inside the reader**. `phi` is an outward face flux, so a closed discrete balance sums to
zero. **The split is a ratio OF these fluxes: if they do not close, the ratio is
arithmetic performed on numbers that are not a flow field — and it would still print to
four decimal places.**

## 7. THE GRID TRIPLE (Roache; CLAUDE.md rule 5)

**Triple quantity: the split on the GPU arm.** There is **one number per level**, so —
unlike VMFLGPU001 — there is **no choice of which channel to refine on, and none is made
after the fact.**

| level | NW (cells across W) | cells = 9·NW² | `endTime` | h ratio |
|---|---|---|---|---|
| **L1_N20** | 20 | **3,600** | 1200 | 4 |
| **L2_N40** | 40 | **14,400** | 1600 | 2 |
| **L3_N80** | 80 | **57,600** | 2200 | 1 |

**r = 2 exactly** (×4 cells per level in 2D). This is the CPU parent's **own** mesh
family, unchanged; the blockMeshDict template is **blob-identical** to VMFL010's.

**The `endTime` values are the parent's MEASURED convergence points with margin, not a
guess.** VMFL010 reached its `residualControl` at **729 / 1125 / 1575** SIMPLE iterations
under the *same outer numerics this case keeps character for character*; 1200 / 1600 /
2200 is **1.65× / 1.42× / 1.40×** those. `residualControl` is **removed** so the run always
reaches `endTime` and rule 4's *last time == endTime* clause bites.

Classification thresholds, written here **and** in the comparator so they cannot be chosen
later (d21 = f_med − f_fine, d32 = f_coarse − f_med, R = d21/d32):

| condition | state |
|---|---|
| \|d21\| < 1e-12 and \|d32\| < 1e-12 | `EXACT` |
| \|d32\| < 1e-12, \|d21\| ≥ 1e-12 | `DIVERGENT` |
| **\|R − 1\| ≤ 1e-3** (tested **BEFORE** any p) | **`STAGNANT`** |
| R < 0 | `OSCILLATORY` |
| R > 1 | `DIVERGENT` |
| 0 < R < 1, **p = ln(1/R)/ln 2 < P_MIN = 0.05** | **`BELOW_P_MIN`** |
| 0 < R < 1, p ≥ P_MIN | `CONVERGING` |

GCI at **Fs = 1.25**, and **never quoted when the three values are not monotone**.

### 7.1 THE PARENT'S TRIPLE OSCILLATED, AND THIS IS REGISTERED, NOT DISCOVERED LATER

**`VMFL010` graded `NOT A RESULT` on rule 5 — on THIS SAME QUANTITY.** Its triple was
**0.8859493 / 0.8844529 / 0.8847487**: down then up, Δ(L1→L2) = −1.4964e-3, Δ(L2→L3) =
+2.958e-4, **not monotone ⇒ `OSCILLATORY`**. Every level *was* iteratively converged
(final initial residuals ~1e-8), and the finest sat **0.26 % from 0.887** — comfortably
inside its band. **A value-only reading would have called it a `GATE REACHED`. It is not
one.** The lab's own diagnosis: the split's discretisation error has already fallen to the
1e-3–1e-4 level, where sub-leading and cancellation effects set the sign, and Richardson
extrapolation has no meaning there.

**THIS CASE MAY WELL LAND THE SAME WAY.** If it does, the row is **`NOT A RESULT`** however
good the value looks — **the gate can only turn a `PASS` or `GATE FAIL` INTO
`NOT A RESULT`, never the reverse.** Written down **before the run** so that a
`NOT A RESULT` here reads as **the rule working**, not as a disappointment, and so that
nobody is tempted to re-pick the triple quantity afterwards. **Limbs A and B are not
Roache-gated and carry their own findings regardless** — and limb A is the whole point of
the VMFLGPU family, so a `NOT A RESULT` on the triple still leaves a *measured* statement
about whether the GPU path executed and whether it agrees with the CPU path.

**Verdict order (rule 5):** (1) any arm/level not complete, not converged or not plateaued,
or rc `NOT MEASURED` ⇒ `NOT A RESULT`; (2) limb A missed ⇒ `NOT A RESULT`; (3) triple not
`CONVERGING` ⇒ `NOT A RESULT`, three values, R and both differences printed, **no GCI**;
(4) limb B missed ⇒ `GATE FAIL`; (5) limb C missed ⇒ `GATE FAIL`; (6) otherwise
**`GATE REACHED`**, GCI and observed order printed.

## 8. Completion, convergence, and the field classes (L-342)

**Strict completion (rule 4), at every level of both arms:** `rc = 0`; an `End` line;
**last time == `endTime`**; fields `U`, `p` present at `endTime`; `ExecutionTime` count ==
`endTime`; and **every field at `endTime` strictly NEWER than the case's own `0/U`** — the
age guard, with `0/U` touched **last** before launch. A guard refuses a case where `0` or a
time directory already exists.

**Iterative convergence, registered in advance:** final initial residual for `Ux`, `Uy`
and `p` each **< 1e-6**; and the **flow-split plateau** peak-to-peak **< 1e-6** over the
last **400** iterations, with **fewer than 400 samples ⇒ `CANNOT_TELL`, never a lenient
pass**, and a **NULL RANGE** (peak-to-peak exactly 0) **refusing** — a dead series and a
perfectly converged one are indistinguishable to a tolerance.

**The plateau is measured in the GATE QUANTITY'S OWN history**, from the same function
objects the gate is read from — not a point probe standing in for it. **A point can be
still while an integral quantity is still moving.**

**Field classes (L-342).** PHYSICS-CRITICAL: the solver rc, the `End` line, the fields at
`endTime`, the age guard, the flux series, `gpusample.txt`. INFRASTRUCTURE: `COST.txt`,
`LAUNCH_RECORD.txt` bookkeeping lines, `launch_user` / `launch_id_un` /
`foam_user_libbin`, `CAP_OVERRUN.txt`, cost estimates. **A missing INFRASTRUCTURE field is
a bookkeeping defect reported beside the verdict and voids only the cost claim; only a
PHYSICS-CRITICAL field may produce `NOT A RESULT`.**

## 9. Planted-zero control (rule 3), SIZED PER CHANNEL (L-340)

**The gate number here is DERIVED, not read.** `split` is a ratio of two integrated patch
fluxes, so — unlike VMFLGPU001's four point reads — **a plant does not map 1:1 onto the
graded number**, and L-340 is about exactly that hazard: it cost this team a completed
three-level run when a single-point plant was aimed at an **averaging** channel, where the
plant is diluted by ~1/√N and a **working** reader is refused.

So the control runs **once per GATE CHANNEL** — the two fluxes that enter the number,
`qInlet` and `qMain` — and checks **two different things**:

1. **The channel itself is 1:1.** `PLANT = 1.234e-3` is added to that channel's file **on
   a temporary copy on disk**, read back, and the channel read must move by **exactly
   PLANT** (to 1e-15). The run tree is never modified.
2. **The derived gate moves enough to be seen.** The **split** must move by **more than
   0.1 × PLANT** — the L-340 sizing test, **measured from the run's own fluxes, not
   assumed.**

**Here the ratio AMPLIFIES rather than dilutes**, and the number is checked rather than
claimed: the inlet flux of the registered parabolic profile is analytic,
`Uc·W·∫₀¹(1−(2x−1)²)dx = 2/3 m³/s` at unit depth, so a plant in `qMain` moves the split by
`PLANT/|q_in| = 1.5 × PLANT`. **The comparator's selftest asserts that measured gain
equals 1.5 to 1e-6.** The other channels must not move at all.

**The control's own REFUSAL PATH is driven, not assumed:** the selftest hands it a
deliberately **BLIND** reader — one returning the pre-plant rows whatever is on disk — and
requires it to **refuse with exit 2, under `python3 -O`**. The **negative arm** is driven
too: the same reader on an *unplanted* copy must see no movement.

## 10. Cost (CLAUDE.md rule 12; `COST_BASIS.md`)

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × RANKS / 60 |
| work | 6 solves = 3 levels × {GPU, forced-CPU}; 3,600 + 14,400 + 57,600 cells; 1200 / 1600 / 2200 SIMPLE iterations |
| **GPU-hour estimate** | **0.51 GPU-h** for the whole case (both arms) |
| basis | **DERIVED, NOT MEASURED**, from the parent's **measured** numbers: VMFL010 ran **0.2167 / 0.5167 / 2.8500 core-min** (13 / 31 / 171 wall s) to convergence at **729 / 1125 / 1575** iterations (`VMFL010/RESULTS.md`) ⇒ **0.01783 / 0.02756 / 0.10857 s per iteration**; at the registered endTimes that is **21.4 + 44.1 + 238.9 = 304.4 s per arm**; ×2 arms = **608.8 s**; a **3× allowance** for the instance's 4 vCPU and petsc4Foam's per-solve setup (the same allowance VMFLGPU001 used) ⇒ **1,826 s ≈ 0.507 h**, carried as 0.51 |
| **GPU-hour CAP** | **1.0 GPU-h**, **ENFORCED in the executable path** by `timeout` per solve, drawing the remaining budget down across solves. **An overrun STOPS the run and does not get a new budget** — `CAP_EXCEEDED.txt` is written and the run stops |
| **cap / estimate** | **1.97×** — a runaway guard, and **deliberately tighter than VMFLGPU001's 5×**. Stated plainly: **if the 3× allowance is optimistic, this cap will stop the run.** That is rule 12 working, not a defect; completed levels stand and their artifacts are kept |
| **core-minutes** | **30.4 core-min** = **15.2 (CPU arm)** + **15.2 (GPU-arm host rank)**. The GPU arm still occupies one host rank for its wall time and that is counted, not treated as free |
| CPU-arm cap | **60 core-min**, **ENFORCED** |
| **dollars, GPU** | **$0.41 DERIVED** (0.51 GPU-h × $0.8048/GPU-h). **NOT MEASURED** |
| **dollars, CPU-arm** | **$0.013 DERIVED** (15.2 core-min ÷ 60 × $0.0513/core-h). On this instance the CPU arm's time is already inside the GPU-hour meter and is **not a separate charge** |
| `cost_basis` label | GPU-hours at the **AWS PUBLISHED PRICE LIST** $0.8048/GPU-h for `g6.xlarge` us-east-2, retrieved 2026-08-23 (`GPU_CAPABILITY_STATE.md` §9, rateCode `JRTCKXETXF`); CPU core-hours at the **owner-stated** $0.0513/core-h. **Dollars are DERIVED, NOT MEASURED — this box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **The CONSOLE figure is STILL OWED and supersedes.** |
| the toolchain build | a **FAMILY** line in `COST_BASIS.md` amortised across the ten VMFLGPU cases, **not charged here** — stated so a reader adding 0.51 GPU-h to the family total does not double-count it |
| authorisation | GPU spend is **outside** the 2026-08-21 CPU blanket; this line is a per-item cost under the standing authority, **not a new ceiling** (rule 9) |
| calibration | at completion, actual GPU-hours and core-minutes from `RUN_RC.*` / `COST.txt` against these estimates, ratio and gap attribution (**contention named separately, never absorbed**), one row appended to `docs/COST_CALIBRATION.md`. **A completion report without that row is incomplete.** |

## 11. The grading path, frozen (`VERIFICATION_CHARTER` §2d)

| what | path (repo-relative, under `cases/ansys_verification/VMFLGPU002/`) | blob sha |
|---|---|---|
| **comparator** | `grade_vmflgpu002.py` | **`8172a0d32d5ab2a433319382f25f24f41dbef2c2`** |
| **launcher** | `run_vmflgpu002.sh` | **`b62542d5487154c4b201cf8ae22fab5d612063e6`** |
| `0/U` (BCs + age-guard marker) | `case/0/U` | `64a75f3e7021cbaacc0cf7febe2cf18ecb840146` |
| `0/p` | `case/0/p` | `31421c17cf7da39873d5e12a4de4e78e30f3b9aa` |
| `constant/transportProperties` | `case/constant/transportProperties` | `c98a811a6cc5a2e957583208a7ef71914ab378f8` |
| `constant/turbulenceProperties` | `case/constant/turbulenceProperties` | `8f52d77dde3cdbad97a9f2478d9ca3944c11d9d3` |
| `system/fvSchemes` | `case/system/fvSchemes` | `a5671a089e780e836cfcaa54ae56f5ffdedd8e58` |
| `system/blockMeshDict.template` | `case/system/blockMeshDict.template` | `194296ad1800fd9acc81466eeb67033d21485340` |
| `system/fvSolution.template` | `case/system/fvSolution.template` | `67f0e0ee4374936799ceba5bbe3297f5c37e34bb` |
| `system/controlDict.template` | `case/system/controlDict.template` | `fb5f61f6d5030a6f1ef48e850f09ba0340fc8c2c` |

**SIX of those blobs are BYTE-IDENTICAL to the CPU parent's frozen case** — `0/U`, `0/p`,
`transportProperties`, `turbulenceProperties`, `fvSchemes` and `blockMeshDict.template`
all carry the same sha as `cases/ansys_verification/VMFL010/case/…`. **The provenance is a
hash identity, not a claim.** Only the two templates the GPU path requires differ:
`fvSolution.template` (petsc linear solvers, `__MATTYPE__`/`__VECTYPE__`) and
`controlDict.template` (fixed `endTime`, `libs (petscFoam)`, the three flux function
objects).

**What changed in `fvSolution`, and what did NOT.** `p`: GAMG → petsc `cg` + `jacobi`.
`U`: smoothSolver → petsc `bcgs` + `jacobi`. **The outer numerics are the parent's,
character for character** — `consistent yes`, two non-orthogonal correctors, relaxation
0.9/0.9, tolerances 1e-9, relTol 0.01/0.1 — because those are what the parent's measured
convergence points were obtained under, and those measurements are this case's `endTime`
basis *and* its cost basis. **Changing the outer loop would silently invalidate both.**
`residualControl` is removed, and `pRefCell`/`pRefValue` are absent because both outlets
carry `fixedValue` p and the pressure level is already determined.

**This document and all of the above are committed in ONE commit, before any compute.**

**LAUNCH-TIME FREEZE CHECK (non-droppable).** Before any solver, `run_vmflgpu002.sh`
resolves `HEAD:<prereg>` and `HEAD:<comparator>` on the instance's own clone, hashes both
on disk, and **aborts** unless each disk blob equals its HEAD blob; the shas and the HEAD
commit are written into `LAUNCH_RECORD.txt`. **An unverified freeze is no freeze.**

### 11.1 Comparator `--selftest`, run at this freeze

**43 checks, GREEN**, and **byte-identical output under `python3` and `python3 -O`, rc 0
both** (`cmp` on the two captures: identical). **Zero `ast.Assert` nodes** in the source,
with **the counter shown able to count a planted one** (1 when an `assert` is appended) —
so the zero is a reading, not a hope (L-332: `python3 -O` deletes asserts).

Among the checks, each shown able to fail: the reference is 0.887 and its kind is
code-to-code so **`PASS` is unreachable**; `TIER_CEILING` is in the fixed vocabulary and is
not `PASS`; 0.884 is carried as context and is **not** the reference; the analytic inlet
flux is 2/3; `split_from_fluxes` is sign-blind; the mass balance closes on a closed set and
**opens** on an open one; the cell counts are 9·NW² so r = 2 is exact; a blind reader makes
the planted-zero control **refuse**; the plant's measured gain is 1.5×; a short plateau
**refuses** as `CANNOT_TELL`; a NULL-RANGE plateau **refuses**; a field older than `0/U`
**refuses** on the age guard; a forced-CPU arm that reports GPU work **refuses**; an
observed order below `P_MIN` routes to `NOT A RESULT` **with no GCI printed anywhere**,
end to end under `python3 -O`; and a corrupt or missing `COST.txt` leaves the verdict
unchanged (L-342).

## 12. What this rung will NOT claim

- **Nothing about Ansys.** This box has no Fluent and no VM2026R1 archive was opened. The
  0.884 column is context.
- **Nothing about GPU performance.** No speed-up is claimed, sought or gated. **A GPU arm
  slower than the CPU arm passes every limb.**
- **No `PASS`.** The reference is a numerical benchmark; the ceiling is `GATE REACHED`.
- **No validation of the tee-junction physics.** Limb C is a code-to-code agreement check.
- **Nothing about whether the parent's oscillation is resolved.** §7.1 registers that it
  may recur; this case does not set out to fix it and will not claim to have.

## 13. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` — and only
these (rule 1). **This rung is `PENDING` until the comparator has graded a completed run
against the gate above.** An expected launch is not a result, and enqueueing is not
authorisation (`QUEUE_ENTRY_STANDARD.md` §1): `SUPERVISION_CHARTER.md` §3 check 4 is the
supervisor's own and is not discharged by this document.

---

## POST-COMPUTE AMENDMENT 5 — 2026-08-27 (dated addendum; VERIFICATION_CHARTER §2d.1 + L-342)

**Appended after first compute. This addendum moves NO gate, limb, band, threshold, cap or
label — it repairs two GRADING-PATH READERS, each a demonstrable error, under the four-condition
repair exception of `VERIFICATION_CHARTER` §2d.1 and L-342. Lines whose number changed above this
section: 0.** Originals in §6, §8 and §11 are struck by nothing; they stand as frozen. Comparator
blob transition **`8172a0d3` → `92a82426`**. Supervisor rulings of 2026-08-27, [lab-attributed];
the supervisor read the frozen comparator at HEAD personally before ruling. Drafted by
`ansys-lane-opus48` (lane H).

**The pre-repair refusals, recorded verbatim (condition c).** The frozen comparator `8172a0d3`,
run against the completed run root, refused at clause C7:

> REFUSE (VMFLGPU002 C7): L1_N20: 1202 ExecutionTime lines, the registered endTime is 1200 (clause 5)

and, with C7 repaired (item 1 below), then refused at limb A:

> REFUSE (VMFLGPU002 A2): L1_N20: the FORCED-CPU CONTROL (mat_type aij, vec_type standard) REPORTED GPU WORK (tell1=True tell3=False). The tells cannot discriminate GPU from CPU on this build, so this row certifies NOTHING.

### Item 1 — clause 5 (C7): the ExecutionTime line count is INFRASTRUCTURE (RULING 2, L-342)

The frozen clause required `ExecutionTime`-line count == endTime. On this build every one of the
six logs carries exactly `endTime` `Time = ` lines and exactly `endTime + 2` `ExecutionTime` lines;
the two extras sit inside `Time = 1`, one before and one after `Initializing PETSc... success`,
BEFORE the first solve — petsc4Foam initialisation timing prints, not solver iterations. This is
the exact defect ruled at **VMFLGPU001 Post-compute Amendment 4** (commit `59110074`, blob
`f4b07b7f`→`21fa2387`) under L-342: a count of TIMING-REPORT lines is a property of what the
libraries print, never of the physics. The repair makes the **`Time = ` line count == endTime** the
physics-critical clause (it REFUSES otherwise); the `ExecutionTime` count is REPORTED as an
INFRASTRUCTURE warning and never refuses. Completion stays established by the `Time =` count, the
last time, the `End` line, the fields at endTime and the age guard — all of which hold.

### Item 2 — limb A: the GPU tell re-based on the GPU %F table VALUE; tell3 dropped (RULING 1, §2d.1)

**The defect is provable from the frozen document itself, with no reference to any run output** —
which is the line the supervisor drew for a legal post-compute repair. This file's own frozen
header states, verbatim:

> TELL 1 IS LOOSE AND CANNOT DISCRIMINATE ON ITS OWN -- PETSc's -log_view prints GPU columns and CpuToGpu/GpuToCpu rows on a CUDA-configured build EVEN WHEN THE SOLVE RAN ON THE CPU (PREREG_TEMPLATE Amendment 5, "THE SAME REQUIREMENT ON THE GPU RECIPE"). THE FORCED-CPU CONTROL IS THE DISCRIMINATOR, and a run graded without it is NOT A RESULT.

The frozen `limb_A()` then refuses at A2 precisely when `tell1` fires on the forced-CPU control —
an outcome the header declares CERTAIN on a CUDA build. **The instrument was frozen guaranteed to
refuse, and that contradiction is visible entirely within the frozen file, before any solver ran.**
That is a demonstrable error (the file contradicts itself), established by evidence that grades
nothing (the file's own header, plus the documented behaviour of PETSc `-log_view`, which prints
the GPU columns on a CUDA build irrespective of where the solve ran). **No measured physics value
enters this justification.**

The repair, restricted to limb A's readers:
- A new reader `gpu_flops_on_device()` reads the **GPU %F column** (the last field of every
  `-log_view` event row) — the percent of an event's flops performed on the device, which is 0 on a
  CPU solve and > 0 on a GPU solve. It is the genuine discriminator; `tell1`'s legend match is not.
- The GPU arm must show `gpu_flops_on_device` True **AND** `tell2` (a solver PID holding device
  memory) — both kept as genuine discriminators.
- The forced-CPU control refuses (A2) only when the control arm itself shows GPU %F > 0 — genuine
  device work in the arm that must not have any — never on the loose `tell1`/`tell3`.
- `tell3` is **dropped from the conjunction**: `-ksp_view` on this build echoes the matrix type in
  the OPTIONS block (`-eqn_p_mat_type aijcusparse`), not as a `type: aijcusparse` line, so `tell3`
  was frozen guaranteed False even on the genuine GPU arm. The `tell1`/`tell2`/`tell3` FUNCTIONS are
  left byte-identical (the header's smoke-test byte-equivalence claim is preserved); they are simply
  no longer the limb-A discriminator.

**Conditions of the ruling, all met.** (a) The justification quotes the frozen header verbatim and
cites the build behaviour, with no measured physics value; (b) the repaired control is DRIVEN, not
read — `--drive-refusal gpu-zero-pctf` forges a GPU-arm log that is cusparse-typed with the
`-log_view` legend present (so the loose `tell1`/`tell3` both fire) but with GPU %F = 0 on every
event row, and the selftest requires it to REFUSE; (c) the pre-repair refusals are recorded verbatim
above and both gradings are cited in `RESULTS.md`; (d) no limb, band, threshold, cap or label moves
— limb A still means "the GPU path provably ran and the forced-CPU control discriminates"; (e) this
amendment is committed BEFORE the re-grade runs, with pre-registration discipline. Selftest **47
checks GREEN** (was 43; +3 reader-function checks, +1 forged-log driven check), byte-identical under
`python3` and `python3 -O`, zero `ast.Assert` nodes.

### The verdict does NOT move — stated plainly, because it is what makes the repair unimpeachable

**Under these rulings the limb-A repair changes NO verdict in either case.** VMFLGPU001 is still
refused earlier, at its frozen plateau clause I5 (row #33, `NOT A RESULT`, unamended). VMFLGPU002 is
still `NOT A RESULT` on its **OSCILLATORY** grid triple (rule 5 step 2, before any band is read). A
post-compute repair that cannot flatter any outcome was authorised, and this record shows it.

### The honest tension, disclosed and NOT papered over (Sanaa's §3 anti-gaming clause, 16:54Z)

Sanaa's standing directive of 2026-08-27 §3 states "Frozen gates never edited post-compute." This
amendment repairs a post-compute limb-A **reader**. The supervisor's position, recorded here as the
ruling's own reasoning: **a reader is not a gate** — no limb, band, threshold, cap or label moves,
and the repair changes no verdict in either case, which is what makes it harmless. The tension is
disclosed rather than argued away: **if Sanaa's clause is read to cover readers too, nothing is lost
— both cases are `NOT A RESULT` either way.** The record carries the tension.
