# T8 entry rung — MTT pure-plume self-similarity: pre-registration (FROZEN)

**FROZEN 2026-08-25, before any solver has run.** This file promotes
`T8_PREREGISTRATION_DRAFT.md` (2026-08-25, committed `240502e2`, blob
`2adcf2ec`, **left untouched on disk beside this file**) to the frozen
pre-registration, and **supersedes it**. The draft is retained unedited as the
record of what was proposed; where this file differs, this file governs.

**Condition at freeze, and how it was checked** (`CLAUDE.md` rule 2, the
pre-compute amendment clause). The run tree is
`verification/runs/T-family/T8_runs/`. At the moment this file is committed
that tree holds `build_t8.py`, `analyse_t8.py` and `run_one_t8.sh` and
**no case directory of any kind**: `T8_MTT_c`, `T8_MTT_m` and `T8_MTT_f`
**do not exist**, no `0/`, no `0.orig/`, no time directory, no mesh, no log,
no `STATUS` file and no `DONE` marker. **Zero core-minutes have been spent on
this rung.** Every ruling applied below is therefore a **pre-compute**
amendment and legal; after the first solver starts, nothing in §1–§10 may
move except by dated addendum that cannot alter a gate, threshold, cap or
label.

**Disclosure — a dry run of the mesh specification.** Before this file was
frozen, `build_t8.py` was executed against a **scratch root** (not the
registered run tree) and `blockMesh`/`checkMesh` were run there, to establish
that the block decomposition of §5 is realisable and that the cell counts are
exactly 6,400 / 25,600 / 102,400. That dry run wrote nothing into the
repository, involved no solver and cost no core-minutes; its purpose was to
avoid freezing a document against an unrealisable mesh. The registered meshes
are rebuilt from the same script at the registered root after this freeze, and
their `checkMesh` output is the record.

Campaign T, rung **T8**, DC-cooling spine position 3, entry arm. Verdict
vocabulary fixed by `VERIFICATION_CHARTER.md` §2 and `CLAUDE.md` rule 1:
**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 0. The supervisor's six rulings, applied

The heat-transfer supervisor read the draft in full on 2026-08-25 and ruled.
All six rulings are applied in the body below; they are listed here so that a
reader can diff this file against the draft without reconstructing why.

| # | Ruling | Where applied |
|---|---|---|
| **R1** | **Grade the FINE-level value; the Richardson extrapolate is REPORTED beside it and is never gated on.** The draft's criterion (3) gated on the extrapolate. A Richardson **sign inversion** is a live defect in this lab's own comparators — `analyse_t3.py:384` and `analyse_t1c.py:337` both compute `richardson = f_fine + e21/den` where `e21 = f_med − f_fine` and the correct form is `f_fine − e21/den`. That defect is survivable **only because it is display-only everywhere it currently lives.** A T8 prereg gating on the extrapolate would make a display-only defect **load-bearing**, in a document written after the defect was known. Grading the fine value is also established practice elsewhere in this lab. | §7 criterion (3); §3; §12 S5 |
| **R2** | The **±0.05 band stands** as a graded band, with two additions: (a) a PASS here is a **joint code-plus-closure statement and is NOT a code-verification claim**; (b) the **deviation and the band-utilisation fraction** are printed for every exponent, not just the verdict. | §4; §7; §10 |
| **R3** | **Fit window tightens to `z/D ∈ [10, 25]`.** `[10, 30]` is retained as **registered control C5**, a reported sensitivity, not a gate. The cost is disclosed up front: `[10, 25]` is only **0.398 decades** of fit range, thin for a log-log slope. | §4; §9 C5 |
| **R4** | **`kEpsilon` is the registered closure, and the reason is a TESTABLE PREDICTION registered before the run**: the round-jet/plane-jet anomaly will bias `α` (REPORT-ONLY) and will **not** move the graded exponents, because those are consequences of the MTT conservation equations and independent of `α`. | §2; §3; §9 P1 |
| **R5** | **Serial, `nProcs = 1`, no decomposition.** | §6 |
| **R6** | A **cost hazard the draft did not name** is registered: the `1.196e5 cell·steps/(core·s)` rate is borrowed from `K2bU3_L025`, a **transient PIMPLE** case, while T8 is a **steady SIMPLE-family** run. Per-step cost differs between solver modes. This is the error shape that made T1b L4 miss its estimate by 31.4 % on a rate borrowed across a mesh jump. | §8 |

**One arithmetic correction to the draft, made here rather than inherited.**
The draft §4 asserts the band "excludes the two nearby wrong answers … by more
than twelve band widths." **That figure is not right and is corrected here.**
The band is ±0.05, so one **band width** is 0.10 and one **half-width** is
0.05. A jet has `n_w = −1` and `n_Q = +1`; the distance from the plume value is
`|−1 − (−1/3)| = 0.6667`, which is **6.67 band widths, or 13.3 half-widths**.
A non-entraining column has `n_w = 0`, a distance of `0.3333` = **3.33 band
widths, or 6.67 half-widths**. The discrimination claim survives — the band
does separate a plume from a jet and from a column by a wide margin — but the
margin is **6.67 band widths on the strongest discriminator and 3.33 on the
weakest**, not twelve. Registering the looser true figure is the point of
R2(b): a reader must be able to see how much of a loose band was consumed.

---

## 1. Case

`T8_MTT_c`, `T8_MTT_m`, `T8_MTT_f` at `verification/runs/T-family/T8_runs/` —
an **axisymmetric 5° wedge** turbulent **pure plume** rising from a circular
buoyancy source of diameter `D = 0.2 m` into a quiescent, unstratified
environment of radius `R = 12 D = 2.4 m` and height `H = 40 D = 8.0 m`, solved
**steady** with `buoyantBoussinesqSimpleFoam` (OpenFOAM v2606,
`/usr/lib/openfoam/openfoam2606`), standard **`kEpsilon`**, `Prt = 0.85`,
`Pr = 0.71`, `nu = 1.5e-05 m²/s`, `TRef = 300 K`, `beta = 1/300 K⁻¹`,
gravity `(0 0 −9.81) m/s²` with `z` vertical and the wedge swept about the
`z` axis, symmetric about the `y = 0` plane.

**Arming guard (rule 4).** `run_one_t8.sh` **refuses** to launch if `0/` or any
time directory already exists in the case. `0/` is created **only at launch**,
by copying `0.orig/`, and **`0/T` is touched LAST**, so that `0/T` dates the
run that was allowed to produce the answer and the age guard of §7 can be
applied. `build_t8.py` writes `0.orig/` and never writes `0/`.

## 2. Reference

**Morton, Taylor & Turner (1956) top-hat plume theory** — the closed-form
self-similar solution for a pure plume from a point source of buoyancy flux
`F₀` in an unstratified environment. **It is derived in this document, not read
from a file**, so no paper acquisition blocks this rung and `CLAUDE.md` rule 15
(title-page verification) does not apply — there is no retrieved artifact to
verify.

**Derivation, in the top-hat conventions used here.** With `b(z)` the plume
radius, `w(z)` the vertical velocity, `g'(z) = g β ΔT(z)` the reduced gravity,
and the entrainment assumption `dQ/dz = 2π α b w`:

```
Q = π b² w              (volume flux,   m³/s)
M = π b² w²             (momentum flux, m⁴/s²)
F = π b² w g' = F₀      (buoyancy flux, m⁴/s³ — CONSERVED, unstratified)
```

Self-similar solution: `b = (6α/5) z`, and eliminating `α` between the three,

```
w(z)  = (0.75 F₀ / z)^(1/3)      ∝ z^(−1/3)     — α CANCELS EXACTLY
Q(z)  = F₀ / g'(z)               ∝ z^(+5/3)
g'(z) = F₀ / Q(z)                ∝ z^(−5/3)  ⇒  ΔT ∝ z^(−5/3)
```

**The three exponents are exact consequences of the conservation equations and
are independent of the entrainment coefficient `α`.** The radius law
`b = (6α/5) z` **does** carry `α`; `α` is therefore **REPORT-ONLY** and is
never graded.

**The closure choice, and the prediction it carries (R4).** Standard `kEpsilon`
is the conventional closure for free shear flow and carries the well-documented
**round-jet/plane-jet anomaly**: it mis-predicts the spreading rate of round
free-shear flows. **Registered prediction P1, before the run** (§9): that
deficiency will bias `α`, which is REPORT-ONLY, and will **NOT** move the
graded exponents `n_w`, `n_T`, `n_Q`. If `α` falls outside the published
0.11–0.13 range for pure plumes while the three exponents stay in band, **that
is P1 confirmed, not a failure.** If the exponents move instead, **P1 is wrong
and must be reported as wrong.**

## 3. Quantities

Three graded exponents, each obtained by ordinary least squares of
`ln(quantity)` on `ln(z − z₀)` over the §4 window, plus one report-only number.
For each graded exponent the comparator prints, always: the **fine-level
value** (the graded one), the **deviation** from the exact value, the **band
utilisation fraction**, the coarse and medium values, the triple state, the
observed order, the GCI at `Fs = 1.25`, and the **Richardson extrapolate as a
REPORTED number that no verdict is a function of** (R1).

| id | quantity | exact | status |
|---|---|---:|---|
| `n_w` | exponent of centreline `w(z)` | **−1/3 = −0.333333** | **GRADED** |
| `n_T` | exponent of centreline `ΔT(z) = T(z) − T_amb` | **−5/3 = −1.666667** | **GRADED** |
| `n_Q` | exponent of `Q(z) = ∫ 2πr w dr` | **+5/3 = +1.666667** | **GRADED** |
| `α` | `(5/6)·db/dz` from the fitted radius slope | 0.11–0.13 published, **no gate** | **REPORT-ONLY** |

**The extrapolate is computed with the CORRECT sign and said so here so that no
later reader can mistake it for the defective form**: with `e21 = f_med −
f_fine` and `den = r^p − 1`, the extrapolate is **`f_fine − e21/den`**, which is
identically `(r^p·f_fine − f_med)/(r^p − 1)`. `analyse_t8.py` **does not import**
`analyse_t1c.py` or `analyse_t3.py` and carries its own GCI routine for exactly
this reason (§12 S5).

## 4. Bands, and the fit window

**Frozen here, before any solver runs, and not derived from any run of this
case: ±0.05 absolute on each exponent.**

| id | band |
|---|---|
| `n_w` | **[−0.383333, −0.283333]** |
| `n_T` | **[−1.716667, −1.616667]** |
| `n_Q` | **[+1.616667, +1.716667]** |

These are **modelling-tolerance bands, not numerical-error bands.** MTT is an
asymptotic self-similar theory and a steady RANS plume is not obliged to
reproduce it to machine precision. ±0.05 is registered as the widest band that
still discriminates: it separates a plume from a **jet** (`n_w = −1`,
`n_Q = +1`) by **6.67 band widths** and from a **non-entraining column**
(`n_w = 0`) by **3.33 band widths** (§0, correcting the draft's "twelve").
**Band utilisation** is reported for every exponent as
`util = |value − exact| / 0.05`, so a reader sees how much of a loose band was
consumed (R2b).

**Fit window: `z/D ∈ [10, 25]`, i.e. `z ∈ [2.0 m, 5.0 m]` (R3).** 30 D in a
40 D domain is 75 % of the height and too close to the outlet to defend; 25 D
is 62.5 % and leaves 15 D of clear domain above the window.

**The cost of R3, registered up front rather than discovered at grading:**
`[10, 25]` spans `log₁₀(2.5) = 0.398` **decades**. That is **thin for a log-log
slope.** A 0.398-decade lever means a small systematic curvature in the profile
translates into a comparatively large slope error; the ±0.05 band is set wide
partly because of this. **This limitation is registered, not discovered.**
`[10, 30]` = 0.477 decades is retained as **control C5**, reported, never gated.

**Sampling stations, registered so that all three levels are fitted at the same
places:** `z/D = 10.0, 10.5, …, 25.0` — **31 stations at 0.5 D spacing**,
identical on every level, values obtained by linear interpolation in `z`
between the two bracketing axial cell-centre planes. C5 uses `z/D = 10.0 …
30.0`, **41 stations**. Using a mesh-independent station set keeps the number
and placement of fit points out of the grid triple.

**No band may be widened, narrowed or reinterpreted after the first solver
starts.**

## 5. Ladder

T-family, DC spine position 3, rung **T8**, entry arm. **Three grid levels at
refinement ratio `r = 2` exactly in both directions**, with **no grading
anywhere** — every level is obtained by doubling the divisions of every block
in both directions, so every coarse cell is split into exactly 2 × 2:

| radial block | `r` range (m) | c | m | f | Δr c / m / f (m) |
|---|---|---:|---:|---:|---|
| 1 (source) | 0.0 → 0.1 | 4 | 8 | 16 | 0.0250 / 0.0125 / 0.00625 |
| 2 | 0.1 → 0.4 | 12 | 24 | 48 | 0.0250 / 0.0125 / 0.00625 |
| 3 | 0.4 → 1.2 | 16 | 32 | 64 | 0.0500 / 0.0250 / 0.01250 |
| 4 | 1.2 → 2.4 | 8 | 16 | 32 | 0.1500 / 0.0750 / 0.03750 |
| **radial total** | | **40** | **80** | **160** | |
| axial (0 → 8.0 m) | | **160** | **320** | **640** | 0.0500 / 0.0250 / 0.01250 |
| **cells** | | **6,400** | **25,600** | **102,400** | |

The block boundary at `r = b₀ = 0.1 m` exists so that the **source patch edge
is an exact mesh face** at every level. Iteration counts **8,000 / 12,000 /
20,000**. GCI at **`Fs = 1.25`**.

**`CLAUDE.md` rule 5 binds without exception** and the gate can only turn a PASS
or GATE FAIL **into** NOT A RESULT, never the reverse. **No GCI is quoted when
the three values are not monotone.**

## 6. Decomposition seed

**Serial, 1 rank, no decomposition (R5)** — `nProcs = 1`, no `decomposeParDict`
is written, `decomposePar` is not run, and each solver is invoked directly
rather than through `mpirun`. **There is no partitioner and therefore no seed
to record.** *This field is recorded because the form requires it, not because
the value is in doubt.* Three single-rank cases running concurrently **is** the
shape Sanaa's concurrency directive asks for ("small single-core cases in
parallel batches of 8–12"); a parallel decomposition would put
partition-dependence inside a gate run for no benefit. If this rung is later
moved to a parallel batch that is a **new registration**, not an amendment.

## 7. Criteria

Per exponent, in this order, **no other order permitted**:

1. **all three levels iteratively converged** — last-two-checkpoint relative
   change `≤ 1e-6` on the field the exponent is built from — **and plateaued**;
   else **`NOT A RESULT`**;
2. **triple `CONVERGING`**; else **`NOT A RESULT`**, with both triples
   (`e21`, `e32`), the observed order and the ratio printed beside it;
3. **`PASS` if the FINE-LEVEL value lies inside its §4 band, else `GATE FAIL`
   (R1).** The **Richardson extrapolate is printed beside it as a REPORTED
   number and no verdict is a function of it.** GCI at `Fs = 1.25` is printed
   either way. **Deviation and band-utilisation fraction are printed either
   way (R2b).**

**Strict completion (`CLAUDE.md` rule 4) is required of every level before it
is read at all**: `rc = 0` **recorded to a `STATUS` file, not inferred from the
log**; an `End` line in `log.solve`; **last time == `endTime`**; fields
**`T U p_rgh alphat nut k epsilon`** present at `endTime` — **`epsilon`, not
`omega`, because the registered closure is `kEpsilon`**; `ExecutionTime` line
count == `endTime`; and **every one of those fields at `endTime` NEWER than the
case's own `0/T`** (the age guard). A level failing any clause is not read.

## 8. Cost, and a real cap

**Predicted 335.3 core-minutes total** — `c` **7.13**, `m` **42.81**, `f`
**285.40** — from a lab rate of **1.196e5 cell·steps/(core·s)** derived from
`K2bU3_L025` (11,600 cells × 1,918 steps in 3.100 core-minutes,
`verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_L025/COST.txt`).
Arithmetic, re-checked at freeze and exact:
`6,400 × 8,000 ÷ 1.196e5 = 428.1 core-s = 7.13 core-min`;
`25,600 × 12,000 ÷ 1.196e5 = 2,568.6 core-s = 42.81 core-min`;
`102,400 × 20,000 ÷ 1.196e5 = 17,123.7 core-s = 285.40 core-min`.
At **$0.0513/core-h** (owner-stated; the box cannot read its own billing) that
is **$0.287 — derived, not measured.**

**REGISTERED MISPREDICTION RISK (R6), named before the run.** The rate
`1.196e5 cell·steps/(core·s)` is borrowed from **`K2bU3_L025`, a TRANSIENT
PIMPLE case**, while **T8 is a STEADY SIMPLE-family run**. Per-step cost is
not the same between solver modes: a PIMPLE step carries outer correctors and
a SIMPLE step does not, and the two are not interchangeable units. **The
arithmetic above is exact; the RATE is the exposure.** This is the same error
shape that made T1b L4 miss its estimate by 31.4 % on a rate borrowed across a
mesh jump. The direction of the error is **not predicted here** — asserting a
direction would be inventing information — only that the rate is
cross-mode-borrowed and therefore the dominant term in the estimate's
uncertainty. This paragraph exists so that the §12 calibration row can
attribute the gap to **misprediction**, not absorb it.

**CAP: 15 / 80 / 500 core-minutes per level, 595 core-minutes total**
(9.92 core-h, **$0.509 derived**). The caps absorb **2.10× / 1.87× / 1.75×**
the prediction. **An overrun stops that level; it does not get a new budget.**

**The cap is enforced as `timeout = cap_core_min × 60 ÷ ranks`**, which at
1 rank is **900 s / 4,800 s / 30,000 s**. A wall-clock timeout is **not** a
core-minute cap and must never be registered as one; at `ranks = 1` the two
coincide numerically and that coincidence is the only reason the wall-clock
instrument is admissible here. A level killed by its cap is **`PENDING`**, a
right-censored measurement, **never `GATE FAIL`**.

**At completion**, the actual is compared with this prediction and lands as a
row in **`docs/COST_CALIBRATION.md`** stating the ratio actual/predicted and
attributing the gap (contention / waste / misprediction, waste named
separately), per `CLAUDE.md` rule 12. **A completion report without that
comparison is incomplete.**

## 9. Controls, the planted zero, and the registered prediction

**The planted zero (`CLAUDE.md` rule 3, non-negotiable).** This family has
already been caught with three unarmed readers
(`T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md`). `analyse_t8.py` **must**,
before it grades anything:

- copy the **fine** level's `endTime` `T` field to a temporary case;
- add **`PLANT = 1.234e-03 K`** to every cell in the **two axis-adjacent radial
  columns**, at every axial level, **in the copy on disk**;
- read the copy back **through the same reader that produces `ΔT(z)`**;
- require the centreline `ΔT` at **every one of the 31 registered stations** to
  shift by **exactly `PLANT`** (tolerance `1e-9 K`). The axis extrapolation of
  §12 S3 is `(9f₁ − f₂)/8`, so shifting both columns by `PLANT` shifts the
  extrapolated centreline value by `(9·PLANT − PLANT)/8 = PLANT` **exactly** —
  the expected response is analytic, not approximate;
- **REFUSE (exit 2) if it cannot see it.** A zero from a reader not shown able
  to see a non-zero is not evidence.

The **same** plant is applied to `U_z` and checked against the `w_c(z)` reader,
on the same terms and with the same refusal.

**Registered prediction P1 (R4), stated before the run.** `kEpsilon`'s
round-jet/plane-jet anomaly will **bias `α`** (REPORT-ONLY) and will **not move
`n_w`, `n_T`, `n_Q`**, because those are consequences of the conservation
equations and independent of `α`. **`α` outside 0.11–0.13 with the three
exponents in band = P1 CONFIRMED.** Exponents out of band = **P1 WRONG**, and
the comparator must say so in those words. P1 **arms no gate**; it is a claim
this rung places on the record so that the closure choice is testable rather
than preferential.

**Registered controls, each reported whichever way it falls:**

- **C1 — far-field quiescence.** Ambient `ΔT` at `r = 12 D` must be **< 1 %** of
  centreline `ΔT` at the same `z`, at every graded station, or the domain is too
  narrow and the row is **`NOT A RESULT`**. *(C1 is the one control that can
  gate; it tests whether the reference's own precondition holds.)*
- **C2 — buoyancy flux conservation.** `F(z) = ∫ 2πr w g' dr` must be conserved
  to **< 5 %** across the fit window, since MTT's derivation assumes it. A
  violation invalidates **the reference**, not the solver, and is reported in
  those words.
- **C3 — virtual origin.** `z₀` at each level, its spread across the three
  levels, the R² of the `b(z)` linear fit it comes from, and the three exponents
  **recomputed with `z₀ = 0`** — all **reported**, none gated.
- **C4 — jet discriminator.** The fitted `n_w` must sit further from `−1` than
  from `−1/3`, proving the fit can tell a plume from a jet. Reported with the
  two distances in band widths.
- **C5 — fit-window sensitivity (R3).** The three exponents are refitted over
  `z/D ∈ [10, 30]` (41 stations) and reported beside the graded `[10, 25]`
  values. **If the two windows disagree by more than one band width (0.10) on
  any exponent, that is DISCLOSED explicitly in the results.** C5 **is not a
  gate** and cannot move a verdict.

## 10. What this does not claim, stated before it runs

**This rung can reach `GATE REACHED` at best and can NEVER reach `HOLDS`.**
MTT is an **analytic** reference, and under Sanaa's ruling of 2026-08-25
(*"a. Uphold"*) an exact or analytic reference scores **V**, never **P**;
validation requires measured physical reality from a public primary with its
pre-registration on disk. **No such primary is held for T8** — measured plume
data of the Papanicolaou & List (1988) class is **NOT ON DISK** and is not
sought by this document. Matrix consequence, precisely: **cell C7
(`axisymmetric × buoyant-thermal`) moves from `NEVER RUN` to a graded `V`+`G`
cell with `P NONE`, and nothing in this rung is a claim about the world.**

**A PASS here is a JOINT code-plus-closure statement and is NOT a
code-verification claim (R2a).** A modelling-tolerance band of ±0.05 grades the
discretisation, the closure and the boundary treatment **together**; it cannot
separate them. Calling that "verified code" would be exactly the overstatement
this family has been caught in before, and this document forbids it in advance.
The GCI is the only numerical-error statement this rung makes, and it is
reported, not gated.

**This rung also does not claim:** anything about a stratified environment;
anything about a plume in cross-flow; any ranking of closures (only `kEpsilon`
is run, and P1 is a claim about `α`, not a comparison); anything about the near
field `z/D < 10`, which is outside the window by construction; or anything
about the transient. It creates, moves and retires **no** gate, threshold,
band, cap or label belonging to any other rung, and it touches **no** frozen
file.

---

## 11. Cross-references and the freeze set

**Superseded draft:** `T8_PREREGISTRATION_DRAFT.md`, commit `240502e2`, blob
`2adcf2ec` — **on disk, unedited.**

**Freeze set, committed at or before this file and hashed at analysis time
against the committed blob** (`CLAUDE.md` rule 2, third clause):

| path | role |
|---|---|
| `docs/campaigns/T-family/T8_PREREGISTRATION.md` | this document |
| `verification/runs/T-family/T8_runs/build_t8.py` | case builder; writes `0.orig/`, never `0/` |
| `verification/runs/T-family/T8_runs/analyse_t8.py` | the comparator — **the grading path, fixed at this commit** |
| `verification/runs/T-family/T8_runs/run_one_t8.sh` | launcher, arming guard, cap instrument |

## 12. Specifications the draft left open, registered here (pre-compute)

The draft did not fix these and a case cannot be built without them. Each is
registered **before** any solver runs.

**S1 — the lateral and top boundaries are OPEN; only the floor annulus is a
wall.** The draft §1 says "quiescent, unstratified, adiabatic-walled domain."
**That phrase is read here as a THERMAL condition, and the thermal condition is
kept: the floor annulus `r ∈ [b₀, R]` at `z = 0` is an adiabatic
(`zeroGradient` on `T`) no-slip wall.** The **far field `r = R` and the top
`z = H` are OPEN** — `p_rgh` `fixedValue 0` (the exact hydrostatic-ambient
condition for an unstratified Boussinesq environment at `TRef`, where
`rhok ≡ 1`), `U` `pressureInletOutletVelocity`, `T`/`k`/`epsilon`
`inletOutlet` with ambient inlet values. **This is disclosed rather than
inherited because it matters**: a no-slip lateral wall would forbid
entrainment, and a plume that cannot entrain cannot satisfy MTT. Registering a
closed lateral boundary would have been registering a guaranteed failure, and
this document declines to do that silently.

**S2 — the source is a `Γ₀ = 1` pure-plume source, and `α_nominal` touches no
gate.** With `Γ = 5 g' b / (8 α w²)`, a pure plume has `Γ = 1`, i.e.
`Ri₀ = g'₀ b₀ / w₀² = 8α/5`. Taking `α_nominal = 0.12` (**used ONLY to set the
source condition; it is not the graded `α`, it appears in no band and in no
gate**): `Ri₀ = 0.192`, and with `b₀ = 0.1 m`, `w₀ = 0.6 m/s`,
`g'₀ = 0.6912 m/s²`, `ΔT₀ = g'₀/(gβ) = 21.1376 K`, `T_source = 321.1376 K`,
`F₀ = π b₀² w₀ g'₀ = 1.30288e-02 m⁴/s³`. Source turbulence: `I = 5 %` →
`k₀ = 1.35e-03 m²/s²`, `ℓ = 0.07 D = 0.014 m` →
`ε₀ = Cμ^{3/4} k₀^{3/2}/ℓ = 5.8232e-04 m²/s³`. Ambient `k = ε = 1e-06`.
Source `Re₀ = w₀ D/ν = 8,000`; plume `Re` at `z = 20 D` is `≈ 5.2e3` — both
comfortably turbulent, which is what makes a RANS closure admissible at all.
**A source with `Γ₀ = 1` is pure from `z = 0`, so the virtual origin sits at
the source and no jet-length correction is needed** — but `z₀` is still refit
per level (C3) rather than assumed.

**S3 — how each quantity is extracted from the mesh, registered so that no
choice can be made after the numbers are seen.**
- **Centreline value at a station**: quadratic-in-`r` extrapolation to `r = 0`
  from the two axis-adjacent cell columns. Both columns lie in radial block 1
  with uniform `Δr`, so `r₂ = 3r₁` and the extrapolation is exactly
  **`f_c = (9 f₁ − f₂)/8`**. This is symmetry-consistent (`∂f/∂r = 0` on the
  axis), mesh-convergent, and — unlike "the first cell value" — not a
  mesh-dependent sampling location.
- **`Q(z)`**: `Q = SCALE · Σᵢ wᵢ Vᵢ / Δz` over the cells of the axial slab,
  restricted to the connected region from the axis out to the first radius
  where `w` changes sign. `SCALE = 2π / sin(5°) = 72.0928` converts the flat-
  sided 5° wedge to the full annulus; **the comparator asserts `SCALE` against
  the mesh's own total volume** and refuses on disagreement > 1e-6 relative.
- **`b(z)`**: top-hat radius from the flux moments, `b = Q / √(π M)` with
  `M = SCALE · Σᵢ wᵢ² Vᵢ / Δz`.
- **`ΔT(z)`**: centreline `T` by the same extrapolation, minus `TRef = 300 K`.

**S4 — `z₀` comes from the radius fit, and that is deliberate.** `z₀` is the
`x`-intercept of the ordinary least-squares line `b(z) = s(z − z₀)` over the
graded window; `α = (5/6)·s`. **`b` is REPORT-ONLY, so `z₀` carries no
circularity into the graded exponents** — it is not derived from `w`, `ΔT` or
`Q`, and so cannot be tuned to make any of their slopes come out right. The
R² of that fit and the exponents recomputed at `z₀ = 0` are both reported (C3).

**S5 — the comparator carries its own GCI routine and imports neither
`analyse_t1c.py` nor `analyse_t3.py`.** Both of those compute
`richardson = f_fine + e21/den` where `e21 = f_med − f_fine`; the correct
Richardson extrapolate is `f_fine − e21/den`. Under R1 nothing here is gated on
the extrapolate, so the defect could not be load-bearing even if inherited —
but inheriting a routine known to be wrong, in a file written after the defect
was recorded, is not something this rung will do. **`analyse_t8.py --selftest`
asserts the correct sign against a closed-form case.**

**S6 — comparator exit-code contract, answering `D522` for this rung.**
`D522` records this lab's own comparator exiting **0** on a rung with **zero
graded rows** — an honest printed summary with a dishonest exit code. That is
forbidden here, and the contract is registered before the run:

| exit | meaning |
|---:|---|
| **2** | **REFUSE** — strict completion unmet for any level, planted zero unseen, mesh/reader inconsistency, or `SCALE` assertion failed. Nothing is graded. |
| **1** | at least one registered row is **`GATE FAIL`** |
| **3** | **no `GATE FAIL`, but fewer than the three registered rows reached the band** — including the zero-graded-rows case. **Non-zero by construction.** |
| **0** | **all three** registered rows reached the band and **all** are `PASS` |

---

**Nothing in this rung has been sent, filed, submitted, uploaded, registered or
posted anywhere outside this box, and nothing in it may be
(`CLAUDE.md` rule 7).**
