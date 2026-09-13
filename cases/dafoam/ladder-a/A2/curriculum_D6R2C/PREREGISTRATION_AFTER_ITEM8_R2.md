# Curriculum D6R2C — PRE-REGISTRATION for the SUCCESSOR to Sanaa's AFTER-ITEM 8

**Item id:** `D6R2C-AFTER8-R2`. Successor to after-item 8, whose arms `DEC`, `DEC2` and `DEC3` are
each closed at **`NOT A RESULT`** and are never re-graded.
**Version 1.2 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`;
carried to 1.1 the same day by that supervisor's six rulings on the draft (§0d), and to 1.2 by the
constant-sweep defect find the supervisor's read forced (§8a) — **all before any compute**.
**This item has burned 0 core-min, started 0 containers and generated 0 meshes at the time of writing.**
**The rule-2 pre-compute condition, stated and checked rather than asserted:** amendments to this file are
legal only while it has produced no compute, and the test of that is that its registered run root
**does not exist**. Checked 2026-09-13 by `ls -d`:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R2-a2-wing-decomposition-retrimmed` —
`No such file or directory`. **After the freeze commit this file takes dated addenda only, and none of
them may alter a gate, a threshold, a cap or a label.**
It is frozen by the commit that introduces this file **together with its three instruments** (section 11).
**No container starts until that commit exists** (`CLAUDE.md` rule 2), and the supervisor's non-delegable
check is the commit, not this sentence.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6): `PREREGISTRATION.md` and `PREREGISTRATION_AFTER_ITEMS.md` are
cited and changed in no respect.

---

## 0. WHY THIS IS A NEW DOCUMENT, AND WHAT KILLED THE ONE IT SUCCEEDS

`PREREGISTRATION_AFTER_ITEMS.md` §1a registered a shape-only state `J_S` **on the assumption that
shape-only is trimmable at matched lift.** Arm `DEC3` measured that assumption false.

**The measurement, from `DEC3`'s own log**
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh/DEC3_20260913T055645Z_1368828.log`):

| what | value | log line |
|---|---|---|
| shape-only `CL` at the baseline incidences | `0.66061408 / 0.74724936 / 0.82092578` | 13554 |
| the registered targets | `0.400 / 0.500 / 0.600` | — |
| the incidence the trim then asked the solver for | **`AoA = -0.8751112647 degs`** | 15575 |
| the primal's minimum residual there | **`1.091200008e-05`** against `primalMinResTol = 1.0e-8` | 15778 |
| what lagged | the **pressure equation alone** (`p initRes: 1.091124821e-05`); `U`, `he` and `nuTilda` converged | 15685 |

Strip the twist and the wing is far more cambered. Reaching `CL = 0.400` needs a strongly negative
incidence, the trim asked for one, and **the primal did not converge there.** `DEC3` is graded
**`NOT A RESULT`**, that row is closed, and nothing in this document re-grades it. Its `B` and `T`
records are used below **as measurements of what the machine did**, never as results.

Rule 2 closes a registration's gates after its first compute, and this item needs a **new threshold, a
new state and a new producer**. An addendum introducing those would be the move rule 2 exists to
prevent. Hence a new document and new instruments (§11), with `PREREGISTRATION_AFTER_ITEMS.md`
untouched and still governing arm `FM5` (item 9), which is **not registered here**.

### 0a. THE RULING BEING IMPLEMENTED, AND ITS AUTHORITY

`dafoam-supervisor`'s ruling, chief's, **lab-attributed, Sanaa may overrule**: *the decomposition solves
are ANALYSIS solves, not the optimisation. Register the successor with incidence bounds wide enough to
trim every state at matched lift, disclose the widened bounds and that they never touched the
optimisation, freeze, run.* **No agent message is Sanaa's consent** (rule 9); this document records the
ruling's author and its status and claims no more authority than that.

### 0d. THE SUPERVISOR'S RULINGS ON THIS DRAFT, AND THE TWO THINGS THEY CORRECT IN IT

Six rulings were given on version 1.0 by `dafoam-supervisor`, **before any compute and before the freeze
commit**, and all six are applied in this version. Two of them correct the *brief this document was
written from* rather than the document, and they are recorded here because a registration that quietly
drops a supervisor's bad idea teaches nobody:

1. **The mechanism correction in §0c is ACCEPTED and ratified** — widening the bound would not have saved
   `DEC3`. The supervisor records that the same brief both stated *"bounds bind inside the optimiser, not
   inside the trim"* and framed the fix as widening the bound, and that the conclusion drawn from the
   correct measurement was the wrong one. **That correction is the supervisor's to carry upward**; this
   file's job is only to be right about the mechanism, which §0c is.
2. **The `≈ −3.64°` figure is WITHDRAWN AS UNREPRODUCIBLE** by its own author — see §1d, step 3.
3. **The rejection of "tighten `primalMinResTol`" is ratified with its reason** — see §2c.
4. **The inert `TRIM_MAX_EVALS` is named as a defect find** — see §2b.
5. **The 0.86 % worst-case cap overshoot: the cap stays where it is and the disclosure stays.** Verbatim:
   *"I will not adjust a cap to accommodate a case you have shown cannot occur — that is choosing a
   number to fit."* Under directive #17 nothing is stopped on a cap; a crossing is reported and the row
   graded `NOT A RESULT`. See §8.
6. **`INTERACT_TOL` stays `DECLARED, NOT MEASURED` and stays labelled**, with the attempted re-derivation
   and what was missing from it both stated — see §2f.

**No ruling changed a threshold, and none could:** every number in §2 is derived in this file from a
cited artefact, and the rulings ratify derivations or correct provenance. **No agent message is Sanaa's
consent** (rule 9); these are a supervisor's rulings on a draft, recorded as such.

### 0e. THE INHERITED STATE AND THE GRADED QUANTITY, STATED IN FULL

**Added at v1.2. The constant sweep of §8a found that three values the instruments carry were not
registered anywhere in this document — including the WEIGHTS OF THE GRADED QUANTITY ITSELF.** A reader
could not have checked those literals against anything. They are stated here.

| quantity | value | artefact | md5 of artefact |
|---|---|---|---|
| `J0` — baseline weighted mean `CD` | `0.0306416314389976151` | `O_mp/d6r2c_evals.jsonl`, `F` record `n = 2` | `2c0b8143caad198cd2e21d8047986aa3` |
| `Jf` — final weighted mean `CD`, as optimised | **`0.0230632595286777639`** | same file, `F` record `n = 88` | same |
| the design vector `x0` and the driver scalers | 96 `shape`, 7 `twist`, 3 `patchV_*` | `O_mp/d6r2c_x0.json` | **`b225fe7fdbd12eaa8a9b8a70835849c8`** |
| the frozen optimisation runscript | — | `d6r2c_opt_runScript.py` | `2f2ae43a627146cf8e0f065b035ada4b` |

**THE GRADED QUANTITY.** `J` is the **weighted mean drag coefficient** over the three conditions:

```
J = 0.25 × CD04  +  0.50 × CD05  +  0.25 × CD06
targets: cl04 -> CL = 0.400 , cl05 -> CL = 0.500 , cl06 -> CL = 0.600
```

**`WEIGHTS = {0.25, 0.50, 0.25}` is carried unchanged from `PREREGISTRATION.md` §1** — it is the
objective `O_mp` was optimised against and it is not this document's to alter. The grader **recomputes
`J` from the per-condition `CD` and these weights** and refuses if the producer's own `J` disagrees by
more than `1.0e-12` absolute; it never takes the producer's word for the graded quantity.

**How the two `J` values are used, because the distinction matters.** `J0` and `Jf` reach the gates by
being **read out of the md5-pinned artefact at grading time**, not from any literal. The module
constants `J0_INHERITED` and `JF_INHERITED` in `d6r2c_dec4_grade.py` are used **only** in the planted
control's refusal message and in the selftest's synthetic tree. A reader seeing them would reasonably
assume they were the anchors; they are not, and that is said here rather than left to be assumed.

**`X0_MD5` IS NOW READ.** In the v1.1 instrument it was declared and never used — see §8a.

### 0b. THE ARGUMENT THAT MAKES THIS LEGITIMATE RATHER THAN A WIDENED THRESHOLD

**The incidence bound `[0.0, 10.0]` is an OPTIMISER DESIGN-VARIABLE bound.** It is written at
`d6r2c_opt_runScript.py:280`:

```python
self.add_design_var("patchV_" + pt, lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)
```

`add_design_var` bounds constrain **what the optimiser may explore**. They are handed to IPOPT and to
nothing else. **A decomposition state is an analysis solve at a prescribed lift, not an optimisation**,
so that bound has no optimisation meaning there.

**THE WIDENED BOUND APPLIES ONLY TO THE ANALYSIS SOLVES OF THIS SUCCESSOR AND NEVER TOUCHED `O_mp`.**
`O_mp`'s result stands exactly as graded: **`GATE FAIL`**, missing `G3` by **2.79×** (worst `CL` miss
`2.787e-03` against the frozen `1.0e-3`), **24.732273 %** weighted drag reduction,
**`Jf/J0 = 0.7526772709407745`**.

**A reader is entitled to check that, and here is how.** The optimisation runscript is **not edited**.
It is loaded by the producer from its own unedited bytes and md5-asserted at
**`2f2ae43a627146cf8e0f065b035ada4b`** — the bytes `O_mp` ran — in three independent places:
`d6r2c_dec4_decomp.py`'s `load_frozen_model`, `d6r2c_dec4_run_arm.sh`'s `G-FREEZE`, and
`d6r2c_dec4_grade.py`'s `D6` (which reads the md5 the producer recorded and fails the gate if it is not
that value). The widened bound exists **only** as a constant in `d6r2c_dec4_decomp.py`. If that md5 ever
moved, the claim in this section would be false, and that is exactly where it is checked.

### 0c. THE CORRECTION THIS DOCUMENT MAKES TO ITS OWN RULING — MEASURED, NOT ARGUED

**WIDENING THE BOUND WOULD NOT HAVE SAVED `DEC3`, AND A SUCCESSOR THAT ONLY WIDENED IT WOULD FAIL THE
SAME WAY.** This is stated first because it is the most important thing in the document.

`findFeasibleDesign` calls `prob.set_val` on `patchV_<pt>` and then `prob.run_model()`
(`mphys_dafoam.py:1175`). It never consults `add_design_var`'s bounds. The `DEC3` traceback is
`AnalysisError: Primal solution failed!` — **not a bound violation.** The trim had already walked
**below** the registered bound, to `-0.8751112647 deg`, and the run died because the **primal stalled**.

So the bound was never binding, and the mechanism that failed is the primal's ability to converge at an
incidence far from the field it starts from. This successor therefore registers **two** changes, and
says which is which:

1. **The widened bound (§1d)** — a **record-consistency** change. It makes the analysis states legal
   inside a declared design space and gives the producer something to assert. On its own it changes
   nothing that executes.
2. **The incidence continuation (§1f)** — the change that addresses the **measured** failure. Every
   incidence jump larger than a measured-converging size is walked in sub-steps, each a converged
   primal, so the trim never again asks for a 3.8-degree jump from a cold-ish field.

---

## 1. WHAT IS REGISTERED

### 1a. THE STATES — SIX, AND WHY

`PREREGISTRATION_AFTER_ITEMS.md` §1a's reasoning is re-read and re-affirmed, not copied: `J_S` exists
because **without it the "shape vs twist" split is an ordering, not a measurement** (§3, `D4`, and the
interaction term `I`); `J_B` exists because the baseline's per-condition `CD` **does not exist anywhere
on disk** (`d6r2c_evals.jsonl` records `obj.J`, three `CL`s, `thickcon` and `volcon`, and no `CD04/05/06`);
`J_opt` exists because it is the reproduction control and because `Δ_trim` cannot be computed without it.

| symbol | state | `shape` | `twist` | `AoA` | gated? |
|---|---|---|---|---|---|
| `J_B` | baseline, trimmed | `0` (96) | `0` (7) | `A(0, 0)` | **YES** |
| `J_T` | twist-only, re-trimmed | `0` (96) | `t*` | `A(0, t*)` | **YES** |
| `J_S` | **shape-only, re-trimmed** — the state `DEC3` could not reach | `s*` | `0` (7) | `A(s*, 0)` | **YES** |
| `J_F` | the full optimum, re-trimmed | `s*` | `t*` | `A(s*, t*)` | **YES** |
| `J_opt` | the optimiser's own final state, **not** trimmed | `s*` | `t*` | `a*` | **YES** |
| `J_B2` | **the baseline re-trimmed a SECOND time, from `O`'s fields** | `0` (96) | `0` (7) | `A(0, 0)` | **NO — REPORTED, NEVER GATED** |

Registered order: **`B → T → S → F → O → B2`**, one container, cold from `0.orig`.
`s*`, `t*` and `a*` are read from `O_mp/d6r2c_evals.jsonl` `F` record `n = 88`, **in the driver-scaled
space that file records**, md5-pinned at `2c0b8143caad198cd2e21d8047986aa3`, and never transcribed here
(L-221/L-222).

### 1b. WHY `B2` EXISTS, AND WHY IT IS NOT A GATE

`N-D48` measured that on this stack **repeating a run is bitwise exact (floor exactly zero)** while
**reaching the same design point by a different path moves `J` by ~3e-5 relative** — and it says in as
many words that the `~3e-5` is *"ONE measurement at ONE design point on one configuration, not a
characterised distribution … a lower bound on what to expect, not a bound to register against."*

`B2` is the same design point as `B` and differs **only in the fields it is reached from** (`B` is cold;
`B2` follows the `O` state). `|J_B2 − J_B|` is therefore a **direct second measurement of exactly that
path-dependence**, at a cost of one state. It is **REPORTED, NEVER GATED**: registering a gate on a
quantity with one prior measurement is precisely what `N-D48` forbids. The grader's selftest drives a
control proving it: moving `J_B2` by `1.0e-2` relative **does not change the label** and **is** reported.

### 1c. "BEFORE ANY PERCENTAGE IS QUOTED" — MECHANICAL, INHERITED UNCHANGED

Sanaa's clause is carried from `PREREGISTRATION_AFTER_ITEMS.md` §1c without alteration and is enforced
by `d6r2c_dec4_grade.py`, not by discipline: the absolute table is written first, and **no percentage
field is written at all** unless every cell is present and finite and every gate but `D4` holds. A hole
in the table is a refusal (`exit 2`, `REFUSE_NO_TABLE`), and the percentage keys are **absent**, not null
and not zero. Every share names its denominator **in the same record** (§1b of that document: the
24.732 % is the reduction at *unmatched* lift and is **not** the number the split applies to).

### 1d. THE INCIDENCE BOUND — DERIVED, NOT CHOSEN

**Step 1 — the demand.** The binding state is `S` at `cl04` (the lowest target on the most cambered
geometry). Three estimates of the incidence that holds `CL = 0.400` there, each from a measured number:

| estimate | arithmetic | result |
|---|---|---|
| **(a) local lift slope** | `dCL/dα` from the trim's own finite difference: `(0.6606825571 − 0.6606140775)/0.001 = 0.0684796` per deg; `2.9303833722 + (0.400 − 0.6606140775)/0.0684796` | **`−0.8753351 deg`** |
| **(b) secant over the measured excursion** | slope `(0.6606140775 − 0.3562777155)/3.8054946369 = 0.0799729` per deg through the two measured `(α, CL)` points; root from the lower point | **`−0.3283974 deg`** |
| **(c) additivity of the measured trim increments** | `a*_cl04 − (A_T,cl04 − A_base,cl04) = 0.577498771 − (3.9002946370 − 2.9303833722)` | **`−0.3924125 deg`** |

(a) is the linear extrapolation the trim itself performed, and it **overshot**: the measured `CL` at
`−0.8751112647 deg` was `0.3562777155`, *below* the target, so the true root lies above. (b) and (c)
agree to `0.064 deg`. **The most negative root any measurement of mine supports is `−0.8753 deg`, and
the best two estimates put it near `−0.35 deg`.**

**Step 2 — the iterates, not the root.** A root-finder visits points it does not keep. The **measured**
overshoot fraction, from the one overshoot on record:

```
Newton step   = 2.9303833722365633 − (−0.8751112647) = 3.8054946369 deg
overshoot     = |−0.8751112647 − (−0.3283974)|        = 0.5467139 deg
fraction f    = 0.5467139 / 3.8054946369              = 0.14366435
```

**Step 3 — THE SUPERVISOR'S UNREPRODUCIBLE FIGURE, WITHDRAWN BY ITS OWN AUTHOR, AND COVERED ANYWAY.**
The brief this document was written from states that reaching the low target needs incidence
**≈ −3.64°**. **It is not reproducible from any `DEC3` artefact.** The string `3.64` does not appear in
the arm's log except in unrelated residual values; the only negative incidence ever requested was
`−0.8751112647`; and the three derivations above give `−0.88`, `−0.33` and `−0.39`.

**`dafoam-supervisor` re-derived it independently and withdrew it**, 2026-09-13, before the freeze: from
the same measured points — `CL = 0.661` at `AoA = 2.930383`, slope `0.0684796`/deg — the incidence for
`CL = 0.400` is **`−0.881`**, which agrees with this document's `−0.8753351` to the third digit. The
supervisor records the provenance in their own words: *"My −3.64 was a figure I inherited from a lane's
extrapolation and repeated as measured."*

**So `−3.64` is recorded here as an UNREPRODUCIBLE FIGURE, not as a derivation that happens to differ,
and this document does not dress it up as one.** It is nonetheless **covered** by the registered bound,
because covering it costs nothing: a bound too tight costs a `NOT A RESULT`, while a bound too wide costs
only that the physics, and not the bound, is what decides. With `f` applied to it:

```
step_req      = 2.9303833722365633 − (−3.640)        = 6.5703833722 deg
overshoot_req = 0.14366435 × 6.5703833722            = 0.9439298 deg
worst iterate = −3.640 − 0.9439298                   = −4.5839298 deg
```

**Step 4 — the physical sanity limit.** The case is a **lift-constrained cruise wing at three positive
target lifts**. It stops being that case at the shape-only wing's **zero-lift incidence**, below which
the wing carries negative lift and no statement about "matched lift at `CL = 0.4`" is being made in the
case as posed. Two measured estimates:

```
local slope   : 2.9303833722 − 0.6606140775 / 0.0684796 = −6.7164907 deg
secant slope  : 2.9303833722 − 0.6606140775 / 0.0799729 = −5.3300930 deg
```

**The conservative one is registered: `A_sanity = −5.3300930 deg`.** (It is conservative because the
secant uses a measured far-field point rather than a local derivative extrapolated nine degrees.)

There is a **second, harder and entirely separate limit that is not aerodynamic**: the primal is
**measured** to converge at every incidence `DEC3` visited in `[+2.9303833, +7.0309608]` and is
**measured to fail** at `−0.8751113`. **The solver's convergence envelope on this mesh has its lower
edge somewhere in `(−0.8751113, +2.9303833]`, and nothing on disk locates it more precisely.** That is
disclosed here, before the run, because it — not the registered bound — is what will decide whether
state `S` is reachable.

**Step 5 — the bound.** The registered bound is the **midpoint of the largest demand ever put on the
record (withdrawn or not) and the sanity limit**: the bound is placed exactly halfway between the most negative incidence anyone has
claimed is needed and the incidence at which the case stops being the case.

```
AOA_LOWER_DEG = ( −4.5839298 + (−5.3300930) ) / 2 = −4.9570114 deg
AOA_UPPER_DEG = 10.0                                (INHERITED unchanged from the runscript)
```

**`AOA_LOWER_DEG = −4.9570114 deg`.** It sits `0.3730816 deg` inside the sanity limit; it covers the
withdrawn `−3.64` figure's worst iterate by `0.3730816 deg`; and it covers the worst iterate the
surviving measurements support (`−0.8753351`) by a factor of **5.66**. **The bound is deliberately NOT
re-derived downward now that `−3.64` is withdrawn**: a bound recomputed after a figure was retracted
would be a bound chosen after seeing which way the argument went, and the wider one costs nothing. `AOA_UPPER_DEG` is inherited: the largest incidence any
state needs is `+7.0309608` (measured, state `T`, `cl06`), and the trim never approached 10.

**IF A STATE STILL CANNOT BE TRIMMED INSIDE IT.** The producer **refuses** (`exit 2`,
`REFUSE_AOA_OUT_OF_BOUND`), the state is **`NOT A RESULT`**, and the requested incidence and the bound
are printed. **THE BOUND IS NEVER WIDENED AT RUN TIME OR AFTERWARDS, AND THE REASON IS PHYSICAL, NOT A
PROMISE:** below `A_sanity` the wing carries negative lift and the case is no longer the case that was
registered. A successor that needed a wider bound would be registering a different experiment.

### 1e. THE CONTINUATION — THE CHANGE THAT ADDRESSES THE MEASURED FAILURE

**`AOA_STEP_MAX_DEG = 0.987284431 deg`** — the **largest single incidence jump whose primal is MEASURED
to have converged on this case**. Every incidence `DEC3` visited, with its outcome:

```
converged: 2.930383372 2.931383372 3.878878201 3.879878201 3.900280084 3.900294637 3.901280084
           4.326126896 4.327126896 5.278160791 5.279160791 5.316955936 5.317036089 5.317955936
           5.941267044 5.942267044 6.928551475 6.929551475 7.029302908 7.030302908 7.030960807
FAILED   : -0.8751112647
```

The largest converging jump is `cl06`'s first Newton iterate of state `T`, `5.941267044 → 6.928551475`
= `0.987284431 deg` — **and that jump changed the geometry as well as the incidence**, so it is a harder
test than a pure incidence step, which is the conservative direction. The jump that **failed** was
`2.930383372 → −0.8751112647` = `3.805494637 deg`, **3.85× larger**.

**`CONT_MAX_STEPS = 12`** — `ceil( (5.941267044 − (−4.9570114)) / 0.987284431 ) = ceil(11.0387) = 12`,
the worst legal excursion divided by the step. Past it the producer refuses
(`REFUSE_CONTINUATION_TOO_LONG`) rather than walking forever.

The producer wraps `prob.run_model` (`IncidenceGovernor`), so it governs the calls `findFeasibleDesign`
makes **internally** — the only place `DEC3`'s jump could have been caught. **It changes no value any
caller observes:** the requested incidence is always the last one solved, so the trim reads the `CL` at
exactly the incidence it asked for; only the field it starts from differs.

### 1f. WHAT `Δ_trim` IS, INHERITED UNCHANGED

The optimiser's final state is **not** at matched lift, and that drag credit is never charged to the
wing's geometry:

```
Δ_trim   ≡ J_opt − J_F                     the drag credit taken by NOT holding lift
Δ_shape  + Δ_twist         = J_F − J_B     the geometric gain AT MATCHED LIFT
Δ_shape  + Δ_twist + Δ_trim = J_opt − J_B                       (identity; gate D3)
```

Both signs of `Δ_trim` are registered outcomes and neither is a surprise afterwards.

---

## 2. THE GATES, FROZEN — AND FOR EACH, WHETHER IT WAS RE-DERIVED OR INHERITED

Graded by **`d6r2c_dec4_grade.py --item 8R2`**, reading `DEC4/d6r2c_dec4.jsonl`, the arm directory, the
arm's own age datum and the md5-pinned inherited artefacts — **all after the container exits.**

| gate | threshold | **re-derived or inherited** |
|---|---|---|
| `D1` trim | `TRIM_TOL = 1.0e-6` | **RE-DERIVED, RETAINED** — §2a |
| `D1` counting | `TRIM_MAX_EVALS = 15` | **RE-DERIVED** from 40 — §2b |
| `D1` incidence | `AOA_LOWER_DEG = −4.9570114`, `AOA_UPPER_DEG = 10.0`, `AOA_STEP_MAX_DEG = 0.987284431`, `CONT_MAX_STEPS = 12` | **NEW** — §1d, §1e |
| `D2-J` | `REPRO_TOL = 1.7162447e-04` relative | **RE-DERIVED** from `1.0e-5` — §2c |
| `D2-GEO` | `GEO_TOL = 1.0e-12` absolute | **NEW** — §2d |
| `D3` | `CLOSE_TOL = 8.423462e-15` | **RE-DERIVED** from `1.0e-12`, **strictly tighter** — §2e |
| `D4` | `INTERACT_TOL = 0.10` | **INHERITED, and still DECLARED NOT MEASURED** — §2f |
| `D5` | refusal, no threshold | **INHERITED unchanged** — §1c |
| `D6` | completion and hygiene, cap `416.919` core-min | **INHERITED, with one NEW clause** — §2g |
| plant | `PLANT = 1.234e-03` | **INHERITED, re-checked against every new threshold** — §7 |

### 2a. `D1` — `TRIM_TOL = 1.0e-6`. RE-DERIVED AND RETAINED, WITH ITS HEADROOM CORRECTED

`PREREGISTRATION_AFTER_ITEMS.md` §3b justified `1.0e-6` as *"24× tighter than the tolerance registered
here"*, from `findFeasibleDesign` achieving `max miss = 4.208e-08` at `x0`. **`DEC3` measured the real
figure and it is much worse than that:**

| state | max `CL` miss achieved | headroom against `1.0e-6` |
|---|---|---|
| `B` | **`5.642771e-07`** (`cl06`) | **1.77×**, not 24× |
| `T` | `1.010771e-08` (`cl06`) | 99× |

**The tolerance is retained at `1.0e-6` and the correction is disclosed rather than used to widen it.**
It is still 1000× tighter than `G3`'s `1.0e-3`, so it cannot hide trim slack — which is the whole reason
it exists. **A state that misses it is `NOT A RESULT` with the achieved miss printed, and `TRIM_TOL` is
never widened** (`PREREGISTRATION_AFTER_ITEMS.md` §3a's prohibition, carried).

The band edge is not representable in IEEE double and **no tolerance was added to `D1` to make it
reachable**; the control drives the attainable values one ulp apart on the coarsest-ulp target, as §3c
of the predecessor records.

### 2b. `D1` — `TRIM_MAX_EVALS = 15`. RE-DERIVED, AND A DEFECT FIND

**DEFECT FIND, NAMED AS ONE AT `dafoam-supervisor`'s instruction: THE REGISTERED CAP OF 40 HAD NO EFFECT
AT ANY POINT IN ANY ARM OF AFTER-ITEM 8. IT WAS A GATE THAT EXISTED ONLY ON PAPER.**

That is the same family as **L-579** — a registration naming an instrument that did not exist — one step
further along: here the instrument existed, the clause existed, the threshold was frozen and published,
and **the code path that would have enforced it was never entered.** A gate is not a gate until
something has been shown to fail it.

**The mechanism.** `d6r2c_after_grade.py:337` reads
`if isinstance(n, int) and n > TRIM_MAX_EVALS`, and **every `DEC3` state recorded
`"n_trim_evals": null`** — `findFeasibleDesign` did not return an int and the fallback
`prob.model._nl_solver_evals` was absent. A cap that cannot be read is not a cap.

Two changes, both registered here:

1. **The count is MEASURED**, by the governor's own call counter, minus the continuation sub-steps
   (which are the producer's doing, not the trim's).
2. **A null count is now a `NOT A RESULT`**, not a silent pass. The grader's selftest drives it — which
   is the point: the clause is now demonstrated to fire, against a synthetic record carrying exactly the
   `"n_trim_evals": null` that every `DEC3` state carried.

**The general rule this pays for, offered to the lab rather than kept here:** a threshold guarded by
`isinstance(x, T) and x > limit` is **inert whenever the producer does not supply `x`**, and a
registration that does not require the producer to supply it has registered a number, not a gate.
**For every gate, drive a control in which it FAILS** — a gate never seen to fire is not evidence that
nothing failed it.

**The value.** `DEC3`'s converging trim visited **5 distinct incidences per condition** in state `T`
(`3.878878201, 3.879878201, 3.900280084, 3.901280084, 3.900294637`). `15 = 3 × 5` — three times the
measured need. **The risk of tightening is stated: a genuinely slow trim now produces `NOT A RESULT`
where 40 would have let it finish.** The registered response to that is a **new registration with a
re-derived cap**, never a widened one mid-flight.

### 2c. `D2-J` — `REPRO_TOL = 1.7162447e-04`. THE HARDEST NUMBER IN THIS DOCUMENT

The predecessor registered `1.0e-5` on `|J_B − J0|/J0` and the run missed it at **`2.860408e-05`**.
`N-D48` explains why, and its explanation rules out the easy answers.

**THE TWO OPTIONS, AND WHY THE ONE THE SUPERVISOR PROPOSED CANNOT WORK.**

`dafoam-supervisor`'s brief offered two: derive a tolerance from the measurement, **or tighten
`primalMinResTol` so the path-dependence falls below the tolerance**. **The second cannot work, and the
arithmetic is short.** It is set out here rather than quietly dropped, at the supervisor's own
instruction — *"a registration that quietly drops a supervisor's bad idea teaches nobody"* — and the
rejection is ratified by them with this reason.
Write `J*` for the exact fixed point and `e` for how far past the tolerance crossing an iterate landed:

```
J0  = J* + e0 ,  |e0| ~ C × 1.0e-8      J0 was produced at primalMinResTol = 1.0e-8 and is FIXED
J_B = J* + eB ,  |eB| ~ C × tau         tau is whatever THIS run converges to
|J_B − J0|  ->  |e0|  as tau -> 0
```

**Tightening this run's primal shrinks `eB` and leaves `e0` exactly where it is.** The gate compares
against an **md5-pinned artefact that cannot be re-converged without destroying the external anchor that
makes it worth comparing against** (L-588). So `|J_B − J0|` is bounded below by `J0`'s own tail no matter
how hard this run converges — and it would cost more compute to learn nothing. **Option 2 is rejected on
a derivation, not a preference, and the supervisor ratified the rejection on reading it.** The general
form is worth carrying: **converging YOUR run harder cannot close a gap against a FIXED reference that
carries its own tail.** It is the price of the external anchor, and the anchor is worth more than the
tightness (L-588).

**WHAT IS REGISTERED, AND ITS DERIVATION.** `N-D48`'s measurement calibrates the mechanism:

```
measured    |J_B − J0| = 8.764756375991e-07 absolute at tau = 1.0e-8
C           = 8.764756e-07 / 1.0e-8                  = 87.648   (dJ per unit residual)
both ends   2 × C × 1.0e-8                           = 1.7529513e-06 absolute
relative    1.7529513e-06 / 0.0306416314389976151    = 5.7208157e-05
safety x3   (N-D48: "ONE measurement at ONE design point … a lower bound, not a bound to
            register against")                        = 1.7162447e-04
REPRO_TOL   = 1.7162447e-04 relative = 5.258854e-06 absolute = 0.0526 drag counts
```

**The factor 3 is a stated margin, not a measurement, and it is labelled so in the record.** The
resulting band sits **6.00×** above the one path-dependence figure that exists — which is the point:
`N-D48` says that figure is a lower bound, so a band at `1×` it would be a band chosen to be missed.

**WHAT IT COSTS, SAID PLAINLY.** At `1.7162447e-04` relative, `D2-J` can no longer see anything smaller
than **0.053 drag counts** in `J`. It is a **gross-fault** clause and nothing more. The grader writes
that sentence into every record, in the `fault_classes_seen` block, so no reader can mistake its zero
for a tight agreement. **The tightness the old `1.0e-5` pretended to is not recovered by relaxing it —
it is recovered by `D2-GEO`, which is why `D2-GEO` exists.**

### 2d. `D2-GEO` — NEW. THE EXTERNAL, PATH-INDEPENDENT ANCHOR (L-588)

**`|thickcon_i(state) − thickcon_i(inherited)| ≤ GEO_TOL = 1.0e-12` for all 100, and the same for
`volcon`, at states `B` (against `n = 2`) and `F` and `O` (against `n = 88`).**

**Why it works where `D2-J` cannot.** `geometry_cl05.thickcon` (100 values) and
`geometry_cl05.volcon` (1 value) are **pyGeo outputs**: pure geometry, computed from the FFD and the
design vector, **never touching the flow solver**. They therefore carry **none** of the convergence-tail
path-dependence that forces `REPRO_TOL` wide. They are present in the md5-pinned
`O_mp/d6r2c_evals.jsonl` at both anchor records — measured, not assumed:

| record | `thickcon` | `volcon` |
|---|---|---|
| `n = 2` (baseline) | 100 values, `min 0.9999999999997795`, `max 1.0000000000005231` | `1.0000000000000309` |
| `n = 88` (final) | 100 values, `min 0.5371435647375022`, `max 1.3289335604832564` | `1.0019113618945679` |

**The discrimination is eleven decades.** The `ADDENDUM 2` scaler defect installed `shape` ten times too
large; on these values that is an `O(0.1)` move against a `1.0e-12` band. `H1` was blind to that defect
because both its sides came from one `DVGeo`; `D2-GEO` is not, because its reference was produced by a
different run, months earlier, and is pinned by md5.

**`GEO_TOL = 1.0e-12`, derived:** values are `O(1)` and a pyGeo thickness constraint is ~10 operations
deep, so the floating-point floor is `~2e-15`; the band is `500×` it. The values are **read from the
pinned artefact, never transcribed into the instrument** (L-221/L-222). A miss whose magnitude is near
the *tolerance* rather than near `0.1` would be a finding about determinism rather than about the design
vector — it is `NOT A RESULT` either way and the band is never widened.

### 2e. `D3` — `CLOSE_TOL = 8.423462e-15`. RE-DERIVED, AND STRICTLY TIGHTER

The predecessor registered `1.0e-12` without deriving it. `D3` is an **arithmetic identity** and its
band is a **floating-point band**; it is not a physics test, and what it catches is a term computed from
a stale or differently weighted `J`.

```
floor       = 12 operations × eps(2.220446049250313e-16) × J_max(0.0316132495761607)
            = 8.4234618e-17
CLOSE_TOL   = 100 × floor = 8.423462e-15
```

**A re-derivation that can only make a gate harder cannot be fitting**, and the grader's selftest
asserts `CLOSE_TOL < 1.0e-12` so the direction is executable rather than asserted. The separate
producer-vs-grader `J` cross-check stays at `1.0e-12` **absolute** and is driven on both sides
(`1e-11` must refuse, `1e-13` must not) — the predecessor's §3c finding, carried.

### 2f. `D4` — `INTERACT_TOL = 0.10`. INHERITED, AND STILL DECLARED NOT MEASURED

`D4` passes iff `|I| ≤ INTERACT_TOL × |J_F − J_B|` with

```
Δ_twist⁽¹⁾ = J_T − J_B   Δ_shape⁽¹⁾ = J_F − J_T      (twist first)
Δ_shape⁽²⁾ = J_S − J_B   Δ_twist⁽²⁾ = J_F − J_S      (shape first)
I = Δ_shape⁽¹⁾ − Δ_shape⁽²⁾ = J_F + J_B − J_T − J_S
```

**A RE-DERIVATION WAS ATTEMPTED AND COULD NOT BE COMPLETED. WHAT WAS MISSING IS NAMED RATHER THAN
WORKED AROUND.** `I = J_F + J_B − J_T − J_S` needs **four** values. `DEC3` produced **two**:

| term | value | source |
|---|---|---|
| `J_B` | `0.030642507914635214` | `DEC3/d6r2c_decomp.jsonl`, `STATE B` |
| `J_T` | `0.0316132495761607` | same file, `STATE T` |
| `J_S` | **MISSING** — the state whose primal stalled | — |
| `J_F` | **MISSING** — never reached; the arm died at `S` | — |

*(The two that exist already say something worth knowing: **twist-only is 3.17 % WORSE than the baseline
at matched lift.** It is not quoted as a result — `DEC3` is `NOT A RESULT` — and it is not used to set
any threshold.)*

**Two of four is not a bound on `I` at any confidence, and no substitute exists**: `|I|` is a difference
of differences, and the two missing terms are the two that carry the shape deformation, which is the
whole quantity `D4` is about. **No measurement in this family bounds the interaction term.** `0.10` remains what the predecessor called it: the level at which *"shape
contributed X and twist contributed Y"* stops describing the wing and starts describing the order the
analyst chose. **DECLARED, NOT MEASURED**, and the grader writes that phrase into the record.

On a `D4` miss the percentages are **qualified, not suppressed** — both orderings printed, `I` named,
`split_is_order_dependent: true` — because Sanaa asked for the contributions and an honest
order-dependent answer is an answer.

### 2g. `D6` — COMPLETION AND HYGIENE. INHERITED, WITH ONE NEW CLAUSE

`rc = 0`; every state in `STATES + ["B2"]` present with `fail = 0`, finite `CD`, `CL` and `J`; every
primal converged to `primalMinResTol = 1.0e-8` or its residual recorded and the arm graded
`NOT A RESULT`; the record strictly newer than the arm's own age datum (`0/U`); **zero** files under the
arm directory newer than the datum owned by uid 0 or gid 0; the cap of §8 not crossed.

**NEW:** the producer's recorded `runscript_md5` must equal **`2f2ae43a627146cf8e0f065b035ada4b`**. That
is how §0b's claim — *the widened bound never touched `O_mp`* — becomes a check.

**NEW at v1.2:** the producer's recorded `x0_md5` and `evals_md5` must equal the §0e values
**`b225fe7fdbd12eaa8a9b8a70835849c8`** and **`2c0b8143caad198cd2e21d8047986aa3`**. **The staged inputs
must be the registered inputs**, and until v1.2 nothing checked the first of those two — see §8a.

### 2h. LABELS

`PASS` = `D1 ∧ D2 ∧ D3 ∧ D4 ∧ D6`, where `D2 = D2-J ∧ D2-GEO ∧ D2-CL`.
`GATE FAIL` = `D1 ∧ D2 ∧ D3 ∧ D6` hold and `D4` misses, with `I`, both orderings and every absolute
number printed beside it.
`NOT A RESULT` = `D1`, `D2`, `D3` or `D6` fails, or the §8 cap is crossed.
`D5` produces a refusal (`exit 2`), not a label.
**No other label and no synonyms** (rule 1). **No Roache triple is claimed and no GCI is quoted** —
single grid throughout (rule 5 does not apply and nothing here will be dressed as grid convergence).

---

## 3. WHICH CLAUSES SEE WHICH FAULTS (L-588, as amended)

L-588's rule as amended is not "how many gates" but **"for each clause, name the fault CLASS it can
see"**, and **at least one clause must compare against a quantity this run did not produce.** The
grader writes this table into every record; it is reproduced here because the registration is where it
has to be true.

| clause | anchored to | fault class it CAN see | what CANCELS in it |
|---|---|---|---|
| **`D2-GEO`** | **EXTERNAL** — `thickcon`/`volcon` at `n = 2` and `n = 88`, md5-pinned, produced months earlier by a different run | **INPUT faults**: wrong design vector, wrong space, wrong scaler, wrong source record, wrong FFD. Discrimination ~11 decades | every flow-solver fault; any error that leaves the geometry identical |
| **`D2-J`** | **EXTERNAL** — `J0`, `Jf`, md5-pinned | **GROSS state faults** only, above 0.053 drag counts | anything below that, which is a property of the solver's stopping rule, not of the gate |
| **`D2-CL`** | **EXTERNAL** — the `n = 88` `CL` vector | trim faults at state `O` | geometry and drag |
| `D1` | the registered targets (frozen literals) + the registered bound | lift not held; an unreadable trim count; an incidence outside the bound; an oversized continuation step | any fault that leaves `CL` on target |
| `D3` | internal | **bookkeeping**: a term from a stale `J`, different weights, or a different record | all physics |
| `D4` | internal | order-dependence of the split. **Not a fault check** | everything else |
| `D6` | internal + the runscript md5 (**EXTERNAL**) | completion, ownership, age, cap, an edited optimisation runscript | every numerical fault |

**Three clauses are externally anchored, and one of them (`D2-GEO`) is anchored at floating-point
tightness on a quantity the flow solver never touches.** That is the structural property item 9's
`H1/H2/H4` family lacked.

**THE STATES THIS FAMILY CANNOT ANCHOR, NAMED.** `T` and `S` carry **no external geometric anchor** — no
record of a twist-only or a shape-only geometry exists anywhere. The unseen fault class is a
DV-installation fault that corrupts **only** the twist-only or shape-only vector while leaving the full
vector correct. It is narrow — all four vectors are assembled by one code path from the same two
md5-pinned arrays — but it is real, and it is **disclosed, not repaired**: writing a clause to cover it
would require a reference that does not exist.

**L-589 is heeded where it bites.** The governor's controls are driven against a **fake** `prob` object,
not against the real model. That control is evidence about **this file's own arithmetic** — the bound
assertion, the sub-step walk, the call count, the recorded path — and is **evidence about nothing in
OpenMDAO, mphys or DAFoam**. The instrument says so at the call site. What the simplified setting cannot
see is named in §11a.

---

## 4. THE RUN

| arm | what it is | ranks | run under this registration? |
|---|---|---|---|
| `DEC4` | the six states in one container, order `B → T → S → F → O → B2`, cold from `0.orig` | 4 | **YES** |

**Run root, NEW and separate:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R2-a2-wing-decomposition-retrimmed`

**Why a new root.** The `D6R2C` root holds the graded `O_mp` artefacts that `O_mp_GRADE.json` cites by
path, and the `D6R2C-AFTER` root holds the closed `NOT A RESULT` rows of `DEC`, `DEC2`, `DEC3`, `FM3`
and `FM4` **and the live arm `FM5`**. Writing into either would put another verdict's evidence under a
new run's feet. **Both are in `FORBIDDEN_ROOTS` in `d6r2c_dec4_run_arm.sh`** and the launcher's selftest
drives `G-ROOT.1` and `G-ROOT.2` against them.

**Seeding, ranks, placement.** Inherited unchanged from `PREREGISTRATION_AFTER_ITEMS.md` §5 and §9:
`base/` copied read-only and hashed at seed; the final design vector staged **as an input, before the
age datum**; `RANKS = 4`, `CPUSET = 2,3,4,5`, `--memory=20g --memory-swap=20g`,
`memory_footprint_gb = 17`; `--user 1000:1000 --group-add 1002`, `-e HOME=/tmp`, **never root**; the
image pinned by digest `sha256:2927768a…f6d35`; checkpoints every 1800 s, last two kept.
**Nothing is stopped by a time or budget cap** (Sanaa directive #17, 2026-09-12): every container prints
`D6R2C_DEC4_DEADLINE_IN_CONTAINER_S: NONE` and no wrapper carries a `timeout`.

**Warm starting, and why `D2` sits at both ends.** Each state after the first warm-starts from the
previous state's converged fields — that is what makes the continuation cheap and it is also what `B2`
measures. `B` is step 1, the coldest; `O` is step 5, with the most warm-start drift behind it; `B2` is
step 6 and is reported rather than gated. **A `D2` failure is `NOT A RESULT` and the fallback — six cold
states — is a NEW registration, not a silent re-run.**

---

## 5. THE MONITOR

**None is registered, for the reason `PREREGISTRATION_AFTER_ITEMS.md` §6 gives and which still holds:**
this arm is **primal-only** — no adjoint, no IPOPT, no design iteration — so Sanaa's item-7 stop rules
(*objective rises three consecutive iterations*, *resume with the step halved*) have no iterate to act on
and no step to halve. What can go wrong is a primal that fails to converge, and that is covered by `D6`
as a **completion** gate and by `TRIM_MAX_EVALS` and `CONT_MAX_STEPS` as **bounds**, not as stop rules.
`d6r2c_dec4_decomp.py` appends a per-state line to `d6r2c_dec4.jsonl` as the run proceeds, so the run is
readable while it runs.

---

## 6. WHAT WAS MEASURED FROM A CLOSED `NOT A RESULT` ROW, AND WHY THAT IS LEGITIMATE

Several thresholds above are derived from arm `DEC3`, which is graded `NOT A RESULT`. **The label is
about the verdict, not about whether the log is real.** `DEC3`'s incidences, lift values, wall times and
residuals are observations of what the machine did, and a pre-registration may derive a threshold from
any measurement provided it says where the measurement came from. **Every one of them is cited to a
line of `DEC3`'s log or a record of `DEC3`'s `.jsonl` above.** No number from `DEC3` is quoted anywhere
in this document as a **result**, and `DEC3`'s row is not re-graded, re-seeded or overwritten.

---

## 7. THE PLANTED CONTROL (rule 3)

`d6r2c_dec4_grade.py` plants **`PLANT = 1.234e-03`** into values it **read back from disk** and
**REFUSES (`exit 2`)** if any plant leaves the verdict at `PASS`. Eight live plants on every real
grading: into `CD` at states `B`, `T`, `F` and `O`; into one `CL` of a matched-lift state; and — new —
into `thickcon` at each of the three `D2-GEO`-anchored states.

**`PLANT` is inherited, and it is re-checked against every threshold this document changed**, because a
plant that is invisible to a new band is not a control:

| band | value | `PLANT` is |
|---|---|---|
| `REPRO_TOL` (the loosest) | `5.258854e-06` absolute in `J` | **234×** it |
| `TRIM_TOL` | `1.0e-6` | 1234× it |
| `GEO_TOL` | `1.0e-12` | 12 decades above it |
| `CLOSE_TOL` | `8.423462e-15` | 15 decades above it |
| `INTERACT_TOL × |J_F − J_B|` | unknown until the run; `~5e-4` if `|J_F − J_B| ~ 5e-3` | the plant goes into `J_T`, which moves `I` by `PLANT` directly |

`--selftest` drives **67 controls in both directions** on synthetic trees in a temporary directory,
touching no run directory: the clean case must reach the unmutated label; each planted defect must flip
it; **and four explicit NEGATIVE controls must NOT flip** — a `1.0e-14` geometric difference, a `1.0e-13`
producer-`J` difference, the measured `2.860408e-05` path-dependence inside the re-derived `REPRO_TOL`,
and a legal multi-leg continuation. **Driven at this draft: `D6R2C_DEC4_GRADE SELFTEST PASS n=67`,
exit 0.**

---

## 8. COST, IN CORE-MINUTES, BEFORE THE RUN (rule 12)

**Measured anchors, all at 4 ranks, all from this family's own artefacts:**

| anchor | value | where measured |
|---|---|---|
| one primal evaluation of **all three** conditions | **48.081 s wall = 3.205 core-min** | `O_mp/d6r2c_evals.jsonl`, `F` record `n = 2`, `eval_wall_s` |
| state `B` cold, **including its own trim** | **91.034 s = 6.069 core-min** | `DEC3/d6r2c_decomp.jsonl`, `STATE B`, `wall_s` |
| state `T`'s trim, 3 conditions × ~5 iterates | **638.294 s = 42.553 core-min** | same file, `STATE T`, `wall_s` |
| container start + staging to the `HEADER` line | **9 s** | `DEC3` stamps: launch `05:56:45Z`, `HEADER` `05:56:54Z` |

**No adjoint is run by this arm.** `O_mp`'s 26 gradient evaluations cost a measured mean of 174.99 s
each; none of that is spent here, and saying so is why the figure below is small.

**The continuation costs whole evaluations, not per-condition ones**, because `run_model` solves all
three conditions at once. Legs per state, from the incidences of §1d/§1e at `AOA_STEP_MAX_DEG`:

| state | from → to (worst condition) | continuation legs | Newton evaluations budgeted | wall s |
|---|---|---|---|---|
| `B` | cold | 0 | measured whole | **91.034** |
| `T` | baseline → `A_T` | 1 | measured whole | **638.294** |
| `S` | `A_T` → `A_S` | **7** | 5 | `12 × 48.081 =` **577.0** |
| `F` | `A_S` → `a*` | **3** | 5 | `8 × 48.081 =` **384.6** |
| `O` | no trim, one evaluation | 0 | — | **48.081** |
| `B2` | `a*` → baseline | **2** | 5 | `7 × 48.081 =` **336.6** |
| container + staging | | | | **9.0** |

```
PREDICTION   2084.6 s wall × 4 ranks / 60 = 138.973 core-min
REGISTERED CAP (3.00×)                     = 416.919 core-min
```

**Derived dollars:** `138.973 core-min = 2.316 core-h × $0.0513 = $0.1188`; at the cap, `$0.3565`.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` class **reported-by-owner** at the owner-stated c7a.4xlarge rate. *(The box is now an
r7a.4xlarge; the rate on record is used unchanged rather than invented.)*

**THE NUMBER THIS ESTIMATE IS WEAKEST ON, NAMED.** *How many Newton evaluations each trim needs after
the continuation has walked the incidence close.* **5 is an estimate, labelled an estimate**, taken from
`DEC3`'s state `T`. It is bounded rather than trusted by `TRIM_MAX_EVALS = 15`.

**THE WORST CASES, BOTH OF THEM, AND ONE IS ABOVE THE CAP.**

| case | arithmetic | core-min |
|---|---|---|
| **realistic worst** — only `S` saturates both bounds; `B`, `T`, `F`, `B2` behave as measured | `9 + 91.034 + 638.294 + (11+15)×48.081 + (3+15)×48.081 + 48.081 + (2+15)×48.081` | **247.957 — INSIDE the cap** |
| **absolute worst** — every trimmed state saturates `CONT_MAX_STEPS` **and** `TRIM_MAX_EVALS` | `9 + 5×(11+15)×48.081 + 48.081` | **420.507 — 0.86 % ABOVE the cap** |

The absolute worst requires every state to walk the full excursion to the bound, which cannot happen:
`B`, `T`, `F` and `B2` have **measured** incidences within `1.1 deg` of where they start. **That is said
here, before the run, rather than discovered at the ledger.**

**THE CAP IS NOT ADJUSTED TO ACCOMMODATE IT, AND THAT IS A RULING, NOT AN OVERSIGHT.**
`dafoam-supervisor`, on this draft, verbatim: *"I will not adjust a cap to accommodate a case you have
shown cannot occur — that is choosing a number to fit."* The cap stays at `3.00×` the prediction and the
overshoot stays disclosed. A crossing writes
`D6R2C_DEC4_CAP_CROSSED`, the row is graded **`NOT A RESULT`**, and **the cap is never raised**. Nothing
is killed on it (directive #17).

### 8a. DEFECT FIND AT THE SUPERVISOR'S READ — THE INSTRUMENT AND THE DOCUMENT CARRIED DIFFERENT CAPS

**THE v1.1 GRADER REGISTERED A CAP OF `407.303` WHILE THIS DOCUMENT REGISTERED `416.919`. A CAP IS
EXACTLY WHAT RULE 2 FREEZES, AND THEY WERE TWO DIFFERENT NUMBERS.** Found by `dafoam-supervisor` reading
the instrument against the text, **before the freeze commit and before any compute**.

**Which figure was right, and how that was established.** Not by making the code match the prose. The
prediction was **re-derived from the anchors of §8's own table**:

```
S : (7 legs + 5 Newton) × 48.081 = 576.972 s      F : (3 + 5) × 48.081 = 384.648 s
B2: (2 legs + 5 Newton) × 48.081 = 336.567 s      O : 48.081 s
staging 9.000 + B 91.034 + T 638.294              total 2084.596 s wall
2084.596 × 4 / 60 = 138.9731 core-min  ->  ×3.00 = 416.9192  ->  416.919
```

**The document is correct and the grader was stale.** The grader's `407.303` implies a prediction of
`135.768`, which is the figure from a **superseded cost model** in which a continuation sub-step was
costed **per condition** (16.027 s) rather than **per evaluation** (48.081 s — `run_model` solves all
three conditions in one call). The document was revised when that model was corrected; the literal in
the instrument was not.

**WHY NO SELFTEST CAUGHT IT, AND THIS IS THE PART THAT GENERALISES.** The grader's cap controls read
`CAPS["DEC4"]` and built their own boundary from it (`CAP + 0.1` must fail, `CAP` must pass). **They
would have passed for any value whatsoever.** That is a self-referential check — **L-588's failure mode,
committed inside the instrument rather than inside the run**, in the same document whose §3 table exists
to name it. A control fed by the number it is checking sees nothing about that number.

**THE THREE REPAIRS.**

1. **The cap is DERIVED, not typed.** `d6r2c_dec4_grade.py` now carries
   `PREDICTION_CORE_MIN = 138.973`, `CAP_FACTOR = 3.00`, `CAPS = {"DEC4": round(138.973 × 3.00, 3)}`.
2. **THERE IS NOW ONE SOURCE.** `d6r2c_dec4_run_arm.sh` no longer carries the figure at all: its
   `cap_core_min()` **calls** `d6r2c_dec4_grade.py --print-cap`, and the call is made **after** `G-FREEZE`
   has pinned the grader's bytes, so the launcher never trusts a number it has not verified. This is the
   same discipline the launcher already applies to `swap_offenders()` — the canonical value is called,
   never re-spelled (L-221/L-222). A cap in two files is two things that can drift, and these two did.
3. **THE CONTROLS NOW HAVE AN EXTERNAL ANCHOR.** Three new selftest clauses assert `138.973` and
   `416.919` — **this section's literals, typed as assertions rather than as sources** — and that the cap
   equals the prediction times the factor. A launcher clause asserts both that the cap is `416.919` and
   that it came from the grader.

### 8b. THE CONSTANT SWEEP THE FIND FORCED, AND THE THREE FURTHER FINDS IN IT

**Every numeric and string constant in both instruments was then compared against the value this
document registers for it — 25 rows, mismatches and matches alike.** A sweep that lists only its
failures cannot be told apart from a sweep that was never run.

**Twenty-one rows matched.** `TRIM_TOL`, `TRIM_MAX_EVALS`, `REPRO_TOL`, `GEO_TOL`, `CLOSE_TOL`,
`INTERACT_TOL`, `AOA_UPPER_DEG`, `AOA_STEP_MAX_DEG`, `CONT_MAX_STEPS`, `PLANT`, `PREDICTION_CORE_MIN`,
`CAP_FACTOR`, the derived cap, `RUNSCRIPT_MD5`, `EVALS_MD5`, `J0_INHERITED`, `FINAL_RECORD_N`,
`CL_TARGETS`, `STATES`, `REPORTED_STATES`, `RECORD` — and where a constant appears in **both**
instruments (`TRIM_MAX_EVALS`, the four incidence constants, `RUNSCRIPT_MD5`, `EVALS_MD5`, `STATES`,
`REPORTED_STATES`) the two agree with each other as well as with this text.

**One row was a SWEEP ARTEFACT and is recorded as one.** `AOA_LOWER_DEG = -4.9570114` appeared to be
absent from this document because the document writes the minus as **U+2212 MINUS SIGN** (`−4.9570114`,
4 occurrences) and the instrument writes ASCII hyphen-minus. **The value is identical.** It is recorded
because a typographic minus defeats a naive text comparison, and the next such mismatch might not be
cosmetic.

**Three rows were REAL FINDS, all of them repaired at v1.2:**

| find | what was wrong | repair |
|---|---|---|
| **`X0_MD5` was a pin that pinned nothing** | `d6r2c_dec4_grade.py` **declared** `b225fe7f…` and **never read it**. The frozen-instrument table would have implied a check that was not performed | `D6` now asserts the producer's recorded `x0_md5` (and `evals_md5`) against §0e; a control drives a wrong `x0` to `NOT A RESULT` |
| **`Jf` was never stated in this document** | the grader carried `JF_INHERITED = 0.0230632595286777639`; the text gave only `Jf/J0` and `J0`, so the literal was uncheckable | §0e states it, with its artefact and md5 |
| **THE WEIGHTS OF THE GRADED QUANTITY WERE NOT REGISTERED** | `J = 0.25·CD04 + 0.50·CD05 + 0.25·CD06` — the objective itself — appeared nowhere in this document | §0e states the objective and the targets in full |

**The third is the worst of the three and it is the one to remember: a registration that does not state
the weights of its own objective has not registered its objective.** It went unnoticed because `J`
"obviously" means the weighted mean — and the grader recomputes `J` from those weights on every row.

### 8c. WHAT THIS FAMILY OF DEFECTS HAS COST THIS ITEM, AND THE STANDING CHECK IT BUYS

Four finds in one night, all the same disease — **a registered clause that is not the clause that
executes**:

| # | find | stage | what was on paper | what executed |
|---|---|---|---|---|
| 1 | **L-579** | the parent item | a grading path named `d6r2c_grade.py` | no such file existed |
| 2 | **§2b** | this draft | `TRIM_MAX_EVALS = 40` | the guarding branch was never entered |
| 3 | **§8a** | supervisor's read | cap `416.919` | cap `407.303` |
| 4 | **§8b** | the sweep | a pinned `x0` | a constant never read |

**THE STANDING CHECK FOR THIS ITEM, adopted by `dafoam-supervisor` on this find:** before any freeze,
**compare every constant in every named instrument against the value the registration states for it, and
report the comparison in full.** And for every gate: **drive a control in which it FAILS, from an
anchor outside the instrument.** Findings 2, 3 and 4 were each invisible to a passing selftest, because a
selftest built from the instrument's own constants is a check on arithmetic and not on registration.

---

**Spend already incurred against after-item 8, carried forward for calibration and never merged into
this item's figure:** arms `DEC` 0.533, `DEC2` 14.800, `DEC3` 63.000 core-min — all `NOT A RESULT`.
`DEC` and `DEC2` are **defect-attributable waste**; **`DEC3` is not** — it falsified a registered
assumption, which is what a pre-registration is for.

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at this arm's completion — actual against the
138.973 above, the ratio, and contention / waste / misprediction attributed **separately** (rule 12,
`COMPUTE_BUDGET_CHARTER.md` §6). A completion report without it is incomplete.

---

## 9. THE MESH AND THE FLOW REGIME

**38,304 cells**, 40,209 points, all hexahedra, 3 patches — `wing` (wall, 1008 faces), `inout` (patch,
1008 faces), `sym` (symmetry, 1672 faces); decomposed 4 ways as 9504 / 9600 / 9608 / 9592. Unchanged
from the base mesh, which this arm never regenerates.

**`M∞ = 0.288`, compressible subsonic**, per `PREREGISTRATION.md` ADDENDUM 2 and Sanaa's own ruling.
**No shock figure can be produced from any artefact of this item.** The run root does not carry the
word "transonic".

---

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not re-grade `O_mp`.** That row is closed at **`GATE FAIL`** and nothing here can move it.
  The **24.732273 %**, the `G3` miss of **2.79×** and **`Jf/J0 = 0.7526772709407745`** stand exactly as
  graded, on the runscript this item pins unchanged.
- **It does not re-grade `DEC`, `DEC2` or `DEC3`.** Three closed `NOT A RESULT` rows, never re-seeded.
- **It does not verify any gradient.** Not one adjoint is solved. That is the `ARM0` / `F_mp` / `D6RF`
  family.
- **It does not register item 9.** The fresh mesh, `H1`–`H4`, `FM_BAND_ABS` and arm `FM5` remain under
  `PREREGISTRATION_AFTER_ITEMS.md`, which this document leaves untouched.
- **It is not a grid study.** Single grid. No Roache triple, no GCI, no observed order (rule 5).
- **It does not claim the primal reaches the A2 accept floor of `1.0e-5`.** `D6RF10` measured that this
  `DARhoSimpleFoam` configuration does not. The `DARhoSimpleCFoam` change is `D6R3` and is deliberately
  not taken here: changing the solver between `O_mp` and its own decomposition would make the
  decomposition a statement about the solver.
- **It does not claim the continuation will make state `S` converge.** §0c and §1d say where the
  solver's measured convergence envelope ends and that nothing on disk locates its lower edge. **If the
  primal still stalls, the arm is `NOT A RESULT` with the residual printed, and `primalMinResTol` is
  NEVER loosened to make it pass.**
- **It does not claim `Δ_shape` and `Δ_twist` are independent.** `D4` measures it either way.
- **It does not adopt the `−3.64°` figure as measured.** §1d says what I could and could not reproduce.
- **It does not satisfy Sanaa's item 10.** The report is a separate record.

---

## 11. THE FROZEN INSTRUMENTS

**Every instrument this document names EXISTS, is in THIS COMMIT, and carries its md5 below.** This
paragraph is here because the defect `PREREGISTRATION.md` ADDENDUM 3 discloses — a registration naming
`d6r2c_grade.py`, an instrument that did not exist in any tree in this repository's history (L-579) — is
exactly what this table is designed to make impossible. **A table that lists what exists cannot show
what is missing**, so the list is closed: **the three files below are every instrument named anywhere in
this document.**

| file | role | md5 at freeze | selftest driven at freeze |
|---|---|---|---|
| `d6r2c_dec4_grade.py` | **THE GRADING PATH** — `D1`–`D6`, `D2-GEO`, the table, the `B2` report, the planted controls, and `--print-cap`, the cap's single source | `4c23b6be959f74b3d840db70bd34e340` | **`D6R2C_DEC4_GRADE SELFTEST PASS n=67`** |
| `d6r2c_dec4_decomp.py` | producer, in-container: six states, the governor, the trims, `d6r2c_dec4.jsonl` | `a5f6023d5eec9b1315ef7f34e635bb29` | **`D6R2C_DEC4_DECOMP SELFTEST PASS n=56`** |
| `d6r2c_dec4_run_arm.sh` | launcher: `G-ROOT.1/2/3`, digest pin, `G-FREEZE`, `G-COLD`, age datum, ledger, rotator. **Carries no cap of its own** — it asks the grader, after `G-FREEZE` | `6c29fe9bbf519fec7ffaf5b29cb34568` | **`D6R2C_DEC4_LAUNCH SELFTEST PASS n=9`** |

All three are **forks**, and the files they were forked from stay on disk **unedited** and keep
governing their own documents:

| fork | parent | parent md5 read |
|---|---|---|
| `d6r2c_dec4_grade.py` | `d6r2c_after_grade.py` | `6c22013af54569ae651f8f23d1088861` |
| `d6r2c_dec4_decomp.py` | `d6r2c_decomp.py` | `42ec0dd582584812a69129a474b2783e` |
| `d6r2c_dec4_run_arm.sh` | `d6r2c_after_run_arm.sh` | **`c4433db6b60f9c695d785a871a6d3c7d`** — **the blob at `HEAD`**, see below |

**THE LAUNCHER'S PARENT, RESOLVED BY TIMING AND RE-CHECKED RATHER THAN ASSUMED.** Version 1.0 of this
file disclosed that the bytes forked from — `c4433db6b60f9c695d785a871a6d3c7d` — were **not** the md5
`PREREGISTRATION_AFTER_ITEMS.md` ADDENDUM 4 §A4.5 records (`fa58d4829295c6b97e647e0a3aa5c422`), and that
the difference had been **inspected and NOT reverted** (rule 10) because it looked like a peer's
uncommitted work.

**It was not uncommitted. It was committed while this file was being drafted, and it is now `HEAD`.**
Verified 2026-09-13 by command, not by recollection:

```
git rev-parse --short HEAD~1                 -> ab9fdec23
git show HEAD:<launcher path> | md5sum       -> c4433db6b60f9c695d785a871a6d3c7d
md5sum <launcher path>                       -> c4433db6b60f9c695d785a871a6d3c7d
```

Commit **`ab9fdec231567eb3acfeffdac6903ae290d147cb`** — *"D6R2C — ADDENDUM 5 AND THE `guard_box` SWAP
REPAIR"* — carries the repair and its disclosure together, and `PREREGISTRATION_AFTER_ITEMS.md`
ADDENDUM 5 §A5.5 records the launcher at this same md5. **So the fork's parent is the committed blob at
`HEAD`, the working tree and `HEAD` agree bit for bit, and the fork is NOT re-taken** — re-taking it
would change nothing and would only move the hash a reader has to check.

*(The repair that commit carries also matters to this arm: `HEAD`'s previous `guard_box` read
`SwapTotal − SwapFree` and would have refused every launch of this item on 8 kB of stale `SwapCached`
that no process holds. `d6r2c_dec4_run_arm.sh` inherits the repaired function by CALLING it, never by
re-spelling it (L-221/L-222).)*

**Every threshold in `d6r2c_dec4_grade.py` — `TRIM_TOL`, `TRIM_MAX_EVALS`, `REPRO_TOL`, `GEO_TOL`,
`CLOSE_TOL`, `INTERACT_TOL`, `AOA_LOWER_DEG`, `AOA_UPPER_DEG`, `AOA_STEP_MAX_DEG`, `CONT_MAX_STEPS`,
`PLANT` and the cap of §8 — is copied verbatim from this document, each carrying the sentence it was
copied from as its comment. Nothing in the grader was chosen by its author.**
**AND THAT SENTENCE IS NOW CHECKED RATHER THAN ASSERTED:** §8b's constant sweep compares all 25 of them,
match and mismatch alike, and §8c makes that sweep a standing pre-freeze check for this item. The first
draft of this file made the same claim and **three of its constants did not hold it**. The launcher pins both
instruments by md5 and refuses (`exit 4`) on any difference, so the instruments that run are the
instruments that were frozen.

### 11a. THE HONEST GAP IN THIS FREEZE, NAMED BEFORE IT IS DISCOVERED

**`d6r2c_dec4_decomp.py` HAS NEVER BEEN EXECUTED AGAINST THE SOLVER**, and neither had its parent at its
own freeze. It cannot be: it runs inside the pinned image against `DARhoSimpleFoam`, and running it is
the compute this document registers. What **is** driven at the freeze is byte-compilation and
`--selftest`, which exercises the pure logic — DV assembly, the driver-scaled space conversion, the
sub-step planner, the governor's bound assertion and call counting, the record writer and every refusal
path — on synthetic inputs, touching no container and no run directory.

**Specifically untested, and it is the new code:** the governor wraps `prob.run_model` on the **real**
OpenMDAO problem. Whether `findFeasibleDesign` calls that attribute (rather than a bound reference
captured at construction) is **read from the library source** (`mphys_dafoam.py:1175`,
`self.om_prob.run_model()`) and **not measured**. **L-589 is the lesson that applies:** the fake-`prob`
control cannot bear on that question, and it does not claim to.

**Registering that it will work would be an assertion, so instead the first compute is cheap and
disposable:**

> **If `DEC4` has not written its `state = B` record within `TRIM_MAX_EVALS` evaluations, or if the
> governor's call counter reads zero at the first state — which is the tell that `run_model` was not
> reached through the attribute — it is stopped as a producer defect, graded `NOT A RESULT`, and
> repaired under `VERIFICATION_CHARTER` §2d.1. The grading path `d6r2c_dec4_grade.py` is NOT touched by
> such a repair, and if it ever must be, that is a new registration.**

The distinction that keeps this legitimate: **a producer defect is a defect in how a number was made and
is repairable with disclosure; a grader changed after seeing data is not.**
