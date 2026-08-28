# F17c-KV40-FLOOR — Kovasznay flow, Re = 40, THE DERIVED ITERATIVE FLOOR 192×128 / 384×256 / 768×512 (`simpleFoam`) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F17c_KV40_FLOOR_PREREGISTRATION.md`
frozen at **`3c01061ea6c773952a6df259c49bcaf4de7f31b5`** (v1.0, 2026-08-27T18:55:50Z,
*"cfd FREEZE F17c_KV40_FLOOR (rule 2): pre-registration + 15 case blobs, nothing
run"*; the run root did not exist at the freeze — §9 of that document records the
absence three ways). **Instrument-check** (`CASE_SELECTION_CHARTER.md` §3, as F17 and
F17b): counts toward no challenge column.

F17c changed **exactly one thing** against F17b: the per-level iteration count, derived
under **L-346** from this ladder's own measurement of F17b's checkpoints at zero new
compute. Meshes, dictionaries, discretisation model, both gates, both bands and every
Class C tolerance are F17b's, unchanged.

Ladder launched by the queue runner; the three levels ran serially on 1 rank
2026-08-27T22:31:42Z → 2026-08-28T02:38:25Z. Grade record
`verification/runs/F17c_runs/F17c_GRADED.json` (25,206 bytes, mtime
**2026-08-28T16:14:12Z**), the grader's default output path, produced by
`cases/F17c_kovasznay_floor/grade_f17c.py --prereg-commit=3c01061e…`. Gated by
`scripts/roache_triple.py::grade_ladder`, **one call node** (`grade_f17c.py:756`); the
grader's own AST census in the JSON reads 0 `assert` nodes across 4 files with the
planted assert seen.

---

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F17-1 `E2_velocity_L2` | **8.895074e−06** | [2.299887e−06, 2.069898e−05] | CONVERGING (dim 2, r = 2.000, monotone) — printed beside, **not a result** | 2.005022 — printed beside, **not a result** | **not quoted** (see below) | **NOT A RESULT** |
| G-F17-2 `u_at_probe` (0.5, 0) | **0.38237650525375** | [0.3823735001308136, 0.3823948460265708], reference 0.3823841730786922 | **CONVERGING** (dim 2, r = 2.000, monotone) | **2.140696** | **0.0011458 % = 4.381227e−06 absolute** | **PASS** |

**Rung tally: PASS × 1, NOT A RESULT × 1.**

The grader's own `why` fields, verbatim from `F17c_GRADED.json`:

    G-F17-1_E2_velocity_L2   NOT A RESULT
        levels medium are not iteratively converged or not plateaued;
        no grid claim can be made from this triple
    G-F17-2_u_at_probe       PASS
        finest triple ('coarse', 'medium', 'fine') CONVERGING at dim = 2,
        observed order 2.1407, GCI 0.0011 % = 4.38123e-06 absolute at Fs = 1.25

Level values (from `<level>/<endTime>/U`, read by the frozen reader):

| level | Nx × Ny | cells | h | endTime | E2 | u(probe)/U0 |
|---|---|---|---|---|---|---|
| coarse | 192 × 128 | 24,576 | 1/128 | 4,000 | 1.4231373408e−04 | 0.38244115766475 |
| medium | 384 × 256 | 98,304 | 1/256 | 8,000 | 3.5504580855e−05 | 0.38238845635175 |
| fine | 768 × 512 | 393,216 | 1/512 | 48,000 | 8.8950735253e−06 | 0.38237650525375 |

**Why G-F17-1 is NOT A RESULT even though its band verdict is PASS, and why no GCI is
quoted for it.** The fine E2 value **is** inside the registered band and the grader's
own `band_verdict` field on that row reads `PASS`. Standing rule 5 **step (1) fires
first**: the MEDIUM level is `NOT_PLATEAUED_TREND`, so no grid claim can be made from
the triple and the row is **NOT A RESULT**. The gate can only turn a PASS or a GATE
FAIL **into** NOT A RESULT, never the reverse — so the `band_verdict` is recorded here
and carries no verdict weight. **No GCI is lifted into the row**, and that is correct
rather than an omission: a GCI is a grid-convergence uncertainty, and a triple that
failed the plateau limb has no grid claim for an uncertainty to attach to. The E2
row's top-level object in the JSON accordingly carries **no** `order`, `GCI_pct` or
`GCI_abs` key, unlike the probe row, which carries all three.

For completeness and explicitly **not as a result**: the E2 triple sub-object holds
`GCI_pct` = **124.068544541885**. That figure is a percentage of a quantity whose
registered reference is **0.0** — a relative uncertainty on a norm whose exact value
is zero. **It is meaningless as a percentage**, which is precisely why it is not
lifted into the row. (F17 recorded the same pathology at 117.44 % and F17b at
227.57 %; the absolute form, `GCI_abs` = 1.103599e−05, is the only one that could
carry meaning here, and it too is not quoted, because the row is NOT A RESULT.)

---

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path the pre-registration names plus the gating script, re-checked by this lane
with `git hash-object <disk>` against `git rev-parse 3c01061e:<path>` —
**16 of 16 SAME, 0 DIFF.** Rule 2's grading-path clause is satisfied: the frozen file
**is** the file that ran.

| path | blob |
|---|---|
| `cases/F17c_kovasznay_floor/grade_f17c.py` | `71939be3` |
| `cases/F17c_kovasznay_floor/exact_f17c.py` | `b1d69d61` |
| `cases/F17c_kovasznay_floor/foam_io_f17c.py` | `430e9a5a` |
| `cases/F17c_kovasznay_floor/build_f17c.py` | `52dd0391` |
| `cases/F17c_kovasznay_floor/proj_f17c.py` | `7671cc45` |
| `cases/F17c_kovasznay_floor/run_f17c.sh` | `1b6b74ad` |
| `case/0/U.template`, `case/0/p` | `b6f3251b`, `0105f6fe` |
| `case/constant/transportProperties`, `turbulenceProperties` | `81921b4b`, `ba5bb3d1` |
| `case/system/blockMeshDict.template`, `controlDict.template` | `ad0f3269`, `630dc7e2` |
| `case/system/fvSchemes`, `fvSolution` | `f0eea325`, `96a0fc1b` |
| `verification/campaign/F17c_KV40_FLOOR_PREREGISTRATION.md` | `123bcefb` |
| `scripts/roache_triple.py` | `78e56a3b` |

`fvSchemes`, `fvSolution`, `0/U.template`, `0/p`, `transportProperties`,
`turbulenceProperties` and `blockMeshDict.template` are byte-identical to F17 and
F17b. `controlDict.template` differs from F17b's `controlDict` because the
per-level `endTime` is templated — that *is* the one change this rung registered.

---

## 3. RULE 4 — strict completion, re-read from the run root by this lane

**All three levels COMPLETE. Every clause holds at every level.**

| level | `RC.txt` | `End` lines | `Time =` lines | `ExecutionTime` lines | last Time == endTime | fields at endTime | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|
| coarse | **0** | 1 | 4,000 | 4,000 | 4000 == 4000 | U p phi | 75 s / 63.74 s |
| medium | **0** | 1 | 8,000 | 8,000 | 8000 == 8000 | U p phi | 672 s / 614.84 s |
| fine | **0** | 1 | 48,000 | 48,000 | 48000 == 48000 | U p phi | 14,031 s / 13,985.02 s |

`Time` count == `ExecutionTime` count == `endTime` at every level.

**Age guard — every field at `endTime` is NEWER than that case's own `0/`** (mtimes
read from disk by this lane; the box runs UTC):

| level | `0/U` written | `<endTime>/U` written | guard |
|---|---|---|---|
| coarse | 2026-08-27T22:31:42.858Z | 2026-08-27T22:32:58.347Z | **holds** (+75.5 s) |
| medium | 2026-08-27T22:33:05.830Z | 2026-08-27T22:44:18.201Z | **holds** (+672.4 s) |
| fine | **2026-08-27T22:44:33.962Z** | **2026-08-28T02:38:24.975Z** | **holds** (+13,431.0 s) |

The grader's own `completion()` agrees at all three levels: `rc` `0` with
`rc_record` **MEASURED**, `done` true, `n_times` 4000 / 8000 / 48000, `latest`
4000.0 / 8000.0 / 48000.0, and the `why` string *"rc 0; End present; latest + dt >
endTime; N `Time` lines == endTime; U and p present at endTime and newer than 0/U"*.

Serial, **1 rank at every level**; `decomposePar` never invoked; decomposition seed
`none` (launcher record, `cases/F17c_kovasznay_floor/launcher.queue.out`). Mesh
admissibility per level from `MESH_LINE.txt` (source `log.checkMesh`): max
non-orthogonality **0°** and max skewness **1.42e−14 / 4.26e−14 / 8.53e−14** against
gates 70° / 4 — the same three meshes, and the same readings, as F17b. Each level's
**written** `controlDict` was read back before its solver started and required to
equal the registered count: 4000 / 8000 / 48000, all confirmed in the launcher record.

---

## 4. CONTROLS — 11 registered, all PASSED; the two live gate plants; `demonstrate()`

**All 11 registered controls in `F17c_GRADED.json` report `passed: true`.** Five of
them are the PZ-named planted controls; the other six are the registered structural
and physical controls. Named in full:

1. `symbolic_substitution_into_steady_NS` — continuity, x- and y-momentum residuals
   identically `0`
2. **`PZ-F17-LAMBDA_planted_1.1x_must_be_nonzero`** — λ × 1.1 planted, momentum
   residuals required non-zero (`residual_is_zero: false`)
3. `constant_ratio_refinement_both_directions` — r = 2.0, 2.0 in **both** x and y
4. `face_averaged_boundary_data_balances_to_roundoff` — net flux 0, 0, **1.110e−16**
5. `model_solved_and_second_order` — model orders **2.001960 / 2.002013**; predicted
   probe errors −5.708149e−05 / −1.425047e−05 / −3.557649e−06
6. **`PZ-F17-CLASSC_four_limbs_each_shown_able_to_refuse`** — flat → PLATEAUED, ramp
   → NOT_PLATEAUED_TREND, step → NOT_PLATEAUED_TREND, short series → **exit 2**
7. **`PZ-F17-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways`** — AST call node
   `[756]`, grep lines `[518, 756]`
8. `solver_dictionaries_agree_with_registration` — ν = 0.025; endTime 4,000 / 8,000 /
   48,000; `writeInterval` 100; `residualControl` **absent**; the `ITERS_BASIS` string
   recording the L-346 derivation
9. `reader_parses_real_solver_written_U_on_this_box` —
   `verification/runs/ansys_verification/VMFL019/L1_30/5/U`, 120 cells (icoFoam,
   v2606)
10. **`PZ-F17c-L342_L346_RRC_infrastructure_vs_physics_driven_both_ways`** — deleting
    an infrastructure field leaves the verdict channel unchanged and refuses only the
    cost claim; corrupting a physics field gives **NOT A RESULT**; an absent
    `RC.txt` reads **NOT MEASURED** with the run complete on the other four
    conditions; a `FOAM FATAL` with the record absent still refuses while the
    `trapFpe` banner does not
11. **`PZ-F17-AMEND1_probe_reference_same_stencil_zero_error_and_plant_read_back`** —
    reference 0.3823841730786922, pointwise exact 0.38237281995386374, stencil error
    1.135312e−05, a zero-error field reads back **0.0**, a 1.234e−03 plant reads back
    1.234e−03

**The two per-gate LIVE plants, into the real graded artefact through the real
reader** — `verification/runs/F17c_runs/fine/48000/U`, the same file the fine row is
graded from:

| gate | reader | planted | read back | delta | result |
|---|---|---|---|---|---|
| G-F17-1 `E2` | `e2_from_files` | **1.2251870695248644e−03** | 1.2251870695248483e−03 | 1.6e−17 | **PASS** |
| G-F17-2 `u_probe` | `u_probe_from_files` | **1.234e−03** | 1.2340000000000129e−03 | 1.3e−17 | **PASS** |

Both read back identically to floating-point round-off. **Standing rule 3 is
satisfied on the artefact that carries the answer**, not on a surrogate.

**`demonstrate()` — both gates driven INSIDE and OUTSIDE through the real reader**
(the grader re-executed the §7 demonstrations at grade time, writing a real OpenFOAM
ascii `volVectorField` at the fine size and reading it back with the same functions
that grade):

| gate | construction | value | band | outcome |
|---|---|---|---|---|
| G-F17-1 | exact + **1×** model error | 6.8996609101e−06 | [2.299887e−06, 2.069898e−05] | **inside** (intended inside) |
| G-F17-1 | exact + **40×** model error | 2.7598643640e−04 | same | **outside** (intended outside) |
| G-F17-2 | exact + **1×** model error | 0.3823806151641 | [0.3823735001, 0.3823948460] | **inside** (intended inside) |
| G-F17-2 | exact + **40×** model error | 0.3822418564957 | same | **outside** (intended outside) |

A gate not shown able to take **both** values causes `demonstrate()` to refuse.
Neither gate refused.

---

## 5. RULE 5 LIMB (1a) — ITERATIVE CONVERGENCE: CONVERGED at all three levels, both gates

Census of the solver's own **initial** residuals over **every** iteration of the
1,200-iteration Class C window, against Ux ≤ 1.0e−06, Uy ≤ 1.0e−06, p ≤ 1.0e−05:

| level | window iterations | `n_above_tolerance` Ux / Uy / p | worst Ux | worst Uy | worst p | state |
|---|---|---|---|---|---|---|
| coarse | 1,200 | **0 / 0 / 0** | 1.4749e−11 | 8.6870e−11 | 1.1299e−08 | **CONVERGED** |
| medium | 1,200 | **0 / 0 / 0** | 4.5824e−11 | 1.2356e−10 | 7.3689e−08 | **CONVERGED** |
| fine | 1,200 | **0 / 0 / 0** | 9.4443e−13 | 3.8094e−12 | 1.0986e−08 | **CONVERGED** |

`n_above_tolerance` is **0 across the whole 1,200-iteration window at every level for
every variable**, and identical for both gates (the census is of the solver, not of
the gate quantity). **The residual limb passes cleanly. It is not what refused this
rung.**

---

## 6. RULE 5 LIMB (1b) — THE CLASS C PLATEAU TABLE, IN FULL

This is the whole story of the rung. Class C is sampled at every written checkpoint
(`writeInterval` 100), over a **12-checkpoint / 1,100-iteration** trailing window,
against the **UNCHANGED** F17b tolerances: trend **2.0e−04** relative drift, mean-split
1.0e−04, variance-ratio band [0.2, 5.0], minimum 20 samples.

**G-F17-1 `E2_velocity_L2`:**

| level | samples | state | relative drift over window | trend tol | drift / tol |
|---|---|---|---|---|---|
| coarse | 40 | **PLATEAUED** | 1.8177e−06 | 2.0e−04 | 0.0091 |
| medium | 80 | **NOT_PLATEAUED_TREND** | **3.7548e−04** | 2.0e−04 | **1.877** |
| fine | 480 | **PLATEAUED** | 3.9823e−05 | 2.0e−04 | 0.199 |

**G-F17-2 `u_at_probe`:**

| level | samples | state | relative drift over window | trend tol | drift / tol |
|---|---|---|---|---|---|
| coarse | 40 | **PLATEAUED** | 3.1144e−09 | 2.0e−04 | 1.6e−05 |
| medium | 80 | **PLATEAUED** | 1.1935e−07 | 2.0e−04 | 6.0e−04 |
| fine | 480 | **PLATEAUED** | 3.0649e−09 | 2.0e−04 | 1.5e−05 |

**Five of the six cells PLATEAUED. One did not, and it decided the rung.**

**The single failing cell, in detail** (`levels_detail[medium].plateau_detail` on the
E2 row): window mean **3.5510767492e−05**, fitted slope **−1.2121516178e−11 per
iteration**, window span **1,100 iterations**. |slope| × span ÷ mean =
1.3334e−08 ÷ 3.5511e−05 = **3.7548e−04**, **1.877× the 2.0e−04 tolerance**.
E2 at medium was still falling by 0.0375 % of itself over its last 1,100 iterations.

**The miss is on the TREND limb alone, and the other two limbs were never reached.**
That level's `plateau_detail` object carries `samples`, `window`, `window_span`,
`window_mean`, `scale`, `fitted_slope`, `relative_drift_over_window` and `trend_tol`
— and **no `half_mean_split`, `stat_tol`, `variance_ratio` or `var_ratio_band` keys
at all**, because the trend limb returns first. The five PLATEAUED cells all carry
those keys (mean-split 1.00e−06 / 2.17e−05 / 1.69e−09 / 6.50e−08 / 1.67e−09; variance
ratios 0.9968–1.0000, every one inside [0.2, 5.0]). **The mean-split and
variance-ratio limbs were not consulted for medium/E2, and no claim is made about
what they would have said.**

**Compare F17b, whose refusal this rung was registered to fix.** F17b's E2 drifts
were 1.818e−06 / **1.459e−02** / **1.350e−01** — medium 73× over tolerance, fine 675×
over. F17c's are 1.818e−06 / **3.755e−04** / **3.982e−05**: the fine level moved from
675× over tolerance to **5× inside** it, and the medium level from 73× over to
**1.877× over**. The floor derivation moved both failing levels by two to four orders
of magnitude of drift. **It did not move medium far enough.** F17b's probe row also
carried a `NOT_STATIONARY_VARIANCE` at medium (variance ratio 0.0968); in F17c that
cell reads variance ratio **0.9968** and PLATEAUED. The probe gate is clean at every
level in F17c and was not clean in F17b.

---

## 7. THE REGISTERED PREDICTION VERSUS THE ACTUAL — THE HEADLINE CLAIM IS FALSIFIED

**§5.2 of the pre-registration, verbatim, written before any solver started:**

> *"The falsifiable content of this rung is that deriving the floor moves the E2 order
> from 1.86 to ≈ 2.09 and turns two NOT A RESULTs into two PASSes."*

**IT TURNED ONE.** The rung returns **PASS × 1, NOT A RESULT × 1**. The registration's
headline falsifiable claim is **FALSIFIED**, and this record states that first rather
than last. §5.2 also said, in the same paragraph: *"If the ladder returns anything
else, the prediction is wrong and the record will say so."* The record says so.

| registered prediction (§5.2) | actual | miss |
|---|---|---|
| G-F17-1 verdict **PASS** | **NOT A RESULT** | **the headline claim, falsified** |
| G-F17-2 verdict **PASS** | **PASS** | met |
| E2 fine value **1.050478e−05** | **8.895074e−06** | **−15.32 %** |
| E2 observed p **2.0885** | **2.005022** | −4.00 % |
| probe observed p **3.4322** | **2.140696** | **−37.63 %** |
| E2 coarse 1.423138e−04 | 1.4231373e−04 | −4.6e−05 % |
| E2 medium 3.559705e−05 | 3.5504581e−05 | −0.26 % |
| probe coarse 3.824412e−01 | 3.8244116e−01 | −1e−05 % |
| probe medium 3.823881e−01 | 3.8238846e−01 | +9.4e−05 % |
| probe fine 3.823832e−01 | 3.8237651e−01 | −0.0017 % |
| both triples CONVERGING | both CONVERGING | met |
| fine inside both bands | inside both bands | met |

**On the probe order specifically:** the −37.63 % miss on p = 3.4322 → 2.140696 is
recorded and is **not** a gate failure, because §5.2 **pre-emptively disclaimed any
order claim for that gate**: *"The predicted probe order 3.43 is **not** ≈ 2 and is
registered as such … no order claim is made for it. It is predicted to PASS **on its
band**, not on its order."* G-F17-2's PASS rests on its band, which is untouched by
the order miss. That the disclaimer was registered before compute is the reason this
record can report a 37 % order miss beside a PASS without either softening the miss
or contaminating the verdict.

**On the two coarse and medium predictions:** the level values were predicted to five
or six significant figures and landed there — the E2 coarse prediction is right to
4.6e−05 % and the probe coarse to 1.1e−05 %. The extrapolation machinery of §4 was not
broken. It predicted the *values* well and the *verdict* wrongly, and the gap between
those two facts is §8 below.

---

## 8. WHAT DID WORK — the floor derivation improved the order, and by more than it promised

Stated as carefully as the falsification above.

| ladder | floor | E2 observed p | distance from theoretical 2 |
|---|---|---|---|
| F17b (inherited floor, 4,000 everywhere) | inherited byte-for-byte | **1.8585** | 0.1415 |
| F17c §5.2 **prediction** | derived per level | **2.0885** | 0.0885 |
| **F17c actual** | derived per level | **2.005022** | **0.005022** |

**The E2 observed order moved 1.8585 → 2.005022, toward theoretical 2, and landed
CLOSER to 2 than the predicted 2.0885 — by a factor of 17.6 in distance.** The floor
derivation did what L-346 said it would do to the *order*. It is the **iterative
provisioning at MEDIUM** that failed, not the derivation's physics and not its
extrapolation.

The probe gate corroborates: **G-F17-2 is the first PASS anywhere in the F17 family
at 768×512.** F17 passed both gates at 24,576 cells; F17b returned NOT A RESULT × 2
at 393,216; F17c returns a graded, plateau-clean, band-inside PASS at 393,216 with
GCI 4.381227e−06 absolute. That is a real gain and it is what the 246.3 core-minutes
bought.

---

## 9. THE MECHANISM — the knowledge item, and the limit of what is established

**How the floor was derived (pre-registration §4, under L-346).** The counts were
derived from **the FINE level's discretisation error**: §4.2 fitted the E2 increments
of F17b's own 40 checkpoints per level as a geometric sequence and found the fine
level **41.40 % short of its own converged value at 4,000 iterations** (ρ = 0.98517,
+2σ 0.98538, last observed ratio 0.98435), extrapolating E2_∞,fine = 1.050478e−05.
Fine was the level identified as short; fine is the level the derivation was built
from. **And fine plateaued cleanly** — drift 3.9823e−05, five times inside tolerance.
**The derivation delivered exactly the level it was derived from.**

**MEDIUM was never the level in question, and medium is the level that failed.** §4.3
solved the same drift equation for medium and got 5,183 (point estimate ρ), 5,262
(ρ + 2σ) and *"≤ 5,300"* (the lane's independent 100-iteration grid search).
**Registered: 8,000** — *"rounding up past the worst of every route"*, a claimed
margin of **8,000 / 5,300 = ×1.51** over the most demanding route. At 8,000 the
measured drift is **3.7548e−04**, **1.877× the tolerance**. A level with a claimed
×1.51 iteration margin missed its own criterion by 88 %.

**THE MEASURED DRIFT IS NON-MONOTONE IN LEVEL:**

    coarse  1.8177e-06        medium  3.7548e-04        fine  3.9823e-05
              (0.009x tol)            (1.877x tol)            (0.199x tol)

**The middle level is 207× worse than coarse and 9.4× worse than fine.** Iterative
difficulty, on this ladder, does not increase monotonically with refinement — it peaks
in the middle. **No route in §4.3 anticipated this.** Every route in that table is a
per-level solve of the same decay equation, and each level's ρ was fitted from that
level's own data, so the machinery *could* in principle have produced a non-monotone
answer; what it did not do is **check** the derived count at a level other than the one
identified as short. The medium count was rounded up past three routes and then
believed.

**A mechanism for WHY medium trends while both its neighbours plateau is NOT
established by this rung.** It is a **measured state, not a diagnosis.** What can be
said from the artefacts alone: medium's fitted ρ from F17b was 0.78558 — the fastest
decay of the three levels — so the routes predicted it needed the *fewest* extra
iterations, and it got the *largest* proportional round-up; that combination produced
the miss, but the reason its actual decay at 8,000 iterations is slower than its
F17b-fitted ρ implies is **not measured here**. The pre-registration's own §8.2 offers
a cache-straddling hypothesis for a *different* non-monotonicity (the per-cell-iteration
*rate*, which also peaks at medium — see §10) and explicitly labels it *"the
non-monotonicity is the measurement; the cache story is a hypothesis."* **The same
discipline applies here, and this record makes no attempt to unify the two
observations.** That they both peak at the medium level is noted as a coincidence in
the artefacts, not as a mechanism.

---

## 10. COST — rule 12 estimate-versus-actual, and the calibration clause of §8.5

Basis registered at §8.5: **`ClockTime × ranks ÷ 60`**, gross and cleaned separately,
waste named separately, ratio actual/predicted, gap attributed, dollars derived.

| item | value |
|---|---|
| registered estimate (prereg §8.3, `proj_f17c.py`'s own arithmetic) | **247.62 core-min** (coarse 1.106, medium 12.251, fine 234.262) |
| registered cap (§8.3) | **370.0 core-min** = 1.4942 × the estimate |
| actual, **MEASURED** from the logs' `ClockTime × ranks ÷ 60` | coarse 75 s → **1.250**; medium 672 s → **11.200**; fine 14,031 s → **233.850**; **246.300 core-min** |
| launcher's own tally (`launcher.queue.out`, *"ALL THREE LEVELS COMPLETE. Cumulative spend: 246.29999999999998 core-min of 370"*) | **246.300** — agrees to every digit |
| grader's `cost_claim.core_min_claim` / `partial_sum_core_min` (`F17c_GRADED.json`) | **246.300 / 246.300**, `defects: []`, class INFRASTRUCTURE |
| ExecutionTime basis, stated beside it | (63.74 + 614.84 + 13,985.02) ÷ 60 = **244.393 core-min** |
| **actual gross** | **246.300** |
| **actual cleaned** | **246.300 — cleaned == gross** (see §11 for the 3600-s row) |
| **waste, named separately** | **0.000 core-min** — no stall, no kill, no re-run, no cap movement; the ladder ran once, completed, and was graded once |
| quantisation | `ClockTime` is integer-second: ± 0.008333 core-min per level |
| share of the registered cap | **66.57 %** (246.300 / 370.0); no overrun, and the cap was never raised |
| dollars | 246.300 ÷ 60 × $0.0513 = **$0.2106 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **0.9947** |

**Per level, against the registered §8.3 projections:**

| level | projected (§8.3) | actual | ratio | projected wall s | actual wall s |
|---|---|---|---|---|---|
| coarse | 1.106 | **1.250** | **1.130** | 66 | 75 |
| medium | 12.251 | **11.200** | **0.914** | 735 | 672 |
| fine | 234.262 | **233.850** | **0.9982** | 14,056 | 14,031 |
| **ladder** | **247.62** | **246.300** | **0.9947** | 14,857 | 14,778 |

**Gap attribution: MISPREDICTION, 0.53 % — and there is essentially nothing to
attribute.**

- **Contention: none detectable.** Ladder `ExecutionTime / ClockTime` =
  14,663.60 / 14,778 = **0.9922**; wall exceeds CPU by **0.78 %**, inside the *"below
  1 %"* bound §8.2 registered from F17b's own wall/CPU ratios. Per level 0.850 /
  0.915 / 0.9967. The box was **not** idle — `box_before.txt` / `box_after.txt` record
  load1 15.84 → 23.08 → 24.69 on 16 cores across the three launches, with
  MemAvailable falling 27.5 GB → 20.2 GB — so a busy box produced a 0.78 % wall/CPU
  gap on this work, which is the same finding F17b recorded and §8.2 registered as a
  contention multiplier of 1.0. The registration's contention bound **held**.
- **Waste: 0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and
  **folded into no ratio above**.
- **The residual 0.53 % is misprediction**, and it is concentrated in the two cheap
  levels: coarse ran 13.0 % over its projection (9 wall s) and medium 8.6 % under
  (63 wall s), while **fine — 94.9 % of the spend — came in 0.18 % under its
  projection.** The two small misses very nearly cancel; the accurate level is the
  one that mattered.

**The calibration lesson, and it is a vindication of a registered choice.** §8.2
registered **no per-doubling growth exponent**, on the explicit ground that the
measured per-cell-iteration rate *"is not monotone in problem size"* — it rises 38.5 %
coarse→medium and falls 20.3 % medium→fine. What `proj_f17c.py` carries instead is
**frozen per-level ratios from one measurement**, with **`GROWTH["fine"] = 0.7967`,
which is LESS THAN ONE** (= 0.7447 / 0.9347, the registered fine and medium rates).
That choice produced a **0.18 %-accurate projection of the level carrying 94.9 % of
the ladder's spend.**

The counterfactual, as arithmetic on the registered figures and labelled as such:
the coarse→medium rate ratio is 0.9347 / 0.6751 = **1.3845**. An exponent fitted to
that step and applied a second time gives a fine rate of 0.9347 × 1.3845 =
**1.2941 core-µs per cell-iteration**, hence 18,874,368,000 × 1.2941e−06 =
**24,426 wall s = 407.10 core-min** — **1.74× the actual 233.850**, and **1.10× the
registered cap of 370**. A projector that could only carry a growth factor above 1
would have projected this ladder **over its own cap** and the rung would not have
been launchable as designed. §8.2's refusal to fit an exponent is **vindicated by
measurement**, and it is the standing F21 / F22 / F18b calibration defect *(base
rates right to 7–10 %, imported growth exponent wrong by +110 to +137 % per
doubling)* not being repeated.

**One measured caveat against the launcher's live re-basing, recorded because it is
less accurate than the frozen projection.** `run_f17c.sh` re-bases the rate from
**this run's** measured rate at the previous level and then applies the frozen
ratio. Its live pre-spend projections were **medium 13.8454** (actual 11.200 →
**0.809**) and **fine 214.1600** (actual 233.850 → **1.092**); the frozen §8.3
projections were **12.251** (0.914) and **234.262** (**0.9982**). At the level that
carries the spend, **the frozen projection was 48× more accurate than the live
re-based one** (0.18 % vs 8.42 % error against the actual). The live re-basing is a *cap-safety* device, not a
calibration instrument, and it never came close to firing (see §11); but the record
should not let its numbers be mistaken for the registered estimate. **The calibration
row in `docs/COST_CALIBRATION.md` is built from the §8.3 registered figures, which
are what rule 12 compares against.**

---

## 11. THE 3600-SECOND ROW — the pre-registration called it correctly, BEFORE COMPUTE

The fine level ran **14,031 wall s**, which trips
`COMPUTE_BUDGET_CHARTER.md` §6's *"a row over 3600 wall s is a stall"* heuristic.

**§8.4 of the pre-registration registered that this would happen and that it would
not be a stall, before any compute:**

> *"`COMPUTE_BUDGET_CHARTER` §6's "a row over 3600 wall s is a stall" heuristic **will
> fire on the fine level and it will not be a stall**: it is a single registered
> 48,000-iteration level. **This is registered now, before compute, so the results
> record cannot be accused of explaining it away afterwards.**"*

**The pre-registration called it correctly.** The evidence that this row is a
registered level and not a stall is on disk and is not an inference from the wall
figure: 48,000 `Time =` lines and 48,000 `ExecutionTime` lines in
`fine/log.simpleFoam`, one `End`, `RC.txt` = 0, 480 written checkpoints, and
`ExecutionTime / ClockTime` = 13,985.02 / 14,031 = **0.9967** — the rank was
delivering CPU for 99.67 % of that wall. A stall is a wall with no work behind it;
this wall has 18.87 billion cell-iterations behind it. §8.4 projected 14,056 wall s
and measured 14,031. **Gross == cleaned at 246.300 core-min; there is nothing to
clean.**

**In-level cap enforcement (§8.3), recorded as it behaved.** The whole remaining cap
was converted to wall seconds and handed to `timeout` around each solver, written to
`<level>/CAP_ALLOWANCE.txt` before the solver started: coarse 22,200 s (remaining cap
370.00), medium 22,125 s (368.75), **fine 21,453 s (357.55)**. The fine level used
**14,031 of its 21,453 s allowance — ×1.529 headroom, 65.4 % consumed.** No `timeout`
fired at any level; no level was killed; **the cap was never raised.** (The
allowances differ slightly from §8.3's registered 22,200 / 22,133 / 21,398 s because
the remaining cap is computed from *actual* spend at each launch, not projected —
that is the registered behaviour, not a departure.)

---

## 12. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- `cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR` reads `launcher_rc=0
  end=2026-08-28T02:38:25Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc` and
  was written by the queue runner. The solver rc per level is `RC.txt` = 0 at all
  three, cited in §3 and read as `MEASURED` by the grader.
- The grader's `cost_claim` carries **no defects**; the cost claim in §10 is not
  refused (`core_min_claim` 246.29999999999998, `partial_sum_core_min` the same, cap
  370.0, `fields` INFRASTRUCTURE).
- **The grader's stdout was not captured to a file under the run root.** F17 and F17b
  each carry a `*_GRADED.out` beside their `.json`; `verification/runs/F17c_runs/`
  contains **only** `F17c_GRADED.json` plus the three level directories. **This lane
  therefore cannot cite an artefact for the grading invocation's exit status** — the
  JSON's existence, its 25,206 bytes of complete content and its 2026-08-28T16:14:12Z
  mtime are the artefacts that exist. **Stated as a gap, not filled by inference.**
- No foreign grade artefact was present in the run root: `F17c_GRADED.json` is the
  only non-level entry.
- `launcher.queue.out` and `queue_entry_F17c_KV40_FLOOR.json` under the case
  directory are the runner's records; not committed by this lane.
- The frozen grader exits 2 under `python3 -O` by construction (`-O` deletes every
  `assert`, including the `_seal` invariants inside `roache_triple.py`); the launcher's
  instrument line records `grade_f17c` and `proj_f17c` both exiting 2 under `-O`, and
  all three selftests passing under plain `python3`.
- Run output stays under `verification/runs/F17c_runs/` and is **not committed**;
  16.8 GB of checkpoints were projected at §8.4 and the run root holds 480 / 80 / 40
  checkpoints as registered.
- Box at the three launches: load1 15.84 / 23.08 / 24.69 of 16 cores, MemAvailable
  27.5 / 25.7 / 20.2 GB (`box_before.txt`); these are **INFRASTRUCTURE observations
  only** — `proj_f17c.py` reads no box state, which is L-349 retired for this rung.

---

## 13. WHAT IS NOT CLAIMED

- **No mechanism for the medium-level trend.** §9 records a measured non-monotone
  drift and explicitly declines to diagnose it. The cache hypothesis §8.2 offers for
  the *rate* non-monotonicity is not extended to the *drift* non-monotonicity, and no
  common cause is asserted.
- **No claim about what iteration count would fix the medium level.** The measured
  drift at 8,000 is 1.877× tolerance; converting that into a required count is a new
  derivation with a new floor, and under rule 2 it belongs in a **successor
  pre-registration written before that compute**, not in this record. Nothing here
  proposes it as done, and no number for it appears above.
- **No re-grade and no amendment.** F17 and F17b are frozen and post-compute; neither
  is re-graded, amended or reinterpreted by this rung. The F17c pre-registration is
  itself post-compute and closed: nothing in this record alters a gate, threshold,
  cap or label.
- **No GCI is claimed for G-F17-1**, for the reason given in §1, and its triple's
  124.07 % figure is not a result in any form.
- **No order claim for G-F17-2**, as §5.2 registered; its PASS rests on its band.
- **No pressure gate** (`p` is not graded), **no turbulence claim** (the case is
  laminar), **no claim about SIMPLE's convergence rate as a solver property** — §4's
  ρ values are measurements of this case on this box.
- **No `BLOCKED-GPU`**: this rung is CPU-only by construction.
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7).
  Everything here stays on this box (rule 8).

Calibration row: lands in `docs/COST_CALIBRATION.md` (id derived at commit time from
the ledger's maximum existing id). Lesson: lands in `docs/LESSONS.md` (number derived
at commit time from the maximum existing lesson number).
