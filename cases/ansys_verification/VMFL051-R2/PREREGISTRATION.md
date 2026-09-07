# VMFL051-R2 — Isentropic Expansion of Supersonic Flow Over a Convex Corner: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NO GRADED SOLVER EXECUTION HAS OCCURRED.** This file is frozen **before any
graded solve starts** (CLAUDE.md rule 2; `SUPERVISION_CHARTER.md` §3 check 4). One
**answer-blind smoke** preceded this freeze — an L1-only, scratch-directory
diagnostic that **never read the graded Mach value** (only peak-to-peak and
mean-*differences*, both value-blind) and never touched the R2 run root. It is
documented in §3 and is the data L-500 sanctions for choosing a lever after the
reflex fix is falsified.

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at
**2026-09-07T16:05:17Z**, read with `date -u` in the same invocation,
**`verification/runs/ansys_verification/VMFL051-R2/` does not exist** — `ls -d`
returned *No such file or directory* and `find` beneath it returned **0 files**.
No `blockMesh`, `topoSet` or `rhoCentralFoam` has run into that run root; no R2
mesh exists there. The answer-blind smoke of §3 ran under a **scratchpad**
directory, not this run root, and its scratch tree is not part of the graded case.

**Launch authorisation comes from the `ansys-verification-supervisor`** after its
own personal freeze verification and its own read of the comparator as a diff, and
**no agent message is Sanaa's consent** (CLAUDE.md rule 9). This freeze does not
authorise its own graded run; a launch-permission block for this case is on
Sanaa's desk and is **HELD**.

**Drafted 2026-09-07 by `ansys-lane-opus` (Opus) for the `ansys-verification`
team**, under `ANSYS_VERIFICATION_CHARTER.md` §5 and `VERIFICATION_CHARTER.md` §6.
This is the **successor to VMFL051 run 1** (register #4, `NOT A RESULT`). It is a
**re-run under one changed lever**, not a fresh case. `RESULTS.md` is written
afterwards in this directory and **does not revise this file**; departures land as
dated addenda at the foot, never by editing above.

---

## 0. What this successor is, and the one thing it changes

**VMFL051: Isentropic Expansion of Supersonic Flow Over a Convex Corner** — Ansys
Fluid Dynamics Verification Manual, Release 2026 R1, **pp. 165–166** (sidecar lines
4268–4335; title page verified against the PDF per CLAUDE.md rule 15: PDF p. 1 and
the `.txt` sidecar both read *"Ansys Fluid Dynamics Verification Manual … Release
2026 R1"*). Inviscid, compressible, ideal-gas supersonic flow (M₁ = 2.5) turns
around a convex corner (interior angle 195° ⇒ a 15° turn) through a **centred
Prandtl-Meyer expansion fan**. The manual's target post-expansion Mach number is
**3.2370** (Table .51.1).

**Run 1's verdict was `NOT A RESULT`** (`cases/ansys_verification/VMFL051/RESULTS.md`,
register #4): its Roache triple on the post-expansion Mach was **`OSCILLATORY`**
(3.2278606 / 3.2233427 / 3.2294356, R = −1.3486, increments changing sign), and two
of three levels failed run 1's snapshot-plateau clause. **Both fired independently;
either alone gives `NOT A RESULT`.** Notably L3's snapshot 3.2294356 sat −0.2337 %
from the target (inside the 0.5 % band on value), but a non-monotone triple is
`NOT A RESULT` whatever its value (rule 5).

**The ONE lever this successor changes:** the per-level gate value is the
**TIME-MEAN of `volAverage(Ma)` over the settled window**, not the single-endTime
**snapshot** run 1 graded. **Everything else is IDENTICAL to run 1** — the same
solver (`rhoCentralFoam`), the same Kurganov-Tadmor + vanLeer scheme, the same
three-level r = 2 mesh family, the **same endTime 7.0e-3 s**, the same sampling
zone, and — load-bearing — the **same gate, 3.2370 ± 0.5 %** (L-487: match the
reduction; do not widen a gate). The solve is **byte-identical** to run 1: every
case-input blob sha in §10 equals run 1's (verified). Only the reduction of the
recorded series changed.

**This is a statement about this lab's `rhoCentralFoam` against the manual's
Prandtl-Meyer reference. It is NOT a statement about Ansys** — this box has no
Fluent and no CFX; the Fluent/CFX archives were not opened.

## 1. The manual, and run 1's still-standing findings

The manual quotes, the derived gas (γ = 1.3990093734749485 from the manual's own
Cp = 1006.43 J/kg-K and MW = 28.966), the closed-form reference values, and the
**three manual defects** (Defect 1: the "incompressible" contradiction; Defect 2:
3.2370 is not the exact PM value at any consistent γ, carrying ≈0.005 % table
rounding; Defect 3: Table .51.2's mislabelled column) are **carried verbatim from
run 1's frozen `PREREGISTRATION.md` §1–§2 and §1a** and are **not re-derived here**;
nothing about them changed and this successor does not touch run 1's frozen file.
All three remain **`NOT FILED`** (contacting Ansys is Sanaa's alone). The gate is
against the manual's printed target **3.2370** (Table .51.1); the closed-form exact
value for the manual's gas, **M₂_EXACT_GAS = 3.2355411372251863**, is a tighter
DIAGNOSTIC only, printed beside the gate and never able to overturn it.

## 2. The gas, the reference values, and which one the gate is against — UNCHANGED

Identical to run 1 (its §2): the gate is against the manual's printed target
**3.2370**; the diagnostic is against **M₂_EXACT_GAS = 3.2355411372251863**
(γ = 1.3990093734749485). The comparator recomputes the Prandtl-Meyer reference by
bracketed bisection and **asserts it against the frozen literals** so a later edit
cannot move it (`--selftest` [C], fired: 46 checks, 0 failures, zero compute).

## 3. THE DIAGNOSIS — why the triple oscillated, argued A-PRIORI and BEFORE the graded run (the crux)

**L-500 governs this section.** A base OSCILLATORY triple is a FINDING to
DIAGNOSE, not a mesh to rebuild on reflex, and it must not be "fixed" by dropping
the level that flipped (rule-2 anti-circularity). The diagnosis below distinguishes
(a) iterative/round-off or temporal noise, (b) a functional-definition sensitivity,
and (c) genuine non-convergence / mesh non-similarity — **before** any graded run,
and the graded Mach value was **never read** in reaching it.

### 3.1 What is established without any new run (from run 1's own record)

- **The mesh is self-similar by construction.** Every level doubles all three cell
  counts and the block map is linear, so h halves exactly and r = 2 is **not
  inferred from a cell count** (run 1 §4.2; blockMesh birth-certified). **Genuine
  mesh non-similarity — reading (c) — is ruled out by construction.**
- **The finest level DID settle; the coarse levels did NOT.** Run 1's snapshot
  plateau peak-to-peak: L1 6.240e−03, L2 3.535e−03, **L3 8.549e−04** (L3 alone
  passed run 1's 1e−3 clause). The residual unsteadiness **falls with refinement**.
- **The level-to-level differences are the same order as the coarse-level residual
  unsteadiness** (run 1 §3): |d32| = 4.518e−03 (0.72× L1 ptp), |d21| = 6.093e−03
  (1.72× L2 ptp). A difference that does not exceed the wobble of the signals it
  differences cannot be cleanly attributed to grid refinement — the L-500 signature
  that the triple is measuring **noise, not discretisation error**.

### 3.2 The answer-blind smoke, and what it FALSIFIED and CONFIRMED

An L1-only smoke was run to a generous endTime (2.8e−2 s = 16 flow-throughs) in a
**scratchpad** directory (never the R2 run root). It read **only** peak-to-peak
(max−min) and mean-*differences* between windows — **the graded Mach value was
never read or recorded** (value-blind, per L-500's prohibition on running a level,
reading the graded quantity, and then picking a lever). All figures below are
value-blind and are the **documented data** L-500 permits for choosing a lever.

1. **More endTime does NOT settle the coarse level — the reflex temporal lever is
   FALSIFIED.** L1's plateau peak-to-peak is **flat at ~6.2–6.7e−3 in Mach across
   endTimes from 7e−3 to 2.8e−2 s** (7e−3 → 6.24e−3; 1.4e−2 → 6.55e−3; 2.1e−2 →
   6.69e−3; 2.8e−2 → 6.69e−3). The oscillation is **temporally persistent**, not a
   decaying transient. Increasing endTime is therefore **not** the lever.
2. **The oscillation is TEMPORAL, not a spatial-reduction artefact — the dated
   plan's downstream-LINE lever (reading b) is FALSIFIED.** The strictly-inner zone
   carries an **identical** peak-to-peak (inner 6.6892e−3 vs gate 6.6865e−3 at
   2.8e−2). A different SPATIAL reduction (the dated plan's downstream line) would
   carry the **same** temporal noise, and a line averages **fewer** cells, so it
   would be **noisier**, not steadier. The gate/inner spatial offset is a small
   **stable** +2.23e−3 (0.069 % of Mach), not an oscillation.
3. **The oscillation is mesh-convergent numerical noise.** Its amplitude falls with
   refinement (L1 6.6e−3, L2 3.5e−3, L3 0.85e−3) — it converges away. It is the
   signature of Kurganov-Tadmor central-scheme noise seeded at the **corner
   singularity** (a single point at which the exact solution is not
   differentiable), radiating into the far field on the coarse mesh.
4. **The TIME-MEAN of the gate signal is STABLE and well-defined.** Over averaging
   windows from the last 20 % to the last 60 % of the run the L1 time-mean moves by
   only **±1.2e−4 in Mach**, and mean(last 50 %) vs mean(last 25 %) agree to
   **7.6e−5** (both ≪ the 0.5 % = 0.0162-Mach band). The early startup transient is
   excluded: mean(first 20 %) vs mean(last 50 %) differs by **0.546** (the flow
   starting from uniform M = 2.5), so the last-half window is safely past it.

### 3.3 The DIAGNOSIS and the LEVER it selects

**Diagnosis: category (a) — noise, not mesh non-similarity — with the precise
sub-mechanism a temporally-persistent, mesh-convergent numerical oscillation.** Run
1's comparator graded a **single-endTime SNAPSHOT** of this oscillation, sampling
it at a random phase; the coarse levels' large-amplitude snapshots landed at
different phases, producing the sign-flipping non-monotone (`OSCILLATORY`) triple.
Reading (c) is ruled out by mesh construction; reading (b) is falsified by the
identical inner/gate peak-to-peak.

**Lever: replace the SNAPSHOT reduction with a TIME-MEAN over the settled window.**
This is the transient-solver analogue of VMFL010-R2's single-lever fix (there:
tighten `residualControl`, re-grade the identical levels). Here the convergence
lever for a stationary numerical oscillation is **time-averaging**, and the smoke
proves the time-mean is the stable, mesh-convergent observable. The lever:

- **keeps ALL THREE mesh levels** (does not drop the flipped level — L-500/rule 2);
- **keeps the same spatial gate zone** (does not adopt the falsified line lever);
- **keeps the same endTime 7.0e−3 s** (the smoke proves more time does not help);
- **keeps the gate 3.2370 ± 0.5 % UNCHANGED** (L-487);
- is a **single measurement/reduction lever**, and its settledness test changes in
  lockstep (§5) because you cannot apply a snapshot-plateau test to a time-mean —
  they are the settledness of the **same observable**, one lever, not two.

**Why not a numerics lever (more dissipative reconstruction / lower maxCo).**
Considered and declined: it would change the **solver being verified** (a
more-dissipative scheme, departing from the lab's F3-proven Kurganov + vanLeer
set), is not guaranteed to remove the corner-seeded noise, and is a larger,
physics-altering change. The time-mean leaves the physics untouched and extracts
the converged mean the smoke has already shown to be stable — the least-invasive,
most defensible lever.

**No prediction is registered of what the time-mean triple will be.** The three
time-means are computed at grade time; if the triple is `CONVERGING` the gate
decides `PASS`/`GATE FAIL`, and if it is still non-monotone the verdict is
`NOT A RESULT` (honest, never rescued by dropping a level or widening the band —
L-500). The finest level's graded value was **not** read to pick this lever.

## 4. Geometry, mesh levels, endTime — ALL UNCHANGED from run 1

Two-dimensional planar slab (one cell thick, `empty`), corner at the origin, wall
turning away 15°, inlet x = −0.3, outlet x = +1.2, top y = +0.65 (the leading Mach
line leaves through the supersonic outlet and never reaches the top — no reflection
by construction). Three levels, refinement ratio 2 exact by construction:

| level | cells | h (m) |
|---|---|---|
| `L1_120x52` | 6,240 | 0.0125 |
| `L2_240x104` | 24,960 | 0.00625 |
| `L3_480x208` | 99,840 | 0.003125 |

**endTime = 7.0e−3 s at every level, UNCHANGED** (4.049 flow-throughs at the inlet
speed U₁ = 867.72872 m/s). All geometry/mesh/time dictionaries are byte-identical to
run 1 (§10 blob shas match run 1's).

## 5. THE REDUCTION AND THE SETTLEDNESS TEST — the changed clause, fixed a-priori

**THE REDUCTION.** The per-level gate value is the **time-mean of `volAverage(Ma)`
over the last `WINDOW_FRAC = 0.50` of rows** of the `gateMach` series — the settled
window ≈ [3.5e−3, 7e−3] s ≈ 12 oscillation periods, past the ~2-flow-through
startup transient. `volAverage(Ma)` is written **every timestep** (controlDict,
unchanged), so the window is dense. The gate value M_lab is the L3 time-mean.

**THE SETTLEDNESS TEST (replaces run 1's snapshot-plateau clause; can only produce
`NOT A RESULT`, never a `PASS`).** A time-mean is settled iff it is **insensitive
to the averaging-window length**:

> **|mean(last 50 %) − mean(last 25 %)| ≤ `TOL_STAT` = 5.0e−4** (in Mach), per level.

**Why this is the correct test, and NOT a widened band.** Run 1's clause required
the *snapshot* series to be flat (peak-to-peak < 1e−3) — the right test when a
snapshot is graded. This successor grades a *time-mean*, whose settledness is that
the **mean has converged**, not that the instantaneous signal is flat. A mean still
in transient fails window-insensitivity strongly (the smoke measured
|mean(first 20 %) − mean(last 50 %)| = 0.546); a stationary-oscillation mean passes
it (the smoke measured 7.6e−5 at L1, the worst level). **`TOL_STAT` sits between
them by construction: 6.6× above the worst settled value and ~13× below the
oscillation amplitude.** The 0.5 % gate is **not** touched, no level is dropped, and
the change is the settledness of the graded observable — one lever with §3's
reduction (L-500; rule-5 one-way street).

**Declared DIAGNOSTICS, never the gate.** The oscillation peak-to-peak and the
approximate number of periods per window are reported per level (so the noise is
visible); the inner-zone consistency clause is carried on the **time-means**
(|⟨Ma⟩_gate − ⟨Ma⟩_inner| / ⟨Ma⟩_gate > 1e−2 at L3 ⇒ `NOT A RESULT`; the smoke
shows this is ~6.9e−4, comfortably inside); and the two isentropic Mach
re-derivations from window-mean ⟨p⟩ and ⟨T⟩.

## 6. THE VERDICT ORDER (CLAUDE.md rule 5), in its stated order

1. **any level whose time-mean is NOT settled** (window-insensitivity > `TOL_STAT`)
   or failing any completion clause of §8 ⇒ **`NOT A RESULT`**; **and** the
   inner-zone clause at L3 ⇒ **`NOT A RESULT`**;
2. **Roache triple on the three time-means** `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/
   `EXACT` ⇒ **`NOT A RESULT`**, with the values, R, increments and order printed
   and **no GCI quoted**;
3. **`CONVERGING`** ⇒ **`PASS`** inside the 0.5 % band else **`GATE FAIL`**, GCI at
   Fs = 1.25 and the Richardson extrapolation printed.

**A GATE-BLIND PHYSICAL-RANGE REFUSAL** (references neither the ±0.5 % band nor
3.2370): each level's time-mean Mach must be finite and in the physical supersonic
range **(1.0, 20.0)** or the comparator **refuses (exit 2)**. The gate can only turn
a `PASS` or `GATE FAIL` INTO `NOT A RESULT`, never the reverse. All classifier
states and both settledness outcomes are exercised by `--selftest`.

## 7. Planted-zero controls (CLAUDE.md rule 3; L-487) — three, none skippable

The comparator **exits 2** if any fails; the run tree is **never modified** (every
plant is written into a temporary copy). Because the gate reduction is now a
**time-mean**, the plant is designed **against the mean** (L-487: sum/mean ⇒ plant a
**PROPER SUBSET**, because a whole-set plant shifts the mean by the plant
identically and could not fail). The comparator **REFUSES the whole-set (inert)
configuration** so the defect cannot be silently reintroduced.

| id | reader under test | plant (proper subset) | expected & refusal |
|---|---|---|---|
| **PZ-1** | the gated `.dat` **time-mean** reader | +1.234e−3 Mach on the **second half** of the window rows of a copy | mean must shift by plant × (n_planted/n_window); refuse if that differs by > 1e−12, or if the subset is the whole window |
| **PZ-2** | the `Ma` **field** reader on disk | +7.77e−2 Mach on the **first half** of the field cells of a copy | field mean must shift by plant × (n_planted/n_total) to 1e−9; refuse if the field is `uniform`, or if the subset is the whole field |
| **PZ-3** | the reference computation itself | +5° turn | solved M₂ must satisfy ν(M₂)−ν(M₁)=turn to 1e−9° and move by > 1e−6 |

**The "known-bad / can-say-no" arms are present and fired**: a **drifting** series
is correctly judged NOT settled (window-insensitivity > `TOL_STAT`); a
**whole-set** plant is refused as the inert L-487 configuration; a **subsonic /
absurd** Mach triggers the gate-blind physical-range refusal. PZ-2 additionally
requires a **non-uniform** field and reports its min/max/mean — the demonstration
that the comparator can read a **non-zero out of the Mach field on disk**.
**`--selftest`: 46 checks, 0 failures**, on fixtures in the real file formats; the
reader and PZ-1's proper-subset plant were additionally driven on the **real** L1
smoke `.dat` (plant shift 6.17e−4 expected, 6.17e−4 seen, error 3.5e−16), value-blind.

## 8. Strict completion (CLAUDE.md rule 4), with the completion basis stated

The comparator refuses (exit 2) on any failed clause and never grades a partial run.
The two departures are carried verbatim from run 1 (declared, tighter-or-equal):

| clause | as checked here |
|---|---|
| **C1** `rc = 0` | `RUN_RC.txt` reads `rc=0` (the SOLVER's own rc, captured inside the driver) |
| **C2** an `End` line | `^End$` in `log.rhoCentralFoam` |
| **C3** last time == endTime | **APPLIES** to this transient solver in DEPARTURE-1 form (below) |
| **C4** fields present at endTime | `T U p rho Ma` — this case's own list |
| **C5** `ExecutionTime` count == endTime | DEPARTURE 2 (below): one `ExecutionTime` per `Time` line, > 0 |
| **C6** age guard | STRICTER: every endTime field newer than the newest file in the case's own `0/` |

**Completion basis — the last-time clause DOES apply here (unlike the steady
`residualControl` cases).** `rhoCentralFoam` is transient and stops **at** endTime
(`stopAt endTime`), so C3 is meaningful — the solver writes at the frozen endTime,
it does not stop earlier on a residual criterion. **DEPARTURE 1**: because
`adjustTimeStep yes`, the adaptive step overshoots endTime by a fraction of a step,
so the literal equality is replaced by **|t_last − endTime| ≤ maxDeltaT (1e−5 s
against 7e−3 s)** and the log's final `Time =` agreeing with the last time
directory to 1e−12 relative. **Verified in the smoke**: t_last = 0.0280005 for
endTime 0.028 — overshoot 5e−7 s, well inside maxDeltaT. **DEPARTURE 2**: the
literal "ExecutionTime count == endTime" is a steady-iteration clause and cannot
hold for an adaptive-step transient solver; the invariant it protects (the log is
not truncated mid-step) is checked directly as one `ExecutionTime` per `Time` line.

The driver's own guards refuse into any pre-existing level directory, refuse unless
the pre-registration **and** the comparator on disk are **byte-identical to their
HEAD blobs** (freeze-pin, rule 2), refuse if `topoSet` left either sampling zone
empty, and enforce the cap with `timeout` (seconds = cap × 60 / ranks).

## 9. Cost (CLAUDE.md rule 12) — basis is run 1's MEASUREMENT of the identical solve

The R2 solve is **byte-identical to run 1**, so the cost basis is run 1's own
**measurement** on this box (`cases/ansys_verification/VMFL051/RESULTS.md` §7 and
`docs/COST_CALIBRATION.md` C-50), far stronger than an a-priori estimate.

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| **basis** | run 1 MEASURED, this exact case, this box: solver CPU L1 7.71 s, L2 59.31 s, L3 467.50 s (= 8.9 core-min idle); wall (with contention) L1 0.15, L2 3.45, L3 19.72 core-min; total **23.32 core-min** |

**Per-level caps (core-min):**

| level | point estimate (run 1 measured wall) | per-level ceiling |
|---|---|---|
| L1 | 0.15 | 2 |
| L2 | 3.45 | 8 |
| L3 | 19.72 | 26 |
| **total (the ENFORCED running cap)** | **23.32** | **28** |

The **enforced cap is a running total of 28 core-min** (`timeout` = 28 × 60 / ranks
s), UNCHANGED from run 1 which used 83.27 % of it. An overrun **stops the run**
(rc 124) and it does not get a new budget; a re-run is a **new rung**, moving no
gate. Idle-box point estimate is 8.9 core-min; the 23.32 figure includes ~14.4
core-min of measured **contention** (run 1 C-50), named separately, never netted.

| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). Core-min are run 1's **measurement** of the identical solve. |
|---|---|
| dollars at the point estimate (23.32 core-min) | **$0.01994 derived** |
| dollars at the cap (28 core-min) | **$0.02394 derived** |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; a blanket is not a per-item read (rule 9) |

**Answer-blind smoke cost (this drafting lane, already spent):** one L1 run to
2.8e−2 s, ~27 s wall = **0.45 core-min**, plus two L1 runs' worth of parsing;
scratch-only, outside the graded budget. Reported, not absorbed.

**Calibration at completion (rule 12):** the run-and-grade lane compares actual
core-min (from `RUN_RC.txt`/`COST.txt`) against the 23.32 point estimate, attributes
the gap (contention/waste/misprediction, waste named separately), and appends one
row to `docs/COST_CALIBRATION.md`. A completion report without that row is incomplete.

## 10. The grading path, frozen (VERIFICATION_CHARTER §2d)

The comparator, the driver and the whole case tree are committed at the R2 freeze
commit; at analysis time the grading path is re-hashed against these blob shas, and
`grade_vmfl051_r2.py --verify-frozen <commit>` **REFUSES (exit 2)** if the file on
disk is not byte-identical to the committed blob. **No threshold, band, reference
value or plant constant in the comparator is settable from the command line.**

| what | path under `cases/ansys_verification/VMFL051-R2/` | committed blob sha |
|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl051_r2.py` | **`582dd1c81f254267f6a0123d6ad5f9067d5aa340`** |
| driver | `run_vmfl051_r2.sh` | `0e1b3d4b7994231959bfd4dad87d696c58f5dea1` |
| **the frozen sampling rule** (identical to run 1) | `case/system/topoSetDict` | `e594d35fe9aa8accb77bde4a8f3fd335ec2e31d8` |
| blockMeshDict template | `case/system/blockMeshDict.template` | `7557bfec1e18f6956e3ed09185f45627af4c32a0` |
| controlDict template (endTime + FOs) | `case/system/controlDict.template` | `48607d91d9c79fda5988430e766a663b5a6d7b4f` |
| fvSchemes | `case/system/fvSchemes` | `25d6f166ffae418d428473f5aeae2e17e8d0bfc6` |
| fvSolution | `case/system/fvSolution` | `885bb5f6ddccc67376a3171ace339bc476f5302b` |
| `0/U` | `case/0/U` | `9d8f63f1ffcb7d5fb652542cd0050261aef963b9` |
| `0/T` | `case/0/T` | `84d6430dc9f32f458141d3dcf2335b98418beca3` |
| `0/p` | `case/0/p` | `3da7331987499f8863e4a7667fd09dec87c4f428` |
| thermophysicalProperties | `case/constant/thermophysicalProperties` | `3734a5a0d9967cff4b1411b359e8ed59d17ae9f6` |
| turbulenceProperties | `case/constant/turbulenceProperties` | `5459d691884eeba27e9759a8bc32871ea262edab` |

**Every case-input blob sha above equals run 1's** (verified with `git hash-object`
against `cases/ansys_verification/VMFL051/case/`) — proof the solve is identical and
that **only the comparator differs**. Run outputs go to
`verification/runs/ansys_verification/VMFL051-R2/<level>/`; the grading JSON is
`verification/runs/ansys_verification/VMFL051-R2/GRADING_VMFL051_R2.json`.

## 11. What CANNOT be verified before the freeze — stated plainly

No **graded** R2 solver has run into the R2 run root, which does not exist (§ top).
What HAS fired, all pre-freeze: the comparator's `--selftest` (**46 checks, 0
failures**, zero solver compute); the reader and PZ-1's proper-subset plant driven
on the **real** L1 smoke `.dat`, value-blind; and the answer-blind smoke of §3
(L1-only, scratch, value-blind). Four things this successor has **not** seen, each
requiring the supervisor's separate launch authorisation:

1. **The three levels' time-mean triple.** Computed only at the graded run; **not
   read** here (choosing the lever from it would be fitting — L-500).
2. **That L2's and L3's time-means are settled at 7e−3 s.** L3 already plateaued in
   run 1 (ptp 8.5e−4) so its mean is settled; L1's mean is settled per the smoke
   (window-insensitivity 7.6e−5); L2 sits between and is judged by the frozen
   settledness clause at grade time, not asserted here.
3. **That the graded run reproduces run 1's byte-identical solve** under the R2
   freeze-pin and age guard. The case inputs are proven identical (§10); the run is
   produced fresh under the R2 driver.
4. **Whether the time-mean triple is `CONVERGING`.** If it is not, the verdict is
   `NOT A RESULT` — no gate, band or cap moves.

## 12. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (rule 1). `PENDING` here means **not yet run** and never softens a
`GATE FAIL`. Nothing about Ansys, Fluent or CFX. Nothing about p₁ or T₁ (the gated
quantity is independent of both). Nothing about the γ = 1.4 alternative (run 1's
declared blind spot: the gate cannot distinguish γ = 1.3990094 from γ = 1.4). Only
a `PASS` is a credential; a `GATE FAIL` or `NOT A RESULT` is a finding, never
softened. **The lever is the time-mean reduction and nothing else; the gate is
3.2370 ± 0.5 %, unchanged and unchanged-able at this freeze.**
