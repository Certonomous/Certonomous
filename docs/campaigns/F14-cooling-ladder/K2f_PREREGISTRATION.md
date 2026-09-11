# K2f — the rack-row module re-registered on a grading path that can actually grade: PRE-REGISTRATION

**Campaign F14, DC-cooling spine. Rung `K2f`. Team: heat-transfer.**
**Drafted 2026-09-11 by a heat-transfer `lab-lane` at ZERO solver core-minutes.**

> # ⚠ DRAFT — **NOT FROZEN. GATES ARE OPEN.**
>
> No gate, band, threshold, floor, cap or label in this file is frozen. It is a
> draft for the heat-transfer supervisor and **it authorises no compute.**
>
> **THE AMENDMENT CONDITION, AND HOW IT IS CHECKED.** Following K2d §14.2's
> stricter restatement rather than its broken first wording:
>
> > **No case directory exists under
> > `verification/runs/F14-cooling-ladder/K2f_runs/` — no `K2f_L1`, `K2f_L2` or
> > `K2f_L3` — no `STATUS.*` file, no `log.solve`, no time directory and no
> > field.**
>
> **How checked:** by listing the run tree on disk, never by asking git and
> never by reading a document. **Checked 2026-09-11 by `test -d`:
> `K2f_runs/` DOES NOT EXIST.** No run tree has been created. **Zero solver
> core-minutes have been spent against this document.**
>
> **No run directory may be created and no solver launched until a freeze
> commit exists on `main`**, and the check is that the commit *is there*.

---

## 0. WHAT THIS RUNG IS

**K2f runs the rack-row module defined by `K2a_RACK_ROW_MODULE_SPEC.md`, on a
three-level grid ladder, and grades a Roache triple on it.** Geometry, boundary
conditions, fluid properties, solver, turbulence model and measured quantities
are **inherited from K2a by citation** exactly as K2d inherited them, and are
not re-derived here.

**It is VERIFICATION, not validation. Every graded quantity carries reference
tier `NONE`.** K2d §0.1's reasoning is inherited whole and is not restated: the
Wibron 2018 configuration is a different room, `K2a:82` excludes it in terms,
and the comparison of §5.5 is **report-only and grades nothing.**

**Sanaa approved `K2a` — the rack-row module — in her own words at ~20:20Z on
2026-09-10. K2f realises that same approved module, unchanged.** Her approval
travels with the case, not with a document's filename. **Nothing in this draft
goes back to her desk and no agent's message is her consent.**

### 0.1 WHY K2d IS BEING REPLACED RATHER THAN REPAIRED

`K2d_PREREGISTRATION.md` §17 (Addendum 4) retires K2d. Two blockers, both on
its pinned grading path:

1. **The gate's inputs were never written.** K2d registered `T_in,max` and
   `U_ha` as in-pass function-object output (`K2d:290`, `K2d:413`); its pinned
   builder emitted **no function objects**. `G-CYCLE` had no input at any level.
2. **The pinned comparator had no grading path.** `analyse_k2d.py:613-619` is a
   stub: `--selftest` or a hardcoded refusal. 31 green selftest arms were wired
   to nothing.

**A §2d.1 repair was declined because it buys nothing** — every level reruns
regardless, so no measurement could be rescued.
`VERIFICATION_CHARTER.md:2155-2157` points the same way: where a repair would
make a graded refinement family incommensurable, the ladder is re-registered
rather than patched.

### 0.2 WHAT K2d NEVERTHELESS MEASURED, AND IT IS THE MOST IMPORTANT INPUT TO THIS DESIGN

K2d's three levels produced no gradeable row, but they produced **residual
histories**, and those are recorded here because they change what this rung
should be. Measured from each level's own `log.solve`:

| level | cells | initial-residual floor reached (Ux) | behaviour after the floor |
|---|---:|---:|---|
| **L1** | 58,368 | **9.8e-10** at iteration 3,000 | **flat from ~1,200 onward.** Converged, six to seven decades, no cycle |
| **L2** | 196,992 | **1.75e-04** at iteration ~800 | **rose and limit-cycled for the remaining 2,200 iterations.** Peaks at ~1000, ~1800, ~2800 |
| **L3** | 664,848 | **1.13e-04** at iteration ~945 | **reversing when killed at 995** — +39.5 % off its own minimum |

Over L2's final 400 iterations the Ux initial residual spanned 1.6524e-04 to
5.0873e-04 — **109.1 % of its own mean, 6 sign changes** in the first
difference; T 104.5 %/16; `p_rgh` 100.6 %/16.

> **THE READING: the steady treatment converges on the COARSE mesh and stops
> converging as the mesh is refined.** L1's residual floor is **five orders of
> magnitude below** L2's. The coarse mesh appears too diffusive to sustain the
> unsteadiness; refining resolves it, and the steady solver then cannot reach a
> steady state.

**This is diagnostic and it is NOT the registered gate.** `G-CYCLE` gates on
`T_in,max` and `U_ha` normalised by range-spanned, never on solver residuals. A
residual limit cycle does not prove those integral quantities cycle above
0.02 % of their range. It is recorded because it is the only convergence
evidence K2d produced and because **it refuted a design this draft was about to
register** (§12.1).

### 0.3 THE SECOND CONSEQUENCE, WHICH IS SHARPER THAN THE FIRST

**If convergence STATE differs across the ladder, the Roache triple is invalid
in principle and not merely by rule.** A triple assumes the three values differ
by *discretisation error*. Three levels that differ in whether they reached a
steady state at all are not solving the same problem in the same regime: the
coarse level converges to a steady state the fine levels say does not exist, and
the inter-level differences then measure a mixture of discretisation error and
convergence state. K2d's Addendum 3 §16.3 named this hazard for a flat
`endTime`; K2d's own residual histories show it in a **worse** form, where the
difference is not iteration count but regime.

**So a `CONVERGED`/`CYCLING` split across this ladder is not a nuisance to be
worked around. It is the rung's most likely finding, and §4 registers its
meaning BEFORE compute.**

---

## 1. THE LADDER — K2a's two levels preserved, K2d's third retained

| level | **target** cells | role |
|---|---:|---|
| **L1** | 59,259 | the cheap level; K2d built it at 58,368 |
| **L2** | 200,000 | **K2a's approved coarse level, unchanged**; K2d built 196,992 |
| **L3** | 675,000 | **K2a's approved fine level, unchanged**; K2d built 664,848 |

Target step **3.3750** at each pair, **r = 1.5000 in three directions**.

**`G-MESHSIM` — inherited from K2d §1.2 unchanged, and it gates on the BUILT
counts read from each level's own `constant/polyMesh`, never on the targets.**
Actual `N(L2)/N(L1)` and `N(L3)/N(L2)` must each lie in **[3.2063, 3.5438]**
(3.375 ± 5 %, **r ∈ [1.4747, 1.5245]**). A pair outside → every graded row
**`NOT A RESULT`**, both ratios and both counts printed.

**K2a's re-pricing clause is checked and NOT triggered**: the two numbers it
protects, 0.20 M and 0.70 M, are preserved.

---

## 2. GEOMETRY, BOUNDARY CONDITIONS, PROPERTIES, SOLVER — INHERITED BY CITATION

**Read `K2a_RACK_ROW_MODULE_SPEC.md` §2, §2.1, §3, §9 at the freeze commit.
Nothing is re-derived here.** K2a's defaults: `N` = 4, `W_r × D_r × H_r` =
0.60 × 1.10 × 2.00 m, `W_ca` = `W_ha` = 1.20 m, `H` = 2.70 m, `L_end` = 0.60 m,
`s_t` = 0.60 m, `n_t` = `N`, `Qv_r,i` = 0.35 m³/s, `ΔT_i` = 12.0 K,
`T_sup` = 289 K, `supply_type` = `tile`, `loop_mode` = `open`.

Fluid properties from the committed K0c dictionaries, not from recall:
**ν = 1.589461e-05 m²/s, β = 3.333333e-03 1/K, TRef = 300.0 K, Pr = 0.71,
Prt = 0.85.** Regime numbers from `K2a` §5: `Re_tile` 3.7e4, `Re_rack` 1.1e4,
`Ri_tile` 0.25, `Ri_rack` 9.3, `Ra_H` 3.0e10.

**Solver: `buoyantBoussinesqSimpleFoam`, steady SIMPLE** (`K2a` §9), stock ESI
v2606, with K2d's two repaired dictionary entries carried forward as case
content and not as a discovery to be made again:
`wallDist { method meshWave; }` (`kOmegaSST` will not start without it), and the
**kinematic** forms — `p_rgh` and `p` in m²/s², `alphat` a kinematic diffusivity
with `alphatJayatillekeWallFunction`, not `compressible::alphatWallFunction`.
**Turbulence: `kOmegaSST`, `Prt` = 0.85**, K2a's specified model, unchanged.

---

## 3. THE MONITORED QUANTITIES — REGISTERED AS FUNCTION OBJECTS, WHICH IS THE DEFECT THAT KILLED K2d

**`G-CYCLE` reads two quantities and K2d wrote neither.** This rung registers
them as case content and registers an arm that proves they were written.

Written by in-pass `functions` entries in `system/controlDict`, at
`writeControl timeStep; writeInterval 50` — the **50-iteration cadence** §4
requires:

- **`T_in,i`** — mass-flow-weighted mean `T` over `rack_i_in`, per rack.
- **`T_in,max`** — max over i of `T_in,i`; the S13 monitored quantity.
- **`θ_i`** = (T_in,i − T_sup)/ΔT_rack,i — the dimensionless recirculation index.
- **`U_ha`** — volume-averaged velocity magnitude over the hot-aisle control
  volume: full `W_ha`, spanning the rack row in `x` from first to last rack
  face, floor to rack top `H_r` = 2.00 m in `z`. K2d §3.3a's definition,
  unchanged — the location `P-K2d-2` names.

### 3.1 `A-INPUT` — THE PRE-FREEZE ARM THAT PROVES THE GATE'S INPUT EXISTS

**This is standing rule 3's principle applied to the gate's INPUT rather than to
its reader, and it is registered because K2d proves the gap is real: a gate
whose input was never produced fails silently, and nothing in K2d would have
caught it.** K2d's builder had 16 green selftest arms; none asked whether the
quantities the gate reads had been written.

> **REGISTERED as a PRE-FREEZE OBLIGATION.** Before this document may be
> frozen, the builder's selftest **builds a throwaway case at the smallest
> workable size, runs the real solver for ~20 iterations, and asserts that every
> registered series file exists, is non-empty, and carries at least one sample
> row for EACH of `T_in,max`, `θ_max` and `U_ha`.** The arm **fails the
> selftest** if any series is absent or empty. The throwaway case is deleted
> after the arm; it is not a graded case and produces no registered number.
>
> **A NEGATIVE ARM is registered with it:** the same assertion run against a
> case built with the `functions` block **removed** must **FAIL**. An arm never
> shown able to fail is not an arm — the identical reason K2d's §3.3b planted a
> cycle into its own detector.

**Freeze is refused until both arms have been driven and their output recorded**
in `K2f_INPUT_ARM_DEMONSTRATION.txt` in the run tree.

---

## 4. ⚠ WHAT `CYCLING` MEANS — DECIDED AND REGISTERED BEFORE THE ANSWER IS KNOWN

**The supervisor's question, answered here rather than after compute: is
`G-CYCLE` returning `CYCLING` a `NOT A RESULT`, or is it the physical answer
this flow class gives?**

> ### REGISTERED: IT IS BOTH, AND THE SECOND DOES NOT SOFTEN THE FIRST.
>
> **(a) For the GRADED ROWS, `CYCLING` or `DRIFTING` at any level is
> `NOT A RESULT`.** Standing rule 5 clause (1) — *"any level not iteratively
> converged or not plateaued → `NOT A RESULT`"* — is **not a lane's to retire
> and not this document's to soften.** Retiring a standard or a gate threshold
> is reserved to Sanaa. §0.3 gives the independent reason the same answer would
> follow anyway: a ladder whose levels differ in convergence state cannot carry
> a discretisation triple.
>
> **(b) For the RUNG, it is a POSITIVE REGISTERED FINDING and is reported as
> one**, under the name **`S-ONSET`** (§4.1). K2d could not report it because it
> could not evaluate `G-CYCLE` at all.
>
> **(c) The two are printed together and (b) may never be written in a way that
> softens (a).** No K2f sentence may read "converged well enough", "essentially
> converged", or any synonym. The verdict on the graded rows is
> `NOT A RESULT`, in those words.

**Why a time-average over the cycle is NOT registered, stated so it is not
proposed later as an easy fix.** `buoyantBoussinesqSimpleFoam` is a **steady**
solver: its outer iterations are **not time**, they are a relaxation sequence
toward a fixed point. A limit cycle in SIMPLE iterates has **no physical
period** and averaging over it produces a number with no defensible
interpretation. Averaging would manufacture a gradeable value out of a
quantity that does not have one. **The rung that can legitimately time-average
is a transient one (§14), and it is not registered here.**

### 4.1 `S-ONSET` — the registered finding, its form fixed in advance

> **`S-ONSET` is a per-level convergence-state census, printed for EVERY level
> whatever the verdicts are**: the `G-CYCLE` state (`CONVERGED` / `CYCLING` /
> `DRIFTING`) for **both** `T_in,max` and `U_ha`, each with its spread as a
> percentage of range-spanned, its sign-change count, its trend fraction, its
> sample count, **and the measured detection floor of §6.2** beside every
> `CONVERGED` reading.
>
> **It states, in the registered words: "the steady `kOmegaSST` treatment of the
> K2a module reads ⟨state⟩ at ⟨cells⟩ cells."** It makes **no** claim about the
> physical unsteadiness of a real data centre, about model-form error, or about
> any resolution not run.
>
> **`S-ONSET` grades nothing and moves no verdict.** It is the registered ground
> for a transient successor under its own pre-registration and its own cost, and
> it is nothing else.

### 4.2 `C-DECOMP` — the cycle must be shown NOT to be a parallel artefact

**A control this draft would not have contained had §0.2's measurement not been
taken.** L1 and L2 differ in mesh — but they also differ in their `scotch`
decomposition, and a limit cycle that is an artefact of domain decomposition or
of rank count would present exactly as a mesh-driven one.

> **REGISTERED: whichever level FIRST reads `CYCLING` or `DRIFTING` is re-run
> once at a DIFFERENT rank count** (registered in §11's table as the level's
> `alt_ranks`), on the **same mesh** and the same dictionaries.
> - **Same `G-CYCLE` state at both rank counts → the state is a property of the
>   case**, and `S-ONSET` reports it as such.
> - **Different states → `S-ONSET` is REFUSED, not reported**, and the rung
>   records that the convergence state is **not reproducible across
>   decompositions**, which is a finding about the parallel path and not about
>   the flow. Both states, both rank counts and both decompositions are printed.
>
> `C-DECOMP` **cannot rehabilitate a graded row.** The graded rows are already
> `NOT A RESULT` whenever it runs, and §5.2's gate is one-way.

**Its cost is registered in §10 and it is not free.**

---

## 5. THE GATE

### 5.1 The graded rows — K2a's, unchanged

| row | quantity | dim | triple? |
|---|---|---|---|
| **G1** | `T_in,max` — the worst-rack inlet temperature | K | yes |
| **G2** | `θ_max` = max over i of `θ_i` | – | yes |
| **G3** | `T_in,1` — the end rack, where end effects are largest | K | yes |
| **G4** | volume-averaged `T` over the cold aisle | K | yes |

### 5.2 Order of evaluation — standing rule 5, one-way

1. **Admission.** `G-MESHSIM` (§1), `G-CHECKMESH` and `G-MINCELL` (§8),
   `G-3D` (§8.2), the planted-zero control (§9.1), the strict completion rule
   (§9.2), and **`A-INPUT`'s artefacts present for every level** (§3.1). Any
   failure → every graded row **`NOT A RESULT`**.
2. **`G-CYCLE`** per level, on **both** quantities. Any level not `CONVERGED` on
   either → every graded row **`NOT A RESULT`**, and **`S-ONSET` is reported**.
3. **Triple classification** per row. `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or
   `EXACT` → that row **`NOT A RESULT`**, value, triple and order printed, **no
   GCI quoted**.
4. **`CONVERGING`** → graded against §5.3, GCI at **`Fs` = 1.25** printed.

**The gate is one-way. It may turn a `PASS` or `GATE FAIL` *into*
`NOT A RESULT` and never the reverse.** No addendum may rehabilitate a row
upward. **Never quote a GCI when the three values are not monotone** — the
comparator emits `null`.

### 5.3 `G-ORDER` and `A-SUBFIRST` — inherited from K2d unchanged

**Band: observed order `p` ∈ (0.5, 3.5)**, with K2d §4.3's justification carried
whole: the report-only referent's own three-grid study on this flow class
reports *"local order of accuracy `p` ranges from 0.0197 to 27.70, with a global
average of 6.583"*. **The band is wider than the lab's usual (1.5, 2.5), a
`PASS` inside it is a WEAKER claim, and no K2f sentence may cite such a `PASS`
as second-order accuracy.** The referent's own 6.583 lies **outside** even this
band, so the band can still fail.

**`A-SUBFIRST` carried unchanged**: any row graded `PASS` with `p` < 1.0 carries
the printed annotation naming sub-first-order convergence as a
structurally-dominant error source and not slow convergence, in stdout, in the
gate JSON as an `annotations` field, and in the results record.

### 5.4 `G-CHECKMESH`, `G-MINCELL`, `G-3D` — inherited from K2d §5 UNCHANGED

**These limbs were sound and are not re-derived.** Every `checkMesh` carries
`-allGeometry -allTopology` with the exact command line written into
`log.checkMesh`; the comparator refuses a log not evidencing both flags; it
parses `Failed N mesh checks` and refuses on `N > 0`; **`Mesh OK.` is not
accepted on its own**; neither line present → `NOT A RESULT` (*unmeasured is not
passing*). **Tolerance registry: EMPTY, zero tolerance.** `G-MINCELL` floor
**5.0 mm** at each of K2d's ten named features. `G-3D` reads the verbatim
`Mesh has N geometric (non-empty/wedge) directions` line — **never** the
`solution (non-empty)` line, which reads 3 for a wedge — censuses `empty` and
`wedge` patch types from `constant/polyMesh/boundary`, and voids every row if
`N ≠ 3` or any such patch is present. **`blockMeshDict` is never read for this.**

### 5.5 The report-only comparison — computed, printed, GRADING NOTHING

K2d §4.4 inherited whole: the digitised Wibron files, **15** temperature rows and
**17** velocity rows, **`REPORTED`, never graded**, with the different-rooms
statement printed in the output on its own face. Digitisation increments carried
from the files' headers so no reader may quote finer than the data was read
(L-28): temperature **±0.03 K**, velocity **±0.007 m/s**, height **±0.005 m**.
Referent instrument uncertainties: temperature **±1 °C**; velocity **±2 % of
reading ±0.02 m/s** (0.05–1 m/s), **±5 %** (1–5 m/s). Title-page verification
(L-144) was performed on 2026-09-10 and is recorded at `K2d:547-553`; the PDF
sha256 is re-pinned in §15.

---

## 6. `G-CYCLE` — THE LIMB ITSELF, CARRIED FROM K2d UNCHANGED

### 6.1 The classifier

Both quantities are sampled every **50 outer iterations**. Over the **last 400
iterations** (≥ 9 samples, **REFUSED** below that):

- **CONVERGED** — peak-to-peak spread ≤ **0.02 %** of the **RANGE THE QUANTITY
  SPANNED OVER THE RUN** (D393's normaliser,
  `heat_monitor_normaliser: range_spanned_over_run`).
- **CYCLING** — spread > 0.02 %, **and** ≥ **3 sign changes** in the first
  difference over the window, **and** linear trend explaining **< 25 %** of
  sample variance.
- **DRIFTING** — spread > 0.02 % and not CYCLING.

**Both limbs CALL `scripts/check_convergence.py::classify_monitor` (`:576`),
which is S13, applies the range normaliser at `:629`, and carries the
null-variation refusal.** Thresholds are read from `docs/physics_rules.yaml` at
run time and **never copied into a case script**. K2d §3.3a.1's honest limit is
carried unchanged: **0.02 % reaches `U_ha` by consistency of normaliser, not by
a measured sweep on a velocity** — D393's insensitivity corpus contained no
velocity — which is why §6.2's floor is reported beside every `CONVERGED`
reading rather than asserted.

### 6.2 Planted-cycle control — the detector must be SHOWN able to detect a cycle

K2d §3.3b unchanged, for **every level and both quantities**, before any level
is classified: a **positive arm** (a sinusoid at 2× the spread threshold, period
200 iterations, must classify `CYCLING` or the comparator **REFUSES at exit 2**);
a **negative arm** (a clean monotone decaying series must not classify
`CYCLING`); and a **measured detection floor** — sinusoids at 1.0×, 0.5×, 0.25×,
0.125×, 0.0625× the threshold, reporting the smallest still classified
`CYCLING`, **printed in the gate JSON and quoted beside any `CONVERGED`
reading.** The comparator refuses rather than grading a rung whose detector has
not demonstrated, on that run's own data, that it works.

---

## 7. `A-DRIVE` — THE COMPARATOR MUST BE SHOWN ABLE TO GRADE A DIRECTORY

**This is the second defect that killed K2d, and it is registered as a
pre-freeze obligation rather than as an intention.** K2d's comparator had 31
green gate-function arms and a `main()` that never read a case directory.

> **REGISTERED as a PRE-FREEZE OBLIGATION.** Before this document may be frozen,
> `analyse_k2f.py` is **run against a real case tree** and must emit **either a
> verdict set or a NAMED REFUSAL citing the limb that refused.** A comparator
> that cannot be pointed at a directory is not a comparator.
>
> Driven in **both directions**, on real paths, with the invocations and exit
> codes recorded in `K2f_DRIVE_ARM_DEMONSTRATION.txt` in the run tree:
> 1. **Against a synthetic complete three-level tree** built by the selftest —
>    must return a verdict set, not a stub refusal.
> 2. **Against an incomplete tree** (one level missing its series) — must return
>    a **named** refusal identifying the missing input, **never** a generic
>    "nothing to grade".
>
> **THE STANDING CORRECTION THIS ENCODES, recorded by the heat-transfer
> supervisor under their own name after K2d:** *a selftest count is evidence
> about gate functions and evidence about nothing else. The check is that the
> comparator can be pointed at a case directory and return a verdict.*

**`scripts/check_comparator_freeze.py` is run before freeze and its output
recorded.**

---

## 8. MESH GATES

As §5.4. **No tolerance may be added after the freeze**, and an entry added
before it must carry its own written justification. **A level whose full check
set fails is `NOT A RESULT` and its mesh is rebuilt — the tolerance is not
widened after seeing the answer.**

---

## 9. CONTROLS AND COMPLETION

### 9.1 Planted-zero control

For **every graded row on every level**, the comparator plants **`1.234e-03`**
(the family constant) into the field on disk by index, re-reads it **through the
production reader from disk**, and asserts the reader returns it. **If the
reader cannot see the plant the comparator REFUSES — exit 2 — and grades
nothing.** A negative arm re-reads the unplanted field and asserts the original
value. It does not degrade and it does not report a zero it has not earned.

### 9.2 Strict completion rule, and a NEW instrument with a NEW allow-list

A level is DONE only if **all** hold: `rc = 0`; an `End` line in `log.solve`;
**last written time == `endTime`**; the required fields
(`T U p_rgh alphat nut k omega phi`) present at `endTime`; `ExecutionTime` count
== `round(endTime/deltaT)`; and **every field at `endTime` NEWER than that
case's own `0/T`** — the age guard.

> **REGISTERED: the instrument is `mark_done_k2f.py`, written for this rung, and
> its allow-list is `("K2f_L1", "K2f_L2", "K2f_L3")`.**
>
> **`mark_done_k2d.py` IS NOT INHERITED.** Its allow-list at `:61` is
> `("K2d_L1", "K2d_L2", "K2d_L3")` and it is pinned by blob to a retired
> registration; a name off the list is refused at exit 2. Reusing it would
> either force this rung to build under K2d's names — inviting exactly the
> confusion §17.8 of that document moved a directory to prevent — or require
> editing a pinned file. **The allow-list is registered here so the builder,
> the launcher and the instrument agree by construction.**
>
> **The comparator CALLS `mark_done_k2f.py` rather than reimplementing its
> clauses**, so there is one implementation of the completion rule for this rung.

### 9.3 Clause 7 — the launch guard, demonstrated BY EXECUTION

The guard **refuses to launch into a case directory where `0/`, any time
directory, or a NON-EMPTY `postProcessing/` already exists** — the last limb
firing on **content**, because OpenFOAM writes a **second** function-object file
on restart rather than overwriting the first, and both then match the
comparator's glob, which is a **wrong number rather than a crash**.

**Before freeze the guard is demonstrated BY EXECUTION, in both directions, on
real paths** — it must **refuse** a directory seeded with a `0/`, refuse one
with a populated `postProcessing/`, and **stay silent** on a clean one — with
every invocation and exit code recorded in `K2f_CLAUSE7_DEMONSTRATION.txt`.
**A clause that has never been executed is a claim, not a guard.**

### 9.4 `writeInterval` — REGISTERED WELL BELOW `endTime`, and this is why

> **`writeInterval 500` with `endTime 3000`** — six restart points per level.

**K2d registered `writeInterval 3000` with `endTime 3000`, so a level that did
not reach `endTime` wrote NOTHING.** `K2d_L3` was killed at iteration 995 of
3,000 and its `processor*/` directories held only `0` and `constant`:
**535.600 core-minutes produced no field, no time directory and no restart
point.** A trip at 33 % of a run should cost 33 % of a run, not all of it.

**Measured disk cost, so this is priced rather than assumed:** `K2d_L2/3000`
occupies **37 MB** at 196,992 cells (~188 bytes/cell, ascii,
`writePrecision 10`), implying **~125 MB** per write at L3's 664,848 cells.
Six writes per level across the ladder ≈ **1.0 GB**. **58 G free on
`/dev/root` at drafting (89 % used)** — adequate, and the figure is stated so a
future reader can re-check it rather than trust it. **`purgeWrite 0`**, so
clause 3's *last written time == `endTime`* is unaffected.

### 9.5 Exit map

**`0 = EXIT_OK`, `1 = EXIT_FAIL`, `2 = EXIT_REFUSE`** — T3's convention. **The
exit code does not carry the verdict** and no record may read it as one: T16c
returned `rc = 0` while every row read `NOT A RESULT`. The verdict is read from
the gate JSON and stdout.

### 9.6 Mutation matrix

Every instrument carries a mutation matrix driven before freeze: a control arm
that must stay silent and one corruption arm per limb that must fire.
**`__pycache__` is cleared between every run** — stale bytecode has inverted
mutation tests in this lab. Registered negative arms: a `log.checkMesh` produced
**without** the flags must be refused; a **sub-floor minimum cell** must be
caught; **a case built with the `functions` block removed must fail `A-INPUT`**
(§3.1); and **`main()` run against an incomplete tree must return a NAMED
refusal** (§7).

---

## 10. COST — rule 12, COSTED BEFORE COMPUTE, ON A RATE MODEL THAT IS NOT LINEAR IN CELLS

### 10.1 The basis, and it is measured on this rung's own geometry

**K2d's §7.1 basis assumed a CONSTANT cell-iter rate and its Addendum 3 §16.2
extrapolated L2 and L3 from L1 on that assumption. The assumption is false and
K2d measured how false.** Contention-free, from each level's `ExecutionTime`:

| level | cells | **cell-iter/core-s** | core-s/iteration | implied exponent |
|---|---:|---:|---:|---|
| L1 | 58,368 | 187,598 | 0.3111 | — |
| L2 | 196,992 | 93,988 | 2.0959 | **N^1.568** (L1→L2) |
| L3 | 664,848 | 37,051 | 17.9441 | **N^1.765** (L2→L3) |

**Cost per iteration scales as N^1.57–N^1.77, not N^1.0** — GAMG work per outer
iteration grows with the mesh.

**THE MODEL IS CHECKED AGAINST A FIGURE IT WAS NOT FITTED TO.** L2's predicted
contention-free cost is 2.0959 × 3,000 ÷ 60 = **104.8 core-min**; L2's
**measured** 138.400 core-min at its **measured** contention of 1.320 gives
138.400 ÷ 1.320 = **104.8 core-min**. The model reproduces the measurement to
0.1 %.

**CONTENTION IS STATED SEPARATELY AND IS NEVER FOLDED INTO THE RATE**
(`ClockTime`/`ExecutionTime`, measured): **L1 1.003, L2 1.320, L3 1.775.** L1's
was measured on a quiet box; L3's was measured while L2 was still running
alongside T4e and a seven-rank `simpleFoam` job on 16 vCPUs.

### 10.2 The ladder cost

At `endTime` 3,000 (§10.3), contention-free, plus a **contended** column at
K2d's measured factors:

| level | ranks | **POINT (contention-free)** | at measured contention | contention used |
|---|---:|---:|---:|---:|
| L1 | 4 | **15.6** core-min | 15.6 | 1.003 |
| L2 | 4 | **104.8** core-min | 138.3 | 1.320 |
| L3 | 8 | **897.2** core-min | 1,592.5 | 1.775 |
| `C-DECOMP` re-run (§4.2) | per §11 | **104.8** core-min (at L2) | 138.3 | 1.320 |
| **ladder** | | **1,122.4** | **1,884.7** | |

**CARRIED BRACKET, NOT THE POINT ESTIMATE: 1,120 – 1,890 core-min.**
**$0.96 – $1.61 DERIVED** at $0.0513/core-h — **derived, never measured**; the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Three honest limits, named rather than glossed.** (i) The **8-rank** L3 row
rests on an **assumed** 4→8 parallel efficiency: **no K2d level ever ran at 8
ranks**, all three ran at 4, and this lab has no 8-rank measurement on this
geometry. It is a **projection**. (ii) The contended column uses K2d's measured
contention, which was a property of that night's load and not of this rung.
(iii) Both assume the solve runs to `endTime`; if `G-CYCLE` fires, the spend
buys `S-ONSET` and a `NOT A RESULT`, **which §4 registers as the expected
outcome** — see §12.

**K2d's spend is NOT carried into this bracket.** Its 689.734 core-min is booked
as waste against K2d (`K2d` §17.7) and is never absorbed into K2f's ratio.

### 10.3 `endTime 3000` — JUSTIFIED FROM L2'S MEASURED BEHAVIOUR, NOT FROM L1'S

**K2d's flat `endTime 3000` was never justified from a measurement; its own
Addendum 3 §16.3 flagged it as a symptom.** Registered here with a reason:

**3,000 iterations is registered as sufficient to DIAGNOSE the convergence
state, and is NOT asserted to be sufficient to reach a plateau.** L2 reached its
residual floor at ~800 and its limit cycle was unmistakable by ~2,000 — three
full excursions (peaks at ~1000, ~1800, ~2800) inside 3,000 iterations, and its
final 400-iteration window carried 6 sign changes on Ux and 16 on T and `p_rgh`.
**`G-CYCLE`'s window is the last 400 iterations at a 50-iteration cadence; L2's
history shows that window lands well clear of the initial transient at 3,000.**

**The distinction matters and is registered:** if a level plateaus, 3,000 was
generous; if it cycles, 3,000 was **long enough to prove it**, which is what
`S-ONSET` needs. **A longer `endTime` is NOT registered**, because L2 spent
2,200 iterations past its floor without descending and there is no measurement
suggesting more would change the state. **If a level reads `DRIFTING` with a
trend still descending, that is the one outcome where 3,000 may be too short,
and it is registered as such**: the rung reports `NOT A RESULT` with the trend
fraction printed, and the ground for a longer-`endTime` successor is a **new
registration and a new cost**, never an extension of this one.

---

## 11. RANKS AND THE HANG GUARD — ONE REGISTERED TABLE, AND THE LAUNCHER ASSERTS AGAINST IT

**This closes the hole K2d's launcher left open.** `launch_k2d.sh:7` read
`GUARD_S="$3"` — it computed no guard and **asserted nothing about the one it
was handed**. A retired watcher passed `8034` by hand
(`RETIRED_2026-09-11/watch_l3.sh:46-47`), 2.52× tighter than the registered
20,250 s and at half the registered ranks, and **K2d_L3 died at 33 % of its
iterations with nothing written.** L1, one level earlier, had used the
registered value exactly — so nothing but the caller changed.

> **THE REGISTERED TABLE. This is the only place ranks or a guard is written,
> and no other number is legitimate.**
>
> | level | `ranks` | `alt_ranks` (§4.2 `C-DECOMP`) | POINT (contention-free) | **hang guard** |
> |---|---:|---:|---:|---:|
> | **L1** | 4 | 2 | 15.6 core-min | **702 s** |
> | **L2** | 4 | 8 | 104.8 core-min | **4,716 s** |
> | **L3** | 8 | — | 897.2 core-min | **20,187 s** |
>
> Each guard is **3× POINT at that level's registered ranks**, computed from
> §10's measured rate model: L1 3 × 15.6 ÷ 4 × 60 = 702 s; L2 3 × 104.8 ÷ 4 × 60
> = 4,716 s; L3 3 × 897.2 ÷ 8 × 60 = 20,187 s.
>
> **The guard is a HANG GUARD and is NOT a budget stop.** 3× POINT is far enough
> above any honest overrun that a trip means the solver has hung. **The cap is
> enforced by §12's staging and by the cost record, never by the timeout.**
> **A trip is triaged as a finding and is never labelled from the exit code
> alone** — K2d's `note=HANG_GUARD_TRIPPED` was written mechanically on `rc=124`
> by a solver that was working at the instant it died.
>
> **REGISTERED LAUNCHER OBLIGATION.** `launch_k2f.sh` **reads this table** and,
> for the level it was asked to run, **asserts that the ranks and the guard it
> was handed equal that level's registered row, and REFUSES (exit 2) otherwise**,
> printing both the handed and the registered values. **It is demonstrated BY
> EXECUTION in both directions before freeze** — a matching pair must launch, a
> mismatched pair must refuse — with both invocations and exit codes recorded in
> `K2f_GUARD_ASSERT_DEMONSTRATION.txt`.

**Ranks above 8 require the supervisor's coordination.** The box is 16 vCPUs and
carried a load average of **27.99** at drafting, with `T4e_IJ_f` (pid 1233987)
and a `rhoCentralFoam` each at ~99 % CPU.

**On launch, reported immediately:** pid, cwd, registration sha, ranks, cap in
core-minutes, guard. **Detachment: `setsid` with `rc` captured INSIDE the
wrapper** — `setsid timeout cmd` exits 0 for every outcome.

---

## 12. STAGING — AND THE STOP THIS DRAFT DOES *NOT* REGISTER, BECAUSE THE DATA REFUTED IT

### 12.1 THE DESIGN I WAS ABOUT TO REGISTER, AND THE MEASUREMENT THAT KILLED IT

**Recorded rather than quietly dropped, because a reader should be able to see
that the staging survived a refutation.**

This draft was going to register a cheap early stop: *run the coarsest level
first, and if it reads `CYCLING`, stop the ladder and report `S-ONSET` without
paying for the expensive levels.* It is an attractive design and **it is wrong
on this rung's own data.**

**K2d's L1 converged to a Ux initial residual of 9.8e-10 and sat flat from
iteration ~1,200** (§0.2). A coarse-level-first stop would have read
`CONVERGED`, concluded the steady treatment was sound, and **authorised exactly
the expensive levels that then cycled.** The stop would have been pointed at the
one resolution where the phenomenon does not appear.

### 12.2 THE STAGING THAT IS REGISTERED

> **`STAGE-1`. L1 runs first and alone.** From its log the comparator measures
> the **actual** cell-iter/core-s rate and re-derives L2 and L3 **on the N^1.6–
> N^1.77 model of §10.1, never on a linear one**. If the re-derived ladder total
> exceeds **1,890 core-min** — the top of the carried bracket — **L3 is NOT
> LAUNCHED**: the rung stops, reports `PENDING` on its ungraded rows with the
> measured rate and re-derived cost printed, and goes back to the supervisor for
> a re-cost. **An overrun stops the run; it does not get a new budget.**
>
> **`STAGE-2`. L2 runs second.** **THE DECISION POINT IS HERE, at the resolution
> K2d measured as the first to cycle, and not at L1.**
> - **L2 reads `CONVERGED` on both quantities** → L3 is launched and the full
>   triple is attempted.
> - **L2 reads `CYCLING` or `DRIFTING` on either quantity** → **`C-DECOMP`
>   (§4.2) runs at L2's `alt_ranks`**, and then **L3 IS NOT LAUNCHED.** The rung
>   reports **`NOT A RESULT` on every graded row** and **`S-ONSET`** with L1's
>   and L2's states.
>
> **This is registered as a stop on the EXPENSIVE level, decided at the CHEAP
> one where the phenomenon actually appears.** It saves L3's **897–1,593
> core-min** in the branch §4 registers as the expected one, and it is fixed
> **before** compute so it cannot be chosen to fit an answer.

**`STAGE-2`'s stop is NOT a budget stop and must not be recorded as one.** It
stops because **L3 cannot contribute to a triple whose middle level is already
ungradeable** (§0.3), not because the money ran out. Under Sanaa's 16:50Z words
cap-*stops* are exempt for 3D runs; **this is a validity stop and would stand
even with an unlimited budget.**

---

## 13. REGISTERED PREDICTIONS — losable, and scored either way

**`P-K2d-1`, `P-K2d-2` and `P-K2d-3` are carried forward UNSCORED from K2d.**
All three are predictions about readings K2d could never evaluate, and scoring
them from residuals would score them on a quantity they were not written
against (`K2d` §17.6).

> **`P-K2f-1` — the convergence state is a function of resolution.** L1 reads
> `CONVERGED` and **at least one of L2, L3 reads `CYCLING` or `DRIFTING`**.
> **HOLDS** if so; **LOSES** if all three converge, or if L1 does not.
> *Basis: K2d's measured residual floors — 9.8e-10 at 58,368 cells against
> 1.75e-04 at 196,992.*

> **`P-K2f-2` — the cycle is a property of the case, not of the
> decomposition.** `C-DECOMP` returns the **same** `G-CYCLE` state at both rank
> counts. **HOLDS** if so; **LOSES** if the states differ — in which case
> `S-ONSET` is refused (§4.2) and the finding is about the parallel path.

> **`P-K2f-3` — the measured rate model REPRODUCES across rungs.** L1's measured
> cell-iter/core-s, extrapolated at the **N^1.568** exponent of §10.1, predicts
> L2's contention-free cost within **±25 %**. **HOLDS** if so; **LOSES**
> otherwise.
>
> **Stated against its own weakness: this is NOT an independent extrapolation
> test.** The exponent was **fitted on K2d's own L1→L2 pair**, so predicting
> K2f's L2 from K2f's L1 with it tests whether the scaling **reproduces from one
> rung to the next**, not whether it was derivable in advance. It is registered
> anyway, at that reduced strength and with the weakness named, because it is
> nearly free to score and because **the linear model it replaces missed the
> same figure by 98 %** — 52.9 core-min predicted against 104.8 measured
> contention-free — which is the miss that cost K2d 535.600 core-minutes. **A
> genuinely independent test of the exponent needs a FOURTH cell count and is
> not registered here.**

**Every prediction GRADES NOTHING.** Each is scored HIT or LOSS and reported
either way; none can move a gate, a band or a verdict. **They are registered
because a prediction we can lose is worth more than a model chosen to pass.**

---

## 14. WHAT THIS RUNG CANNOT REACH

- **It is not validation and establishes no agreement with any experiment.**
- **It measures one module at one configuration** — `N` = 4, one row, K2a's
  defaults. It says nothing about other `N`, two-row layouts, containment,
  raised floors or plena.
- **It cannot measure model-form error.** The `kOmegaSST` risk K2d recorded at
  its §3.2 — an eddy-viscosity model of the class Wibron's abstract indicts, and
  K0d's SST recirculation finding against Annex 20 LDA data — **is carried and
  is still unmeasurable by this rung.**
- **A `PASS` inside the widened (0.5, 3.5) band is a weak claim** and is not a
  claim of second-order accuracy.
- **`S-ONSET` is a statement about a steady solver's behaviour on three meshes.
  It is NOT a measurement of physical unsteadiness in a data centre**, and no
  K2f sentence may present it as one.
- **Closure is necessary, never sufficient** (`K2a` §8): a solve with the aisle
  flow entirely wrong still closes once converged.
- **THE TRANSIENT SUCCESSOR IS NOT REGISTERED HERE.** If `S-ONSET` reports the
  steady treatment inadequate, the rung that can legitimately time-average is
  `buoyantBoussinesqPimpleFoam` at K2a's planning figure of **5–10×** this
  cost — **a new rung, a new registration and a new cost. A lane does not
  register it and nothing in this document authorises it.**

---

## 15. FREEZE BLOCK — **FILLED AT FREEZE, 2026-09-11.**

| item | value |
|---|---|
| `GRADING_PATH_FREEZE_COMMIT` | *recorded in the freeze commit's message* |
| `build_k2f.py` | `c850883be4e7827de0a0384589b10bf38d472f7e` |
| `analyse_k2f.py` | `c7ccd5f406334b42a6fa32f58d3b83466ec6f235` |
| `mark_done_k2f.py` | `40a1daaae59b10ecd4446747c88588d887adbf45` |
| `launch_k2f.sh` | `97a768d982ff63ebeba081f3c0da74a7b65ec401` — **pinned in this rung**, unlike K2d where it was not |
| `scripts/roache_triple.py` | `23afaee32f770f9f38a827e38ac963b9368b7707` — **re-pinned §19.8**; the draft's pin was the PRE-repair blob |
| referent PDF sha256 | `4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77` |

**`launch_k2f.sh` IS PINNED, and K2d's was not.** K2d's launcher was the file
that accepted a hand-passed guard; a launcher that asserts against a registered
table (§11) is **on the grading path** and is pinned with everything else.

**The comparator verifies each frozen file IS the file that ran by hashing it
against the committed blob, and REFUSES (exit 2) rather than grading if any
digest fails to reproduce.**

---

## 16. ORDER OF OPERATIONS — binding once frozen

1. This document committed, then **frozen by sha by the heat-transfer
   supervisor**.
2. Instruments written; **mutation matrix driven**, `__pycache__` cleared
   between runs.
3. **`A-INPUT` driven, both arms** (§3.1) — recorded.
4. **`A-DRIVE` driven, both directions** (§7) — recorded.
5. **Clause 7 demonstrated BY EXECUTION**, all three limbs — recorded.
6. **§11's launcher assertion demonstrated BY EXECUTION**, both directions —
   recorded.
7. **Supervisor reads every measurement script AS A DIFF, personally.**
8. **Freeze commit verified present on `main`** — the commit *is* there, not
   meant to be.
9. `STAGE-1`: L1 only. Rate measured, ladder re-derived on the N^1.6–N^1.77
   model, §12.2's cost stop evaluated.
10. `STAGE-2`: L2. **The §12.2 decision point.**
11. L3, **if and only if `STAGE-2` permits.**

**Steps 3, 4, 5 and 6 are PRE-FREEZE OBLIGATIONS. Freeze is refused until all
four have been driven and recorded.** Each exists because K2d's absence of it
was measured, not imagined.

---

## 17. WHAT THIS DRAFT DOES NOT DECIDE

1. **Whether this rung is worth running at all.** §0.2 says `P-K2f-1` is likely
   to HOLD, and §4 registers that a HOLD means `NOT A RESULT` on every graded
   row. **The supervisor should decide explicitly whether the deliverable —
   a repaired and demonstrated instrument, plus `S-ONSET` as the registered
   ground for a transient successor — is worth 1,120–1,890 core-min**, or
   whether the line should go straight to a transient registration. **This lane
   does not decide it and has not assumed it.**
2. **Whether the transient successor is built** (§14). New rung, new
   registration, new cost.
3. **Whether `endTime` should be per-level rather than flat.** §10.3 registers
   flat 3,000 with a diagnostic justification; a per-level ladder is a different
   design and is not registered here.
4. **Whether §7.3 of K2d placed its timeout column inside that freeze.** Left
   open there and not settled here; no K2f verdict turns on it.
5. **Whether K2bU3R3's mesh acceptance needs revisiting** in light of §5.4.
   Booked by the supervisor as a disclosure; this document only inherits the
   measurement.

---

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). **This document is a DRAFT, is NOT FROZEN, authorises no compute,
and no run tree exists.** Solver compute spent against it: **zero.***

---

## 18. PRE-FREEZE AMENDMENT 1 — 2026-09-11. **MY COST BRACKET WAS NOT BRANCH-INVARIANT, AND `C-DECOMP` AT L3 WAS UNREGISTERABLE**

**This document is NOT FROZEN, so this is a legal pre-compute amendment under
standing rule 2, which requires the condition and how it was checked.**

**CONDITION:** *"No case directory exists under
`verification/runs/F14-cooling-ladder/K2f_runs/` — no `K2f_L1`, `K2f_L2` or
`K2f_L3` — no `STATUS.*`, no `log.solve`, no time directory and no field."*
**HOW CHECKED:** by `test -d` on disk at **2026-09-11T15:58:08Z**, immediately
before this amendment was written — never by asking git, never by reading a
document. **`K2f_runs/` DOES NOT EXIST. Zero solver core-minutes have been
spent against this document; no gate is being changed after an answer was
seen.**

**Base version amended:** commit `0fda4ce13`, blob
`1c054623fc48a63a039d91fbd463c96bc32ba016`.

### 18.1 HOW IT WAS FOUND — by checking a subtraction I was invited to check

The supervisor computed the cost of the branch where `P-K2f-1` HOLDS by
subtracting §10.2's L3 rows from §10.2's ladder total, and **asked for the
arithmetic to be checked rather than accepted.**

**The subtraction is VALID and the supervisor's figure is right.** Per column:
1122.4 − 897.2 = **225.2** contention-free; 1884.7 − 1592.5 = **292.2**
contended. Exact bracket for that branch: **225.2 – 292.3 core-min**,
**$0.19 – $0.25 derived** (never measured). The supervisor's "223–297" is that
figure to within rounding.

**But checking it exposed that the single bracket cannot be subtracted that way
in general, because §10.2's total silently assumed ONE branch.**

### 18.2 THE DEFECT, STATED PLAINLY

§10.2's ladder row summed `L1 + L2 + L3 + C-DECOMP`, **with `C-DECOMP` priced at
L2**. That is only correct when **L2 is the first level to cycle.** §4.2 runs
`C-DECOMP` at *whichever level first reads `CYCLING` or `DRIFTING`*, and §11's
table registers **no `alt_ranks` for L3** (the cell reads `—`).

**So if L1 and L2 converge and L3 cycles, `C-DECOMP` is UNREGISTERABLE as
drafted, and the branch cost exceeds the bracket I registered.** Computed on
§10.1's model:

| branch | levels run | `C-DECOMP` at | **contention-free** | **contended** |
|---|---|---|---:|---:|
| **B1** — L1 `CONVERGED`, L2 cycles (**`P-K2f-1` HOLDS; the expected branch**) | L1, L2 | L2 | **225.2** | **292.3** |
| **B2** — L1, L2 `CONVERGED`, L3 cycles | L1, L2, L3 | **L3** | **1,914.8** | **3,339.0** |
| **B3** — all three `CONVERGED`, triple graded | L1, L2, L3 | none | **1,017.6** | **1,746.5** |
| **B4** — L1 itself cycles (`P-K2f-1` LOSES) | L1 | L1 | **31.1** | **31.2** |

**B2 exceeds §10.2's registered 1,890 bracket top by 1.01× contention-free and
by 1.77× contended.** A cost bracket that is right for three branches and wrong
for the fourth is the same shape of defect as K2d's flat `endTime`: a number
carried forward without asking whether the case it was computed for is the case
that will occur.

### 18.3 THE REPAIR — and it TIGHTENS the registration rather than loosening it

**1. §11's table gains `alt_ranks` for L3: `4`.** Registered because K2d ran L3
at 4 ranks, so it is a demonstrated configuration on this geometry rather than
a guess. **§11's registered ranks for L3 remain 8 and its hang guard remains
20,187 s, both unchanged.** The `C-DECOMP` re-run at L3 carries its own guard,
computed identically at 3× POINT on **4** ranks: 3 × 897.2 ÷ 4 × 60 =
**40,374 s**.

**2. §10.2's single bracket is REPLACED BY §18.2's PER-BRANCH TABLE**, and the
branch is named in every cost statement. **No figure in §10.1's rate model,
§10.3's `endTime` justification, or §11's registered ranks and guards is
altered by this amendment.**

**3. B2 CARRIES A REGISTERED STOP, and it is a stop rather than a new budget.**

> **If L1 and L2 read `CONVERGED` and L3 reads `CYCLING` or `DRIFTING`,
> `C-DECOMP` at L3 IS NOT LAUNCHED automatically.** The rung stops, reports
> **`NOT A RESULT` on every graded row**, and reports `S-ONSET` **with the field
> `decomp_control: NOT RUN` printed against L3's state.**
>
> **In that branch `S-ONSET` MAY NOT be cited as establishing that the cycle is
> a property of the case rather than of the parallel path.** The gap is labelled
> in the output, not left for a reader to infer. Launching `C-DECOMP` at L3
> requires the supervisor's re-cost against B2's figures — **an overrun stops
> the run; it does not get a new budget** (rule 12).

**This is the honest form.** The alternative — quietly pricing `C-DECOMP` at L2
and running it at L3 anyway — would have spent 897–1,593 unregistered
core-minutes, which is a larger overrun than the one that retired K2d.

### 18.4 `nice` — A REGISTERED DECISION WITH ITS REASON, NOT AN INHERITED HABIT

An **uncommitted** one-line change in the retired `launch_k2d.sh` adds
`nice -n "${NICE:-0}"` to its `setsid` line. It is another agent's unfinished
work, it was **inspected and not reverted** (rule 10), and **nothing here
inherits it.** The supervisor asked that K2f state its own choice and why.

> **REGISTERED: `launch_k2f.sh` does NOT `nice` the solver.**
>
> **The reason is that this lab's cost unit makes `nice` actively
> cost-distorting.** Core-minutes are **wall seconds × ranks ÷ 60**. `nice` does
> not reduce the work done or the wall time of the niced process — it makes that
> process yield, **increasing its own wall time** while its ranks stay
> allocated. A niced K2f would therefore bill **more core-minutes for
> identically the same computation**, and the rung's estimate-versus-actual
> calibration would record a misprediction that was really a scheduling choice.
> K2d already shows the magnitude available to this effect: L3's contention
> factor of **1.775** was measured with no `nice` at all.
>
> **What is registered instead, because contention should be MEASURED and not
> silently managed:** every level records **both `ClockTime` and
> `ExecutionTime`**, and §10's cost rows carry the contention factor
> `ClockTime`/`ExecutionTime` **as a separate column**, never folded into the
> rate. That is what let this rung's model reproduce L2's measured cost to
> 0.1 % (§10.1).
>
> **Contention management belongs in a scheduler, not in a per-rung launcher,
> and it is not a lane's decision to make lab-wide.** This clause binds K2f and
> claims nothing about any other rung.

### 18.5 WHAT THIS AMENDMENT DOES NOT DO

**It changes no gate, no band, no threshold, no floor and no label.** §4's
meaning of `CYCLING`, §5's evaluation order and one-way property, §5.3's order
band, §6's `G-CYCLE` thresholds, §9's completion clauses and §10.3's `endTime`
are untouched. The `alt_ranks` cell it fills was empty, and every cost figure it
adds is **new**, not a relaxation of an existing one. **B2's stop is a
constraint this document did not previously carry**, and B2's cost is disclosed
rather than discovered after launching the expensive level — **which is exactly
what K2d's §7.2 was for and exactly what its §16.2 re-derivation failed to
do.**


---

## 19. PRE-FREEZE AMENDMENT 2 — 2026-09-11T16:46:16Z. **FOUR CORRECTIONS FOUND BY BUILDING AND RUNNING THE INSTRUMENTS**

**This document is NOT YET FROZEN, so this is a legal pre-compute amendment under
standing rule 2, which requires the condition and how it was checked.**

**CONDITION:** *"No case directory exists under
`verification/runs/F14-cooling-ladder/K2f_runs/` — no `K2f_L1`, `K2f_L2` or
`K2f_L3` — no `STATUS.*`, no `log.solve`, no time directory and no field."*
**HOW CHECKED:** by `test -d` on each of the three names and `ls` for
`STATUS.*` and `log.solve`, **on disk**, at **2026-09-11T16:46:16Z**, immediately before this
section was written and **after all of this session's throwaway compute** — never
by asking git, never by reading a document. **All three are ABSENT. Zero solver
core-minutes have been spent against this document; no gate is being changed
after an answer was seen.**

**How found:** the §3.1 and §7 pre-freeze obligations were driven, and driving
them required writing `_functions_block()` and `analyse_k2f.py` and pointing
them at a real OpenFOAM case. **Every correction below was found by execution,
not by re-reading.**

### 19.1 §3 — `T_in,max` AND `θ_i` ARE **DERIVED**, NOT WRITTEN BY FUNCTION OBJECTS

§3 lists four monitored quantities as "Written by in-pass `functions` entries".
**Two of the four are not, and do not need to be.** Struck and replaced:

> **`T_in,i`** and **`U_ha`** are WRITTEN by in-pass `functions` entries —
> `surfaceFieldValue` / `weightedAreaAverage` / `weightField phi` on
> `rack<i>_in` for the first, and `mag` → `magU` → `volFieldValue` /
> `volAverage` over `haZone` for the second.
>
> **`T_in,max`** and **`θ_i`** are **DERIVED BY THE COMPARATOR** from those
> producers:
> - `T_in,max` = max over i of `T_in,i`. **This is a maximum over four PATCH
>   AVERAGES and is NOT what a function object's `max` operation returns**,
>   which is a maximum over FACES — a different quantity, reading the hottest
>   face rather than the hottest rack.
> - `θ_i` = (`T_in,i` − `T_sup`)/`ΔT_rack,i`, an affine map whose two
>   constants are registered at §2 from K2a's defaults.
>
> **`A-INPUT` (§3.1) asserts the PRODUCERS, and the derivations are algebra on
> them.** `U_ha` needs two function objects and not one: `volFieldValue`
> cannot take a magnitude on the fly, and **the volume average of a vector is
> not the volume average of its magnitude** — on a recirculating hot aisle the
> first can sit near zero while the second is the registered number.

**Why this is an amendment and not a detail:** *a registration that misdescribes
how its own gate inputs come to exist is how K2d died.*

### 19.2 §3.1 — THE ARM'S CADENCE, BECAUSE AS REGISTERED THE ARM COULD NOT FIRE

§3.1 registers the throwaway at **"~20 iterations"** while §3 registers a
**50-iteration** function-object cadence. **A 20-iteration run writes NO SAMPLE
AT ALL**, so the arm as registered could not fire. Added:

> **The `A-INPUT` throwaway runs its function objects at a cadence small enough
> that samples land inside its iteration count** — driven at **cadence 2 over 20
> iterations, 10 samples per series**. The **function-object declarations are
> identical to the ladder's**; only `executeInterval`/`writeInterval` differ.
>
> **The reason the cadence must differ is the arm's whole point:** an arm
> asserting on an **empty** producer cannot distinguish *"the `functions` block
> is absent"* from *"the block is present and not yet due"*, and those are
> exactly the two cases the arm exists to separate. The arm must run where the
> distinction is **observable**.
>
> **The ladder's registered cadence is UNCHANGED at 50** (§3, §6.1), and the
> comparator **REFUSES** a graded series written at any other cadence — see
> §19.4.

### 19.3 §5.1 — G4's COLD-AISLE CONTROL VOLUME, **REGISTERED**, WITH ITS ARITHMETIC

§5.1 registers G4 as "volume-averaged `T` over the cold aisle" and **nowhere
defines the volume**, while §3 fixes `U_ha`'s to the metre. A gate whose control
volume is undefined cannot be graded. **Registered here as the exact parallel of
the `HA_BOX` §3 already carries, derived from K2a's approved module geometry:**

> **`CA_BOX` = (0.60, 0.00, 0.00) → (3.00, 1.20, 2.00) m**, cellZone `caZone`.
>
> | axis | `HA_BOX` (registered, §3) | `CA_BOX` (registered here) | rule applied |
> |---|---|---|---|
> | **x** | 0.60 → 3.00 | **0.60 → 3.00**, *identical* | the rack row's first-to-last face: `L_end` = 0.60 to `L_end` + `N·W_r` = 0.60 + 4 × 0.60 = 3.00. Span **2.40 m** |
> | **y** | 2.30 → 3.50, full `W_ha` | **0.00 → 1.20**, full `W_ca` | the aisle's own width. `W_ca` = `W_ha` = **1.20 m** (K2a defaults, §2) |
> | **z** | 0.00 → 2.00 | **0.00 → 2.00**, *identical* | floor to rack top `H_r` = 2.00 m |
>
> **Volume: 2.40 × 1.20 × 2.00 = 5.760 m³ — identical to `HA_BOX`'s 5.760 m³
> by construction**, because `W_ca` = `W_ha` and the x and z extents are the
> same rule. The two boxes are exact mirrors across the rack row.
>
> **Both boxes land on block boundaries exactly**, so `boxToCell` selects whole
> cells and no partial cell is included: y = 0.00, 1.20, 2.30, 3.50 are all
> block edges of the registered `Y` decomposition, as are x = 0.60, 3.00 and
> z = 0.00, 2.00. At L1 each zone is **32 × 16 × 24 = 12,288 cells**, and the
> builder's `topoSet` **measured** `haZone` at **12,288 cells, 5.7600000000
> m³** on the throwaway — the arithmetic is checked against the mesher, not
> asserted.
>
> **Why floor-to-`H_r` and not floor-to-ceiling:** the parallel with the
> registered `HA_BOX` is the reason of record, and the physical reason agrees —
> the 0.70 m above rack top is ceiling-return space, and averaging it in would
> report a volume the racks do not draw from.

**Until this section was written, no G4 verdict was a registered measurement, and
the comparator printed that on every run. It now IS registered; the comparator's
print stands until a reader confirms this section, and it costs nothing.**

### 19.4 §6.1 — THE PRODUCER'S CADENCE IS ASSERTED AGAINST THE CLASSIFIER'S

Found by execution. `scripts/check_convergence.py::classify_monitor` sizes its
window as `window_iterations // sample_interval_iterations + 1` = 400 ÷ 50 + 1
= **9 samples, READ FROM THE THRESHOLD FILE**, and **never reads the time column
of the series it was handed**. A series written at any other cadence is windowed
over the wrong span and **returns a STATE rather than an error.**

> **REGISTERED:** the comparator asserts that every graded series' **measured**
> sample cadence equals §6.1's registered **50**, and **REFUSES (exit 2)**
> otherwise. It also asserts that the thresholds `classify_monitor` actually
> used equal this document's registered numbers, and **refuses on drift** — a
> threshold file that has moved away from the registration is a refusal, never a
> silent regrade.

**This is not K2f-specific and nothing else in the lab has it.** Routed to the
verification team as lab property; it binds K2f here and claims nothing about
any other rung.

### 19.5 §15's cross-check constant — **2.0576 %, not 2.0575 %**

The published T23G2R Q4 row reads **order 0.9917, GCI 2.0576 %** at
`verification/runs/T-family/T23G2R_runs/T23G2R_COMPARATOR_STDOUT.txt:125`.
`analyse_k2f.py --xcheck` reproduces both exactly and runs inside
`--selftest`, so the citation sits in an executable check (standing rule 6).

### 19.6 WHAT THIS AMENDMENT DOES NOT DO

**It changes no gate, no band, no threshold, no floor and no label.** §4's
meaning of `CYCLING`, §5.2's evaluation order and one-way property, §5.3's
order band (0.5, 3.5), §6.1's 0.02 % / 400 / 50 / 9 thresholds, §9's completion
clauses, §10.3's `endTime` 3000, §11's ranks and guards and §12.2's L2 stop are
**untouched**. §19.3 fills a control volume that was **empty**, and §19.1, §19.2
and §19.4 make the document describe what its own instruments do. **§19.4 is a
constraint this document did not previously carry.**

### 19.7 **THE PRE-COMPUTE CONDITION, RESTATED AS WHAT WAS ACTUALLY CHECKED — because as written it is now FALSE**

**The header condition of this document (§0, and §18's opening) reads
`K2f_runs/` **DOES NOT EXIST**. THAT IS NOW FALSE.** The directory exists and
holds `build_k2f.py`, `analyse_k2f.py`, `mark_done_k2f.py`,
`launch_k2f.sh` and three demonstration files. **Struck and replaced by what
was checked:**

> **CONDITION AS CHECKED:** `verification/runs/F14-cooling-ladder/K2f_runs/`
> **exists and contains instruments and demonstrations only** — it carries
> **zero level directories (`K2f_L1`, `K2f_L2`, `K2f_L3`), zero
> `STATUS.*`, zero `DONE.*` and zero `log.solve`.**
>
> **COMMAND RUN, VERBATIM, at 2026-09-11T16:48:24Z:**
> ```
> find K2f_runs/ -maxdepth 2 \( -name "K2f_L[123]" -o -name "STATUS.*" \
>      -o -name "DONE.*" -o -name "log.solve" \) | wc -l
> ```
> **Result: `0`.** Zero solver core-minutes have been spent against this
> document.

**WHY THIS IS AN AMENDMENT AND NOT A QUIBBLE.** The substance was true and
reported truthfully throughout; only the *text* went stale the moment instruments
were written into the directory. But **a pre-compute condition is the entire
evidentiary content of standing rule 2** — it is what proves the gate could not
have been chosen to fit the answer — and **a condition a later reader can falsify
with one `test -d` destroys that proof even though nothing dishonest
happened.** An amendment resting on a condition that is false as written is
**DEFECTIVE EVEN WHERE ITS SUBSTANCE HOLDS**, and this is the K2d failure class
exactly: **K2d died of a registration whose text described a state of the disk
that the disk did not have.** §18's amendment, written when the directory really
was absent, was sound when written and is re-grounded here.

### 19.8 `scripts/roache_triple.py` — **RE-PINNED**, because the pinned blob was NOT the file that would run

**Found by checking the pin rather than trusting it, immediately before freeze.**
§15 pinned `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8`; the file on disk is
`23afaee32f770f9f38a827e38ac963b9368b7707` — the verification team repaired the
shared instrument at commit `a7b3846d8` **this same hour**, after this rung's
cross-check was taken. The repair is **verdict-neutral** (`why` text only; a
state it has not been taught now REFUSES instead of reaching for a reassuring
sentence), so nothing measured is invalidated.

> **§15 is re-pinned to `23afaee32f770f9f38a827e38ac963b9368b7707`, the file
> that will actually run.** The cross-check was **re-driven against the repaired
> file** and still reproduces the published T23G2R Q4 row exactly — **order
> 0.9917, GCI 2.0576 %**.
>
> **AND THE COMPARATOR NOW CHECKS IT.** `verify_freeze()` originally hashed
> only this rung's own four files, so §15's claim that the comparator "verifies
> each frozen file IS the file that ran" was **not true of the shared
> instrument**. It now covers every file §15 pins and **REFUSES (exit 2)** on any
> mismatch. **A shared instrument moves under a rung without the rung being
> told — that is what makes it shared — so the digest is checked at GRADE time
> and not only at freeze time.**

