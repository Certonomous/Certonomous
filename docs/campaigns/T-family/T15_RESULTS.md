# T15 results — UNSTEADY axisymmetric turbulent plume on T8's fine mesh

**RUNG VERDICT: `NOT A RESULT` — on all four graded rows (`S1`, `V1`, `V2`, `V3`).**

**The run is COMPLETE. The GRADING is not.** The frozen comparator
`analyse_t15.py` **REFUSED (exit 2)** inside the planted-zero control, at
`analyse_t15.py:501-504`, **before a single graded row was reached**. No value of
`S1`, `V1`, `V2` or `V3` exists in any artifact on disk, and none is supplied
here. A rung whose comparator refused has no graded value; it does not have a
degraded one.

**Why `NOT A RESULT` and not `PENDING`.** `PENDING` is the display/queue state for
work not yet run (`VERIFICATION_CHARTER.md` §9). This rung ran, to completion, at
a measured 1,195.817 core-minutes. The instrument then refused. That is a
`NOT A RESULT`, and calling it `PENDING` would hide 1,196 core-minutes of spent
compute behind a queue label.

Pre-registration: `docs/campaigns/T-family/T15_PREREGISTRATION.md`, machine twin
`verification/runs/T-family/T15_runs/T15_registered.json`.
Run root: `verification/runs/T-family/T15_runs/`.
Grading output: `verification/runs/T-family/T15_runs/T15_GRADE_OUTPUT.txt` (14 lines).

---

## 1. The freeze set — seven of seven MATCH, verified at this writing

Each file's disk bytes hashed with `git hash-object` and compared against its own
blob at `HEAD`, in one invocation:

| file | blob |
|---|---|
| `analyse_t15.py` | `8b5e787f` |
| `T15_registered.json` | `61239ae9` |
| `mark_done_t15.py` | `40eba7db` |
| `build_t15.py` | `9ddf0285` |
| `mtt_t15.py` | `f66b33c0` |
| `exact_t15.py` | `56209a45` |
| `run_one_t15.sh` | `4f0b4630` |

**No drift. No frozen file edited.** The freeze commit is **`de0683c7`**,
2026-08-26; first compute began **2026-08-27T08:57:37Z**. **Standing rule 2 is
clean:** the gate, the bands, the cap and the labels were committed a day before
the solver started.

## 2. Completion — the run IS complete, on all six conjuncts of standing rule 4

Re-measured from the case's own artifacts at this writing, not taken from the
marker:

| conjunct | measured | source |
|---|---|---|
| `rc = 0` | **0** | `STATUS.T15_UP_f` |
| an `End` line | **1** | `T15_UP_f/log.solve` |
| last time == `endTime` | **240 == 240** | `log.solve`, `T15_registered.json` `endTime_s` |
| `ExecutionTime` count == `endTime`/`deltaT` | **24 000 == 24 000** | `log.solve` |
| registered fields present at `endTime` | **T U p_rgh alphat nut k epsilon UMean TMean UPrime2Mean TPrime2Mean** | `T15_UP_f/240/` |
| the age guard | asserted by `mark_done_t15.py`, which wrote **`DONE.T15_UP_f`** | `DONE.T15_UP_f` |

`STATUS.T15_UP_f` reads `capped=no checkmesh_rc=0 note=clean`, solver
`buoyantBoussinesqPimpleFoam` at
`/usr/lib/openfoam/openfoam2606/.../buoyantBoussinesqPimpleFoam`, 1 rank, wall
**71,749 s**, started 2026-08-27T08:57:37Z, ended 2026-08-28T04:53:26Z. Four time
directories written: **60, 120, 180, 240**.

**The failure is in the instrument, not in the solve.** Nothing here is a run
defect and nothing suggests one.

## 3. THE REFUSAL, quoted and located

`T15_GRADE_OUTPUT.txt`, last line:

> `REFUSE: planted-zero control S1(FLUCTUATION): a CONSTANT offset of one mean moved sigma/mean by 9.95e-05 -- a working fluctuation reader must be nearly blind to a constant offset; this one is not`

**The limb is `analyse_t15.py:501`:**

    if d_const > 0.5 * ref:

It sits in the **constant-offset arm** of the `C_PZ` control's fluctuation
reader. The comparator calls `planted_zero_control(...)` at `:701` and builds its
graded rows at `:709-713`; **the refusal at `:501` is upstream of `:709`, so the
rows were never constructed.** That is control-flow, read at source, not an
inference from the output's length.

## 4. WHY THE REFUSAL FIRED — a defect in the control, measured algebraically

**The constant-offset arm cannot pass. Its test is an exact tie for every
dataset, and the outcome is decided by floating-point evaluation order.**

The arm plants a constant `c = 1.0 × mean_scale` into the probe column over the
window (`:497`, `_plant_probe_file(..., alternate=False)`, which adds `+mag` to
the z-component of the **same single column** `_s1_of` reads, located from the
probe file's own header at `:238-242`). `mean_scale = abs(mean)` (`:462`), and
`window_stats` returns `rel_sd = sd / abs(mean)` (`:293`).

**Adding a constant equal to the window mean doubles the mean and leaves the
standard deviation untouched.** So for `mean > 0`:

    S1_after = sd / (2·mean) = S1_before / 2      ⇒   d_const = S1/2   EXACTLY

and the test is `S1/2 > 0.5 × S1` — **an exact equality, never a strict
inequality, in exact arithmetic.** For `mean < 0` the new mean is exactly zero,
`rel_sd` returns `inf` (`:293`), and the refusal is certain. **There is no value
of the data for which this arm passes on its merits.**

**The printed number corroborates it rather than contradicting it.**
`d_const = 9.95e-05` is printed at `%.3g`; the threshold it exceeded is
`0.5 × ref`. The two agree to the printed precision, which is what an exact tie
broken by round-off looks like.

**The control's own docstring names the inversion it was built to avoid** — *"a
planted-zero control sized against a converged field is blind precisely on the
cases where a reader most needs checking"* (`:383-385`) — and the comment block at
`:475-487` sets out, carefully and correctly, why a dispersion-ratio reader
cannot be held to the additive readers' `0.1 × plant` rule. **The three
substantive arms it registered instead all passed** (§5). **The fourth, the
near-blindness arm, was written with a RELATIVE threshold against a quantity that
the plant scales exactly, and a relative threshold cannot express "nearly blind"
for a ratio the plant halves by construction.** An absolute tolerance, or a
comparison against `S1/2` with a tolerance, would have expressed the intent.

**THIS IS NOT REPAIRED HERE, and that is deliberate.** `analyse_t15.py` is frozen
and has fired; standing rule 6 forbids editing it, and `VERIFICATION_CHARTER.md`
§2d.1 is not this lane's route. **The successor registration `T15b`
(`docs/campaigns/T-family/T15b_PREREGISTRATION.md`, frozen, not run) is where a
corrected control belongs.** No instrument was written for this record.

## 5. WHAT DID PASS — reported, and scored by nothing

**These are controls and reference-route checks. None of them is a graded row and
none of them carries a rung verdict.** They are recorded because the compute
bought them.

**`C_REF` — the MTT referent, verified by route B before any comparison
(`mtt_t15.py`), four of four:**

| id | what | measured |
|---|---|---|
| **B1** | the closed form satisfies the three MTT ODEs at z = 3 | entrainment **3.741e-10**, momentum **1.029e-10**, dF/dz **1.735e-15**; `h²` ratios **3.999, 4.000** (second order, as it must be) — **`PASS`** |
| **B2** | flux identities `Q²/(πM) = b²`, `M/Q = w`, `F/Q = g′` | worst relative **4.953e-16** — **`PASS`** |
| **B3** | the registered source sits ON the similarity solution | `z₀ = −0.694444444 m`; `w(0) = 0.600000000` vs `w₀ = 0.600000000` (rel **0.00e+00**), `g′(0)` rel **1.61e-16**, `F₀` rel **0.00e+00** — **`PASS`** |
| **B4** | an independent RK4 integration reproduces the closed form | worst `|num − closed|/closed` **1.535e-13**; fitted exponents `n_w` **−0.333333333333**, `n_T` **−1.666666666667**, `n_Q` **+1.666666666667**, worst deviation **6.706e-14** — **`PASS`** |

**`C_OP` — operand identity (L-331).** `nu`, `beta`, `TRef`, `b₀`, `w₀`, `g′₀`
read from the case files; `F₀` recomputed **0.013028813053**, matching `CASE.txt`
to **2.49e-12**.

**`C_GEOM` — MEASURED geometry, from `0/Cx`, `0/Cz`, `0/V` written by OpenFOAM.**
`r₁ = 0.00416270092325 m`, `r₂ = 0.00971296882092 m`, `r₂/r₁ = 2.333333333`
(printed and asserted nowhere — T8 GROUND 2); `dz = 0.0125 m`; the wedge→annulus
scale **72.091466** measured from the mesh's own total volume against the
flat-sided nominal `2π/sin 5° = 72.091466`, **relative difference 2.374e-12**.

**`C_CO` — Courant.** Max over the whole run **1.1528** (reported); max over the
registered window [120, 240] s **0.9870** against a floor of 1.00 — **ok**.
Registered prediction P5 said the window max would be ≤ 0.8; **it is 0.9870, so
P5 is a MISS**, recorded as a miss.

**`C_STAT` — stationarity precondition.** Window drift **0.00064** of the mean
against a floor of 0.050, over **1,201 samples** on [120, 240] s — **ok**, by a
factor of 78.

**`C_BOUND` — ε/k bounding, reported and deliberately never gated.**
**0 lines over 24,000 steps = 0.00000 per step.** **Registered prediction P6 said
bounding would occur on at least 1 % of steps, and named zero bounding as its own
falsifier — *"which would itself be the finding that the transient formulation
removes the closure's unrealizability"*. THE FALSIFIER FIRED.** T8 bounded ε on
every level from `Time = 24`; the unsteady formulation on the same mesh with the
same closure bounded it **not once in 24,000 steps**. This is a
**reported-not-gated physics finding**, it is the sharpest thing this rung
produced, and it stands independently of the grading refusal because `C_BOUND` is
registered as never gated.

**`C_Z0` — virtual origin, reported.** `z₀ = +0.078337 m` from the `b(z)`
x-intercept (T8 §12 S4's registered route), against the MTT closed form's
**−0.694444 m** at α = 0.12.

**Three of four planted-zero arms `PASS`** (the fourth is §4):

| reader | plant × its own scale | recovered | floor |
|---|---|---|---|
| `w_axis(POINT)`, 2 cells | 0.001234 × **0.711717** | **0.000878259** | 1e-07 × scale |
| `T_axis(POINT)`, 2 cells | 0.001234 × **303.495** | **0.374513** | 1e-07 × scale |
| `b_th(INTEGRATING)`, 123 cells | 0.001234 × **0.471346** | **0.00369158** | 1e-07 × scale |

## 6. The four graded rows — no values exist, and none is inferred

| row | quantity | registered band | value | verdict |
|---|---|---|---|---|
| **S1** | σ(w)/mean(w) at the axis probe, z = 3.0 m, over [120, 240] s | [0.000, 0.020] | **NOT PRODUCED** | **`NOT A RESULT`** |
| **V1** | `n_w`, OLS slope of ln(w̄) on ln(z − z₀), z/D ∈ [10, 25], 31 stations | [−0.38333, −0.28333] | **NOT PRODUCED** | **`NOT A RESULT`** |
| **V2** | `n_T`, same fit on ln(T̄ − T_ref) | [−1.71667, −1.61667] | **NOT PRODUCED** | **`NOT A RESULT`** |
| **V3** | `db/dz` from the top-hat radius on MEASURED cell volumes | [0.132, 0.156] | **NOT PRODUCED** | **`NOT A RESULT`** |

**The registered predictions P1–P4 are therefore UNSCORED, in either direction.**
P1 (the plume settles), P2, P3 and P4 (V3 fails while V1 and V2 pass — T8's
kEpsilon round-jet anomaly biting the entrainment coefficient and not the
exponents) **were not tested by this rung and must not be reported as confirmed
or as falsified.**

### 6.1 One quantity IS recoverable by algebra, and it is REPORTED, not graded

The refusal message prints `d_const = 9.95e-05`. §4 shows that
`d_const = S1/2` exactly. **Therefore `S1 ≈ 1.99e-04`, to the three significant
figures the message carries.**

**THIS IS AN ALGEBRAIC INFERENCE FROM A REFUSAL MESSAGE. IT IS NOT A GRADED
VALUE AND IT CARRIES NO VERDICT.** It was never passed through `apply_gate`, it
was never checked against `gate1`, and the registered band was never applied to
it. It is recorded here because the compute measured it and a `NOT A RESULT`
hides no measurement — and it is recorded with its provenance so that no reader
can mistake it for a score.

**Read for what it is worth and no more:** 1.99e-04 sits roughly **100×** inside
the registered band `[0, 0.020]`, which is the direction P1 predicted. **P1 is
still unscored.** A number recovered from a refusal message is not the number the
frozen instrument would have written, and the difference is exactly the point of
freezing an instrument.

## 7. ROACHE TRIPLE GATING — there is no triple here, by registration

`T15_registered.json` registers **`"grid_triple": false`** and a capability
ceiling that reads, verbatim:

> *"CAN DO, CAVEATS — ONE MESH. No Roache triple exists for this rung and none may be computed from it; no GCI, no Richardson extrapolate and no discretisation uncertainty is quoted on any row."*

**Standing rule 5 clauses (2) and (3) have no operand on this rung.** No triple
state, no observed order, no GCI and no Richardson extrapolate appears anywhere in
this record, and none may be derived from it. Clause (1) — a level not converged
or not stationary — was tested by `C_CO` and `C_STAT` and passed (§5); it is not
the reason for the `NOT A RESULT`, and §3 is.

## 8. Cost — rule 12, estimate against actual

| | figure | basis |
|---|---:|---|
| POINT, registered | **1,307 core-min** | `T15_registered.json` `cost.point_core_min` |
| CAP, registered | **2,600 core-min** (`timeout_s` 156,000) | same |
| **ACTUAL, MEASURED, gross wall basis** | **1,195.817 core-min** | `STATUS.T15_UP_f`: `wall_s=71749`, `ranks=1` |
| ACTUAL, solver-only basis | **1,179.188 core-min** | `log.solve` last `ExecutionTime = 70751.29 s` |
| **ratio actual/predicted** | **0.915×** (wall) · **0.902×** (solver-only) | |
| fraction of CAP | **46.0 %** of 2,600 core-min; **46.0 %** of the 156,000 s timeout | |
| dollars, **DERIVED, NOT MEASURED** | **$1.0224** actual vs **$1.1175** predicted, at $0.0513/core-h | owner-stated rate; the box cannot read its own billing |

**GROSS IS THE PUBLISHED FIGURE AND NO CLEANED FIGURE IS OFFERED.** The 3,600
wall-second stall marker, read literally against this single-row `STATUS`, would
clean a **71,749 s registered transient — capped at 156,000 s before compute** —
down to zero. Its operand is a per-arm run-root ledger row, not one registered
long transient. **Referred as a rule-scope question; this lane does not
reinterpret a standard.**

**ATTRIBUTION OF THE 8.5 % UNDERSPEND — misprediction in the conservative
direction, one cause, no contention penalty and no waste.** The POINT came from a
scratch probe measuring **3.267 core-s per step over steps 6–20**
(`cost.rate_scratch_source`); 24,000 × 3.267 / 60 = 1,306.8, the registered 1,307.
Measured over the whole run: **2.9895 core-s per step** (wall) and **2.9480**
(solver). **Steps 6–20 are start-up** — the registration's own P5 records the
scratch Courant at 1.053 at start-up decaying through 0.72 by t = 0.12 s, so the
probe sampled precisely the regime where PIMPLE does the most corrector work.
Corroborating the single cause: the measured **2.9195e-05 core-s per cell-step**
against T8's measured SIMPLE rate of 6.397e-06 core-s per cell-iteration gives a
**PIMPLE/SIMPLE ratio of 4.564** against the registered 4.99 — **9.3 % high, the
same sign and the same order as the 9.8 % per-step over-price.**

**NAMED SEPARATELY, NOT LAUNDERED INTO THE RATIO: 16.629 core-min (1.39 % of
gross) is wall-minus-`ExecutionTime`** — mesh and field I/O,
`writeCellCentres`/`writeCellVolumes`, solver start-up. That is not waste (it
bought the `0/Cx`, `0/Cz`, `0/V` the `C_GEOM` control reads and the four written
time directories) and not a stall; it is the wall/solver basis gap, stated so a
reader can choose a basis.

**WASTE: the honest figure is the whole 1,195.817 core-minutes of GRADING VALUE,
and 0.000 core-minutes of COMPUTE.** No run failed, none was re-run, none was
capped. The solve is on disk, complete, and a corrected comparator registered as
a successor could grade it without spending a core-minute more. **The compute is
not lost; only the verdict is.** That distinction is the reason this rung is
worth recording rather than writing off.

**A `docs/COST_CALIBRATION.md` row is OWED and is NOT YET LANDED.** The drafted
row sits at `verification/runs/T-family/T15_runs/COST_CALIBRATION_ROW_DRAFT.txt`
and is explicit that it *"records COST ONLY"* and that *"the science is ungraded
and must not be reported as graded"*. Its provisional id is stale by
construction — the id is re-derived from the ledger's tail at commit.

## 9. Disclosures

- **NO GRADED ROW EXISTS ON THIS RUNG.** Four rows were registered; four are
  `NOT A RESULT`. The rung supplies **no capability claim** and must not be cited
  as one.
- **The refusal is an instrument defect, not a run defect** (§4), and it is
  **reported, not repaired** — the file is frozen and has fired.
- **The one substantive result this rung produced is `C_BOUND`'s zero** (§5): the
  unsteady formulation bounded ε **not once in 24,000 steps** where T8 bounded it
  on every level. It is a **reported-not-gated** finding, registered as ungated
  before compute, and it stands.
- **P5 MISSED** (window Courant 0.9870 against a predicted ≤ 0.8, floor 1.00 —
  inside the control, outside the prediction). **P6's falsifier FIRED.** **P1–P4
  are UNSCORED.**
- **P1's registered limit still applies to anything a successor concludes**: a 5°
  axisymmetric wedge admits no azimuthal mode, so a settled `S1` could only ever
  have excluded *axisymmetric* unsteadiness.
- **No triple, no GCI, no Richardson extrapolate** (§7) — by registration, not by
  omission.
- No frozen file edited (rule 6). No compute run for this record. **Nothing sent,
  filed, uploaded, posted or registered outside this box** (rule 7).
