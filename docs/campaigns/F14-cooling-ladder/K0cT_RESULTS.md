# K0c turbulent rung — executed. GATE FAIL against a real experiment

Executed 2026-08-18 against `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2,
which was written first, by a different agent, at zero compute. **Nothing in this
document edits that specification.** Every reference value and every pass band was
parsed out of it by `K0cT_runs/analyse_k0ct.py` at run time; the analyser holds no
reference number of its own and exits 2 if the specification will not parse.

This is the campaign's first comparison against **primary experimental data the
lab did not produce**: ERCOFTAC Classic Collection Case 079, Betts and Bokhari, a
2.18 × 0.076 × 0.52 m tall differentially heated cavity at Ra 0.86e6 and 1.43e6,
22 data files committed under `reference-data/betts_bokhari/` with the archive
SHA-256 in the manifest.

---

## Verdict

**GATE FAIL. 8 of 18 graded rows failed.**

| | |
| --- | --- |
| Core stratification S, hi Ra | solve **0.2353** against reference **0.095**, deviation **0.140** on a band of **0.05** — **FAIL** |
| Core stratification S, lo Ra | solve **0.2209** against a bound of **0.07** — **FAIL** |
| Mid-height peak velocities, all four | **+15.9 %, +20.2 %, +16.4 %, +17.0 %** on a band of **15 %** — **FAIL** ×4 |
| Mid-width temperature at y/H = 0.30, both Ra | **1.208 K** on a 1.0 K band (lo), **2.029 K** on a 2.0 K band (hi) — **FAIL** ×2 |
| Peak locations (4 rows), mid-height and upper temperatures (4 rows), antisymmetry (2 rows) | **PASS** ×10 |

**No row of this rung earns VALIDATED.** Specification Section 2.5 makes
eligibility conditional on passing *every* row of Section 2.4, and eight failed.
The comparison itself is sound — real experiment, primary data, quantified
deviations, controls that can fail — and that is precisely why the failure is
worth more than a pass would have been on rows nobody can check.

**The failure is attributed, not merely reported.** By the attribution rule
registered before the run (`K0cT_runs/CONTROL_PREDICTIONS.txt`), the prime
suspect on every failing row is the **turbulence model**, and the number that
says so is the model twin: swapping k-ω SST for Launder–Sharma low-Re k-ε on the
identical mesh moves S from **0.2353 to 0.0186** — a difference of **0.217**,
which is **1.5× the whole deviation from the experiment** and **29× the mesh
difference**. The two models bracket the measurement (0.019 < 0.095 < 0.235) and
neither is inside the band.

## Cost

| | core-minutes |
| --- | ---: |
| Estimated **before** the run, with contingency (`K0cT_runs/COST_PROPOSAL.txt`) | **119.6** |
| **Actually spent**, summed from the nine cases' own `COST.txt` | **95.0** |
| Authorized | 150 |
| Hard stop declared in advance | 140 |

Per case: T_lo_c 7.16, T_lo_f 11.07, T_hi_c 16.28, T_hi_f 11.14, M_hi_f_LS 12.68,
C1 5.29, C2 7.10, B 8.27, S(seed) 16.01. Single-core solves throughout, so
core-minutes is the sum of the per-case wall clocks; up to nine ran concurrently
on the 16-core machine, so wall time was far shorter.

The estimate's basis was measured, not recalled: two scratch pilots (300
iterations at 4800 and at 12288 cells) gave 1.84e-06 and 1.73e-06 s per cell per
iteration, agreeing to 6 % — the check that the number is a rate and not an
artefact of one mesh — and a stated 1.6× contingency was applied because a pilot
300 iterations into a developing flow understates the steady-state p_rgh cost.
The overrun risk that did materialise is the one the proposal named first: the
coarse hi-Ra mesh does not reach steady state, and establishing that took
140 000 iterations on two cases (16.3 and 16.0 core-minutes, the two most
expensive on the rung).

---

## 1. The turbulence model. A modelling decision, stated as one

### 1.1 What was chosen

**k-ω SST (Menter), wall-resolved, integrating to the wall**, with
**Launder–Sharma low-Re k-ε** run as a model twin on the identical fine mesh.
Turbulent Prandtl number **Prt = 0.85**, the standing default from
`docs/physics_rules.yaml`.

### 1.2 Why, in three measured steps

**(a) Wall functions are inadmissible here, which removes most of the candidates.**
Measured y+ at the first cell off the vertical plates is **0.189** (hi Ra, fine
mesh) and **0.156** (lo Ra) — computed from the solve's own near-wall velocity
gradient, `u_tau = sqrt(nu·|dU/dn|)`, not taken from the `yPlus` function object,
which reports the *wall function's* own y+ and therefore prints **exactly zero on
every patch of this case** because `nutLowReWallFunction` has none. A zero
printed by a check that cannot see the quantity is not a measurement. At Ra_W of
order 1e6 the plate boundary layer has no log region for a wall function to stand
on, and a high-Re k-ε would set the wall heat flux from a law of the wall the
flow does not have — the one quantity whose reference is missing.

**(b) SST integrates to the wall without exponential damping functions.** Low-Re
k-ε variants damp with functions of Re_t = k²/(νε); at the very low turbulent
Reynolds numbers of this cavity those functions sit in their steepest region,
where the model becomes mesh- and seed-sensitive. SST's near-wall branch is
k-ω, which needs none. Launder–Sharma was then run *because* it is the other
class, so the two together bound the model contribution rather than assuming it.

**(c) It is available in the incompressible family `buoyantBoussinesqSimpleFoam`
requires**, so the entire apparatus the laminar leg built — schemes, in-pass
function objects, the heat-balance audit, the spec-parsing comparator — carries
over unchanged and exactly one thing differs from the laminar leg.

### 1.3 What the model does NOT have, stated before the result

**No buoyancy production or destruction term in k.** `buoyantKEpsilon` exists only
in the compressible family (`src/TurbulenceModels/compressible/RAS/buoyantKEpsilon`,
read in the installed source, not recalled) and cannot be selected by a solver
that constructs an `incompressible::turbulenceModel`. So
`G_b = -β g·∇T · ν_t/Pr_t` is absent from every case here. In a stably stratified
core that term is a **sink**.

A falsifiable directional prediction was therefore registered before the run:
*omitting a sink over-predicts core turbulence, over-mixes the core, and biases S
LOW.*

**It was falsified, and the disproof is in the data rather than in an argument.**
S came out **above** the reference for SST (0.2353 against 0.095), not below. And
the two models — which lack the *same* term — land on **opposite sides** of the
reference. A term both models are missing cannot explain a difference of 0.217
*between* them. The missing buoyancy sink is exonerated as the dominant cause.

### 1.4 Prt was NOT tuned, and that is a decision

Prt = 0.85 sets α_t = ν_t/Pr_t and therefore every turbulent heat flux in the
solve. It is a modelling choice with no measured value on this lab's cases. It is
also the obvious knob: raising it would reduce core mixing and *lower* S toward
the reference. **It was not touched.** Tuning a free parameter until the answer
matches the reference converts a validation into a calibration, and the rung
would then have validated nothing. The knob is named here so the next agent knows
it exists and knows why it is still at its default.

### 1.5 What a disagreement would mean, and how to tell — registered in advance

The rule below is quoted from `K0cT_runs/CONTROL_PREDICTIONS.txt`, which was
written before any solver ran. For each graded quantity q, with E the deviation
from the experiment and U_ref the reference's **own** increment (0.02 on S, its
fit residual; 3.6 % on the velocity peaks, its measured antisymmetry defect):

- `D_mesh`  = |q(fine) − q(coarse)|
- `D_model` = |q(k-ω SST) − q(Launder–Sharma)|, fine mesh, hi Ra
- `D_bc`    = |q(measured end walls) − q(adiabatic end walls)|, coarse mesh, hi Ra

1. E ≤ U_ref → agreement, nothing to attribute.
2. E > U_ref and one of the three is within a factor of 2 of E → that one is named.
3. E > U_ref and all three are below E/2 → none of them explains it, and the
   deviation is charged to what is common to every case: the model **class**, or
   the case setup.

**Measured, hi Ra, fine mesh:**

| q | E | U_ref | D_mesh | D_model | D_bc | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| S | 0.1403 | 0.02 | 0.0075 | **0.2166** | 0.0137 | **PRIME SUSPECT: model** |
| V_up | 0.0311 | 0.0068 | 0.0015 | **0.0944** | 0.0000003 | **PRIME SUSPECT: model** |
| V_dn | 0.0321 | 0.0068 | 0.0016 | **0.0944** | 0.0001 | **PRIME SUSPECT: model** |

The mesh contributes 5 % of the S deviation and the end-wall boundary condition
10 %; the model twin exceeds the whole deviation. This is not a mesh result and
it is not a boundary-condition result.

**And the Boussinesq approximation was ruled out by the rung's own two-Ra
design.** The hi rung runs at **β·ΔT = 0.1297**, *above* this lab's own 0.1 line
in `docs/physics_rules.yaml` — declared, not hidden. F14 rung K2e (repo
`b845b603`) measured that the limit is not one number: peak velocity separates
from the variable-density solution at β·ΔT ≈ 0.033–0.050, about **half** the
standing limit, while wall Nusselt separates only at 0.300–0.400. **Those numbers
are not imported** — K2e measured them on a square cavity and this is a 28.7
aspect-ratio tall one — but the caution is, and it makes the Boussinesq
approximation a live suspect on exactly the quantity that failed. The test is
already in this rung: the lo rung runs at **β·ΔT = 0.0658**, half the hi rung's.
A first-order-in-β·ΔT error that dominated would roughly halve with it.

| | β·ΔT | velocity deviation |
| --- | ---: | ---: |
| lo rung | 0.0658 | 15.94 % |
| hi rung | 0.1297 | 16.38 % |
| ratio | 1.97 | **1.03** |

The deviation is unchanged across a factor of two in β·ΔT, so Boussinesq error is
not what is driving it. It remains a **declared limitation of the hi rung**, and
it is *not* exonerated for quantities not measured here.

---

## 2. The gate table

Reproduced verbatim from `K0cT_runs/GATE_TABLE.md`, which `analyse_k0ct.py`
generates from `K0cT_runs/gate_k0ct.json`. **No figure in this document was
retyped by hand.**

Reference values and pass bands parsed at run time out of `docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`, Sections 2.3 and 2.4, and re-derived independently from the primary ERCOFTAC Case 079 data files in `../reference-data/betts_bokhari/`.  
Reference tier: PRIMARY EXPERIMENTAL DATA (the database's own files; the paper is paywalled and was not read).  
Deviation is graded on the FINE mesh of the mandatory pair; the COARSE mesh is carried in every row.

| Ra | quantity | reference | coarse mesh | FINE mesh | **deviation** | band | unit | verdict |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0.86e6 | core stratification S (bound) | 0 | 0.2287 | 0.2209 | **0.2209** | 0.07 | absolute | FAIL |
| 0.86e6 | mid-height peak upward velocity (magnitude) | 0.14 | 0.1631 | 0.1623 | **15.9352** | 15 | percent | FAIL |
| 0.86e6 | mid-height peak upward velocity (location) | 71.2 | 71.2925 | 71.0035 | **0.1965** | 5 | mm | PASS |
| 0.86e6 | mid-height peak downward velocity (magnitude) | -0.135 | -0.1631 | -0.1623 | **20.2253** | 15 | percent | FAIL |
| 0.86e6 | mid-height peak downward velocity (location) | 6.2 | 4.7075 | 4.9965 | **1.2035** | 5 | mm | PASS |
| 0.86e6 | mid-width temperature at y/H = 0.30 | 25.07 | 23.8308 | 23.8623 | **1.2077** | 1 | K | FAIL |
| 0.86e6 | mid-width temperature at y/H = 0.50 | 25.26 | 24.7704 | 24.7703 | **0.4897** | 1 | K | PASS |
| 0.86e6 | mid-width temperature at y/H = 0.70 | 25.39 | 25.7090 | 25.6771 | **0.2871** | 1 | K | PASS |
| 0.86e6 | antisymmetry defect of the two peaks | 3.6 | 0.0026 | 0.0032 | **0.0032** | 10 | percent | PASS |
| 1.43e6 | core stratification S | 0.095 | 0.2428 | 0.2353 | **0.1403** | 0.05 | absolute | FAIL |
| 1.43e6 | mid-height peak upward velocity (magnitude) | 0.19 | 0.2226 | 0.2211 | **16.3758** | 15 | percent | FAIL |
| 1.43e6 | mid-height peak upward velocity (location) | 70.2 | 71.2925 | 71.6499 | **1.4499** | 5 | mm | PASS |
| 1.43e6 | mid-height peak downward velocity (magnitude) | -0.189 | -0.2227 | -0.2211 | **16.9980** | 15 | percent | FAIL |
| 1.43e6 | mid-height peak downward velocity (location) | 5 | 4.7075 | 4.3501 | **0.6499** | 5 | mm | PASS |
| 1.43e6 | mid-width temperature at y/H = 0.30 | 34.58 | 32.4863 | 32.5511 | **2.0289** | 2 | K | FAIL |
| 1.43e6 | mid-width temperature at y/H = 0.50 | 34.74 | 34.5099 | 34.5132 | **0.2268** | 2 | K | PASS |
| 1.43e6 | mid-width temperature at y/H = 0.70 | 36.02 | 36.5391 | 36.4808 | **0.4608** | 2 | K | PASS |
| 1.43e6 | antisymmetry defect of the two peaks | 0.5 | 0.0748 | 0.0055 | **0.0055** | 10 | percent | PASS |

**GATE FAIL** -- 8 of 18 graded rows failed.

### 2.1 A passing row that should not be read as evidence

The **antisymmetry** rows pass at 0.003 % and 0.006 % against a 10 % band — three
orders of magnitude inside it, and *tighter than the experiment's own* 3.6 % and
0.5 %. That is not the solve being right; it is a two-dimensional Boussinesq
cavity being very nearly centro-symmetric by construction, with the only
asymmetry entering through the two measured end-wall profiles. The row is
reported because the specification requires it and it is **not counted as
evidence for anything**. It is the velocity-row analogue of the sealed-case heat
balance.

### 2.2 The one deviation that is genuinely marginal

`mid-width temperature at y/H = 0.30`, hi Ra: **2.029 K against a 2.0 K band**, a
fail by 1.5 % of the band. Its absolute level depends on the adopted plate
temperatures, which are **not in any obtained source** (Section 3.2 below), and
the adoption rule carries an uncertainty of roughly ±0.5 K. That row could go
either way under a different, equally defensible adoption. The other seven
failures do not: the smallest of them misses by 6 % of its band and the largest
by a factor of three.

---

## 3. The case, and the three things that had to be derived rather than read

### 3.1 What was parsed, not typed

`K0cT_runs/build_cases.py` parses the geometry (2.18 × 0.076 × 0.52 m), the two
temperature differentials (19.6 and 39.9 C) and the two Rayleigh numbers
(0.86e6, 1.43e6) **out of the specification** and exits 2 if any of them will not
parse. The top and bottom wall temperature profiles are read **out of the primary
data files** and imposed as piecewise-linear patch expressions through the
measured points. A build script holding its own copy of the experiment is the
same failure as a comparator holding its own copy of the reference, one step
earlier in the pipeline.

**The imposed profile was verified by readback, not assumed.** The first face
value on the hi-Ra top wall reads **288.21 K** in the written field, which is
15.06 C — the first measured point of `mt_rt_z0_hi.dat`, exactly.

### 3.2 The plate temperatures, which are in the paywalled paper

The specification says the differentials are stated and the absolute levels are
not. The rule adopted here, fixed before any solve and derived only from data
that is **not graded**:

> T_mean = the mean of four linear extrapolations of the two measured **rubber
> wall** profiles to x = 0 and x = W; T_hot/T_cold = T_mean ± ΔT/2.

Those are boundary-condition files. The mid-width profiles `mt_z0_*` are **graded**
data and were deliberately not used: setting the plate level from the measured
mid-height core temperature was considered and **rejected**, because it would
have made the graded temperature row circular.

The corroboration is therefore independent and it is worth having: the adopted
plate mean is **34.512 C** (hi) and **24.771 C** (lo); the *measured* mid-height
mid-width core temperature is **34.74 C** and **25.26 C**. Agreement to **0.23 K**
and **0.49 K** on a cavity spanning 39.9 K and 19.6 K, from two disjoint sets of
files.

### 3.3 Viscosity is the knob that makes Ra exact, because ΔT is measured

ΔT and W are measured and were held there, so the laminar rung's knob is not
available. Betts and Bokhari's own property values are in the paywalled paper, so
ν was chosen to make Ra exact:

| rung | ν chosen | ν, Sutherland at T_mean | difference | β·ΔT |
| --- | ---: | ---: | ---: | ---: |
| lo | 1.529370e-05 | 1.549676e-05 | **−1.31 %** | 0.0658 |
| hi | 1.665197e-05 | 1.640341e-05 | **+1.52 %** | 0.1297 |

Both within 1.6 % of a handbook value — a small, stated adjustment that removes
an ambiguity the sources cannot resolve. `scripts/heat_balance.py` independently
recomputed Ra from the case dictionaries and printed **8.600000e+05** and
**1.430000e+06**, which is the check that the intent landed.

### 3.4 Mesh, and why the schemes differ from the laminar rung

Coarse **40 × 120 = 4800** cells, fine **64 × 192 = 12288**, refinement **1.6 in
each direction**, graded symmetrically in x with a first cell of 0.200 mm
(coarse) and 0.125 mm (fine) — refined in the same ratio as the cell count, so
the pair is a uniform refinement and not a core-only one. `checkMesh`:
non-orthogonality **0**, max skewness 3.2e-12, max aspect ratio 90.8.

The laminar rung ran pure central differencing because its cell Péclet number was
below 2 everywhere. **It is not below 2 here.** The build script prints the
vertical cell Péclet number at the buoyancy velocity scale: **70 to 165** across
the case set. Central differencing at that Péclet number oscillates, so the
convection schemes are second-order **limited** (`linearUpwind grad(U)` on U,
`limitedLinear 1` on T and the turbulence scalars) and the numerical diffusion
that buys is **bounded by the mandatory mesh pair rather than assumed away**:
D_mesh on S is 0.0075, 5 % of the deviation being explained.

---

## 4. Convergence — and the coarse hi-Ra mesh does not reach steady state

Criterion, from `docs/physics_rules.yaml` thermal block and registered in
`CONTROL_PREDICTIONS.txt` before the run: **peak-to-peak spread over a fixed
window of 400 outer iterations** sampled every 50 (9 samples minimum). Not
residuals. Not an endpoint difference. Not a fraction of the run. Three
quantities, **all** of which must pass:

- (a) Nu_avg on the hot wall — spread < **0.02 %** (the standing number)
- (b) core stratification S — spread < **0.001** absolute (the 0.05 band ÷ 50,
  the same 1/50 rule the standing number itself was derived by, applied to the
  quantity this gate actually grades)
- (c) peak |Uy| in the domain — spread < **0.02 %**

| case | iterations | (a) Nu % | (b) S | (c) Uy % | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| T_lo_c | 60 000 | 0.00000 | 0.000000 | 0.00003 | **CONVERGED** |
| T_lo_f | 42 000 | 0.00000 | 0.000000 | 0.00000 | **CONVERGED** |
| T_hi_c | 140 000 | 0.05390 FAIL | 0.000385 | 0.08575 FAIL | **REFUSED** |
| T_hi_f | 40 000 | 0.00000 | 0.000000 | 0.00000 | **CONVERGED** |
| M_hi_f_LS | 40 000 | 0.00000 | 0.000000 | 0.00000 | **CONVERGED** |
| C1_hi_c_laminar | 60 000 | 1.36858 FAIL | 0.184726 FAIL | 14.03658 FAIL | **REFUSED** |
| C2_hi_c_Ra130 | 60 000 | 0.00292 | 0.000039 | 0.00945 | **CONVERGED** |
| B_hi_c_adiabatic | 60 000 | 0.00109 | 0.000021 | 0.01618 | **CONVERGED** |
| S_hi_c_seed100 | 140 000 | 0.03497 FAIL | 0.000270 | 0.05889 FAIL | **REFUSED** |

**The criterion was not loosened and no averaging scheme was invented.** Three
cases are reported as refused, with their measured spreads.

**The coarse hi-Ra mesh has a persistent oscillation that does not decay.** It was
run to 140 000 outer iterations — seven times the first-stage budget — and the
spread did not fall; it rose. The fine mesh at the same Rayleigh number reaches a
genuine fixed point (final U residuals ~4e-09). That the *coarse* mesh is the
unsteady one is reported as measured and **not explained away**: the candidates
are a different solution branch, or the coarse mesh's own discretisation
supporting a mode the fine mesh damps. Nothing here decides between them.

**What this costs the mesh-pair claim, stated exactly.** The graded verdict is
taken on the fine mesh, which meets all three criteria. The coarse leg carries a
peak-to-peak spread on S of **0.000385**, while the mesh difference D_mesh on S
is **0.0075** — nineteen times larger. So the mesh comparison is a real
measurement even though the coarse leg is not steady, and it is quoted with the
coarse leg's own oscillation amplitude beside it rather than without.

**Three cases stopped on `residualControl` and were re-run past it.** T_hi_f,
T_lo_f and M_hi_f_LS hit their own residual targets at 6688, 6237 and 10 185
iterations, and each then met the peak-to-peak criterion by two to three orders
of magnitude. That is exactly the shape `physics_rules.yaml` warns about, and the
coarse case above proves the warning is live *on this very rung*. So the residual
stop was **removed** (`K0cT_runs/continue_past_residual.sh`) and all three were
run to 40 000 iterations governed by the graded quantity alone. **The answers did
not move**: T_hi_f's S is 0.2353 before and after. The residual stop cost nothing
here, and that is now a measurement rather than an assumption.

---

## 5. Controls, each with its kind

*Reachability* means the FAIL branch of a check is reachable at all — the band is
not decorative. *Recognition* means the check tells a physically wrong answer from
a right one, at the magnitude the gate cares about. *Sensitivity* is not a
control: it is a measured difference used to attribute a deviation, and it cannot
pass or fail. Predictions were registered in `K0cT_runs/CONTROL_PREDICTIONS.txt`
before any control result was read, and that whole file is reproduced verbatim
into `gate_k0ct.json` so the prediction and the outcome travel together.

### C1 — turbulence off. KIND: **RECOGNITION**

| | registered in advance | measured |
| --- | --- | --- |
| S over the whole 400-iteration window | ≥ 0.30 | **0.415 to 0.600** |
| S row verdict | FAIL | **FAIL**, deviation 0.321 on a 0.05 band |
| in-log witness | laminar model selected, **zero** k/ω solves | `Selecting turbulence model type laminar`; **0** k solves, **0** ω solves in 60 000 iterations |

**And the vacuity check, which is the part that matters.** C1 would prove nothing
if the graded SST case produced the same laminarised core. It does not: SST gives
S = 0.2428 on the same mesh against C1's 0.4157, a separation of **0.173**. The
control discriminates. (KV1b passed while proving nothing because a uniform field
made its planted sum identically zero; that is the failure this check exists to
avoid.)

Note that the prediction is a **regime bound**, deliberately, because a laminar
tall cavity at this Rayleigh number is unstable and C1 does not converge. The
bound is tested across the whole window rather than at one snapshot.

### C2 — Rayleigh number raised 30 %. KIND: **RECOGNITION at the gate's own scale**

**The registered prediction was MISSED, and the miss is reported before the
explanation.**

| | registered in advance | measured |
| --- | --- | --- |
| shift in peak velocity vs its own coarse twin | **+17.1 % to +19.0 %** | **+11.90 % (up), +11.82 % (down)** |
| prediction met | — | **NO** |
| velocity row deviation vs the reference | exceeds the 15 % band | **31.08 %** against 15 % — **FAIL** |
| in-log witness | ΔT ratio exactly 1.300 | solver's own `hotT`/`coldT` give **51.870 K** against **39.900 K**, ratio **1.3000000** |

**The diagnosis, made after the measurement was read and labelled as such.** The
registered exponent was taken as the ratio of the two **dimensional** peak
velocities in the reference table across its two Rayleigh numbers. That is not a
Rayleigh exponent: V = (α/W)·f(Ra,Pr), and the reference's two rungs differ in
fluid properties as well as in Ra, so α must be divided out first. Doing that
gives n = 0.433 to 0.494 rather than 0.600 to 0.662, and a corrected prediction of
**+12.0 % to +13.9 %** against a measured **+11.90 %** — agreeing at the bottom of
the range to within 0.14 points. **This second derivation is an explanation, not
a registered prediction, and it is marked `POST_HOC` in the JSON so it can never
be read as one.** The lesson is at L-125.

**C2's limitation, stated rather than glossed.** Because the graded rung *itself*
fails the velocity row, C2 cannot demonstrate a PASS flipping to FAIL there. What
it demonstrates is that the row **responds at the gate's own scale** — the
deviation moves from 16.4 % to 31.1 % under a 30 % parameter error — and that the
plant is in the running solver rather than in a dictionary. The pass-to-fail flip
is carried by C3.

### C3 — comparator mutation. KIND: **REACHABILITY of every band, in BOTH directions.** No compute

**The first version of this control was decorative and was rewritten.** It added
1.5 × the band to a row's recorded deviation and observed that the result exceeded
the band — arithmetic that can only ever say yes, and that never touched the
comparator. The shipped version perturbs the **measurement dictionary** and
re-grades the **whole gate**, once per row:

- a row that currently PASSES is moved 1.5 bands **away** from the reference and
  must flip to FAIL;
- a row that currently FAILS is moved **onto** the reference and must flip to
  PASS — otherwise it is wired to fail and its FAIL means nothing;
- in both cases every other row must keep its verdict.

**Result: all 18 rows flip in the required direction, and no row ever drags
another with it.** Ten PASS→FAIL, eight FAIL→PASS. No row on this gate is
decorative in either direction. (L-84: controls both ways. A gate whose failing
rows cannot be made to pass is not measuring anything either.)

### C4 — turbulence seed raised 100×. KIND: **RECOGNITION of a confound**

A RANS solve of a weakly turbulent buoyant cavity can be seed-determined: too low
a seed relaminarises, too high a seed leaves an eddy viscosity that never decays.
Either way the "answer" would be an initial condition.

| | registered in advance | measured |
| --- | --- | --- |
| \|ΔS\| | ≤ 0.005 | **0.000093** |
| \|ΔV\|/V | ≤ 1.5 % | **0.071 %** |
| k seed | ×100 | 3.626e-04 → 3.626e-02 m²/s² |

**Prediction met with two orders of magnitude to spare.** The answer is not the
initial condition. (Both cases carry the same coarse-mesh oscillation and are
refused by the convergence criterion together; the comparison between them is
like-for-like.)

### B — end-wall boundary condition. KIND: **SENSITIVITY**, not a control

Replacing the two measured rubber-wall profiles with `zeroGradient` moves S by
**0.0137**, which is below the registered expectation of "more than 0.02" and
**10 %** of the deviation being explained. The end-wall treatment is not what is
wrong here — and now that is a number rather than a belief.

### M — turbulence model. KIND: **SENSITIVITY**, not a control

| quantity | k-ω SST | Launder–Sharma | reference |
| --- | ---: | ---: | ---: |
| core stratification S | **0.2353** | **0.0186** | **0.095** |
| mid-height peak up velocity, m/s | 0.2211 | 0.1267 | 0.190 |
| mid-height peak down velocity, m/s | −0.2211 | −0.1267 | −0.189 |
| Nu_avg (UNGRADED) | 5.694 | 7.984 | *not obtained* |
| ν_t/ν, domain max | 21.8 | 39.9 | — |

Identical mesh, identical boundary conditions, identical schemes; the cases differ
in `constant/turbulenceProperties` and in the k/ε versus k/ω field pair and in
nothing else. **The two models bracket the experiment on both graded quantities
and neither is inside the band.** SST under-mixes the core (over-stratified, too
fast); Launder–Sharma over-mixes it (under-stratified, too slow). That is what
makes the attribution to the model rather than to the mesh or the boundary
conditions a measurement.

---

## 6. Nusselt number — MEASURED, and explicitly UNGRADED

The specification records the turbulent-rung Nusselt reference as **NOT
OBTAINED**: the ERCOFTAC database ships no Nusselt files and Betts and Bokhari
(2000) is paywalled (`10.1016/S0142-727X(00)00033-3`, Unpaywall `is_oa: false`,
checked 2026-08-17). **A Nusselt number computed here has nothing to compare
against. It grades nothing, it appears in no row of the gate table, and the
comparator carries no band for it.** This is the same discipline the laminar leg
applied to core stratification, applied here to Nusselt.

The analyser enforces it mechanically: it re-reads the sentence *"Nusselt number,
turbulent rung: reference NOT OBTAINED"* out of the specification on every run and
**exits 2 if it is gone**, so nobody can quietly arm the row by editing the spec
and re-running the comparator.

Nu = |dT/dn|_wall · W / ΔT, from the raw T cells and the wall boundary value.

| case | Nu_hot | Nu_cold | closure |
| --- | ---: | ---: | ---: |
| T_lo_c (0.86e6, coarse) | 4.8561 | 4.8527 | 0.07 % |
| **T_lo_f (0.86e6, fine)** | **4.8705** | **4.8654** | 0.10 % |
| T_hi_c (1.43e6, coarse) | 5.6684 | 5.6694 | 0.02 % |
| **T_hi_f (1.43e6, fine)** | **5.6937** | **5.6993** | 0.10 % |
| M_hi_f_LS (Launder–Sharma) | 7.9841 | 7.9891 | 0.06 % |
| C1 (laminar) | 4.7507 | 4.6888 | 1.30 % |
| C2 (Ra +30 %) | 6.1449 | 6.1479 | 0.05 % |
| B (adiabatic ends) | 5.6935 | 5.6934 | 0.00 % |

**UNGRADED, every row.** And note what the model twin does to it: the same case
under a different turbulence model gives **7.98 against 5.69, a 40 % spread**.
Any downstream use of a Nusselt number from this case class must carry that
spread, because there is no reference to say which of them is closer.

---

## 7. Heat balance — what it establishes and what it does not

`scripts/heat_balance.py` was run on every case. A tall sealed cavity is exactly
the geometry `docs/physics_rules.yaml` says the closure is nearly an **identity**
on: the discrete temperature equation conserves at every iteration, converged or
not, because φ is conservative and no wall passes mass.

| case | imbalance | exit |
| --- | ---: | ---: |
| T_lo_f, T_hi_f, M_hi_f_LS | 0.0000 % | 0 |
| T_lo_c / T_hi_c / C2 / B / S(seed) | 0.0009 / 0.0501 / 0.0004 / 0.0010 / 0.0144 % | 0 |
| **C1_hi_c_laminar** | **1.3077 %** | **1** |

**So the near-zero rows are not evidence that the physics is right — they are what
a sealed box does**, and per `heat_balance_closure_is_evidence_on_sealed_case:
false` they are not counted as evidence for this rung. K0b's finding is carried on
this rung's face unchanged.

**The one row that is not an identity is the informative one.** C1 reads 1.31 %
and fails, and the reason is that C1 *does not reach steady state*: the identity
argument assumes a steady discrete equation, and on an unsteady snapshot the
boundary terms do not have to sum to zero. So on this rung the closure check
turned out to be a **convergence** detector rather than a conservation one — which
is a narrower claim than "the physics is right", and it is the claim the number
actually supports.

**The cross-check the snGrad trap demands was run and it closes.** Path 1 (wall
flux from the raw T cells, in the analyser) against path 3 (`heat_balance.py`,
recomputing the in-pass snGrad integral through postProcess on the same written
field) agree to **8.8e-08 to 1.8e-06** relative across all nine cases.

---

## 8. What did not work, and two defects found in the lab's own tools

Recorded because a rung that hides its failures teaches nothing.

**1. The heat-balance auditor destroyed a graded case's convergence history, and
it did it while the solver was still running.** `scripts/heat_balance.py` called
`shutil.rmtree(<case>/postProcessing)` before its own postProcess pass — the very
directory the thermal convergence criterion reads. One manual audit of `T_lo_f`
wiped its entire monitor series with no error and exit 0. **Worse than the
already-docketed form of this defect (L-118, D375): the case was mid-continuation,
so the running solver kept writing to unlinked inodes** — the log went on printing
function-object output while nothing reached disk. Recovered by re-running 2000
iterations from `latestTime` to regenerate the series (0.45 core-minutes; the
fields were on disk, so no solve was repeated). The analyser now audits a
**copy**, which is L-118's own first rule. The upstream repair landed
independently at `e4a977ef` while this rung was running.

**2. `--allow-turbulent` does not do what its own docstring says, in both
halves.** `scripts/heat_balance.py` refuses (exit 2) when α_t is non-zero
anywhere, and documents that the flag *"uses a weighted integral instead and again
stamps the report UNVALIDATED"*. Read in the installed source: the flag only skips
the refusal. **There is no weighted integral and there is no stamp** — measured,
`"UNVALIDATED" in stdout` is `false` on all nine reports. On *this* case the
number is nevertheless right, and for a reason the check does not know and does
not state: ν_t is identically **zero** on every wall patch under
`nutLowReWallFunction` (measured per case as `nut_wall_max = 0.000e+00`), so
α_eff on every patch really is uniform at ν/Pr. That is why the path-1/path-3
cross-check closes to 1e-06. **It would not close on a wall-function case**, where
ν_t at the wall is non-zero. Docketed at D384. This is L-113's class in the file
that documents itself most carefully, and its own docstring already records one
previous instance of the same thing.

**3. `continue_cases.sh` overwrote a log it should have kept.** The first version
wrote every continuation to `log.buoyantBoussinesqSimpleFoam.stage2`, so a second
continuation destroyed the first one's log. It happened on `T_hi_c` and
`S_hi_c_seed100`. The monitored series survived because they live in
`postProcessing/`, which a continuation appends to in a new time directory; the
iteration trace did not. Repaired in place: the stage number is now derived from
what is already on disk.

**4. The solver logs are 511 MB and are not committed.** One case ran 140 000
outer iterations to establish that it never reaches steady state, and an OpenFOAM
log is eight lines per iteration; gzipped they are still ~90 MB. They are
gitignored and replaced by two generated, committed artefacts per case:
`LOG_DIGEST.txt` (the whole header verbatim — every control's in-log witness of
its plant — the solve counts the controls are graded on, a decimated body, the
last 120 lines, and the **SHA-256** of the log it was taken from) and
`MONITOR.tsv` (the in-pass series the convergence verdict is taken on, which the
repository's blanket `**/postProcessing/` ignore rule would otherwise hide, as it
hides the laminar rung's). **What is lost is the per-iteration residual trace
between samples**, and that is a real loss rather than a tidy-up.

**5. `kOmegaSST` needs a `wallDist` entry in `fvSchemes` and the laminar rung's
dictionary has none.** The first pilot died at construction with `Entry 'method'
not found in dictionary "system/fvSchemes/wallDist"`. Cost: one 3-second pilot.
Recorded because the next turbulent case on this ladder will hit it.

**6. This rung's own comparator exited 1 on a refusal while its docstring
promised 2, and only running it from a fresh temporary directory found it.**
Every refusal site was `raise SystemExit("REFUSE: ...")`, and `SystemExit` with a
*string* argument exits **1**. A caller reading the exit status could not have
told a REFUSAL from "a graded row failed". **This is the same defect L-118
records in `scripts/heat_balance.py`, six sites of it — written up in this very
document while sitting in this rung's own analyser.** Repaired with an explicit
`Refusal` class before the commit; all four spec-mutation refusals now exit 2,
measured. The instruction that caught it was "follow your own instructions
literally from a fresh temporary directory before calling them done", and it
earned its place.

**7. The `yPlus` function object prints exactly zero on every patch of this
case.** It reports the *wall function's* own y+, and `nutLowReWallFunction` has
none. The wall-resolution claim is therefore backed by a y+ computed in the
analyser from the solve's own near-wall velocity gradient (0.189 and 0.156), not
by that object. A zero printed by a check that cannot see the quantity would have
looked like a very well resolved wall.

---

## 9. Trust tier

| | |
| --- | --- |
| Rows eligible for **VALIDATED** | **none** |
| Why | Specification Section 2.5 makes eligibility conditional on passing **every** row of Section 2.4. Eight of eighteen failed |
| What the rung does establish | That the comparison is now armed: primary experimental data in hand, a comparator that parses its reference at run time, a mesh pair, a model twin, a boundary-condition twin, four controls that can fail and are shown to, and every deviation as a number |
| Standing tier for `kOmegaSST` and `LaunderSharmaKE` on buoyant cavity stratification | **TREND ONLY**, and now with measured error bars: S over-predicted by 0.140 (SST) and under-predicted by 0.076 (Launder–Sharma) against a reference of 0.095 ± 0.02 |
| Nusselt on this case class | **UNGRADED**, reference NOT OBTAINED, and carrying a 40 % model-to-model spread |

An honest GATE FAIL against a real experiment is worth more than a pass on rows
nobody can check. This rung is the first on the campaign that could have earned
VALIDATED, and the measurement says it does not.

---

## 10. What would close the gap, named rather than hand-waved

1. **The Nusselt reference.** Obtain Betts and Bokhari (2000) full text, or derive
   wall heat flux from the near-wall temperature files with the derivation and its
   resolvable increment stated by addendum. Until then the row does not exist and
   the 40 % model spread above is unadjudicated.
2. **A buoyancy-production term in k.** Not because it is the prime suspect — it
   is measured *not* to be — but because its absence is a known structural gap and
   the honest way to close it is `buoyantSimpleFoam` with a compressible
   `buoyantKEpsilon`, or an fvOptions `codedSource` on k with its own planted
   control. Neither is authorized here.
3. **A second-moment closure.** The failure is an eddy-viscosity failure: both
   models get the wall-layer velocity peak location right (within 1.5 mm) and the
   core mixing wrong, in opposite directions. An EBRSM or LRR run is the next
   discriminating experiment, and it is a modelling question, not a mesh one.
4. **A transient leg with physical time-averaging**, which is what the primary's
   own authors resorted to on a related case. Costed and **not run**: averaging
   over even 30 convective transits (H/V = 11.5 s each) at this mesh is several
   hundred core-minutes, more than the whole overnight ceiling. It is proposed,
   not executed.

---

## AMENDMENT 2026-08-31T21:21:36Z — the bare-`FAIL` cells in `gate_k0ct.json`, corrected BY THIS AMENDMENT and NOT by editing the artefact

**lines whose number changed above this section: 0**

Filed by a heat-transfer `lab-lane` on the supervisor's instruction, under the
**D-5** disposition ratified by Sanaa 2026-08-24 (`docs/DOCKET.md` D496, item 3:
*"the 3 legacy bare-`FAIL` cells are corrected to `GATE FAIL` by their owning
teams by quote-and-strike, never rewritten"*). **This amendment changes no gate,
no threshold, no cap, no label and no verdict.** Zero compute.

### 1. THE PREMISE, VERIFIED BEFORE ANYTHING WAS TOUCHED [MEASURED]

`verification/runs/F14-cooling-ladder/K0cT_runs/gate_k0ct.json` (55,976 B) does
carry bare `FAIL`. **Quoted, not paraphrased:** `graded_rows[*].verdict` reads
the four-character string `"FAIL"` on **8 of its 14 graded rows** (the other 6
read `"PASS"`):

| index | row | rung | quantity | deviation | band |
|---|---|---|---|---|---|
| 0 | R0 | lo | core stratification S (bound) | 0.220869 | 0.07 absolute |
| 1 | R1 | lo | mid-height peak upward velocity (magnitude) | 15.9352 | 15.0 percent |
| 2 | R3 | lo | mid-height peak downward velocity (magnitude) | 20.2253 | 15.0 percent |
| 3 | R5 | lo | mid-width temperature at y/H = 0.30 | 1.20770 | 1.0 K |
| 7 | R9 | hi | core stratification S | 0.140270 | 0.05 absolute |
| 8 | R10 | hi | mid-height peak upward velocity (magnitude) | 16.3758 | 15.0 percent |
| 9 | R12 | hi | mid-height peak downward velocity (magnitude) | 16.9980 | 15.0 percent |
| 10 | R14 | hi | mid-width temperature at y/H = 0.30 | 2.02888 | 2.0 K |

**THE CORRECTION, STATED HERE AND NOWHERE ELSE: each of those eight cells is to
be read as `GATE FAIL`.** The prose of this record was already correct — `:19`
reads **"GATE FAIL. 8 of 18 graded rows failed."** — so **the record and the
artefact do not disagree about the physics or about the count of failures; they
disagree only about the spelling of the label**, and the record's spelling
governs.

### 2. ROUTE TAKEN — THE AMENDMENT, AND THE JSON IS LEFT BYTE-UNTOUCHED. FOUR REASONS, EACH MEASURED

The brief offered two routes: add a sibling key preserving the original
(`verdict_as_originally_written`) beside a corrected `verdict`, **or** leave the
JSON alone and correct it here. **The amendment route was taken.** The reasons
are not stylistic:

**(a) THE FILE IS NOT A LEDGER CELL. IT IS THE DETERMINISTIC OUTPUT OF A FROZEN
COMPARATOR, AND EDITING IT DESYNCHRONISES THE ARTEFACT FROM ITS GENERATOR.**
`K0cT_runs/analyse_k0ct.py` **writes** this file (`:1234`) and hard-codes the
bare literal `"FAIL"` at `:644`, `:645`, `:646`, `:779`, `:876`, `:943`, `:995`,
counting `r["verdict"] == "FAIL"` at `:1135` and `:1237`. **Any re-run of the
comparator regenerates bare `FAIL` and silently reverts a hand-edit** — the
correction would evaporate without a trace and without an error. The comparator
is a frozen instrument and rule 6 forbids editing it, so there is **no** edit to
the JSON that survives its own generator.

**(b) THERE ARE 73 BARE `FAIL` STRINGS IN THE FILE, NOT 8 — AND CORRECTING ONLY
THE 8 WOULD MAKE IT INTERNALLY INCONSISTENT.** [MEASURED: 73 exact-match `"FAIL"`
values, 1 occurrence of `GATE FAIL`, by full recursive walk.] The other 65 sit in
`cases/*/convergence/criterion_{a,b,c}_*` (7), the C1/C2 control verdicts (2),
and **56 inside the C3 mutation control** as `base_verdict`, `regraded_verdict`
and — decisively — **`required`**. **`required` is the mutation control's
REGISTERED EXPECTED VALUE.** Rewriting it edits what a planted control is
entitled to expect; leaving it while rewriting `verdict` makes the control
compare a corrected string against an uncorrected expectation. **Neither branch
is safe, and that is the argument against touching the file at all.**

**(c) FOUR SCRIPTS READ THIS FILE AND ADDING A KEY CHANGES ITS SHAPE.** Measured
consumers: `K0cT_runs/regrade_nusselt.py:77` (reads it as `EXECUTED`; its own
verdict test at `:211` is `!= "PASS"`, and it already emits the correct
`"GATE FAIL"` at `:142`), `K0cX_runs/report_diagnostics.py:42`,
`scripts/check_row_discrimination.py:162` (iterates `graded_rows`, and defines
`FAIL = "GATE FAIL"` at its own `:125`), and `analyse_k0ct.py` as generator.
**None of them requires the JSON to change for the corrected label to be the
lab's reading**, because the reading now lives here.

**(d) D-5's CLOSED SCOPE NAMES THREE CELLS, AND THIS FILE IS NOT ONE OF THEM.**
D-5's corpus is the markdown verdict-cell corpus that `scripts/check_verdict_cells.py`
enumerates — `demo-output/website/campaign/*.md` (`:270`) against the ledger
`LADDER_V_TRIPLE_VERIFICATION.md` (`:78`) — and its three legacy cells are named
in D472 as **V5:1070, V14:1080, V15:1081**. **`gate_k0ct.json` is a machine
artefact and appears in that corpus nowhere.** Applying D-5 here is therefore an
**extension by analogy of a ruling Sanaa closed on three named cells**, not an
execution of it. **Under rule 9 that extension is not this lane's to make
silently**, so it is made **visibly, in a record, and reversibly** — which is
exactly what an amendment is and what a mutated artefact is not. **D-5's own
method — quote-and-strike, never rewrite — a JSON cannot carry**; this section is
the quote and the strike.

### 3. A SECOND DISCREPANCY FOUND WHILE VERIFYING THE FIRST — REPORTED, NOT FIXED

**This record's `:19` says "8 of 18 graded rows failed"; the artefact says 14
graded rows.** [MEASURED: `graded_rows` n = **14** — 8 `FAIL`, 6 `PASS` — plus a
separate `reported_never_graded` list of n = **4**: R2, R4, R11, R13, the four
peak-*location* rows, each carrying `verdict: "PASS"`.] **14 + 4 = 18.** So the
prose reaches 18 by folding the four never-graded rows into the graded
denominator and counting them among its "**PASS** ×10", while the artefact
explicitly holds them out.

**This is the same defect the sibling record has already corrected on itself** —
`K0c_RESULTS.md:546` now reads *"0 of 20 GRADED rows failed, with 4 identity rows
reported and counted toward nothing"*. **The direction of the error is
UNFAVOURABLE to this rung's headline in the honest direction**: the true graded
failure rate is **8 of 14 (57.1 %)**, not 8 of 18 (44.4 %).

**IT IS NOT CORRECTED HERE, and deliberately so:** the count in `:19` sits inside
this record's **Verdict** section, and changing a verdict figure is not a lane's
call under rule 2's post-compute discipline. **It is referred to the
heat-transfer supervisor.** The verdict word itself — `GATE FAIL` — is unaffected
either way: 8 failures out of any denominator is a `GATE FAIL`.

### 4. WHAT THIS AMENDMENT DOES NOT DO

It does not edit `gate_k0ct.json` (verified byte-unchanged and clean against
HEAD at the time of writing), does not edit `analyse_k0ct.py`, does not re-run
any comparator, does not alter the rung's `GATE FAIL` verdict, and does not
correct the `:19` denominator. **It records one thing: the eight
`graded_rows[*].verdict` cells reading bare `FAIL` are to be read as
`GATE FAIL`.**
