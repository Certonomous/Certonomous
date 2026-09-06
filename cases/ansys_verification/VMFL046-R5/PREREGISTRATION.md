# VMFL046-R5 — PRE-REGISTRATION

**Supersonic flow with a normal shock in a converging–diverging nozzle.**
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155 (VMFL046)**.

> **THIS IS A ONE-LINE CONFIGURATION CHANGE. IT IS NOT A GATE CHANGE, NOT A NUMERICS
> CHANGE AND NOT A MESH CHANGE.** Exactly one byte of the eleven `case/` inputs moves — the
> `p` outlet boundary condition, from a **fully-reflecting `fixedValue`** to a
> **partially non-reflecting `waveTransmissive`**. The gate (`x_shock` vs **1.250 m**,
> band **5 %**), the plateau threshold (**`DELTA_X = 6.250e-04 m`**), `endTime = 0.080 s`,
> `maxCo 0.5`, `maxDeltaT 1.0e-04`, `ddtSchemes Euler`, `Gauss vanLeer(V) 1`, the mesh, the
> refinement ratio `r = 2` and the sampler are **all carried forward from R4 byte-identical**,
> and the comparator is **the same repaired file, pinned by blob**. **Nothing in the gate is
> widened.**

---

## 1. WHY THIS DOCUMENT EXISTS — R4 IS `NOT A RESULT`, AND THE OUTLET IS THE PRIME SUSPECT

VMFL046 has been run R2/R3/R4 with `rhoPimpleFoam`. The live verdict is **VMFL046-R4 =
`NOT A RESULT`**: the Roache triple graded **OSCILLATORY** and `x_shock` did not reach a
plateau by **252–282×** of `DELTA_X` over the registered window — a shock that hunts, never
settling. The manual asserts the flow is **steady** and **laminar**, and the reference is
White's analytical 1-D nozzle solution with the normal shock at `x ≈ 1.2485 m` (frozen gate
**1.250 m**).

R2, R3 and R4 all imposed a **fully-reflecting `fixedValue p = 176 325 Pa`** outlet. **A
reflecting outlet is the classic source of a spurious nozzle-shock limit cycle**: an
acoustic wave generated at the shock reflects off the constant-pressure boundary and returns
to drive the shock, closing a feedback loop that sustains a hunt which the physics does not
have. That mechanism is exactly what R4 measured — a periodic waveform, not a decaying
residual (R3 §5.3: 85.4 % of the log-residual variance in a single ~4168-iteration mode
matching the `x_shock` period to within 1 %).

**R5 changes the one configuration item that would create that artifact, and nothing else.**

---

## 2. THE ONE CHANGE — REFLECTING → NON-REFLECTING OUTLET, AND WHY IT IS A CONFIG MOVE *TOWARD THE MANUAL*

| | R4 (and R2/R3) | **R5** |
|---|---|---|
| `p` outlet BC | `fixedValue; value uniform 176325` | `waveTransmissive; field p; psi thermo:psi; gamma 1.4; fieldInf 176325; lInf 2.0; value uniform 176325` |
| `U` outlet BC | `inletOutlet` | **unchanged** |
| `T` outlet BC | `inletOutlet` | **unchanged** |
| everything else | — | **byte-identical to R4** |

The one changed file is `case/0/p`, line 10. The diff is one line replaced by one line
(`diff` shows `10c10`); the ten other `case/` files are byte-identical to R4's committed
blobs (§8).

**WHY THIS IS A CONFIG CHANGE AND NOT A GATE CHANGE.** The manual's reference solver is
**Ansys Fluent**, whose *pressure-outlet* boundary is **partially reflecting** — it holds a
target static pressure in the far field while transmitting outgoing acoustic waves rather
than bouncing them back. OpenFOAM's `fixedValue` is at the **fully-reflecting** extreme of
that same axis (it pins `p` on the face and reflects every wave); `waveTransmissive` is a
**partially non-reflecting** outlet that relaxes the face pressure toward `fieldInf` over a
far-field length scale while advecting disturbances out. **R5 moves the numerical outlet
condition from the fully-reflecting extreme toward the partially-reflecting condition the
manual's own reference solver uses.** It changes the *physical faithfulness of the boundary
model*, not the *criterion by which the answer is judged*: the gate value 1.250 m, the 5 %
band, `DELTA_X`, the plateau window and the reader are all carried forward unchanged.

> **A gate change would move 1.250 m, the 5 % band, `DELTA_X`, `endTime`, `maxCo` or the
> plateau window. NONE of those moves. Only the boundary model moves, in the direction of
> the reference.** (`CLAUDE.md` rule 5 gate-only-tightens; Sanaa `4ae4b33`: gates are never
> widened.)

---

## 3. `lInf` — FIXED BY GEOMETRY ALONE, GATE-BLIND, NOT TUNED

`waveTransmissive` needs one length, `lInf`: the far-field relaxation distance over which the
face pressure is pulled toward `fieldInf`. As `lInf → 0` the condition degenerates to
`fixedValue` (fully reflecting — R4's defect); as `lInf → ∞` it becomes purely advective
(no mean-pressure anchoring, which a subsonic outlet needs). It must therefore be a finite,
domain-scale length, and **it must be pinned before the freeze by an argument that does not
depend on where the shock sits**, because the shock location is the answer.

> **`lInf = 2.0 m` — the full streamwise length of the nozzle**, stated by the manual itself
> (*"Length of the nozzle = 2 m"*, VM2026R1 p. 155) and built into the mesh (inlet `x = 0`
> to exit `x = 2.0`). It is a **pure geometric constant of the domain**: it is the same
> number whether the shock stands at 1.0 m, 1.25 m or 1.5 m, so it **cannot be chosen to
> move `x_shock`**. The relaxation length is set to the domain's own streamwise extent, which
> is the standard domain-scale choice for this boundary.

**THE ANSWER-DEPENDENT CANDIDATE IS REJECTED, AND WHY.** The other candidate was the
**subsonic downstream length ≈ 0.85 m** (R3 §5.4). That figure is defined as *"the subsonic
section **downstream of the shock**"* — i.e. exit minus shock location — so **its value is a
function of where the shock is: the answer.** Pinning `lInf` to it would couple the boundary
model to the quantity being graded, which is precisely the tuning this registration must not
do. **It is therefore not used.** `lInf` is fixed to the answer-independent full-duct length
`2.0 m`, and **no probe is run to select it** — running a probe to pick the relaxation length
that best moves the shock would be answer-dependent tuning by another name.

---

## 4. THE GATE — CARRIED FORWARD FROM R4 BYTE-IDENTICAL, COMPARATOR PINNED BY BLOB

The grading path is **the R4 §2aw-repaired comparator, reused byte-for-byte.** It reads
`log.rhoPimpleFoam`, `RUN_RC`, the `controlDict` clock, the centreline history and the `T`
field — none of which depends on the `p` outlet BC — so the same file grades R5's runs
exactly as it grades R4's.

| limb | value | provenance |
|---|---|---|
| primary reference | **`x_shock` = 1.250 m** | White analytical normal-shock location, **unchanged from R1–R4** |
| band | **5 %** (half-width 0.0625 m) | **unchanged from R1–R4** |
| plateau | **`DELTA_X = 6.250e-04 m`** | **unchanged from R2–R4** (charter §31) |
| plateau statistic | `ptp` over two adjacent windows `W = endTime/10`, plus mean drift | **unchanged** |
| reader | interpolating last downward `M = 1` crossing, consuming only the registered window | **unchanged** |
| ceiling | **`GATE REACHED`** | model-sameness differs (viscous 2-D NS vs inviscid quasi-1D); **`PASS` is unreachable and the comparator contains no code path that prints it** |
| secondaries | observed order in [0.5, 2.5], GCI ≤ 15 % | **demote-only** (charter §21.3) |

**Refinement:** `r = 2` grid triple, identical to R1–R4: converging / diverging / transverse
counts 40 / 120 / 20 doubling twice, giving 3 200, 12 800 and 51 200 cells at the three
levels **L1**, **L2**, **L3**. Sampler `nPoints = 2(NXA+NXB)+1` = 321/641/1281, refining with
the mesh. **Grading pin:**

| artifact | blob sha | note |
|---|---|---|
| **`grade_vmfl046_r5.py`** (**THE GRADING PATH**) | **`476de16ab3e4f3572435e7e8a729ff617a08fc62`** | **byte-identical to R4's `grade_vmfl046_r4.py`** (the §2aw-repaired comparator, live at commit `89d7dce4`); `--selftest` = **67 arms, 67 ok, 0 FAILED** under `python3` and `python3 -O` |
| `case/0/p` (**THE ONE CHANGED FILE**) | `1f3a65e4b2a71ee431b7b90149b97a73e6d0befe` | was `b2bdcfcf…` (R4 `fixedValue`) |
| the other ten `case/` inputs | **identical to R4's pins** (VMFL046-R4 §10) | byte-identity proved by `diff -rq` and per-file `git hash-object` |

> **THE COMPARATOR IS REUSED, NOT RE-DERIVED.** Its blob equals `476de16a…`; the gate,
> plateau threshold and `DELTA_X` inside it are therefore **byte-for-byte** what graded R4.
> Any edit to those is a gate change and is void here. The banner strings inside the file
> still read "R4" — this is the deliberate consequence of a byte-identical reuse, chosen so
> the blob is provably the repaired-and-selftested file rather than a hand-edited near-copy;
> the case-id in the banner is cosmetic and names no gate quantity.

---

## 5. THE DIAGNOSTIC LOGIC — PRE-COMMITTED, BEFORE ANY RUN

R5 is a **controlled single-variable experiment**: it changes only the outlet reflectivity.
Its two outcomes are pre-committed so neither can be re-interpreted after the fact.

> **BRANCH (a) — THE HUNT COLLAPSES TO A PLATEAU.** Every level plateaus (`P1,P2,P3 ≤
> DELTA_X`) and the Roache triple on `x_shock` is `CONVERGING`. **Conclusion: the R4 hunt was
> an OUTLET-REFLECTION ARTIFACT — a configuration defect, not physics.** The verdict is then
> the comparator's: **`GATE REACHED`** inside the 5 % band with no secondary fired, else
> **`GATE FAIL`**. This would be the first VMFL046 configuration to produce a graded result,
> and the finding "the reflecting outlet, not the numerics, sustained the hunt" is recorded.
>
> **BRANCH (b) — IT STILL HUNTS.** Any level fails the plateau at `endTime = 0.080 s`.
> Verdict **`NOT A RESULT`** (rule 5 step 1), with every level's P1/P2/P3 and its multiple
> of `DELTA_X` printed. **Conclusion: outlet reflection is NOT the cause** — the unsteadiness
> survives a non-reflecting boundary, so it is either genuine physical unsteadiness at this
> resolution or a deeper numerical cause. **This escalates to the R6 successor (§6) and, if
> R6 also hunts, to Sanaa's desk under §37.4 ("the question is OPEN").** No threshold,
> `endTime`, `maxCo` or plateau window is widened as a remedy in either branch.
>
> **BRANCH (c) — A LEVEL HITS ITS COST CAP (`rc 124`).** **`NOT A RESULT` (budget/kill
> class)**; the successor re-files its estimate from this run's own logs (§7). No cap is
> raised mid-flight and no partial result is graded (`check_completion` refuses `rc ≠ 0`, a
> missing `End`, or a last `Time` short of `endTime`).

**Because R4 and R5 differ in exactly one boundary condition, a difference in outcome is
attributable to that boundary condition and to nothing else.** That is the experimental
value of the byte-level parity.

---

## 6. THE PRE-COMMITTED R6 SUCCESSOR — `rhoCentralFoam`, THE DENSITY-BASED PATH

Pre-committed **before** R5 runs, so branch (b) has a defined next step and cannot become an
occasion to widen R5's gate. If R5 still hunts under a non-reflecting outlet, the suspicion
moves from the boundary to the **pressure-based segregated solver** (`rhoPimpleFoam`), and R6
switches to the **density-based, shock-capturing** solver `rhoCentralFoam` — the Kurganov–
Noelle–Petrova central-upwind method of **Greenshields, Weller, Gasparini & Reese (2010),
Int. J. Numer. Meth. Fluids 63:1–21, DOI 10.1002/fld.2069** (filed §9), which OpenFOAM
provides specifically for high-speed compressible flow with shocks.

**R6 RECIPE, PRE-STATED (the corrected tutorial recipe):**

- `fluxScheme Kurganov`;
- `reconstruct(rho)`, `reconstruct(U)`, `reconstruct(T)` all `vanLeer` (TVD);
- `maxCo 0.2` (explicit density-based time stepping needs a tighter Courant limit than the
  implicit `rhoPimpleFoam` `maxCo 0.5`);
- `waveTransmissive` outlet with `lInf 2.0 m` **carried forward from R5** by the same
  geometric argument (§3);
- same mesh, same `endTime`, same gate, same plateau threshold, same comparator.

> **TEMPERATURE BOUNDING — VERIFIED, NOT ASSUMED.** `rhoCentralFoam` bounds `T` by its **TVD
> reconstruction of the conserved variables**, not by an `fvOptions limitTemperature` entry,
> which it **structurally lacks** (verified by the supervisor at source). The comparator's
> **N4 limb** — "the `limitTemperature` bounds must be non-binding at `endTime`" — is
> therefore **not applicable to R6 and must be replaced**, not carried across as-is; R6 will
> re-derive an equivalent physical-range refusal from the reconstructed field. **This is
> flagged as a comparator delta the R6 registration must make; it is not made here, and R5's
> comparator is unaffected** (R5 keeps `rhoPimpleFoam` and its `limitTemperature`, so N4
> stays live and correct for R5).

---

## 7. COST — POINT ESTIMATE FROM R4's OWN MEASURED ACTUALS, NO NEW PROBE (rule 12)

**The point estimate is R4's three graded-run actuals, carried forward unchanged: 489.0
core-min.** This is a *deliberate* method choice, ruled by the supervisor, and it is
answer-blind: the basis is R4's **cost** artifact (its per-level `ClockTime`), never R4's or
R5's **flow** — so filling the caps from it does **not** let this document see the shock
location before the freeze. **No R5 probe is run** — and running one to select a cost would
also risk seeing the answer, which is precisely what a pre-registration must not do.

**BASIS — R4's per-level measured actuals** (`docs/COST_CALIBRATION.md` row
`C-20260906T170500...` and its correction `C-20260906T183000...`; register row **#61**;
core-min = `ClockTime` × 1 rank ÷ 60):

| level | R4 measured wall | **R4 measured core-min (= R5 point estimate)** | per-level cap (~3×) |
|---|---|---|---|
| **L1** | 484 s | **8.07** | **27** |
| **L2** | 3,280 s | **54.67** | **183** |
| **L3** | 25,576 s | **426.27** | **1,400** |
| **total** | 29,340 s | **489.0** | **1,610** (running) |

**WHY R4's COST IS A CONSERVATIVE POINT ESTIMATE FOR R5.** `waveTransmissive` changes a
**boundary evaluation on one outlet patch only** (it evaluates `psi`, a wave speed and a
relaxation term on the exit faces each step); it does **not** change the per-cell-step rate of
the 3 200 / 12 800 / 51 200-cell interior, and the mesh, numerics and `endTime` are
byte-identical to R4. If the non-reflecting outlet **settles** the flow (branch (a)), it can
only **reduce** the number of steps to `endTime`; if it does **not** (branch (b)), the run
still stops at the same geometric `endTime = 0.080 s`. So R4's measured envelope over-bounds,
or at worst matches, R5's — it cannot be exceeded on physics grounds by the one change made.

**THE +10 % CONTENTION ALLOWANCE GOES IN THE CAP, NOT THE POINT ESTIMATE.** This is the R4
calibration lesson landed verbatim (`docs/COST_CALIBRATION.md` id `C-20260906T170500...`):
*"the ×1.10 contention allowance should be filed as a CAP component and not folded into the
point estimate, because folded in it systematically biases every ratio to ≈ 0.91× on a quiet
box and hides exactly this kind of accuracy."* The point estimate is therefore the **bare
measured basis 489.0 core-min**; the caps below carry both the contention allowance and the
charter's ~3× headroom.

**CAPS (charter §26.2), mirroring R4's frozen caps** — per level **27 / 183 / 1 400**,
running total **1 610 core-min** (each ≥ 3× its per-level basis; 1 610 ≥ 3 × 489.0). **An
overrun STOPS the run** (`rc 124`, branch (c), rule 12); it does not get a new budget. The
caps are enforced twice in the driver — a per-level cap and a running total.

**`cost_basis`.** core-min = wall_s × ranks ÷ 60, **measured** from `ClockTime` (the R4
actuals above). Dollars are **derived, not measured** at **$0.0513/core-h** (c7a.4xlarge,
owner-stated 2026-08-21/22; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5): point estimate **489.0 core-min → $0.418 derived**; running
cap **1 610 core-min → $1.377 derived**.

**Predicted-vs-actual row owed at completion** (rule 12): a `docs/COST_CALIBRATION.md` row
comparing this 489.0-core-min point estimate against R5's graded actual, attributing the gap
(the settling of the flow under a non-reflecting outlet is expected to reduce L2/L3 steps, so
an actual **below** the basis would confirm branch (a) had a cost signature as well as a
plateau signature).

**This case is now launch-ready on the cost axis:** the point estimate is committed, the caps
are filled from a measured basis, and no probe is owed.

---

## 8. PARITY — PROVED FROM THE BYTES

`diff -rq VMFL046-R4/case VMFL046-R5/case` reports **exactly one differing file** (`0/p`), and
`diff` on that file reports **exactly one changed line** (`10c10`). Per-file `git hash-object`
confirms the ten unchanged files carry R4's exact blobs and only `0/p` moved
(`b2bdcfcf… → 1f3a65e4…`). **The single-variable claim of §2 and §5 is thus a measured
property of the files, not an assertion.**

---

## 9. FILES

| what | path |
|---|---|
| this registration | `cases/ansys_verification/VMFL046-R5/PREREGISTRATION.md` |
| **the grading path** (blob `476de16a…`) | `cases/ansys_verification/VMFL046-R5/grade_vmfl046_r5.py` |
| case inputs (11 files; ten byte-identical to R4, `0/p` changed) | `cases/ansys_verification/VMFL046-R5/case/` |
| predecessor, **READ-ONLY** | `cases/ansys_verification/VMFL046-R4/` · `verification/runs/ansys_verification/VMFL046-R4/` |
| R6 method paper (filed, title-verified, `NOT committed`) | `docs/papers/verification_validation/greenshields_2010_rhocentralfoam.pdf` + `.txt` |
| run root (**must not exist or be empty at launch**) | `verification/runs/ansys_verification/VMFL046-R5/` |

### 9.1 FREEZE-READINESS — BOTH BUILD STEPS NOW DONE (stated plainly)

1. **A run driver** (`run_vmfl046_r5.sh`) with a both-directions parity assert on the single
   `0/p` delta — ten files byte-identical to R4, `0/p` the documented change — mirroring how
   R4's driver asserted parity to R3 plus its own delta. **BUILT.** It sources the OpenFOAM
   v2606 environment before asserting its tools (the VMFL072 G-00 lesson), constructs L1/L2/L3
   from the templates exactly as R4 does, refuses in both directions if parity is violated
   (any non-`0/p` input differing from R4, or `0/p` unchanged / not carrying `waveTransmissive`
   `lInf 2.0`), enforces the per-level and running caps, and writes a per-level `RUN_RC`.
   `bash -n` clean; the parity logic verified against the real R4/R5 trees (10 identical + 1
   changed = 11 = R4's file set).
2. **The cost caps** (§7). **FILLED** from R4's own measured per-level actuals (8.07 / 54.67 /
   426.27 core-min, point estimate 489.0), no new probe — the basis is R4's cost artifact,
   which is answer-blind. Caps 27 / 183 / 1 400, running 1 610.

Both were compute-adjacent build steps; neither alters the gate, which is fully specified
above. **No compute has been performed** — the run root
`verification/runs/ansys_verification/VMFL046-R5/` does not yet exist (a launch-ordering step,
not a freeze defect).
