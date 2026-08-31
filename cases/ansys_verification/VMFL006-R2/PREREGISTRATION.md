# VMFL006-R2 — PRE-REGISTRATION — Multicomponent Species Transport in Pipe Flow

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27–28 (index p. 27).**
Drafted by `ansys-lane-opus48` (Opus 4.8) on 2026-08-31, for the
`ansys-verification-supervisor` to freeze by sha before any graded compute (CLAUDE.md
rule 2). This document is the gate's entire evidentiary content: it fixes the reference,
the band, every constant, the grading path and the cost **before** the solver runs, so
the gate cannot have been chosen to fit an answer. Frozen file under CLAUDE.md rule 6.

**This is a NEW registration succeeding R1 — NOT an edit of R1.** R1's frozen package
(`cases/ansys_verification/VMFL006/`, freeze `e28a6a29`) is untouched, and its register
row **#49 `NOT A RESULT` STANDS**. R2 does not delete, re-label or soften it; a re-run
after a repair is a new row citing the old one (ANSYS_VERIFICATION_CHARTER §6).

## 0. Why R1 died, and why this is the best kind of failure to repair

R1's solve was **clean**. Every L3 station lay inside the 1 % band, worst
**0.091621 % at x = 0.10 m — 10.9× inside the band** (self-verified in this lane by
reading R1's L3 `postProcessing/mixCup_*` files on disk and applying the frozen
normalization against `REF_LAB`), on a `CONVERGING` triple (R1's supervisor recorded
p = 0.6770, GCI 0.032 % against a 1 % ceiling). **The physics was fine.** R1 graded
`NOT A RESULT` because its **convergence clause was JOINTLY UNSATISFIABLE** across the
family:

- **L1 and L2** drove the T residual to the **double-precision floor** (8.874106×10⁻¹⁵
  and 9.988851×10⁻¹⁵, self-verified from R1's `solverInfo.dat`) and went **exactly
  flat**, tripping R1's **NULL-RANGE refusal** — a plateau test whose log10 range is
  exactly zero read a fully-converged channel as a dead one.
- **L3** was **still descending at `endTime = 3000`** (1.837040×10⁻⁸, self-verified)
  and never reached `RES_FLOOR = 1×10⁻⁹`, tripping the floor limb.

**No level could satisfy both limbs.** The comparator refused (exit 2) rather than
degrade — the defect is in the **registration**, not the instrument. R2 repairs the
registration.

## 1. Case, reference and manual pages

| Field | Value | Source |
|---|---|---|
| Case | VMFL006-R2 — Multicomponent Species Transport in Pipe Flow | manual p. 27 |
| Reference source | W.M. Kays & M.E. Crawford, *Convective Heat and Mass Transfer*, 3rd ed., McGraw-Hill, pp. 126–134, 1993 | manual p. 27 |
| Reference kind | **ANALYTICAL, EXACT** — the Graetz series for the circular-tube constant-wall-composition problem | §2 |
| Ansys solver (context) | Ansys Fluent (`Species-diffusion.cas`) — this box has no Fluent; reproduced in OpenFOAM | charter §2 |
| Lab solver | `scalarTransportFoam` (OpenFOAM v2606), axisymmetric 5° wedge, momentum NOT solved | §2, §3 |
| Geometry | pipe radius R = 0.0025 m, length L = 0.1 m | manual p. 27 |
| Flow | fully developed laminar Poiseuille profile imposed at inlet, mean velocity 1 m/s; Re_D = 500, Sc = 0.6993006993 | manual p. 27, §2 |
| Gate quantity | mixing-cup average of the **normalized** mass fraction of species A, θ = (Y_wall − Y_A)/(Y_wall − Y_in), at ten axial stations 0.01…0.10 m | manual p. 28, Table .06.1 |

**Boundary composition (manual p. 27):** Y_A(inlet) = 0.5, Y_A(wall) = 0.9. Hence
`Y_IN = 0.5`, `Y_WALL = 0.9`, θ = (0.9 − Y_A)/(0.9 − 0.5).

**The manual's Results table (p. 28, Table .06.1) — CORROBORATION and CONTEXT ONLY,
never the gate:**

| x (m) | Target (4 dp) | Ansys Fluent | Ratio |
|---|---|---|---|
| 0.01 | 0.8225 | 0.8227 | 1.002 |
| 0.02 | 0.7308 | 0.7309 | 1.001 |
| 0.05 | 0.5469 | 0.5471 | 1.004 |
| 0.10 | 0.3555 | 0.3557 | 1.006 |

(All ten stations are in the comparator; four shown here.) The **Target** column is a
4-decimal transcription of the same closed form (rounding floor 1.406470×10⁻⁴ relative)
and is **corroboration only**; the **Fluent** column is **context only**. The gate is the
lab's own full-double-precision evaluation of the series (§3). At x = 0.01 m the lab
reference `REF_LAB[0] = 0.82218145775507556` agrees with the Target 0.8225 to −0.0387 %,
inside the manual's own rounding floor.

## 2. The physics, and why the reference is EXACT for this model

Fully developed laminar flow carries two species A and B in a circular tube, with
**identical fluid properties** — equal densities (ρ = 1 kg/m³), equal viscosities
(μ = 1.0×10⁻⁵ Pa·s), equal binary diffusivity (D_AB = 1.43×10⁻⁵ m²/s) — precisely so the
computed field can be compared with an analytical solution. With equal properties and
**no reaction**, the species conservation equation reduces **exactly** to a single
passive-scalar transport equation:

> div(ρ **u** Y_A) = div(ρ D_AB grad Y_A)

`scalarTransportFoam` solves exactly this (`div(phi,T) = laplacian(DT,T)`) with DT = D_AB;
the momentum equation is **not** solved (the parabola is imposed by `make_u_vmfl006.py`).
The exact solution is the Graetz series in τ = x·D_AB/(2 R² u_m), evaluated in this lab to
full double precision (§3). The only difference between the lab field and the reference is
therefore **discretisation error** — the residual a Roache triple bounds. This is the
ground for PASS-capability (§14). Sc = 0.6993006993 and Re_D = 500 are recorded; they gate
nothing.

## 3. The gate reference: lab-evaluated, two independent instruments

**Byte-identical to R1** (`graetz_reference_vmfl006.py` carried over unchanged; verified by
`cmp` against R1). `REF_LAB` (comparator L134–137) is the frozen gate reference, produced
by **instrument B** (shooting: vectorised RK4 + `brentq`), full double precision, and
reproduced at grade time by **instrument A** (finite-volume Sturm–Liouville,
`eigh_tridiagonal`, comparator `reference_reproduction()` L320), which shares no code, no
discretisation and no library routine with B. Frozen values:

```
REF_LAB = [0.82218145775507556, 0.7305062043265339,  0.65899626674118539,
           0.59893375759528111, 0.54670065061324469, 0.50036111562132735,
           0.45873436650210847, 0.42103757365934918, 0.38671790452501825,
           0.355363267178404]
```

Series truncation `REF_TRUNC_N_TERMS = 14` (L165): worst neglected tail 5.873210×10⁻²¹
relative at x = 0.01 m — below double precision, 1.70×10¹⁸× margin against the band.
Measured inter-instrument spread `REF_INSTRUMENT_SPREAD = 2.383599×10⁻⁶`, inside
`REF_REPRO_TOL = 1.0×10⁻⁵` (L142). This lane confirmed the reproduction runs green.

## 4. Levels and the TWO-DIRECTIONAL refinement — why this triple is entitled to Roache treatment

Three levels, refinement ratio **r = 2.0** (`RATIO`, L174), triple taken on station
x = 0.10 m (`TRIPLE_I = 9`, L195). **Byte-identical mesh family to R1** (case/ diff clean).

| Level | NX (axial) | NR (radial) | Cells = NX·NR | Cells vs coarser | Max AR (R1 checkMesh) |
|---|---|---|---|---|---|
| L1 (coarse) | 200 | 20 | **4 000** | — | 8.84 |
| L2 (medium) | 400 | 40 | **16 000** | **×4** | 8.75 |
| L3 (fine) | 800 | 80 | **64 000** | **×4** | 8.71 |

**BOTH NX and NR double at every level, so the cell count grows ×4 per level, not ×2, and
the maximum aspect ratio HOLDS at 8.84 / 8.75 / 8.71 rather than degrading.** This is the
geometric similarity a Roache triple requires: each cell halves in both x and r, so the
aspect ratio is fixed across levels. **This is exactly what VMFL038 R1 lacked** — its
triple refined in one direction only (Ny doubled, Nx fixed), cells grew ×2, aspect ratio
degraded 4→8→16, the triple diverged and no p or GCI was quotable, and that omission cost
this team a case earlier today. VMFL006-R2's ×4 growth with constant AR is stated here,
not left to be inferred, as the entitlement to Roache treatment under CLAUDE.md rule 5.
`run_vmfl006_r2.sh` L98–100 declares `NX=(200 400 800)`, `NR=(20 40 80)`; the launcher's
birth-certificate check (L149–150) and the comparator's completion clause (L591–594)
**both refuse** unless `cells == NX·NR` exactly at each level.

## 5. THE ONE SUBSTANTIVE CHANGE — a convergence clause SATISFIABLE across the whole range (the intellectual core of R2)

**One change per run.** Everything else carries over from R1 unless a reason forbids it
(§16 records what is byte-identical). This section is the reasoning, not a patch.

### 5.1 The principle the clause must embody

R1's clause conflated two distinct facts and made them jointly unsatisfiable. R2's clause
separates them:

1. **A residual at the double-precision floor and flat is CONVERGED, not stalled.** A
   plateau test whose log10 range is exactly zero must read that as **success**, never a
   null-range refusal. R1's L1/L2 — descended from O(1) to ~9×10⁻¹⁵ and locked bit-exact —
   are the archetype: the field has stopped moving, which *is* convergence.
2. **A level still descending at `endTime` has not converged and must not be graded as if
   it had** — but the honest fix for a level that needs more iterations is **more
   iterations, not a looser floor.**

### 5.2 What R2 changes — two coupled edits, and only two

**(a) `endTime` 3000 → 8000** (`run_vmfl006_r2.sh` L38; `ENDTIME_EXPECTED = 8000`,
comparator L224). **`RES_FLOOR` is UNCHANGED at 1×10⁻⁹** (L238) — the fix is iterations,
not a looser floor.

*Why 8000, and why it is essentially certain.* R2's L3 mesh and setup are **byte-identical**
to R1's, so R2's L3 residual trajectory for iterations 1–3000 is **deterministically the
same** as R1's measured one, then continues the established geometric descent. From R1's
`solverInfo.dat` (self-measured this lane) the asymptotic per-iteration reduction factor is
~0.994 (0.00214–0.00269 log10-decades/iter, **accelerating**). Taking the **slowest**
observed rate 0.00214 dec/iter as a conservative bound, from L3's it=3000 value
(1.837×10⁻⁸, log10 = −7.736):

- crosses `RES_FLOOR = 1×10⁻⁹` (log10 = −9) near **it ≈ 3591**;
- reaches the machine floor (~1×10⁻¹⁴) near **it ≈ 5927**.

At `endTime = 8000` the last `PLATEAU_WINDOW = 200` samples (it 7801–8000) sit **at the
machine floor** with ~2000 samples of margin — robust against a 2× slower-than-observed
rate. L1 (floor by it≈500) and L2 (floor by it≈1500) merely extend their existing flat
plateaus. There is essentially no prediction risk here: this is the same run, longer.

**(b) The NULL-RANGE refusal is replaced by a POSITIVE PROOF-OF-DESCENT** (comparator
`convergence()`, L624–742). The clause, in order — each REFUSES (exit 2) except the final
CONVERGED return:

1. `n < MIN_ITERS = 1000` → CANNOT_TELL (never a lenient pass).
2. `n < PLATEAU_WINDOW = 200` → refuse.
3. a non-positive residual in the window → unreadable, refuse.
4. **PROOF-OF-DESCENT / CHANNEL LIVENESS:** `peak = max` over the **whole run** must be
   `> RES_FLOOR`, else refuse. A live residual starts unconverged (O(1)) and **drops**; a
   channel at or below the floor for the entire run never demonstrated convergence, it
   *assumed* it. **This is the null-range refusal's INTENT expressed as a positive test**,
   so an exactly-flat plateau AT the floor is now CONVERGED while a dead channel is still
   refused.
5. **CONVERGENCE FLOOR:** `worst = max` over the **window** must be `≤ RES_FLOOR`, else
   refuse ("still descending or stalled high"). **This is the test that reads a zero-range
   plateau at machine precision as SUCCESS** — there is no null-range refusal, so a
   bit-exact flat window at or below the floor passes here.
6. **NOT GROWING:** the log10 second-half mean must not exceed the first-half mean, else
   refuse. On a bit-exact flat plateau the two are exactly equal, so this passes; it
   refuses only a window climbing back up.

Returns CONVERGED with `log10_ptp` (0.0 when bit-exact flat) and `flat_at_floor` REPORTED,
never gated.

### 5.3 Satisfiability PROVEN, not argued (a clause no real run can satisfy is worse than none)

Two proofs, both on **real bytes**:

**On R1's actual physics** (this lane, driving `grade_vmfl006_r2.convergence()` against R1's
on-disk `solverInfo.dat`): **R1's L1 grades CONVERGED** (n=3000, window max 8.874×10⁻¹⁵,
peak 1.0, log10_ptp 0.0, flat_at_floor True) — the exact case R1 wrongly refused; **R1's L2
grades CONVERGED** (window max 9.989×10⁻¹⁵, log10_ptp 0.0); **R1's L3 at 3000 REFUSES**
(window max 6.183×10⁻⁸ > floor, still descending) — correct, and the reason R2 raises
endTime.

**By a planted control** (`convergence_control()`, L744–894, run in `main()` and
`--selftest`), which writes synthetic `solverInfo.dat` files to disk and drives the
PRODUCTION `convergence()` path over the four cases the brief names plus three more, and
refuses if any mis-grades:

| synthetic case | shape | intended verdict | returned | cause |
|---|---|---|---|---|
| exactly-flat-at-machine-floor | descend → bit-exact 8.874e-15 (ptp 0) | CONVERGED | CONVERGED | — |
| cleanly-converged | descend → ~1e-11, small non-zero range | CONVERGED | CONVERGED | — |
| still-descending-at-endTime | window ~7e-7, descending | NOT A RESULT | REFUSED | floor |
| genuinely-stalled-at-high-residual | descend then flat at 1e-3 | NOT A RESULT | REFUSED | floor |
| never-descended (dead channel < floor) | flat 1e-12 throughout | NOT A RESULT | REFUSED | descent/liveness |
| growing under the floor | descend 1e-13 → climb 1e-10 (≤ floor) | NOT A RESULT | REFUSED | growing |
| too-few-iters | n = 999 | NOT A RESULT | REFUSED | CANNOT_TELL |

Each lands the intended verdict; the control additionally asserts the flat-at-floor case
reports `log10_ptp == 0.0` (proving the null-range refusal is truly gone) and the
cleanly-converged case reports a non-zero range. **The clause CAN return each outcome** —
that is the whole lesson of R1, discharged with controls rather than argument.

### 5.4 Strict completion (CLAUDE.md rule 4) — carried over, with the anchored-pattern trap named

`completion()` (L504–623) is unchanged from R1 except that `ENDTIME_EXPECTED` is now 8000.
`scalarTransportFoam` prints **no `ExecutionTime` line**, so the rule-4 clause-5 equivalent
— the count of `^Time = ` lines must equal `endTime` — is declared here, not improvised, as
R1 declared it and it held exactly (3000/3000 on R1's L1). **The anchored-pattern trap,
named:** a bare `Time = (\d+)` also matches the substring inside an `ExecutionTime = …`
line; the comparator anchors `re.findall(r"^Time = (\d+)", lt, re.M)` (L523-equivalent) so a
line starting with `E` cannot match. The `End` line is matched as `\nEnd`, never a bare
`End`. Exactly **two** numeric time directories per level (`0` and `endTime = 8000`) are
expected, selected numerically with a cardinality refusal (§10).

## 6. The gate quantity, the band, and every registered constant

**Gate:** for every one of the ten stations at L3, |θ_lab − REF_LAB| / |REF_LAB| ≤ `TOL`,
`TOL = 0.01` (relative, per station, at L3). θ_lab is the mixing-cup average read from the
`weightedAverage(T)` surfaceFieldValue with weight field φ at each station face zone.

| Constant | Value | Comparator line |
|---|---|---|
| `TOL` | 0.01 | L171 |
| `GCI_MAX` | 0.01 (= TOL) | L194 |
| `P_MIN` | 0.05 | L175 |
| `FS` | 1.25 | L173 |
| `RATIO` | 2.0 | L174 |
| `PLANT` | 1.234e-03 | L172 |
| `TRIPLE_I` | 9 (x = 0.10 m) | L195 |
| `ENDTIME_EXPECTED` | **8000** (was 3000 in R1) | L224 |
| `MIN_ITERS` | 1000 | L236 |
| `PLATEAU_WINDOW` | 200 (FIXED) | L237 |
| `RES_FLOOR` | 1.0e-09 (**unchanged from R1**) | L238 |
| `Y_IN` / `Y_WALL` | 0.5 / 0.9 | L169–170 |
| `REF_REPRO_TOL` | 1.0e-05 | L142 |
| `WEDGE_BIAS_WORST` | 8.0353e-04 | L222 |
| `WEDGE_FLUX` | 2.7236169608643178e-07 | L243 |
| `FLUX_REL_TOL` | 1.0e-06 | L244 |
| Solver / RANKS | `scalarTransportFoam` / 1 | launcher L36, L97 |
| `CAP_CORE_MIN` | 18 (unchanged) | launcher L37 |

**Why TOL = 0.01, and why R2 inherits it — read §12.** The band is set from the case's
agreement class (the manual's own Fluent-vs-Target ratios span 1.001–1.008, i.e. 0.1–0.8 %),
never from a run. It is **byte-identical to R1's frozen band** and is **not tightened** —
see §12 for why inheriting it unchanged is the correct and non-fitting choice.

## 7. The planted-zero control — at every level, BEFORE any clause that can refuse (CLAUDE.md rule 3)

`planted_zero()` (L896–931) plants `PLANT = 1.234e-03` into a **copy** of the mixing-cup
`.dat` row on disk, re-reads it through the same single-value parser the gate uses, and
**refuses (exit 2)** unless the reader moves by exactly PLANT. It is a fall-through refusal:
the only way it returns is to have seen the plant.

**RESTRUCTURED FOR R2 (`grade_levels()`, L1178):** the plant now fires at **every level
(L1, L2, L3) BEFORE the completion/convergence clauses that can refuse.** In R1 the plant
loop ran *after* the level loop, so R1's convergence refusal fired first and **the plant
never ran on the graded path**. The plant is a control on the READER — it operates on a
copy of one `.dat` row and is independent of whether the physics clauses pass — so it runs
first, and its firing is on the record regardless of any later refusal. All three levels
feed the Roache triple; L3 decides the band.

## 8. The AST no-assert guard, and interpreter-invariance

`ast_no_assert_guard()` (L288) parses the comparator's own source on disk and refuses
(exit 2) if any `assert` survives — `python3 -O` strips asserts, so every refusal is an
explicit `raise`. Proven to **fire** by the selftest (fed a constructed source containing an
assert). This lane confirmed: `--selftest` **55/55, 0 failures, rc 0 under BOTH `python3`
and `python3 -O`, stdout byte-identical between the two**; `mutation_test_vmfl006_r2.py`
**24/24** (now including mutation G, convergence floor defanged, and H, descent/liveness
defanged — both caught under both interpreters).

## 9. Live cross-instrument reference reproduction, 10. numeric time-dir selection

Both **carried over from R1 unchanged.** §9: `reference_reproduction()` (L320) re-evaluates
the ten reference values at grade time with instrument A and refuses unless the worst
disagreement against frozen `REF_LAB` (instrument B) is ≤ `REF_REPRO_TOL = 1×10⁻⁵`
(measured 2.383599×10⁻⁶). §10: `pick_time_dir()` (L369) selects numerically (`max(..., key=
float)`), never lexicographically, with a **cardinality refusal** (two dirs per level: `0`
and `endTime`; one per postProcessing station), matching the regex `^[0-9]+(\.[0-9]+)?$`,
never a `[0-9]*` glob (L-339).

## 11. The axisymmetric-wedge Clause-A bias — WITH ITS SIGN

Carried over from R1 (charter Amendment 1.4 Clause A). The 5° wedge's bias is **azimuthal**,
so no grid refinement removes it — invisible to the Roache triple, the GCI and every
convergence check, hence a setup obligation with the freeze as its deadline. **What does
NOT reach the gate:** the mixing cup is a ratio sum(φ·T)/sum(φ); the azimuthal area factor
sin(t)/t is constant in r, cancels exactly, and biases the gate by **zero** (N-AV9's
0.1269 % area deficit biases sum(φ), which the conservation control gates on purpose,
`WEDGE_FLUX = 2.7236169608643178×10⁻⁷`, `FLUX_REL_TOL = 1×10⁻⁶`). **What DOES reach it** is
only the arc/area ratio sec(t/2): θ_wedge(x) = θ_true(τ·sec(t/2)). **SIGN: NEGATIVE** (θ
biased LOW, growing with x); worst `WEDGE_BIAS_WORST = 8.0353×10⁻⁴` = **0.080353 %** at
x = 0.10 m, **12.45× margin** against the 1 % band. The clause binds disclosure, not the
tolerance; the band is unchanged and meetable on the wedge.

## 12. THE §11.2 BAND CAVEAT — RESTATED FOR R2, BOTH HALVES, NOT QUIETLY DROPPED

**R2 inherits R1's band, so it inherits R1's §12 caveat — and it is stated in full here, not
dropped.**

**Half one — the caveat, unchanged.** The comparator's `TOL = 0.01` was first *committed*
on 2026-08-31 (`6ad5d28b`), but the R1 comparator sat untracked on disk from 2026-08-26 and
a pre-freeze smoke ran on 2026-08-26. **Git therefore cannot prove the band predates the
first VMFL006 field produced on this box.** R2's band is byte-identical to R1's, so this
caveat rides with R2's register row exactly as it rode with R1's. R2 must **not** be cited as
a git-proven prediction-first freeze of the band; it is a re-freeze of an inherited band
carrying a disclosed, bounded gap.

**Half two — why R2 is STRONGER, stated precisely.** **R1 has now RUN.** Its measured worst
L3 station is **0.091621 %** against the 1 % band (self-verified this lane from R1's L3
`mixCup_*` files) — **the band is demonstrably 10.9× LOOSER than the achieved accuracy.** A
band 11× wider than the answer it must admit **cannot have been fitted in the favourable
direction**: gate-fitting bends a band toward the answer to secure a pass, and a band that
sits 11× outside the achieved deviation is the opposite motion. Inheriting it unchanged is
therefore not favourable-direction fitting. (R1's own §12 already showed the only pre-band
VMFL006 data on this box — the smoke — sat ~6.9 % off the reference, ~7 band-widths outside
a 1 % band, so a fitted band would have been *wider*, not tighter. R1's run now corroborates
that from the other side: the converged answer is 11× *inside*.)

**And the band is NOT tightened.** Seeing R1's 0.091621 % and then narrowing the band to,
say, 0.2 % would itself be gate-fitting — fitting *after* seeing the answer, in the
rigorous-looking direction. **A ceiling is the one the charter imposes (the agreement
class), never the most conservative available.** The band stays 0.01. This is a deliberate
refusal to fit, in either direction, recorded so a hostile auditor sees the choice was made
knowingly. **No section of this registration reaches the freeze with an open gate question
(§11.2).**

## 13. The outcomes named in advance

`verdict_for()` (L967) yields exactly one, in this order: **PASS** (triple CONVERGING, GCI ≤
GCI_MAX = 1 %, all ten stations within TOL = 1 % of REF_LAB); **GATE FAIL** (CONVERGING,
GCI ≤ 1 %, ≥ 1 station outside the band); **NOT A RESULT** (triple not CONVERGING, or p <
P_MIN, or GCI > GCI_MAX, or any completion/control/convergence/reproduction clause refuses,
or `RUN_RC.txt` absent → rc_unknown with physics still printed); **BLOCKED** (a
blockMesh/checkMesh/topoSet/solver crash — a crash is a finding, not a retry — a mesh
refusal, or the budget timeout rc 124). `PENDING` is the queue/display state only.

## 14. Verdict ceiling — PASS-CAPABLE (§11.1)

Unchanged from R1's reasoning. This registration declares a Roache triple and its reference
is **ANALYTICAL** — the exact solution of the same continuum model the solver discretises
(§2). Under `ANSYS_VERIFICATION_CHARTER` §11.1, `VERIFICATION_CHARTER` §2f.3's CONTINUUM cap
is the **NO-TRIPLE** ceiling and does not cap a limb that declares a triple returning
`CONVERGING`, graded by CLAUDE.md rule 5 step 3. §11.1 limit 3 caps an **EXPERIMENTAL**
reference; **this reference is analytical, not experimental**, so that limit does not bite.
This case does not invoke §2h and decides none of the questions §11.1 limit 2 / §2h.3 refer
to Sanaa. Precedent: register row #46 (VMFL069-R2, PASS), verification-team-audited
2026-08-31. **Verdict ceiling: PASS.**

## 15. Cost (CLAUDE.md rule 12) — EXTRAPOLATED from R1's MEASURED per-level cost, a BRACKET

**R2 has a measured anchor that R1 lacked: R1's own run.** R1 measured the whole three-level
case at **1.633 core-min** (L1 5 s / L2 18 s / L3 75 s at `endTime = 3000`, RANKS = 1). R2
raises `endTime` to 8000; per-level wall scales ~linearly in the iteration count for the
solve (the mesh-generation portion is fixed and does not scale), so this is an **IN-FAMILY
EXTRAPOLATION** (same case, same mesh, same solver, only the iteration ceiling changed) — no
cross-family transfer is claimed. Label: **EXTRAPOLATED**, not measured.

- **Linear-in-iterations upper** (whole per-level wall scaled by 8000/3000 = 2.667):
  L1 13.3 s / L2 48 s / L3 200 s → **261.3 s = 4.36 core-min.**
- **Solve-only-scales lower** (mesh-gen fixed, only the solve scales): ≈ **4.1 core-min.**
- **Contention allowance:** a ~1.3× busy-box factor on the upper → **≈ 5.7 core-min.**
- **BRACKET: ≈ 4.1 to 5.7 core-min; point estimate ≈ 4.4 core-min** for the whole
  three-level run.
- **Cap:** `CAP_CORE_MIN = 18`, **unchanged** (frozen in `run_vmfl006_r2.sh` L37). The point
  estimate is 24 % of the cap; even the pessimistic 5.7 core-min is 32 %. The launcher's
  per-level `timeout_s` is the operative guard (§16); at an 18 core-min running total, L3
  gets ~1000 s against a ~200 s expectation, a 5× margin for contention. An overrun **stops
  the run** (rule 12); it gets no new budget.
- **Dollars, DERIVED not measured** (the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER` §5): at $0.0513/core-h, ≈ **$0.0035 to $0.0049**. Trivially under
  the $25 pre-authorised ceiling; costed per item regardless (a blanket is not a per-item
  read, rule 9).
- **cost_basis:** owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22),
  REPORTED-BY-OWNER. **Actuals will be compared against this bracket at close-out** (rule 12
  calibration) and one row appended to `docs/COST_CALIBRATION.md`.

## 16. Grading path, freeze manifest, and what is byte-identical to R1

- **Comparator:** `cases/ansys_verification/VMFL006-R2/grade_vmfl006_r2.py` — the grading
  path, fixed at the freeze commit, verified at launch by `run_vmfl006_r2.sh`'s HEAD-blob
  check. Selftest 55/55 rc 0 under `python3` and `python3 -O`, byte-identical stdout; mutation
  24/24; no `__pycache__` at freeze.
- **Reference module:** `graetz_reference_vmfl006.py` — **BYTE-IDENTICAL to R1** (`cmp` clean).
- **Velocity writer:** `make_u_vmfl006.py` — **BYTE-IDENTICAL to R1** (`cmp` clean); a
  launcher-gated file.
- **Launcher:** `run_vmfl006_r2.sh` — differs from R1's only in `ENDTIME` (3000 → 8000), the
  three gated-file paths (→ VMFL006-R2), and header comments. `CAP_CORE_MIN = 18`, `RANKS = 1`,
  per-level age guard and budget timeout unchanged. **Runner-side cap enforcement is
  ADVISORY / INERT / OFF** (`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3`); the operative
  guard is the launcher's per-level `timeout_s`, and this registration makes **no `ENFORCE`
  claim** of the runner.
- **Mutation test:** `mutation_test_vmfl006_r2.py`.
- **Case inputs:** `case/**` — **BYTE-IDENTICAL to R1** (`diff -rq` clean, 8 files). `endTime`
  is substituted by the launcher via `__ENDTIME__`, so it is not carried in
  `controlDict.template`; the iteration-count change lives only in the launcher.

**Run root:** `verification/runs/ansys_verification/VMFL006-R2/` — verified **absent** at
freeze time (`test -e` recorded in the freeze commit message with a UTC timestamp). The
launcher's age guard is **per-level** (it checks `$RUN_ROOT/L1/0`, `.../L2/0`, `.../L3/0`,
not the root), so an empty run root created after the freeze does not consume the guard.

---

**Freeze declaration.** Every section above is decided; no section defers a gate, band,
threshold, cap, level, ceiling or label to a later decision (§11.2). The one honest gap — git
cannot prove the band predates the first field — is disclosed in full in §12, is stated with
both halves (including why R1's now-measured 10.9× margin makes inheriting the band
non-fitting), and is not an open question but a bounded risk carried into the register row.
The one substantive change from R1 — the convergence clause — is proven satisfiable in §5.3
on both R1's real data and synthetic controls. R1's frozen files are untouched; register row
#49 stands.
