# PRE-REGISTRATION — VMFL034-R3: Particle Aggregation inside a Turbulent Stirred Tank — THE FROZEN-FLOW RE-SCOPE

**DRAFT — NOT YET FROZEN.** Successor to **VMFL034-R2** (register row **#59**,
verdict **NOT A RESULT**): R2 died **SIGFPE (rc 136)** at `t≈0.082 s` at **all
three levels**, in `dragModels::SchillerNaumann::CdRe()` computing `Re^0.687` on a
**non-positive Re** — a **LIVE two-phase drag domain error**. R2 was triaged as a
drag-closure domain error, **not mesh-dependent**. The R2 bytes are **NOT edited
and NOT reverted** (CLAUDE.md rule 6, rule 10); R2 stands in history as a
registration whose live-flow solve could not produce a verdict.

Drafted by `ansys-lane-opus` (running as **claude-opus-4-8**), 2026-09-07
(`date -u` in the drafting invocation: `Mon Sep  7 14:34:34 UTC 2026`). **This lane
froze nothing, committed nothing, ran no graded solver, and touched no archive
copy.** The lane compiled and ran an **ephemeral, answer-blind startup smoke** of
the frozen-flow solver (`§SOLVER`), which produced **no gradeable moment**. The
supervisor performs `SUPERVISION_CHARTER` §3 check 4 and freezes (the commit is the
freeze).

---

## §R. WHAT R3 REPAIRS — the one R2 defect, and the manual-faithful fix

**The defect (measured, register #59):** R2 solved the **live** two-phase Euler
momentum/pressure system with `SchillerNaumann` drag coupling. During that live
solve the drag coefficient `CdRe = 24(1 + 0.15 Re^0.687)` was evaluated on a `Re`
that went non-positive as the coupled velocity field diverged → `Re^0.687` domain
error → SIGFPE at `t≈0.082 s`, uniformly across S1/S2/S3.

**The fix (the manual's OWN regime):** the Ansys VMFL034 setup **decouples the flow
from the moments**. The manual states verbatim (p.121): *"Moments are solved on a
frozen flow field."* Its journal solves the carrier first, then **freezes it** and
solves only the six moments:

```
solve set equations mixture flow yes ke yes mp no      # 1) solve the carrier flow + k-epsilon
solve iterate 700
solve set equations mixture flow no ke no mp no         # 2) FREEZE the flow and k-epsilon
solve set equations phase-2 moment-0..5 yes             # 3) turn the 6 QMOM moments ON
solve iterate 2000                                       #    transport the moments on the FROZEN field
report population-balance moments outlet () () 6 no
```

**R3 realises exactly this in OpenFOAM.** The carrier k-ε field is solved **once**
and **frozen**; only the alpha-continuity and the **constant-kernel** population
balance are transported on the frozen field, by a **frozen-flow build of
`reactingTwoPhaseEulerFoam`** (`§SOLVER`) whose PIMPLE loop **omits** the
pressure-velocity-energy block. That block (`pU/UEqns.H`, `EEqns.H`, `pU/pEqn.H`)
is the **only** site in the v2606 reactingEuler solver that invokes
`fluid.Kd()` / `fluid.momentumTransfer()` → `SchillerNaumann::CdRe()`. With it
removed, the R2 domain error **cannot recur — structurally, not by bounding.**

**This is a manual-faithful NUMERICS lever, not a gate-fitting change.** The band,
the targets, the size-group triple and the aggregation kernel are R2's,
**byte-for-byte** (`§R.6`). The regime change (freezing the flow) is the manual's
own; **it does not, and cannot, widen the gate** (L-487 anti-circularity: `§4`).

### §R.6 WHAT SURVIVES INTACT — R2's settled physics and gate, reused unchanged

R3 changes **only the solver** (live-flow → frozen-flow) and the comparator (two new
gate-blind guards, `§10a`, `§N`). Every physics input and every gate quantity is
identical to VMFL034-R2:

- The **band**: relative, uniform **± 0.76 %** on every gated moment (`§4`).
- The **gate conjunction**: **m1, m2, m3, m4, m5**; **m0 DEMOTED** to a calibration
  limb (setting `β₀_OF` for `Da=100` *sets* m0 by construction).
- The **constant aggregation kernel** `β₀_OF = 2000 m³/s` (`constantCoalescence`,
  `Da = β₀·m0_feed·τ = 100`), `α₂ = 1e-2`, `κ = π/6`, `τ = 5 s` (rescaled).
- The **archive feed moments** `(1, 1.108, 1.39, 1.91, 2.821, 4.423)` and the
  Wheeler/KR sectional feed (feed-moment guard, D3, `§R.5`-equivalent retained).
- The **r = 2 size-group triple 16/32/64** (`§7`).
- The **rescaled operating point** (walls 6.06/6.00 m/s, inlet 0.10 m/s, τ = 5 s,
  `endTime = 25 s = 5τ`) with **Da preserved exactly** and **well-mixedness
  MEASURED** (comparator refuses `CoV(m0) > 0.10`).
- **Nominal, not SI, units** — size range O(1) over [0.45, 22.0].

The dispersed phase is named **`air`** and the population balance **`bubbles`**
(template-inherited from the ESI `bubbleColumnPolydisperse` case); **there is no air
and there are no bubbles** — they label the crystal/particle phase (retained
deliberately; renaming re-opens the field interface). Any record citing this case
carries this note.

---

## §0. CLEAN-SLATE ASSERTION (CLAUDE.md rule 2 — the condition, and how it was checked)

**NOT YET RUN. NO VMFL034-R3 GRADED SOLVER HAS EVER STARTED.** Every band, ratio,
cap, criterion and label below was fixed with no VMFL034-R3 **moment** in existence.
Checked in the drafting invocation, 2026-09-07T14:34Z:

| condition | check | result |
|---|---|---|
| the graded run root does not exist | `test -e verification/runs/ansys_verification/VMFL034-R3` | **RUN ABSENT** |
| the register carries no VMFL034-R3 row | `grep -c VMFL034-R3 verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| no VMFL034-R3 graded run exists | `find verification/runs -iname '*VMFL034-R3*'` | **0 hits** |

The **ephemeral answer-blind smoke** (`§SOLVER.3`) ran only under the session
scratchpad and produced **no gradeable moment** (it was 5 timesteps, refused by the
comparator's own m0-calibration guard as non-converged). It dates nothing here.
Before first **graded** compute, amendments to this file are legal and must state
the condition and how it was checked, naming the run directory
`verification/runs/ansys_verification/VMFL034-R3/` that **does not exist**. After
first graded compute, dated addenda only (rule 2).

---

## §1. SOURCE (CLAUDE.md rule 15 — title-page-verified against the PDF)

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **printed pages 121–122**
(PDF pages 135–136), read from the sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
(lines 3245–3331) and verified against the PDF in the struck registration
(`cases/ansys_verification/VMFL034/PREREGISTRATION.md §1`). Reference: B. Wan,
T.A. Ring, K. Dhanasekharan, J. Sanyal, *"Comparison of Analytical Solutions for
CMSMPR Crystallizer with QMOM Population Balance Modeling in Ansys Fluent"*, China
Particuology, Vol. 3, pp. 213–218, 2005. The gate reference is the **analytical**
Target column of Table .34.1:

| Moment | Target (analytical) | band (relative) |
|---|---|---|
| m0 | 0.132 | ± 0.76 % (CALIBRATION) |
| m1 | 0.225 | ± 0.76 % |
| m2 | 0.547 | ± 0.76 % |
| m3 | 1.910 | ± 0.76 % |
| m4 | 9.073 | ± 0.76 % |
| m5 | 53.797 | ± 0.76 % |

The Ansys Fluent (QMOM) column is context, **not** the gate. This is a
discretisation-vs-exact comparison. The manual's own modelling note — *"Moments are
solved on a frozen flow field"* — is the physical basis for R3's re-scope (`§R`).

---

## §SOLVER. THE EXACT OpenFOAM SOLVER / CONFIG PATH — AND THE FIX-UNTIL-RUNS EVIDENCE

**Solver family:** OpenFOAM ESI **v2606** (`/usr/lib/openfoam/openfoam2606`),
`reactingTwoPhaseEulerFoam` sectional population balance — the same family R2 used.

**The concrete path is a TWO-STAGE frozen-flow run, the direct analogue of the
manual's journal:**

- **STAGE 1 — the carrier (answer-blind).** `simpleFoam` (incompressible, steady,
  single-phase) with the **standard k-ε** model on the 2-D box mesh (`blockMesh` +
  `topoSet`, reused byte-for-byte from R2), moving top/bottom walls (6.06 / 6.00 m/s
  rescaled), inlet 0.10 m/s, outlet `p = 0`. Converged → the frozen carrier
  `U, phi, k, epsilon, nut`. This is the manual's *"flow yes ke yes … iterate 700"*.
  It is **decoupled from the moments** (the moments never feed back to the flow), so
  it **cannot be tuned to the answer** — it is answer-blind infrastructure.

- **STAGE 2 — the moments on the frozen field (graded).** Stage-1 `U/phi/k/epsilon`
  are mapped in and **frozen**; the case runs
  **`reactingTwoPhaseEulerFoamFrozen`** — a build of `reactingTwoPhaseEulerFoam`
  whose PIMPLE loop is reduced to `fluid.solve(); fluid.correct();` (alpha-continuity
  via MULES + `populationBalances_[i].solve()` with the constant kernel) and
  **omits `pU/UEqns.H`, `EEqns.H`, `pU/pEqn.H`**. `endTime = 25 s = 5τ`,
  `deltaT = 1e-4`. This is the manual's *"flow no ke no … moments yes … iterate"*.

**Solver source (frozen, pinned in `§D`):**
`cases/ansys_verification/VMFL034-R3/solver/reactingTwoPhaseEulerFoamFrozen/`
(`reactingTwoPhaseEulerFoamFrozen.C`, `createFields.H`, `createFieldRefs.H`,
`Make/files` → `$(FOAM_USER_APPBIN)`, `Make/options` = the stock reactingEuler libs).
The driver compiles it with `wmake` and records the binary hash before Stage 2.

### §SOLVER.1 FIX-UNTIL-RUNS (§2ay) — established, with evidence

**Claim: OpenFOAM CAN do frozen-flow constant-kernel QMOM/sectional aggregation.**

1. **The constant kernel is in this build and already ran.** `constantCoalescence`
   (`type constant; rate 2000 [m³/s]`) is compiled into
   `platforms/linux64GccDPInt32Opt/lib/libreactingMultiphaseSystem.so`
   (`constantCoalescence.C:addToCoalescenceRate` adds `rate_` of dim Volume/Time =
   β₀). **R2 itself ran this exact kernel for ~820 timesteps** (to `t≈0.082 s`)
   before dying — in drag, never in the population balance. The aggregation model is
   therefore **empirically proven** in-build.

2. **The R2 crash site is confined to the removed block.** `fluid.Kd()` (→
   `MomentumTransferPhaseSystem::Kd` → `dragModel::K()` → `SchillerNaumann::CdRe`)
   is invoked at `pU/pEqn.H:42` and via `fluid.momentumTransfer()` at
   `pU/UEqns.H:8`. The moment/continuity path does **not** reach it:
   `fluid.solve()` → `PopulationBalancePhaseSystem::solve()` → `twoPhaseSystem::solve()`
   (alpha continuity via MULES; the only interphase term is the **turbulent-dispersion**
   `DbyA`, guarded by `.found()`, not drag) **+** `populationBalances_[i].solve()`
   (`populationBalanceModel.C` — no drag call). Verified against the v2606 source.

3. **The frozen-flow solver COMPILES and RUNS clean.** The lane built
   `reactingTwoPhaseEulerFoamFrozen` (`wmake`, 343 KB binary) and ran an **ephemeral
   answer-blind smoke** on the R2 **S1 (16-group)** mesh + fields:
   **rc = 0, reached `End`, 5 timesteps, 0 momentum/pressure/drag solves, 85
   population-balance sizeGroup solves**, Sauter mean diameter and `Σ f_i = 1`
   computed, and `alpha.air`, `U.air`, `p`, `f0..f15.air.bubbles` all written at
   `endTime`. **No SIGFPE** — the exact point (drag domain error) where R2 died
   `rc 136`. The comparator then read this real frozen-solver output end-to-end (all
   guards fired; it correctly **refused** the 5-step non-converged read at the
   m0-calibration guard). This confirms **startup, stepping, field output and the
   removal of the R2 mechanism** — answer-blind, no gradeable moment produced.

**There is no acceptable-fail here:** OpenFOAM plainly *can* do the case; the frozen
flow is the manual's own procedure. `§2ay`'s "the only acceptable reason for a fail
is if OpenFOAM can't do the case" does not apply.

### §SOLVER.2 The defensive secondary (documented, not the primary)

`limitVelocity` (fvOption; `src/fvOptions/corrections/limitVelocity`) is available
should the **frozen carrier** itself need velocity bounding anywhere. It is a
documented secondary only; the primary root-fix is the frozen-flow re-scope, which
removes the live drag entirely. `limitVelocity` is **not** in the primary run.

---

## §4. THE GATE (band and verdict rule — UNCHANGED from R2; L-487)

### §4.2 The band — relative, uniform ± 0.76 %

`tol = q + d`, both relative: `q = 0.379 %` (the reference's honest uniform relative
quantisation, `0.0005/0.132`) and `d = 0.379 %` (numerical allowance, set equal to
`q`, never larger). `tol = 0.758 % ≈ ± 0.76 %` on every gated moment. The band was
fixed with no VMFL034-R3 number in existence (`§0`). **The frozen-flow re-scope does
not move it** — the manual's regime check cannot widen a gate (L-487).

### §4.4 The verdict rule (rule-5 ordered)

1. Strict completion (`§9`) fails on any level → **NOT A RESULT**.
2. Well-mixedness not met → **NOT A RESULT** (comparator refuses, exit 2).
3. Planted control (`§10`), the L-487 plant-design guard (`§10a`), the feed-moment
   guard, or the physical-range guard (`§N`) does not hold → **NOT A RESULT** (no
   number produced; comparator refuses, exit 2).
4. Any gated moment's size-group triple not `CONVERGING` → that moment **NOT A
   RESULT**; if any of m1–m5 is NOT A RESULT the case is **NOT A RESULT** (rule 5).
5. Otherwise, on the CONVERGING finest-level (S3 = 64 groups) values: **all five**
   gated moments m1..m5 inside ± 0.76 % → **PASS** (GCI printed per moment); **any**
   outside → **GATE FAIL**. m0 is reported beside the gate against 0.131774; a miss
   > 3 % REFUSES, never licenses a PASS.

### §4.5 THE LAB'S PREDICTION (stated before any graded run)

**The lab predicts PASS.** The frozen-flow QMOM constant-kernel aggregation in a
well-mixed CMSMPR is a case with a **known analytical steady state**; Ansys Fluent's
own QMOM lands every moment inside 0.7 % (Table .34.1, ratio 1.000–1.007). With the
flow decoupled exactly as the manual specifies and volume conserved by the sectional
feed (m3 exact by construction), the lab expects the **sectional** discretisation to
converge to the same steady state within the ± 0.76 % band on the finest (64-group)
level, with the largest residual on **m4/m5** (tail-truncation + sectional
resolution) and m3 essentially exact. The **discretisation risk** (not a PASS
certainty) is that the coarser levels may leave m5 marginally out of band and the
Roache triple must be CONVERGING for the verdict to stand (rule 5). This prediction
is the freeze's evidentiary content: it was fixed before any graded moment existed.

---

## §7. THE ROACHE TRIPLE REFINES THE SIZE GROUPS — `r = 2` on class count (UNCHANGED)

> **THE GATED QUANTITIES' DOMINANT DISCRETISATION ERROR IS SIZE-GROUP TRUNCATION.
> THE ROACHE TRIPLE REFINES THE NUMBER OF SIZE CLASSES `N_g` AT A CONSTANT RATIO
> `r = 2`, THE SPATIAL MESH AND THE FROZEN CARRIER HELD FIXED.**

| level | class count | role |
|---|---|---|
| **S1** | `N_g` = 16 (coarse) | triple |
| **S2** | `2·N_g` = 32 (medium) | triple |
| **S3** | `4·N_g` = 64 (fine) | triple — the gate is read here |

The concrete family is **`16/32/64`** (r = 2 exactly on class count; the base was
defended by measured feed reconstructions in R2 `§R.1`). The size range
`[0.45, 22.0]` (nominal) is held fixed across levels **and across the frozen
carrier** (the same Stage-1 flow is mapped to all three levels; only the sizeGroups
differ). Per moment, at `Fs = 1.25` (rule 5): a triple not monotone gets no GCI; a
triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` grades **NOT A RESULT**; only
`CONVERGING` moments are gate-eligible, read at S3 with GCI printed. **The comparator
asserts the ratio against the actual class counts and REFUSES a non-constant triple.**

---

## §9. STRICT COMPLETION (CLAUDE.md rule 4) + AGE GUARD

Binding on every level (S1, S2, S3); comparator **refuses, exit 2**, on any failed
clause. `rc = 0` (captured **inside** the detached wrapper); a standalone `End` in
the **Stage-2 solver** log (`log.reactingTwoPhaseEulerFoamFrozen`, resolved from the
Stage-2 `controlDict` `application`, never `log.blockMesh`); last written time ==
`endTime` (25); `alpha.air`, `U.air`, `p` and every `f<i>.air.bubbles` present at
`endTime`; and every `endTime` field **newer** than the case's own `0/alpha.air`
launch marker (the driver touches `0/alpha.air` **last** and asserts it newest;
refuses a pre-existing `0/` or time dir). **Note:** under frozen flow the carrier
fields (`U.air`, `p`) are unchanged in value but are **re-written** by
`runTime.write()` at `endTime`, so they are legitimately newer than the marker
(confirmed on the smoke).

---

## §10. THE PLANTED CONTROL (CLAUDE.md rule 3) — designed against the reduction (L-487)

The moment reduction is a weighted **sum over all N bins**, so a plant over the
**whole** reduction set cancels identically (L-487 failure 1, cancellation). The
comparator therefore perturbs a **PROPER SUBSET** of bins (`PLANT_SUBSET = [8, 9]`,
`PLANT = 3.21e-4`) in the outlet `f<i>` and requires the measured moment response to
equal the response computed from the frozen geometry the comparator holds
(`Δm_k = (α₂/κ)·PLANT·Σ_{i∈S} d_i^{k−3}`). `--selftest` proves three mutated readers
REFUSE (drop κ; wrong power `d²`; wrong moment power `d^{k+1}`), and the plant runs on
the **real** reader before any zero is trusted (confirmed on the smoke output).
**Refusal is exit 2 and writes no grading number.**

### §10a THE L-487 PLANT-DESIGN GUARD — makes the degenerate defect UNREPEATABLE

`_assert_plant_nondegenerate(ngrp)` **REFUSES (exit 2)** if `PLANT_SUBSET` is ever
the whole `ngrp`-bin reduction (it would cancel to a fixed shift `Δm_k` for **every**
input — including all zeros — and could not fail). This is L-487's *"a construction
that makes the defect unrepeatable, not merely fixed"*: the next editor cannot
silently reintroduce the cancellation. `--selftest` drives both the accepted
(proper-subset) and refused (whole-set) configurations.

---

## §N. THE PHYSICAL-RANGE GUARD (gate-blind realizability — new in R3)

`physical_range_guard(m)` **REFUSES (exit 2)** on physically impossible moments,
**referencing no manual target, no band, and no gate quantity** — a filter on the
*reading*, upstream of the band (R6-N4 pattern). A set of integer moments `m_k` of a
**non-negative** size distribution must be **(a)** strictly positive, and **(b)**
log-convex: Cauchy–Schwarz on adjacent moments gives `m_{k+1}² ≤ m_k·m_{k+2}` for any
positive measure. A measured moment set violating either is not the moment set of any
real particle population and cannot be graded. `--selftest` proves a valid set (the
manual moments) is accepted, a negative moment is refused, and a non-log-convex set
is refused. **It moves no gate quantity** (L-487): it cannot turn a GATE FAIL into a
PASS or vice-versa — only into NOT A RESULT, which is what rule 5 permits.

---

## §12. COST — the frozen-flow r = 2 triple 16/32/64

- **Method:** anchored on the **measured** frozen-flow smoke rate — **0.022 s/step at
  16 groups**, single rank, on this box (`§SOLVER.1`, ephemeral). The aggregation
  loop is ~N², so S1(16) ≈ 0.022, S2(32) ≈ 0.088, S3(64) ≈ 0.352 s/step (N²
  over-estimates, since the transport part scales as N, not N² — the estimate is
  conservative). At `endTime 25 s / deltaT 1e-4 = 2.5e5 steps/level`:
  S1 ≈ 1.5, S2 ≈ 6.1, S3 ≈ 24.4 core-h. Stage-1 carrier (single-phase steady,
  shared across levels) ≈ 0.5 core-h once.
- **Estimate:** **≈ 33 core-h** for the triple + carrier — **cheaper than R2's
  43.9** (no momentum/pressure/energy solve), as the frozen re-scope predicts.
  **Derived $ = $1.69** at $0.0513/core-h (**derived, not measured** — the box cannot
  read its billing, `COMPUTE_BUDGET_CHARTER §5`; the per-step rate is
  **reported-by-owner** from the smoke). Well under the $25 pre-authorised ceiling.
- **Caps (rule 12; an overrun STOPS the run, rc 124):** Stage-1 carrier = **60
  core-min**; per-level Stage-2 caps **S1 = 200, S2 = 750, S3 = 3000 core-min**
  (~2× each estimate); **RUNNING TOTAL cap = 3960 core-min** (66 core-h, 2× the
  ≈ 33 estimate). An overrun does not get a new budget.
- **Estimate-vs-actual ratio:** PENDING the graded run; filed to
  `docs/COST_CALIBRATION.md` at process completion (rule 12).

---

## §15. THE OUTCOMES, NAMED IN WRITING BEFORE COMPUTE

1. **PASS** — all five gated moments inside ± 0.76 % at S3, all size-group triples
   CONVERGING, `§9`/`§10`/`§10a`/`§N`/feed-guard/well-mixedness satisfied. GCI per moment.
2. **GATE FAIL** — any of the five converged gated moments outside ± 0.76 % (with GCI).
3. **NOT A RESULT** — completion, well-mixedness, a size-group triple not CONVERGING,
   the plant, the plant-design guard, the feed guard, or the physical-range guard failing.
4. **NOT A RESULT** (budget) — a `§12` cap fires (rc 124).
5. **NOT A RESULT** (solver death) — non-zero rc; a non-zero rc is a finding, not a retry.
6. **BLOCKED** — the Stage-1 carrier or the Stage-2 startup fails for a reason that is
   not a physics result.

---

## §D. GRADING-PATH PIN — COMPLETED AT THE FREEZE, NOT DEFERRED

The queue row (authored later, NOT by this lane) repeats this list verbatim so the
daemon can verify the pins without trusting this document.

| artifact | path | git blob |
|---|---|---|
| **grading_freeze** (comparator) | `cases/ansys_verification/VMFL034-R3/analyse_vmfl034_r3.py` | `5fc867d964250b27639362e20f43b0af69c4840c` |
| solver source (top-level) | `.../solver/reactingTwoPhaseEulerFoamFrozen/reactingTwoPhaseEulerFoamFrozen.C` | `405273b19dcf08641b9c555fae8ab04fe360d49b` |
| solver source (createFields) | `.../solver/reactingTwoPhaseEulerFoamFrozen/createFields.H` | `df7c20a798bbc3663575aee20c06e4058fdd2b20` |
| solver source (createFieldRefs) | `.../solver/reactingTwoPhaseEulerFoamFrozen/createFieldRefs.H` | `a8247c9e1cd5b5b240a57e1c0e31a07dfc5ce0e6` |
| solver Make/files | `.../solver/reactingTwoPhaseEulerFoamFrozen/Make/files` | `e2a515e3d7ffbdfe76ad7cd5f56d93fdaa9996e7` |
| solver Make/options | `.../solver/reactingTwoPhaseEulerFoamFrozen/Make/options` | `aba9ee616dc0999337b8bf8cab8287ae5ab24d5b` |

sha256 of the comparator's disk bytes:
`494d8ee48f483d26a1f605309846b2f41cf06f1e1b189dfac56472f7deeb4dd8`.

### §D.1 CASE-INPUT MATERIALISATION — the pre-compute step (rule 2)

The physics case inputs (mesh, `constant`, `system`, `0.orig`, and the frozen
`grids/{S1,S2,S3}` size-group instances) are **byte-identical to VMFL034-R2's frozen
inputs** (`§R.6`) and are reused unchanged. Before first graded compute (and named
here per rule 2, naming the run dir
`verification/runs/ansys_verification/VMFL034-R3/` that does **not** exist), the
supervisor/next lane materialises R3's case: **(1)** stage R2's frozen inputs (from
R2's freeze commit) into `cases/ansys_verification/VMFL034-R3/`, verified by blob
hash against that commit; **(2)** author the Stage-1 `simpleFoam` carrier setup
(single-phase k-ε on the same mesh) and the two-stage driver `run_vmfl034_r3.sh`
(compile the pinned solver, run Stage 1, freeze/map the carrier, run Stage 2);
**(3)** set `FREEZE_COMMIT` = the R3 case-input freeze commit at that freeze. A
GRADED run REFUSES while `FREEZE_COMMIT` is the placeholder. This freeze pins the
**prediction, the gate, the comparator and the solver source** — the entire
grading-decision path; the case-input staging is mechanical reuse of already-frozen
R2 material, verifiable by hash.

---

## §17. FREEZE CLAIM

When the supervisor commits this file it freezes it **before the graded run, before
the moment data, and before the reading**: no VMFL034-R3 graded solver has run
(`§0`), no VMFL034-R3 moment data exists, and no VMFL034-R3 moment has been read by
any comparator (the answer-blind smoke produced none). The lab's prediction (`§4.5`)
is on record. The grading path is fixed at the pre-registration commit and verified
by hashing the pinned comparator and solver source against their committed blobs
before grading (rule 2).
