# VMFL006 — PRE-REGISTRATION — Multicomponent Species Transport in Pipe Flow

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27–28 (index p. 27).**
Drafted by `ansys-lane-opus48` on 2026-08-31, for the `ansys-verification-supervisor`
to freeze by sha before any graded compute (CLAUDE.md rule 2). This document is the
gate's entire evidentiary content: it fixes the reference, the band, every constant,
the grading path and the cost **before** the solver runs, so the gate cannot have been
chosen to fit an answer. Frozen file under CLAUDE.md rule 6.

**Prediction-first status.** `git log --all` shows **no PREREGISTRATION.md has ever
existed for this case in any branch**; the only commit touching the case is `6ad5d28b`
("PROTECTIVE CAPTURE OF 44 UNTRACKED FILES — THIS IS NOT A FREEZE"). This is the first
freeze. **Read §12 before believing this is a clean prediction-first freeze — it is not,
and §12 says exactly why and what partly rescues it.**

---

## 1. Case, reference and manual pages

| Field | Value | Source |
|---|---|---|
| Case | VMFL006 — Multicomponent Species Transport in Pipe Flow | manual p. 27 |
| Reference source | W.M. Kays & M.E. Crawford, *Convective Heat and Mass Transfer*, 3rd ed., McGraw-Hill, pp. 126–134, 1993 | manual p. 27 |
| Reference kind | **ANALYTICAL, EXACT** — the Graetz series for the circular-tube constant-wall-composition problem, the closed form the source gives | §2 |
| Ansys solver (context) | Ansys Fluent (`Species-diffusion.cas`) — this box has no Fluent; the case is reproduced in OpenFOAM | charter §2 |
| Lab solver | `scalarTransportFoam` (OpenFOAM v2606), axisymmetric 5° wedge, momentum NOT solved | §2, §3 |
| Geometry | pipe radius R = 0.0025 m, length L = 0.1 m | manual p. 27 |
| Flow | fully developed laminar Poiseuille profile imposed at inlet, mean velocity 1 m/s; Re_D = 500, Sc = 0.6993006993 | manual p. 27, §2 |
| Gate quantity | mass-weighted (mixing-cup) average of the **normalized** mass fraction of species A, θ = (Y_wall − Y_A)/(Y_wall − Y_in), at ten axial stations 0.01…0.10 m | manual p. 28, Table .06.1 |

**Boundary composition (manual p. 27):** Y_A(inlet) = 0.5 uniform, Y_A(wall) = 0.9.
Hence `Y_IN = 0.5`, `Y_WALL = 0.9`, and the normalization θ = (0.9 − Y_A)/(0.9 − 0.5).

**The manual's Results table (p. 28, Table .06.1) — CORROBORATION and CONTEXT ONLY,
never the gate:**

| x (m) | Target (4 dp) | Ansys Fluent | Ratio |
|---|---|---|---|
| 0.01 | 0.8225 | 0.8227 | 1.002 |
| 0.02 | 0.7308 | 0.7309 | 1.001 |
| 0.03 | 0.6593 | 0.6594 | 1.002 |
| 0.04 | 0.5992 | 0.5993 | 1.002 |
| 0.05 | 0.5469 | 0.5471 | 1.004 |
| 0.06 | 0.5006 | 0.5007 | 1.002 |
| 0.07 | 0.4589 | 0.4591 | 1.004 |
| 0.08 | 0.4212 | 0.4215 | 1.007 |
| 0.09 | 0.3869 | 0.3872 | 1.008 |
| 0.10 | 0.3555 | 0.3557 | 1.006 |

The manual's **Target** column is a 4-decimal transcription of the same closed form and
is **corroboration only**; Ansys's **Fluent** column is **context only**. Neither is the
gate. The gate reference is the lab's own full-double-precision evaluation of the same
series (§2, §3). At x = 0.01 m the lab reference `REF_LAB[0] = 0.82218145775507556`
agrees with the manual's Target 0.8225 to **−0.0387 %**, inside the manual's own 4-dp
rounding floor (1.406470e-04 relative) — the corroboration holds.

## 2. The physics, and why the reference is EXACT for this model

Fully developed laminar flow carries two species A and B in a circular tube. Species A
enters at the inlet (Y_A = 0.5), species B enters from the wall (so Y_A = 0.9 at the
wall). **The manual states the fluid properties are identical for both species** — equal
densities (ρ = 1 kg/m³), equal viscosities (μ = 1.0×10⁻⁵ Pa·s), equal binary diffusivity
(D_AB = D_BA = 1.43×10⁻⁵ m²/s) — **precisely so that the computed field can be compared
with an analytical solution.**

With equal properties and **no reaction**, the species conservation equation reduces
**exactly** to a single passive-scalar transport equation:

> div(ρ **u** Y_A) = div(ρ D_AB grad Y_A)

`scalarTransportFoam` solves exactly this (`div(phi,T) = laplacian(DT,T)`), with `DT` =
D_AB = 1.43×10⁻⁵ m²/s and `phi` built from the imposed velocity. **The momentum equation
is not solved:** the fully developed parabolic profile the manual prescribes is imposed
exactly by `make_u_vmfl006.py`, so ν never enters the graded run. The problem is the
Graetz–Nusselt mass-transfer problem with a **constant-composition wall**, whose exact
solution in the Graetz coordinate τ = x·D_AB/(2 R² u_m) is the eigenfunction series

> θ(τ) = Σ_n G_n exp(−λ_n² τ) · (mixing-cup weighted eigenfunction)

evaluated in this lab to full double precision (§3).

**Why this makes the reference the exact solution of the SAME continuum model the solver
discretises.** The gate reference is not a benchmark from another code and not a
correlation: it is the closed-form solution of the identical continuum PDE
`scalarTransportFoam` discretises, under the identical geometry, boundary composition and
imposed velocity. Therefore the only difference between the lab field at a station and
the reference is **discretisation error** — the residual a Roache triple is built to
bound. This is the ground for PASS-capability (§14).

**Dimensionless numbers, recorded (they gate nothing):** Sc = ν/D_AB = 1e-5/1.43e-5 =
0.6993006993; Re_D = ρ·U_avg·2R/μ = 500 (laminar, as the manual states).

## 3. The gate reference: lab-evaluated, two independent instruments

`REF_LAB` (comparator lines 122–125) is the frozen gate reference, ten values at the ten
stations, produced by **instrument B** (shooting: vectorised RK4 + `brentq`), full double
precision. It is reproduced at grade time by **instrument A** (finite-volume
Sturm–Liouville, `eigh_tridiagonal`), which shares no code, no discretisation and no
library routine with B (§9). Frozen values:

```
REF_LAB = [0.82218145775507556, 0.7305062043265339,  0.65899626674118539,
           0.59893375759528111, 0.54670065061324469, 0.50036111562132735,
           0.45873436650210847, 0.42103757365934918, 0.38671790452501825,
           0.355363267178404]
```

**Series truncation, registered (comparator lines 141–155).** `REF_TRUNC_N_TERMS = 14`.
At the worst (smallest-x, slowest-converging) station x = 0.01 m the full neglected tail
(n = 14…59) is **5.873210×10⁻²¹ relative** = `REF_TRUNC_REL_WORST`. Carrying the series
from 14 to 60 terms moves θ(x=0.01) by one ULP. The truncation is **below double
precision** — "exact" here is measured, not asserted, at **1.70×10¹⁸× margin** against the
band. Measured inter-instrument spread (shooting vs finite volume) is
`REF_INSTRUMENT_SPREAD = 2.383599×10⁻⁶`, well inside the reproduction tolerance
`REF_REPRO_TOL = 1.0×10⁻⁵` (§9).

## 4. Levels and the TWO-DIRECTIONAL refinement — why this triple is entitled to Roache treatment

Three levels, refinement ratio **r = 2.0** (`RATIO`), taken on station x = 0.10 m
(`TRIPLE_I = 9`, the last of the ten):

| Level | NX (axial) | NR (radial) | Cells = NX·NR | Cells vs coarser |
|---|---|---|---|---|
| L1 (coarse) | 200 | 20 | **4 000** | — |
| L2 (medium) | 400 | 40 | **16 000** | **×4** |
| L3 (fine) | 800 | 80 | **64 000** | **×4** |

**BOTH NX and NR double at every level, so the cell count grows ×4 per level, not ×2.**
Verified against the frozen mesh generator: `run_vmfl006.sh` lines 99–100 declare
`NX=(L1 200 L2 400 L3 800)` and `NR=(L1 20 L2 40 L3 80)`; line 127 substitutes both into
`blockMeshDict.template`; the launcher's birth-certificate check (lines 149–150) and the
comparator's completion clause (`grade_vmfl006.py` lines 591–594) **both refuse** unless
`cells == NX·NR` exactly at each level. NX stays a multiple of 10 so a mesh **face** sits
exactly on each of the ten gate stations at every level.

**Why this section exists, stated so a hostile reader sees the trap avoided.** An hour
before this freeze, VMFL038 graded `NOT A RESULT` because its triple refined in **one
direction only** (Ny doubled, Nx fixed): cells grew ×2 per level, aspect ratio degraded
4→8→16, the triple diverged at R = 9.05, and **no p and no GCI were quotable at all**.
VMFL006 does not repeat that error: refining both directions by 2 keeps the cell aspect
ratio **fixed across levels** (each cell halves in both x and r), which is the geometric
similarity a Roache triple requires. The ×4-per-level growth and the fixed aspect ratio
are the reason this triple is entitled to Roache treatment under CLAUDE.md rule 5, and
they are stated here rather than left to be inferred.

## 5. Strict completion clause (CLAUDE.md rule 4) — with the anchored-pattern trap named

There is **no residualControl** in this case (`fvSolution`): every level runs the frozen
`endTime = 3000` (`ENDTIME_EXPECTED`) iterations of a `steadyState` solve (deltaT = 1),
so "last time == endTime" is met literally on every level and the cost of every level is
known at freeze time. `scalarTransportFoam` prints **no `ExecutionTime` line**, so the
equivalent iteration-count clause is used and is declared here, not improvised. The
comparator (`completion()`, lines 481–598) refuses (exit 2) unless **all** of:

1. `RUN_RC.txt` present and `rc == 0` (an absent `RUN_RC.txt` → `rc_unknown` → NOT A
   RESULT, printing every physics number; a bookkeeping loss does not un-run the solver,
   L-342);
2. an `End` line present (`\nEnd`);
3. `endTime` in `system/controlDict` equals `ENDTIME_EXPECTED = 3000`;
4. the log's **last** `Time = N` line has N == endTime;
5. the **count** of `Time = N` lines == endTime (the ExecutionTime-count equivalent);
6. exactly **two** numeric time directories at the level (`0` and `endTime`), the newest
   selected numerically and equal to endTime (§10);
7. fields `T`, `U`, `phi` present at endTime (X or X.gz);
8. **age guard:** `T` and `U` at endTime strictly newer than `0/T` (0/T is touched last
   at launch, so it dates the run allowed to produce the answer);
9. a mesh `birth_certificate.json` present, `mesh_ok` true, `cells == NX·NR`.

**THE ANCHORED-PATTERN TRAP, NAMED (brief's requirement).** A bare regex `Time = (\d+)`
matches the substring inside an `ExecutionTime = …` line as well, which would inflate both
the last-time reading and the count. The comparator defends against this by anchoring:
`re.findall(r"^Time = (\d+)", lt, re.M)` (line 523) requires `Time` at the **start of a
line** (`^` under `re.M`), so `ExecutionTime = ` — whose line starts with `E`, not `T` —
cannot match. This case's solver happens not to emit `ExecutionTime` lines, but the
anchoring is the load-bearing defence and is stated so no future reader loosens it to an
unanchored pattern. The `End` line is likewise matched as `\nEnd`, not a bare `End`.

**Iterative convergence (`convergence()`, lines 601–650), PHYSICS-CRITICAL:** measured on
the T residual channel from the `residuals`/`solverInfo` function-object file, over a
**FIXED** window `PLATEAU_WINDOW = 200` samples (never a fraction of the run, so it cannot
loosen when endTime changes); fewer than `MIN_ITERS = 1000` iterations → CANNOT_TELL, never
a lenient pass; a null-range (dead-channel) series is refused; a growing series is rejected;
`RES_FLOOR = 1.0×10⁻⁹` is the absolute floor T_initial must sit at or below across the
window. T is the only equation solved, so the clause gates on T and nothing else (L-338).

## 6. The gate quantity, the band, and every registered constant

**Gate:** for every one of the ten stations at L3 (fine), |θ_lab − REF_LAB| / |REF_LAB| ≤
`TOL`, with `TOL = 0.01` (relative, per station). θ_lab is the mixing-cup average
θ = (Y_WALL − ⟨T⟩_φ)/(Y_WALL − Y_IN) read from the `weightedAverage(T)` surfaceFieldValue
with weight field φ at each station face zone.

**Every registered constant, transcribed from the frozen comparator (never invented):**

| Constant | Value | Meaning / comparator line |
|---|---|---|
| `TOL` | 0.01 | frozen band, relative, every station, at L3 (L159) |
| `GCI_MAX` | 0.01 | fine-grid GCI ceiling, = TOL (L182) |
| `P_MIN` | 0.05 | observed-order floor (L163) |
| `FS` | 1.25 | Roache safety factor (L161) |
| `RATIO` | 2.0 | grid refinement ratio (L162) |
| `PLANT` | 1.234e-03 | planted-zero perturbation (L160) |
| `TRIPLE_I` | 9 | Roache triple station index (x = 0.10 m) (L183) |
| `ENDTIME_EXPECTED` | 3000 | frozen iteration count (L212) |
| `MIN_ITERS` | 1000 | below → CANNOT_TELL (L213) |
| `PLATEAU_WINDOW` | 200 | FIXED convergence window (L214) |
| `RES_FLOOR` | 1.0e-09 | absolute residual floor (L215) |
| `Y_IN` | 0.5 | inlet mass fraction, manual p.27 (L157) |
| `Y_WALL` | 0.9 | wall mass fraction, manual p.27 (L158) |
| `REF_REPRO_TOL` | 1.0e-05 | cross-instrument reproduction tol (L130) |
| `REF_TRUNC_N_TERMS` | 14 | series truncation (L153) |
| `WEDGE_ANGLE_DEG` | 5.0 | wedge total angle (L201) |
| `WEDGE_BIAS_WORST` | 8.0353e-04 | worst θ bias magnitude, x=0.10 m (L210) |
| `WEDGE_FLUX` | 2.7236169608643178e-07 | flat-wedge flow rate (L220) |
| `FLUX_REL_TOL` | 1.0e-06 | conservation-control tolerance (L221) |
| Solver | `scalarTransportFoam` | run_vmfl006.sh L178 |
| `CAP_CORE_MIN` | 18 | running-total budget cap (run_vmfl006.sh L33) |
| `RANKS` | 1 | serial (run_vmfl006.sh L32) |

**Why TOL = 0.01 and why it was not fitted.** The band is set from the case's agreement
class, not from a run. The manual's own Ansys-vs-Target agreement (Ratio column) spans
1.001–1.008, i.e. Fluent itself sits 0.1–0.8 % off the reference on this case; a 1 %
band is of that class. **The band's provenance and the one honest gap in the freeze are
in §12, headed for a hostile auditor — read it.** The comparator's `TOL = 0.01` line is
byte-identical in content between `HEAD` (`6ad5d28b`) and the working tree being frozen
here: the band did not move when the comparator's verdict ceiling was raised from
`GATE REACHED` to `PASS`.

## 7. The planted-zero control — at every level (CLAUDE.md rule 3)

`planted_zero()` (lines 700–733) plants `PLANT = 1.234e-03` into a **copy** of the
mixing-cup `.dat` row on disk, re-reads it through the same single-value parser the gate
uses, and **refuses (exit 2)** unless the reader moves by exactly PLANT (|delta − PLANT| >
1e-12 → refuse). The reader is a single-value parser on one `.dat` row, so the plant is
undiluted and the reader delta equals the plant exactly. It is a **fall-through refusal**:
the only way the function returns is to have seen the plant. `grade_levels()` runs this
control at **every graded level (L1, L2, L3)** before any level's value is trusted, so a
zero-reading reader cannot certify any level. A comparator without a fired plant has
produced no number.

## 8. The AST no-assert guard

`ast_no_assert_guard()` (lines 265–290) parses the comparator's **own source on disk**
and refuses (exit 2) if any `assert` statement survives anywhere in it. `python3 -O`
strips every `assert`, so a control written as an assert vanishes in exactly the mode
someone reaches for to grade faster; this guard reads the bytes rather than trusting a
docstring. It is proven to **fire** (not merely pass) by the selftest, which feeds it a
constructed source containing an assert. The verdict-vocabulary check (line 824) and the
planted-zero refusal are likewise explicit `raise`, never asserts. Confirmed by this lane:
selftest passes under **both** `python3` and `python3 -O` (rc 0, "SELFTEST: all checks
passed").

## 9. Live cross-instrument reference reproduction (at grade time)

`reference_reproduction()` (lines 297–339) re-evaluates the ten reference values at grade
time using **instrument A** (finite-volume Sturm–Liouville, ~0.11 s) and refuses (exit 2)
unless the worst relative disagreement against the frozen `REF_LAB` (instrument B,
shooting) is ≤ `REF_REPRO_TOL = 1.0×10⁻⁵`. Instrument A shares no code, no discretisation
and no library routine with instrument B, so this catches a mistyped constant, bit-rot, or
a reference silently edited to fit an answer, in a tenth of a second. Confirmed by this
lane: `graetz_reference_vmfl006.py` run standalone reproduces `REF_LAB` (shooting matches
to the printed digits; finite volume agrees within the measured 2.383599×10⁻⁶ spread).

## 10. Numeric time-directory selection with cardinality refusal

`pick_time_dir()` (lines 346–387) selects a time directory **numerically** (`max(..., key=
float)`), never lexicographically — lexicographic ordering puts '900' after '1500' and
'0.5' after '0.05', which would grade a half-time field as the answer. It carries a
**cardinality refusal**: this case runs one detached solver per level to endTime with no
restart path, so exactly the expected count of numeric time directories must be present
(**two** at a level: `0` and `endTime`), and anything else refuses rather than "picking the
newest" of an unexpected set. The completion clause additionally requires the chosen
directory to **equal** endTime and to agree with the log's last Time. Time directories are
matched by the regex `^[0-9]+(\.[0-9]+)?$`, never a `[0-9]*` glob (which also matches
`0.orig`, L-339).

## 11. The axisymmetric-wedge Clause-A bias — WITH ITS SIGN

Per `ANSYS_VERIFICATION_CHARTER` Amendment 1.4 Clause A, the 5° wedge's geometric bias is
stated **before** the freeze, with its sign and magnitude, in the error budget. It is
**azimuthal**, so no grid refinement removes it: it is invisible to the Roache triple, the
GCI, and every convergence check — hence a setup obligation with the freeze as its
deadline.

**What does NOT reach the gate, and this is the half easy to get wrong.** The graded
quantity is a **mixing-cup ratio** sum(φ·T)/sum(φ). On a flat wedge the azimuthal area
factor sin(t)/t is constant in r, so it multiplies numerator and denominator alike and
**cancels exactly**. N-AV9's area deficit — sin(t)/t = **0.1268756046250763 %** at
t = 5° — therefore biases sum(φ) (the conservation control gates that against the flat
value on purpose, `WEDGE_FLUX = 2.7236169608643178×10⁻⁷`, `FLUX_REL_TOL = 1×10⁻⁶`) but
biases **the gate by exactly zero**.

**What DOES reach the gate** is only the arc/area **ratio** sec(t/2): each radial-diffusion
face area divided by its cell volume is scaled by sec(t/2), so the effective Graetz
coordinate is τ·sec(t/2) and θ_wedge(x) = θ_true(τ·sec(t/2)). The resulting bias on the
graded quantity is:

- **SIGN: NEGATIVE.** θ is biased **LOW**, and the magnitude grows with x.
- Worst magnitude `WEDGE_BIAS_WORST = 8.0353×10⁻⁴` = **0.080353 %** at x = 0.10 m.
- Per-station (`WEDGE_BIAS_ON_THETA`, lines 207–209): −1.2559e-04, −2.0684e-04,
  −2.8164e-04, −3.5451e-04, −4.2720e-04, −5.0053e-04, −5.7483e-04, −6.5016e-04,
  −7.2644e-04, −8.0353e-04.
- Margin against the 1 % band at the worst station: **12.45×**.

The clause binds **disclosure, not the tolerance**: the band is unchanged. The bias is
disclosed at 0.080353 % against a 1 % band with 12.45× margin, so the band is meetable on
the wedge and the obligation is discharged by this statement.

## 12. THE SUPERVISOR'S §11.2 RULING — READ THIS, HOSTILE AUDITOR: THIS FREEZE CANNOT PROVE THE BAND PREDATES THE FIRST VMFL006 FIELD ON THIS BOX

**This section is the supervisor's ruling, made before the freeze and going in as a
numbered section, not a footnote. It states the one honest gap in this freeze plainly.**

**The gap.** The comparator's `TOL = 0.01` was first **committed** on 2026-08-31
(`6ad5d28b`, the protective capture). But the comparator file sat **untracked on disk from
2026-08-26**, and a pre-freeze smoke test ran on 2026-08-26
(`cases/ansys_verification/VMFL006/prefreeze_smoke/`). **Therefore git cannot prove the
band predates the first VMFL006 field produced on this box, and this registration says
exactly that rather than implying a freeze it does not have.** The freeze's normal
evidentiary content — "the gate could not have been chosen to fit the answer, because it
was committed before any field existed" — is **weakened here**: the earliest field predates
the earliest commit of the band.

**What partly rescues it — stated as an argument, NOT as proof:**

1. **The smoke is not a converged reading of anything.** It ran to `Time = 20` of the
   graded `endTime = 3000` — **0.6667 %** of the graded iteration count (smoke mode sets
   endTime = 20; `prefreeze_smoke/L1/RUN_RC.txt` records `endTime = 20`, `rc = 0`,
   `wall_s = 0`).

2. **The smoke's own value is nowhere near the reference — computed here, not asserted.**
   The raw station value at x = 0.01 m is `T = 0.5485797239364`
   (`prefreeze_smoke/L1/postProcessing/mixCup_x01/0/surfaceFieldValue.dat`,
   `weightedAverage(T)`, weight field φ). Applying the comparator's own normalization
   θ = (Y_WALL − T)/(Y_WALL − Y_IN) = (0.9 − 0.5485797239364)/(0.9 − 0.5) =
   **0.878550690159**, and comparing against `REF_LAB[0] = 0.82218145775507556`:

   > relative deviation = (0.878550690159 − 0.82218145775507556) / 0.82218145775507556
   > = **0.0685606 = 6.8561 %**, which is **6.856 band-widths** outside the 1 % band.

   The only VMFL006 data that existed on this box before the band was committed sat **~6.9 %
   off the reference — about seven full band-widths outside a 1 % band.** It is not a
   plausible thing to fit a 1 % band *to*.

3. **A band fitted to that data would have been WIDER, not tighter.** Fitting a gate to the
   only available data would have made the gate **easier** to pass — a band around a value
   that misses by 6.9 % is a band of order several percent, or one deliberately loosened.
   The frozen band is 1 %, which is **harder** than anything the smoke could justify.
   Gate-fitting bends a band toward the answer to *secure a pass*; a band set tighter than
   the only data on hand is the opposite motion. **This does not prove the band was not
   fitted; it proves that if it was, it was fitted in the direction that costs the case,
   which is not what gate-fitting is.**

**Residual risk, stated plainly.** Git's timeline cannot exclude that the value 0.01 was
chosen with knowledge of some later, more-converged VMFL006 field that is not on disk and
left no commit. Nothing on this box demonstrates such a field existed; the register row
this freeze produces must carry this section's caveat and must **not** be cited as a clean
prediction-first freeze. This is the honest floor: the freeze is legitimate as a
first-freeze whose band is anti-fitted by the argument above and corroborated by the
manual's own agreement class (§6), but it is **not** a git-proven prediction-first freeze,
and the row says so.

*(This lane confirms the arithmetic of point 2 independently: θ = 0.878550690159, deviation
= 6.8561 % = 6.856 band-widths. The supervisor's estimate "~6.9 %, about seven
band-widths" holds. The arithmetic supports the ruling; it is not stopped.)*

## 13. The four possible outcomes, named in advance, with the verdict each yields

The comparator's single verdict path (`verdict_for()`, lines 771–826) yields exactly one
of these, decided in this order:

1. **PASS** — the L3 triple returns `CONVERGING` (rule 5 step 3), the fine-grid GCI ≤
   `GCI_MAX = 1 %`, **and** all ten stations lie within `TOL = 1 %` of `REF_LAB`. This is a
   credential (§14).
2. **GATE FAIL** — triple `CONVERGING`, GCI ≤ 1 %, but **at least one** station outside the
   1 % band. A finding, printed with the offending station(s), value, reference and band.
3. **NOT A RESULT** — any of: the triple is not `CONVERGING` (DIVERGENT / STAGNANT /
   OSCILLATORY / EXACT, or observed order p < `P_MIN = 0.05`), in which case **no GCI is
   quoted**; **or** the triple is `CONVERGING` but the fine-grid GCI **exceeds** `GCI_MAX =
   1 %` (an uncertainty may not exceed the band it qualifies — this ceiling can only turn a
   PASS/GATE FAIL *into* NOT A RESULT, never the reverse, rule 5); **or** any completion,
   control or reproduction clause refuses; **or** `RUN_RC.txt` is absent (`rc_unknown`,
   L-342 — physics numbers still printed).
4. **BLOCKED** — the solver or launcher cannot produce a gradeable field at some level: a
   `blockMesh`/`checkMesh`/`topoSet`/`scalarTransportFoam` crash (a crash is a finding, not a
   retry), a mesh-cell refusal, or the budget timeout `rc = 124` (`CAP_CORE_MIN` fired; rule
   12 gives it no new budget). No gradeable field exists, so no PASS/FAIL is available.

`PENDING` is the queue/display state only (not yet run). No outcome softens a GATE FAIL to
PENDING, and the register records whichever of the above lands, whatever it is.

## 14. Verdict ceiling — PASS-CAPABLE (§11.1), and its justification

This registration declares a Roache triple, and its reference is **ANALYTICAL** — the exact
solution of the same continuum model the solver discretises (§2). Under
`ANSYS_VERIFICATION_CHARTER` §11.1, `VERIFICATION_CHARTER` §2f.3's CONTINUUM cap
("`GATE REACHED` maximum, `PASS` unavailable") is the **NO-TRIPLE** ceiling: it does not cap
a limb that declares a triple returning `CONVERGING`, which is graded by CLAUDE.md rule 5
step 3. §11.1 limit 3 caps an **EXPERIMENTAL** reference at `GATE REACHED` even on a
converging triple; **this reference is analytical, not experimental, so that limit does not
bite.** This case does **not** invoke §2h (the no-triple floor-demonstration clause) and
claims to decide none of the questions §11.1 limit 2 / §2h.3 refer to Sanaa. Precedent:
register row #46 (VMFL069-R2, PASS), which the verification team audited on 2026-08-31 and
upheld. **Verdict ceiling: PASS.**

## 15. Cost (CLAUDE.md rule 12) — EXTRAPOLATED, a BRACKET, no measured anchor

**There is NO measured VMFL006 cost.** The pre-freeze smoke's `COST.txt` records
`total_wall_s = 0`, `total_core_min = 0.0` (endTime = 20 completed in under one integer
second, unresolved), so it anchors nothing beyond "L1 at 20 steps takes < 1 s". The figure
below is **EXTRAPOLATED** from cell counts and a justified throughput, given as a bracket.

- **Cell-steps (deterministic, from the frozen levels and endTime):**
  (4 000 + 16 000 + 64 000) cells × 3 000 iterations = **2.52×10⁸ cell-steps.**
- **Assumed single-core throughput** for a `steadyState` scalar-transport solve — one T
  equation per iteration, `smoothSolver`/`symGaussSeidel`, `nSweeps 2`, `relTol 0.01`,
  small laminar mesh — **between 5×10⁵ and 5×10⁶ cell-steps per second per core.** The upper
  end is a well-cached few-sweep solve; the lower end allows cache pressure and box
  contention. This is an assumption, not a measurement.
- **Resulting bracket (RANKS = 1, so core-min = wall_s/60):**
  - fast (5×10⁶): 50.4 s wall → **0.84 core-min**;
  - slow (5×10⁵): 504 s wall → **8.4 core-min**.
  - **BRACKET: ≈ 0.8 to 8.4 core-min for the whole three-level run.**
- **Cap:** `CAP_CORE_MIN = 18`, unchanged (frozen in `run_vmfl006.sh`). Even the pessimistic
  8.4 core-min is 47 % of cap; the cap's per-level `timeout_s` fires only if throughput falls
  below **2.33×10⁵ cell-steps/s** (≈ 2.4× worse than the pessimistic assumption) — the margin
  a contended box needs. An overrun **stops the run** (rule 12); it gets no new budget.
- **Dollars, DERIVED not measured** (the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER` §5): at $0.0513/core-h, ≈ **$0.0007 to $0.0072**. Trivially under
  the $25 pre-authorised ceiling.
- **cost_basis:** owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22),
  REPORTED-BY-OWNER, not measured. **Actuals will be compared against this bracket at
  close-out** (rule 12 calibration) and one row appended to `docs/COST_CALIBRATION.md`.

**What is assumed, restated for the calibration row:** the throughput window 5e5–5e6
cell-steps/s/core, serial execution (RANKS = 1), and that all three levels run to
completion. If any level times out, the recorded actual is the partial spend to that point
and the verdict is NOT A RESULT / BLOCKED per §13.

## 16. Grading path and freeze manifest

- **Comparator:** `cases/ansys_verification/VMFL006/grade_vmfl006.py` — the sha committed
  by this freeze is the grading path (fixed at this commit, verified at launch by
  `run_vmfl006.sh`'s HEAD-blob check). Selftest 47/47 rc 0 under `python3` and `python3 -O`;
  mutation test 18/18 rc 0; no `__pycache__` at freeze.
- **Reference module:** `graetz_reference_vmfl006.py` (instruments A and B).
- **Launcher:** `run_vmfl006.sh` (`CAP_CORE_MIN = 18`, `RANKS = 1`, per-level age guard and
  budget timeout). **Runner-side cap enforcement is advisory/inert** per
  `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3`; the operative guard is the launcher's
  per-level `timeout_s`, not any runner cap.
- **Velocity writer:** `make_u_vmfl006.py` (imposes the parabola; checked by the launcher's
  freeze gate).
- **Mutation test:** `mutation_test_vmfl006.py`.
- **Case inputs:** `case/0/T`, `case/constant/{transportProperties,physicalProperties}`,
  `case/system/{controlDict.template,blockMeshDict.template,fvSolution,fvSchemes,topoSetDict}`.

**Run root:** `verification/runs/ansys_verification/VMFL006/`. Verified **absent** at
freeze time (`test -e` recorded in the freeze commit message). The launcher's age guard is
**per-level** (it checks `$RUN_ROOT/L1/0`, `.../L2/0`, `.../L3/0`, not the root), so an
empty run root created after the freeze does not consume the guard.

---

**Freeze declaration.** Every section above is decided; no section defers a gate, band,
threshold, cap, level, ceiling or label to a later decision (§11.2). The one honest gap —
git cannot prove the band predates the first field — is disclosed in full in §12 and is not
an open question but a stated, bounded risk carried into the register row.
