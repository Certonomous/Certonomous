# VMFL072-R4-A — PRE-REGISTRATION (DRAFT, NOT YET FROZEN)

**STATUS: DRAFT. UNTRACKED. NOTHING HERE IS FROZEN AND NO SOLVER MAY LAUNCH ON IT.**
Committing this file *together with* its comparator, driver, apply script and
`base/` inputs **is** the freeze (`CLAUDE.md` rule 2). The freeze must exist, and
its sha named in the launch record, **before** the first solver starts. The
supervisor performs the `SUPERVISION_CHARTER` §3 check-1 (comparator diff, read as
a diff) and check-4 (pre-registration committed before compute) **personally**;
this lane's own `--selftest` is evidence, not that read.

Authored by an `ansys-lane-opus48` lane for the `ansys-verification-supervisor`.
Design authority for the *strategy* is the supervisor's decision record
`docs/ansys_verification/VMFL072_R4_FIX_DECISION.md` (2026-09-11). This document
does not redesign that strategy; it pins the numbers the freeze requires.

---

## §1. WHAT R4-A IS, AND IS NOT

R4-A is the **diagnostic control that VMFL072-R3 never had**. R3-L3 (256×64)
died `rc=136` SIGFPE in `DILUPreconditioner::calcReciprocalD`, reached via
`PBiCGStab::solve` from `kinematicThinFilm::evolveRegion()`
(`velocityFilmShellFvPatchVectorField::updateCoeffs()`). The R3 controls B2 and C1
completed, but B2 moved **three** variables at once relative to L3 (`H_IN`,
`U_IN`, `DELTAT`), so it establishes only that the 256×64 mesh is *not
intrinsically fatal* — not which knob lets it survive.

- R4-A moves **exactly one knob, the precursor film thickness `h0`**, at **fixed
  256×64 grid** with `U_IN` and `DELTAT` **pinned to L3's values** (decision §3
  R4-A). It answers one question: *does precursor thickness alone let 256×64 reach
  `endTime`, and if so does the film-thickness answer stay in the case's band?*
- It adds a **passive observer** of the minimum film thickness and maximum film
  velocity per timestep. The observer **alters no field** — see §4; it is a parse
  of stdout the solver already writes.
- It is **NOT** a clip/floor on film height, and **NOT** a DILU→diagonal
  preconditioner swap. Both are forbidden by the decision record §5: they suppress
  the fault by hiding the state that causes it. **The crash is the measurement.**
- It is **NOT** an upstream filing. Rule 7 stands: submissions parked, nothing
  leaves the box, no defect-report draft exists or is being written.

## §2. THE ONE KNOB, AND EVERYTHING THAT IS PINNED

`h0` is set in `base/0.orig/U`, boundary `film`, `velocityFilmShell` (R3 hard-coded
`h0 1e-5;` and `deltaWet 1e-5;`). It enters the solver at **two source sites**
(installed source, verified in R3 §3.8):

- `kinematicThinFilm.C:159` `h_ = max(h_, h0_)` — the post-solve floor;
- `filmTurbulenceModel.C:157` `Cw = 3·mu/((h + h0)·rho)` — the laminar
  `quadraticProfile` friction denominator. `Cw.clamp_max(5000)` does **not** catch
  a *negative* `(h+h0)`, so a transient undershoot below `−h0` poisons the diagonal
  and is the proximate cause of the `calcReciprocalD` SIGFPE.

`deltaWet` tracks `h0` (R3 convention `deltaWet == h0`). **The single registered
knob is `h0`; `deltaWet` is set equal to it and is not an independent variable.**

**PINNED at L3's values for every rung (from `apply_level.sh` R3 level table):**

| quantity | pinned value | source |
|---|---|---|
| **`RANKS`** | **`1` (serial, registered)** | §8 — R3 ran serial; the ladder is cheap |
| grid `NX×NY×NZ` | `256 × 64 × 1` | R3 L3 |
| `H_IN` (inlet film height) | `7.1084204656e-04` m | R3 L3 (= 1.30 δ_N*, L-487 over-thick inlet) |
| `U_IN` (inlet film velocity) | `0.537381243` m/s | R3 L3 |
| `DELTAT` | `1.25e-03` s | R3 L3 |
| `WRITEINTERVAL` | `40` | R3 L3 (→ 200 written dirs, endTime 10.0 exact) |
| `endTime` | `10.0` s, 8000 steps | R3 L3 |
| property closure (Γ,μ,ρ,…) | R3 §2.5, unchanged | — |
| `Cf` | `0` | R3 §3.3 |

Because `U_IN` and `H_IN` are both pinned, Γ = ρ·h_in·U_in = 0.381 kg/m/s is pinned
too, so `q = Γ/ρ` is pinned and the RHS of the film balance is a **frozen constant**:

```
h²(h + h0) = 3·ν·q / g_s  =  δ_N³  =  1.664792e-10 m³      (R3 §2.4, all pinned)
```

**Limb B's reference dN*(h0) tracks h0** and is nothing but the exact steady
discrete state the solver admits at that h0 — the same non-circular construction
R3 used (R3 §2.4: "δ_N* defined as the solver's own exact state … a change in h0
leaves Limb B exact"). Per rung the comparator Newton-solves the frozen balance for
that rung's `h0`. This is the sense in which **exactly one knob moves**: `h0` moves;
`H_IN`, `U_IN`, `DELTAT`, grid and closure do not; and the reference is a *function
of* the one knob, not an independent second knob.

## §3. THE h0 LADDER — ANSWER-BLIND, AND WHY THESE THREE

Two bounds are knowable **before any run**, from the frozen band and prior disk
evidence — neither is read off an R4-A result, so the choice is answer-blind:

- **Survival lower bound.** 256×64 is *known to crash at h0 = 1e-5* (R3-L3, on
  disk). R2 crashed at h0 = 1e-7. So any surviving h0 is **> 1e-5** on present
  evidence.
- **Answer-retention ceiling.** dN*(h0) leaves the frozen Limb-A band
  `[0.543234, 0.566766]` mm (§5) at its lower edge when **h0 ≈ 2.09e-05 m**
  (dN*(2.09e-5)=0.543234 mm, Newton-solved). Above that ceiling the *exact* answer
  is out of band regardless of survival, so such an h0 can never satisfy the
  retention half of the gate.

The "survive **and** retain" window is therefore at most the sub-octave
**(1e-5, 2.09e-5] m**. The ladder samples that window plus one crash-side control,
all within the decision record's "factor of 10 of 1e-5" abandonment window
`[1e-6, 1e-4]`:

| rung | `h0` (m) | dN*(h0) (mm) | in Limb-A band? | in survive-and-retain window? | role |
|---|---|---|---|---|---|
| **A1** | `5.0e-06` | 0.548453 | yes | **no** (below the 1e-5 floor) | directional / **monotonicity** control; outcome NOT pre-asserted |
| **A2** | `1.5e-05` | 0.545160 | yes | **yes** | interior of the window — a pivot rung |
| **A3** | `2.0e-05` | 0.543528 | yes | **yes** (just under the 2.09e-5 ceiling) | upper edge of the window — a pivot rung |

**⚠ SURVIVAL MAY BE NON-MONOTONE IN h0 — a named alternative, registered before the
run.** The intuition "larger h0 = higher floor = more protective" is **only half the
physics**, and R4-A does not rest on it. The *same* h0 sits in the friction
denominator `Cw = 3·mu/((h + h0)·rho)`: a **larger** h0 gives a **smaller** `Cw`, i.e.
**less** velocity damping, i.e. **more** exposure to the velocity runaway
(`max_magU`, §4) that is the proximate cause of the crash. Floor-effect (protective,
rising h0) and friction-effect (de-stabilising, rising h0) pull in **opposite
directions**, so survival need not be monotone in h0 and A3 is not guaranteed to be
the safest rung. **Both orderings are anticipated:** if survival rises with h0 the
floor dominates; if it falls, the friction term dominates; a non-monotone result
(e.g. A2 survives, A3 does not) is a legitimate, pre-registered outcome, not a
surprise. **A1 (5e-6, below the window)** is therefore registered as a *directional
control on the monotonicity question* — its outcome (crash or survive) is **not
pre-asserted**; it tells us which effect dominates on the thin side.

**Why h0 = 1e-5 is NOT a rung.** Its crash and its observer trace already exist on
disk: `verification/runs/ansys_verification/VMFL072-R3/L3/log.pimpleFoam` records,
at the last step before the fault, `Film h min/max = (1e-05 0.00913667…)` and
`Film mag(U) min/max = (… 4.22121389542e+13)`. That trace is cited here as prior
evidence (§4); re-running it would spend a rung on a known outcome.

**Why h0 = 1e-4 is NOT a rung.** dN*(1e-4) = 0.518720 mm is **already below the
band floor** (−5.71 % vs Nusselt), so a 1e-4 rung could only ever *fail* retention;
it carries no information the 2.09e-5 ceiling does not.

**All three rung references are in-band by construction** (I chose h0 below the
ceiling). Consequence: *in the viable window, survival is the pivotal question and
answer-retention is guaranteed in-band* — a surviving rung is Limb-B exact and
Limb-A `GATE REACHED`; a crashing rung is `NOT A RESULT` on the answer and a
positive datum on the mechanism.

**Why three points are sufficient here — and what they are and are not sufficient
FOR.** Three rungs cannot prove "no h0 anywhere survives." They do not need to. The
survive-and-retain window is **bracketed on both sides by facts knowable before the
run**: below by the crash floor (256×64 crashes at h0 = 1e-5, on disk) and above by
the retention ceiling (dN* leaves the band at h0 ≈ 2.09e-5). That bracket is the
sub-octave **(1e-5, 2.09e-5]**, and **A2 (1.5e-5) and A3 (2e-5) are the two rungs
inside it** — A1 (5e-6) is below it. So the abandonment question is posed over a
*bounded* interval that two interior points sample well, not over the whole real
line. **Abandonment criterion, stated precisely (supersedes the loose wording of
decision §4):** the constant-precursor approach is **ABANDONED for VMFL072** if
**neither in-window rung (A2, A3) survives in-band**. A1 surviving would be a *bonus*
survivor below the window, informative about monotonicity (above), but it is **not
the pivot** — the pivot is A2/A3. If A2 or A3 survives in-band, its h0 is carried to
R4-B (the 512×128 scaling test, a separate freeze). Whether to add a third in-window
point is a design call reserved to the supervisor's check-1.

## §4. THE OBSERVER — PASSIVE, ALTERS NO FIELD

The decision record asks for "min hf_film per timestep, written to its own
artifact … it must not clip, floor or otherwise alter any field." **The solver
already writes this to stdout**, once per timestep, from the film model:

```
Film h min/max        = (<min_h> <max_h>)
Film mag(U) min/max    = (<min_magU> <max_magU>)
```

The observer is therefore a **read-only parse of the captured `log.pimpleFoam`**
into `min_hf_film.tsv` (`Time  min_h  max_h  min_magU  max_magU`). It runs after
(or streams alongside) the solver and **cannot alter a field** because it never
touches the case — it reads the log. This is stronger than an in-solver
functionObject, which would at least share the solver's address space.

**⚠ A measured limitation the supervisor must weigh (check-1).** The post-solve
floor `h = max(h, h0)` means `min_h` is **pinned at the rung's own h0** and *cannot*
reveal sub-floor dewetting — at the R3-L3 fault `min_h` reads exactly `1e-5`, the
floor, not zero. The dewetting instead manifests as the **velocity runaway**:
`max_magU = 4.22e+13` m/s at the same step. So the observable that actually measures
the pathology is **`max_magU`**, not `min_h`. `min_h` confirms only that the floor
engaged. The observer therefore records both, and the diagnostic reading keys on
`max_magU` blowing up in the step(s) before the fault. This is reported as a
finding, not hidden: the decision record's literal "min hf_film" observable is
partly blind by construction, and R4-A says so.

The observer is **diagnostic only**; it enters no gate (avoiding the
"diagnostic-only annotation" trap only in that its numbers are *reported*, never
used to launder a verdict).

## §5. THE GATE

Per rung, in order:

1. **SURVIVAL** — two conjuncts, both required:
   - **Completion** (`CLAUDE.md` rule 4), transferred verbatim from R3's
     `check_completion` (C-01…C-07): `rc==0`; an `End` line; last time ==
     `endTime` 10.0; fields present at endTime; 200 written dirs; 8000
     `ExecutionTime` lines; age guard (every endTime field newer than `0/U`).
   - **C-08 — VELOCITY-BOUNDEDNESS (the runaway gate).** The maximum over every
     logged `Film mag(U) min/max` line must stay below a registered physical bound
     **`MAGU_MAX_BOUND = 100 m/s`** at *every* step through completion. Rationale
     (answer-blind, §4): the physical film scale is `U_IN = 0.537` m/s and terminal
     velocity is O(1) m/s, so 100 m/s is two decades above physical; the observed
     runaway floor is ≥ 4e13 m/s (R3-L3), so the bound sits in the empty gap between
     the physical scale and the runaway and cannot false-fire on a bounded transient
     (the R3-L3 pre-fault values 4.35 → 11.03 m/s are below it; the fault value
     4.22e13 is far above). This gate catches a run that **completes with rc==0 but
     went unphysical** — the completion clauses alone would pass it. `min_h` is a
     **CONTEXT reading only, never a gate** (it is pinned at h0 by the post-solve
     floor, §4).
   A rung that fails **either** conjunct is **`NOT A RESULT`** on the answer and is
   recorded as *does-not-survive* with its observer trace (the `max_magU` runaway is
   the tell; `min_h` is context).
2. **ANSWER-RETENTION** (surviving rungs only), unchanged bands from R3 §5:
   - **Limb A** (primary, vs manual): `e_A = |δ_mon − 0.555 mm| / 0.555 mm ≤ 2.12 %`.
     Admissible `δ_mon ∈ [0.543234, 0.566766]` mm. Inside → **`GATE REACHED`**
     (its ceiling); outside → **`GATE FAIL`**; either overridden to **`NOT A
     RESULT`** by a completion/instrument/plant refusal.
   - **Limb B** (code verification, vs the rung's own exact state):
     `e_B = |δ_mon − dN*(h0)| / dN*(h0) ≤ 0.101 %`. `PASS`-capable. dN*(h0) is the
     §2/§3 Newton solution for that rung's h0.

**FAMILY OUTCOME / ABANDONMENT (registered in advance; precise form in §3):** the
pivot is the two **in-window** rungs A2 (1.5e-5) and A3 (2e-5). If **neither A2 nor
A3** both **survives** (completion + C-08) and lands `δ_mon` **in band**, the
constant-precursor approach is **ABANDONED for VMFL072** and the successor moves to
`kinematicSingleLayer` or a VOF re-formulation (`docs/ansys_verification/
FIX_SUCCESSOR_REGISTRY.md`). A1 (below the window) surviving is a *bonus* survivor,
not the pivot. If an in-window rung **survives in band**, its h0 is carried to
**R4-B** (the 512×128 scaling test — a separate freeze, not launched here).

**The gate cannot be widened.** A failing limb is worked/fixed/re-registered, never
softened (R3 §7.3).

## §6. HOW THE NUMBER IS READ — TRANSFERRED FROM R3, PER RUNG

Everything about *reading* δ_mon transfers **unchanged** from
`compare_vmfl072_r3.py`, applied per rung on the 256×64 field:

- monitor window `x∈[0.440,0.460]`, `y∈[0.025,0.075]` m; **area-weighted** mean
  (`monitor_mean`); geometry from `checkFaMesh`;
- the instrument floor `T_FLOOR = 2.7750e-07` m (plateau ptp / station spread);
- the **admissibility floor** `D_MIN_ADMISSIBLE = 1e-06` m (C-13);
- **both planted controls** (`CLAUDE.md` rule 3; L-487): `PLANT_P = 1.234e-05` m
  into a proper sub-region, read back, refuse if the reader cannot see it. P1
  (single level) applies per rung; P2 (cross-level, guards a reader that reads one
  level three times) is **re-scoped** — see §9, it now guards a reader that reads
  one rung three times or confuses rungs.

**What does NOT transfer:** the R3 exactness gate over the L1/L2/L3 refinement
triple and the C1/B2 controls. R4-A is a **single-grid** ladder; there is no grid
refinement in it, so **no Roache triple is declared** (`CLAUDE.md` rule 5: the
required statement is made explicitly here — R4-A establishes survival and
retention at fixed 256×64, it does **not** establish grid convergence; that is
R4-B's job).

## §7. THE REGISTERED PREDICTIONS (prediction-first, `CLAUDE.md` rule 2)

Answer-blind hypotheses, recorded before the runs:

- **A1 (h0=5e-6):** below the window → **outcome NOT pre-asserted** (§3
  non-monotonicity: floor-effect and friction-effect pull opposite ways). Its
  survive/crash outcome tells us which effect dominates on the thin side. If it
  survives, δ_mon → dN*=0.548453 mm (in band).
- **A2 (h0=1.5e-5):** interior of the window → **outcome genuinely open**; if it
  survives, δ_mon → dN*=0.545160 mm, e_A ≈ 1.775 %, e_B ≈ 0.
- **A3 (h0=2e-5):** upper edge of the window → **outcome genuinely open** (larger h0
  is NOT unambiguously safer, §3); if it survives, δ_mon → dN*=0.543528 mm,
  e_A ≈ 2.067 % (margin to the band floor only 0.054 %), e_B ≈ 0.
- **Family:** if neither A2 nor A3 survives in-band → **ABANDON** (§5). No single
  outcome is pre-asserted; survival may be non-monotone in h0.

If a run lands materially away from its prediction, our reading of the installed
film solver is refuted — a finding worth more than a passing row.

## §8. COST (`CLAUDE.md` rule 12)

**Anchor — named, per rung, to a measured prior level.** Every rung's estimate is
anchored to the **one measured completed run on this exact 256×64 grid: R3 control
B2 = 28.62 core-min** (completed, 12 800 steps, serial). Per-step:
`28.62 / 12800 = 2.235938e-03` core-min/step. An R4-A rung is **8 000 steps** (L3
`DELTAT`), so a **surviving** rung ≈ `8000 × 2.235938e-03 = 17.89 core-min`. A
**crashing** rung dies early and is cheap: R3-L3 crashed at 887/8000 steps =
**2.375 core-min measured**.

**Anchor quality, stated honestly.** B2 is the *same grid* but a *different h0 and a
different step count* — so this is a same-grid, step-scaled anchor, **not** the
byte-identical anchor that let VMFL051-R3 land at ratio 0.983. The h0 change may move
per-step PBiCGStab iteration counts in the thin region, so the surviving-rung figure
is **predicted, not measured** — no completed 8000-step 256×64 run exists (R2-L3 and
R3-L3 both died partial). A completed R4-A rung would be the first clean measurement
of it (see calibration below).

**`RANKS = 1` (serial), registered.** Justification from measurement, not habit: R3's
levels were tiny (L1 0.38, L2 2.90, L3 2.375, B2 28.62, C1 2.63 core-min), so the
ladder is cheap and one rank is sufficient; a serial run also occupies exactly one
core, which is the good-citizen choice on an oversubscribed box (below). Serial ⇒
core-min = wall-s ÷ 60 exactly and the `timeout` cap is exact.

**⚠ CONTENTION — and its effect on the calibration (rule 12; `COMPUTE_BUDGET` §6).**
For a one-rank job, contention inflates wall-s and therefore core-min for the *same*
work, and the two cannot be separated within a serial run — the cost unit *is* wall
time here. The box has been measured as high as **load 44.74 on 16 vCPU (2.8×
oversubscribed)** while other teams run Sanaa's-priority 3D/multipoint work. Two
registered consequences:
- **R4-A is launched by hand when load drops, NOT filed as a queue entry a daemon
  could pick up.** Rule 2 is satisfied by the freeze existing before compute; it
  does not require compute to follow immediately. Adding an ansys solver at load 44
  would take cores directly from Sanaa's priority.
- **The completion calibration row MUST state the execution load / oversubscription
  factor** (e.g. `uptime` load average at launch and at grade). A wall-clock figure
  taken at load 44 is not comparable to one taken at load 12; the ratio
  actual/predicted attributes the gap, and **contention waste is named separately
  (`COMPUTE_BUDGET` §6), never absorbed into the ratio.** The caps below carry a
  cushion for moderate contention, but a run executed under heavy oversubscription
  is flagged in its row as such.

| rung | steps | pure-work est. (core-min) | **per-rung CAP** | cap seconds |
|---|---|---|---|---|
| A1 | 8000 (or early crash) | 17.89 (≤2.4 if it crashes) | **40** | 2400 |
| A2 | 8000 | 17.89 | **40** | 2400 |
| A3 | 8000 | 17.89 | **40** | 2400 |
| | | | **FAMILY CAP 120** | |

- **Cap basis:** 40 core-min ≈ 1.68× B2's measured 28.62 and ≈ 2.24× the 17.89
  pure-work estimate — headroom for ~2× contention on a load-12 box, while still
  stopping a genuine non-crashing runaway. **An overrun STOPS THE RUN** (rule 12):
  `timeout` kills it, `rc=124`, the comparator refuses at completion. It is **not**
  re-budgeted.
- **⚠ THE FAMILY CAP ACCUMULATES ACROSS RUNGS — the D604 fix, folded in.** D604
  (confirmed live at HEAD: `run_vmfl063_r3.sh:98` `TOTAL_CORE_MIN=0` resets the cap
  per invocation) must **not** be reproduced here. The R4-A driver runs **all three
  rungs in ONE invocation** and keeps a **running `TOTAL_CORE_MIN` that is set to 0
  exactly once, before the loop, and accumulated across A1→A2→A3**; before each rung
  it computes `REMAIN = 120 − TOTAL_CORE_MIN` and, if `REMAIN ≤ 0`, **aborts the
  remaining rungs** (rule 12 — an overrun stops the run, it is not re-budgeted). The
  per-rung `timeout` is set to `min(40, REMAIN)` core-min so the family cap binds
  even mid-rung. The running total is **not** reset per rung and does **not** rely on
  a persisted file — accumulation lives in the single invocation's own variable.
- **Expected actual (predicted):** if A1 crashes (~2–5), A2 open, A3 survives
  (~18): ~**25–40 core-min** family; worst case all three survive ~**54 core-min**;
  family cap 120 leaves comfortable headroom.
- **Dollars — DERIVED, never measured** (box cannot read its billing,
  `COMPUTE_BUDGET_CHARTER` §5): family cap 120 core-min = 2.0 core-h ×
  $0.0513/core-h = **$0.1026 derived**; expected ~54 core-min = 0.9 core-h →
  **$0.046 derived**. Well inside the $25 pre-authorisation; CPU only.
- **Good citizen:** serial, one rung at a time → R4-A occupies **at most one core**
  at any instant, and never touches the VMFL017 tree or process.
- **Calibration at completion (rule 12):** the actual core-min from the logs are
  compared against the family estimate here; the row states the ratio
  actual/predicted, attributes the gap (contention/waste/misprediction, waste named
  separately per `COMPUTE_BUDGET_CHARTER` §6), and lands in `docs/COST_CALIBRATION.md`.
  A completed 8000-step 256×64 rung would be the **first clean measurement** of that
  quantity (R3-L3 and R2-L3 both died partial). A completion report without this row
  is incomplete.

## §9. THE GRADING PATH, THE COMPARATOR SUCCESSOR, AND WHAT IS OWED BEFORE FREEZE

**The comparator is a pinned grading path and is the supervisor's check-1.** R4-A is
a *different family shape* from R3 (single grid, per-rung survival, no refinement
triple), so the successor is not a light edit of `compare_vmfl072_r3.py`; it
**reuses R3's reader/plant/completion core (~80 %)** as a library and replaces the
family verdict. Precise spec of the successor `compare_vmfl072_r4a.py`:

- **REUSE UNCHANGED:** `read_points/faces/labels/area_scalar`, `load_geometry`,
  `read_checkfamesh_area`, `window_mask`, `area_mean`, `monitor_mean`,
  `check_completion` (C-01…C-07), the plant machinery (`_plant_fraction`,
  `_replant_and_reread`, `plant_p1`), `T_FLOOR`, band constants `BAND_A/BAND_B`,
  monitor window, `D_MIN_ADMISSIBLE`, `PLANT_*`.
- **NEW (isolated in one clearly-marked `# ==== R4-A FAMILY VERDICT ====` section,
  so check-1 is a clean diff):** (1) `dnstar(h0)` — Newton on the frozen
  `DN_CUBED = 1.664792e-10`; read each rung's h0 from its `LEVEL_APPLIED.txt`, verify
  it against the registered {A1:5e-6, A2:1.5e-5, A3:2e-5} table, refuse on mismatch.
  (2) `observe(log)` — parse `Film h min/max` / `Film mag(U) min/max` into
  `min_hf_film.tsv`; `min_h` is **context only**, but the **max over all
  `Film mag(U)` maxima feeds the C-08 gate** (`MAGU_MAX_BOUND = 100 m/s`, §5). (3)
  `check_survival(rung)` — completion (C-01…C-07, reused) **AND** C-08 boundedness.
  (4) `verdict_rung(rung)` — survival→retention as §5. (5) `family()` — §5
  abandonment keyed on the in-window rungs A2/A3. (6) P2 re-scoped to guard a reader
  that reads one rung three times or swaps rungs. Every refusal is explicit
  `refuse()`/`sys.exit(2)`, **never a bare `assert`**.
- **REUSED CORE STAYS BYTE-FAITHFUL** to `compare_vmfl072_r3.py` (the reader, plant
  and completion functions) so the supervisor can hash the shared functions and read
  only the new section as the diff.
- **Both planted controls must fire on the real R3-L3 crash data on disk**
  (`verification/runs/ansys_verification/VMFL072-R3/L3/`) — the selftest exercises
  P1/P2 against that trace, not only synthetic fixtures.
- **`--selftest` must pass before freeze**, green under `python3` **and**
  `python3 -O`, with new mutants: one per new verdict conjunct (completion-fail →
  NOT A RESULT; **the C-08 max_magU gate — a run that COMPLETES with rc==0 but has a
  velocity runaway, which must be REFUSED, and the selftest carries the mutation
  control that goes RED when the max_magU gate is removed**); e_A band edge both
  sides; e_B; dN*(h0) mismatch refusal; observer parse; both plants firing. **This
  lane's selftest is evidence; the supervisor's diff read is the gate**
  (`SUPERVISION_CHARTER` §3).
- **Comparator pin:** `git hash-object` of the frozen comparator, recorded here at
  freeze, verified by the driver against the committed blob (R3 §9.1/G-03).
- **Driver + apply + base:** the driver mirrors `launch_vmfl072_r3.sh`'s eight
  guards, retargeted to R4-A paths and iterating rungs A1/A2/A3; `apply_level.sh`
  gains an `H0` column and tokenizes `@H0@`/`@DELTAWET@` in `base/0.orig/U` (draft
  in this directory). All frozen files committed in the **same commit** as this doc.

**THE COMPARATOR PIN (§9.1 — the driver's G-03 reads this line).**

> **COMPARATOR_BLOB = ca2c73c70ce72a9aa12cf436a482ba83246158f1**

This is `git hash-object cases/ansys_verification/VMFL072-R4-A/compare_vmfl072_r4a.py`
taken **without committing**, so the pin is stable (writing it here changes *this*
file's blob, not the comparator's). The driver reads it out of this document
(G-03), so there is one source of truth before the freeze commit exists. **If the
supervisor edits the comparator during check-1, this pin must be recomputed.** At
the freeze the comparator and this document are committed in the **same commit**,
and the driver verifies every frozen file against its blob at that commit (G-02).
`--selftest`: **27 passed, 0 failed** under both `python3` and `python3 -O`
(includes the C-08 runaway gate, its mutation control that goes red without the
gate, both plants, and P1 firing on the real R3-L3 crash field on disk).

**THE LAUNCH — BY HAND, WHEN LOAD DROPS, NEVER AS A DAEMON QUEUE ENTRY.**
Once the freeze commit exists (sha = `<FREEZE_SHA>`) and load is acceptable, the run
is three serial invocations of the (to-be-frozen) driver, one rung at a time, then
one grade — mirroring R3's `launch_vmfl072_r3.sh` signature:

```
# ONE invocation: the driver runs A1→A2→A3 serially (one rank), accumulating the
# family cap across rungs (D604 fix, §8) and stopping if 120 core-min is reached.
VMFL072R4A_PREREG_SHA=<FREEZE_SHA> bash cases/ansys_verification/VMFL072-R4-A/launch_vmfl072_r4a.sh
# grade only after the invocation returns (all rungs complete-or-crashed):
python3 cases/ansys_verification/VMFL072-R4-A/compare_vmfl072_r4a.py --runroot verification/runs/ansys_verification/VMFL072-R4-A
```

**No queue JSON is filed for R4-A** — a daemon must not pick it up; it is fired by
hand when `uptime` load is back near ~12/16 or below. The driver
(`launch_vmfl072_r4a.sh`) and comparator (`compare_vmfl072_r4a.py`) **now exist** in
this directory: driver `bash -n` clean with guards G-00/G-01/G-03 exercised (all
refuse correctly without the freeze); comparator `--selftest` 27/0 green under
`python3` and `python3 -O`. They await the supervisor's check-1 diff read and the
freeze commit before either is run.

**FREEZE CHECKLIST — for the supervisor's §3 check-4:**

- [ ] Every gate, band, threshold, cap, level, ceiling, label and h0 value is a
      number or a fixed label here (no open question).
- [ ] `VERIFICATION_CHARTER` §2b condition named+checked:
      `verification/runs/ansys_verification/VMFL072-R4-A/` **does not exist** at
      freeze (checked below).
- [ ] No pre-freeze run of R4-A was performed (§0/§1). The R3-L3 log cited in §3/§4
      is *prior* R3 evidence, not an R4-A pre-freeze run.
- [x] `compare_vmfl072_r4a.py` drafted, `--selftest` **27/0 green under `python3`
      and `python3 -O`** (this lane); reused core hash-identical to R3's comparator.
      **STILL OWED: the supervisor's check-1 diff read, personally** — the selftest
      is evidence, not that read.
- [x] `launch_vmfl072_r4a.sh` drafted, `bash -n` clean, guards refuse correctly.
- [ ] comparator, apply, driver and `base/` inputs committed in the same commit as
      this file; the §9 pin matches the committed comparator blob.
- [ ] `h0` ladder {A1 5e-6, A2 1.5e-5, A3 2e-5} confirmed answer-blind (edges from
      known-crash 1e-5 and the frozen band ceiling 2.09e-5, not from any result).

**Condition check (this draft):** at the time of writing, `verification/runs/
ansys_verification/VMFL072-R4-A/` **does not exist** (checked: `ls -d` returns
nothing). Committing this draft with its comparator and inputs is the freeze; no
solver may launch before that commit exists and is named in the launch record.

## §10. WHAT THIS REGISTRATION DOES NOT KNOW

- Whether *any* constant h0 exists that both survives 256×64 and retains the answer
  — three rungs test three points in the sub-octave viable window (§3 honest limit).
- Whether the failure threshold scales with cell size — that is **R4-B**, a separate
  freeze; R4-A is single-grid and declares no Roache triple.
- The mechanism beyond "consistent with dewetting driving `(h+h0)` negative and
  poisoning the diagonal": R4-A *measures* the velocity runaway (`max_magU`) that
  accompanies the fault, but the post-solve floor hides the sub-floor h that would
  confirm it directly (§4).
- The completed 8000-step 256×64 cost — R4-A would measure it for the first time.
