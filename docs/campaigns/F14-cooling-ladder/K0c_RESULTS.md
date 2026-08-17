# K0c laminar rung — executed. F14 cooling ladder

Executed 2026-08-17 against `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`, which
was written first, by a different agent, at zero compute. **Nothing in this
document edits that specification.** The reference values and every pass band
were parsed out of it by `K0c_runs/analyse_k0c.py` at run time rather than
copied into the comparator, so a comparator holding its own private copy of the
reference — this lab's most repeated failure, written in code — cannot happen
here. If the specification cannot be parsed the analyser exits 2 and grades
nothing.

**This is the first rung on this ladder that could have been wrong.** K0a and
K0b were capability rungs: they proved the solver runs. This one compares
against published values the lab did not produce.

## Verdict

**GATE PASS. 0 of 24 graded rows failed.**

Every deviation is a number in the table below, coarse mesh beside fine mesh in
every row. The largest deviation anywhere on the gate is **1.139 percent**, on
Nu_min at Ra = 1e6, against a band of 3.0 percent. The tightest band on the
gate is 1.0 percent on Nu_avg, and the worst Nu_avg deviation is **0.588
percent**, also at Ra = 1e6. Total compute charged to the eleven cases that
produced this table: **41.73 core-minutes**, plus roughly 44 core-minutes
discarded and accounted for below.

Three things a reader should hold on to before the table. The gate could have
failed and was checked to be able to: control C2 plants a 10 percent Rayleigh
error and the same comparator fails it at 3.19 percent against the 1.0 percent
band. The energy-balance rows all read 0.000 percent and that is **not**
evidence of anything — on a sealed box the boundary heat balance is nearly an
identity, and C3 exists to say exactly how far that row can and cannot be
trusted. And the core stratification is measured and **ungraded**, because its
reference was never obtained.

## Trust tier, unchanged by this result

Per the specification's Section 2.5, passing the **laminar** rung alone
"supports verification claims only and caps at TREND ONLY". This rung is a
verification result against a numerical benchmark. It is not an experimental
comparison and it does not lift anything above TREND ONLY. The turbulent rung
of the same gate — the only one that can — was **not run** and is not
authorized.

## The reference, and its tier

Tier **SECONDARY**, unchanged and not upgraded by anything here. de Vahl Davis
(1983) is paywalled (`10.1002/fld.1650030305`, Unpaywall `is_oa: false`) and was
not read; the values are carried from Han and Xie (2019) Table 3, corroborated
by Gjesdal (2003) Table 1 and INL/EXT-09-15333 Table 3 where they overlap. The
specification says all of this and the analyser reproduces the tier string into
its own output so a reader of the JSON cannot lose it.

## The one thing that is measured and NOT graded

The specification records that the **laminar core stratification reference was
NOT OBTAINED** — no read source tabulates it and both candidate primaries are
paywalled. Stratification is therefore **measured and reported below, and it
grades nothing**. A rung must never pass against a number the executing agent
produced itself. The same holds for the turbulent-rung Nusselt reference, which
is also NOT OBTAINED and is outside this rung.

## The gate table

Reproduced verbatim from `K0c_runs/GATE_TABLE.md`, which
`K0c_runs/analyse_k0c.py` generates from `K0c_runs/gate_k0c.json`. **No figure
in this document was retyped by hand** — transcription is how a number loses
its source.

Reference tier: SECONDARY (Han and Xie 2019 Table 3, attributed to de Vahl Davis 1983, which is paywalled and was not read).  
Reference values and pass bands parsed at run time out of `docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`.  
Graded estimator: Nu_2pt (solver-consistent snGrad from raw T cells); declared before the run, see this file's docstring.  
Deviation is REL = 100 x |solved - reference| / |reference|, graded on the FINE mesh; the coarse mesh of the mandatory pair is carried in every row.

| Ra | quantity | reference | coarse mesh | coarse dev % | FINE mesh | **FINE dev %** | band % | verdict | 3-pt estimator | 3-pt dev % |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1e+03 | Nu_avg | 1.1180 | 1.1191 | 0.096 | 1.1181 | **0.010** | 1.0 | PASS | 1.1181 | 0.012 |
| 1e+03 | Nu_max | 1.5050 | 1.5128 | 0.520 | 1.5080 | **0.199** | 2.0 | PASS | 1.5080 | 0.196 |
| 1e+03 | Nu_min | 0.6920 | 0.6892 | 0.410 | 0.6907 | **0.182** | 2.0 | PASS | 0.6908 | 0.172 |
| 1e+03 | u1max | 3.6490 | 3.6326 | 0.449 | 3.6455 | **0.096** | 2.0 | PASS | n/a | n/a |
| 1e+03 | u2max | 3.6970 | 3.6925 | 0.121 | 3.6966 | **0.010** | 2.0 | PASS | n/a | n/a |
| 1e+03 | energy_balance | n/a (a defect, not a target) | 0.0000 | 0.000 | 0.0000 | **0.000** | 0.5 | PASS | n/a | n/a |
| 1e+04 | Nu_avg | 2.2430 | 2.2574 | 0.644 | 2.2480 | **0.222** | 1.0 | PASS | 2.2483 | 0.235 |
| 1e+04 | Nu_max | 3.5280 | 3.5772 | 1.394 | 3.5427 | **0.418** | 2.0 | PASS | 3.5430 | 0.426 |
| 1e+04 | Nu_min | 0.5860 | 0.5831 | 0.490 | 0.5845 | **0.249** | 2.0 | PASS | 0.5849 | 0.190 |
| 1e+04 | u1max | 16.1780 | 16.1185 | 0.367 | 16.1703 | **0.047** | 2.0 | PASS | n/a | n/a |
| 1e+04 | u2max | 19.6170 | 19.5959 | 0.108 | 19.6258 | **0.045** | 2.0 | PASS | n/a | n/a |
| 1e+04 | energy_balance | n/a (a defect, not a target) | 0.0000 | 0.000 | 0.0001 | **0.000** | 0.5 | PASS | n/a | n/a |
| 1e+05 | Nu_avg | 4.5190 | 4.5590 | 0.886 | 4.5310 | **0.266** | 1.0 | PASS | 4.5320 | 0.288 |
| 1e+05 | Nu_max | 7.7170 | 7.8902 | 2.245 | 7.7639 | **0.608** | 2.0 | PASS | 7.7668 | 0.646 |
| 1e+05 | Nu_min | 0.7290 | 0.7245 | 0.614 | 0.7272 | **0.252** | 2.0 | PASS | 0.7277 | 0.175 |
| 1e+05 | u1max | 34.8100 | 34.7848 | 0.072 | 34.7552 | **0.157** | 2.0 | PASS | n/a | n/a |
| 1e+05 | u2max | 68.2200 | 68.4397 | 0.322 | 68.6524 | **0.634** | 2.0 | PASS | n/a | n/a |
| 1e+05 | energy_balance | n/a (a defect, not a target) | 0.0000 | 0.000 | 0.0000 | **0.000** | 0.5 | PASS | n/a | n/a |
| 1e+06 | Nu_avg | 8.8000 | 8.8848 | 0.964 | 8.8518 | **0.588** | 1.0 | PASS | 8.8560 | 0.637 |
| 1e+06 | Nu_max | 17.9250 | 17.9817 | 0.316 | 17.7354 | **1.057** | 3.0 | PASS | 17.7596 | 0.923 |
| 1e+06 | Nu_min | 0.9890 | 0.9754 | 1.376 | 0.9777 | **1.139** | 3.0 | PASS | 0.9789 | 1.025 |
| 1e+06 | u1max | 64.6300 | 64.9496 | 0.495 | 64.8916 | **0.405** | 2.0 | PASS | n/a | n/a |
| 1e+06 | u2max | 219.3600 | 220.4954 | 0.518 | 220.5412 | **0.538** | 2.0 | PASS | n/a | n/a |
| 1e+06 | energy_balance | n/a (a defect, not a target) | 0.0000 | 0.000 | 0.0000 | **0.000** | 0.5 | PASS | n/a | n/a |

**GATE PASS** — 0 of 24 graded rows failed.

## Convergence, on the graded quantity

Criterion: Nu_avg, as printed by the running solver's own in-pass function object every 50 iterations, has a PEAK-TO-PEAK SPREAD below 0.02 percent over the last 400 outer iterations of the case. 0.02 percent is one fiftieth of the tightest band on this gate. A fixed iteration window is used rather than a fraction of the run because a last-quarter window silently loosens as a run is extended. The spread is gated rather than the endpoint difference because Ra1e6_m192 approaches steady state as a decaying oscillation of period about 400 iterations, and an endpoint test over a 400-iteration window can be aliased by exactly that.

| case | peak-to-peak spread over last 400 iterations, % | endpoint drift, % | residualControl met | final T initial residual | mesh | wall clock s |
| --- | ---: | ---: | :---: | ---: | ---: | ---: |
| Ra1e3_m32 | 0.000936 | 0.000198 | yes | 2.32e-09 | 32x32 | 5.6 |
| Ra1e3_m64 | 0.002813 | 0.002813 | yes | 4.29e-09 | 64x64 | 36.1 |
| Ra1e4_m40 | 0.001999 | 0.001894 | yes | 2.73e-09 | 40x40 | 8.1 |
| Ra1e4_m80 | 0.003590 | 0.000750 | yes | 4.72e-09 | 80x80 | 69.2 |
| Ra1e5_m64 | 0.002039 | 0.001874 | yes | 6.08e-09 | 64x64 | 37.2 |
| Ra1e5_m128 | 0.000904 | 0.000309 | yes | 8.94e-09 | 128x128 | 355.5 |
| Ra1e6_m128 | 0.000258 | 0.000145 | yes | 7.15e-09 | 128x128 | 453.9 |
| Ra1e6_m192 | 0.000219 | 0.000044 | yes | 9.98e-09 | 192x192 | 1081.7 |
| C1_Ra1e5_m128_g0 | 0.008403 | 0.008403 | yes | 9.77e-09 | 128x128 | 58.6 |
| C2_Ra1e5_m128_dT110 | 0.001479 | 0.001065 | yes | 8.00e-09 | 128x128 | 366.5 |
| C3_Ra1e5_m64_source | 0.123720 | 0.123720 | yes | 8.90e-09 | 64x64 | 31.7 |

## The snGrad cross-check

Path 1 (wall flux built from the raw T cells, this script) against path 3 (`scripts/heat_balance.py`, which recomputes the in-pass snGrad integral through postProcess on the same written field). Reading `grad(T)` back from disk instead is wrong by 37 percent on this case class.

| case | relative difference | heat_balance.py exit | imbalance % | Q_hot W |
| --- | ---: | ---: | ---: | ---: |
| Ra1e3_m32 | 1.98e-16 | 0 | 0.00003 | 3.188275e-06 |
| Ra1e3_m64 | 1.99e-16 | 0 | 0.00003 | 3.185527e-06 |
| Ra1e4_m40 | 4.63e-13 | 0 | 0.00003 | 6.431513e-05 |
| Ra1e4_m80 | 1.38e-15 | 0 | 0.00007 | 6.404578e-05 |
| Ra1e5_m64 | 3.90e-16 | 0 | 0.00001 | 1.298878e-03 |
| Ra1e5_m128 | 9.80e-16 | 0 | 0.00002 | 1.290899e-03 |
| Ra1e6_m128 | 1.60e-15 | 0 | 0.00000 | 2.531308e-02 |
| Ra1e6_m192 | 2.21e-15 | 0 | 0.00000 | 2.521889e-02 |
| C1_Ra1e5_m128_g0 | 1.11e-15 | 0 | 0.00003 | 2.849054e-04 |
| C2_Ra1e5_m128_dT110 | 5.71e-16 | 0 | 0.00001 | 1.461400e-03 |
| C3_Ra1e5_m64_source | 3.66e-16 | 1 | nan | -1.036849e-03 |

## Controls

### C1 — gravity off. KIND: **RECOGNITION** (gross), and it also demonstrates **reachability**

Plant: `constant/g` set to `(0 0 0)` on an exact twin of the Ra = 1e5 fine case.
With no buoyancy the cavity solves pure one-dimensional conduction and Nu is
exactly 1 at every height.

| | predicted, registered in advance | measured |
| --- | --- | --- |
| Nu_avg | 1.000 | 1.0000098 |
| Nu_max | 1.000 | 1.0000102 |
| Nu_min | 1.000 | 1.0000096 |
| u1max, u2max | 0.000 | 0.000, 0.000 |
| REL(Nu_avg) vs the Ra = 1e5 reference | 77.87 percent | **77.87 percent** |
| gate verdict on this case | FAIL | **FAIL** — every Nu row failed |

**In-log witness of the plant**: the running solver printed
`Solving for Ux, Initial residual = 0` at **every one** of its momentum solves
(`momentum_identically_zero = True`), and its `hotT`/`coldT`
function objects reported a wall dT of 1.0881622 K — **unchanged**
from the graded case. That pair of facts is what identifies *which* plant is in
the solver: gravity, not the temperature difference.

### C2 — Rayleigh number raised 10 percent. KIND: **RECOGNITION at the gate's own scale**

This is the control that answers "can this gate fail?" for the row that
actually grades the rung. The predicted shift was derived from the gate's own
reference table before the run: Nu ~ Ra^n with n between 0.289 and 0.304 from
the table's own successive ratios, so a 10 percent Ra error gives
n x ln(1.10) = 2.76 to 2.90 percent.

| | predicted, registered in advance | measured |
| --- | --- | --- |
| Nu_avg shift vs the graded Ra = 1e5 case | +2.6 to +3.0 percent | **+2.916 percent** |
| Nu_avg | 4.63 to 4.66 | 4.6632 |
| REL vs the Ra = 1e5 reference 4.519 | 2.6 to 3.0 percent, exceeding the 1.0 percent band | **3.190 percent** |
| gate verdict on this case | FAIL | **FAIL** |

**In-log witness of the plant**: the wall temperatures the *running solver*
printed every 50 iterations give a dT of
1.1969784 K against the graded case's
1.0881622 K — a ratio of
**1.1000000**, and a Rayleigh number reconstructed from
the solver's own output of 1.100000e+05. A plant
living only in `0.orig/T` would not move those lines.

**This is the load-bearing control.** A 1.0 percent band that could not see a
10 percent error in the driving parameter would make the rung's pass mean
nothing. It sees it with a factor of three to spare.

### C3 — a planted volumetric heat source. KIND: **REACHABILITY** of the energy-balance row, and a stated limit

| | predicted, registered in advance | measured |
| --- | --- | --- |
| net boundary flux recovers the source | -5.000e-03 W to within 0.1 percent | **-4.999996460e-03 W**, error **-0.000071 percent** |
| energy-balance row | FAIL, tens of percent against a 0.5 percent band | **341.73 percent — FAIL** |
| `scripts/heat_balance.py` exit status | non-zero | **1** |

**In-log witness of the plant**: `buoyantBoussinesqSimpleFoam` echoed
`Selecting finite volume options type scalarSemiImplicitSource` / `Source: heatPlant`
at construction in every stage of the run. A source sitting in
`constant/fvOptions` but never constructed would leave that log empty.

**And the limit, which matters more than the pass.** On a sealed, impermeable,
steady cavity with no source, the boundary heat balance is very nearly an
**identity**: the discrete temperature equation conserves at every iteration,
converged or not. That is K0b's C3 finding and it applies unchanged here. Every
energy-balance row in the gate table above reads 0.000 percent, and **that is
not evidence that the physics is right — it is what a sealed box does.** C3
shows the row's FAIL branch is reachable and that the row recognises a genuine
conservation defect. It does **not** show the row has any power against the
failure modes this rung actually faces: wrong Ra, wrong Pr, under-resolved
boundary layers. The row is reported because the specification requires it, and
it is not counted as evidence for the rung.

### C4 — comparator mutation. KIND: **REACHABILITY of every band, one at a time**. No compute

C1 to C3 show that *some* rows can fail. They say nothing about whether the
other rows are wired to pass. C4 perturbs each solved value in turn by 1.5x its
own band, in the direction *away* from the reference, and requires that row —
and only that row — to flip to FAIL.

**Result: `every_row_reachable = True`** across all
24 rows. No row on this gate is decorative.

### C5 — relaxation invariance. KIND: **RECOGNITION of a confound**

Added after the convergence refusal described below forced a change of
relaxation factors mid-campaign. Changing relaxation is supposed to change the
path to the fixed point and not the fixed point. C5 asks rather than asserts:
every case that had **already met the convergence criterion** under the stage-1
factors is a witness, and its Nu_avg must not move by more than the criterion
itself when re-converged under the stage-2 factors.

| witness | Nu_avg, stage-1 factors | Nu_avg, final | shift | verdict |
| --- | ---: | ---: | ---: | --- |
| Ra1e3_m32 | 1.119071 | 1.119078 | 0.00062 percent | PASS |
| Ra1e4_m40 | 2.257398 | 2.257443 | 0.00198 percent | PASS |
| Ra1e5_m64 | 4.558948 | 4.559023 | 0.00166 percent | PASS |
| Ra1e6_m128 | 8.884714 | 8.884817 | 0.00117 percent | PASS |

Criterion 0.02 percent; the largest shift is
0.00198 percent, a factor of ten inside it.
The relaxation change moved the path, not the answer.

**Four witnesses out of eleven cases, and why the other seven are not — added
2026-08-17 after the question was asked.** C5 originally reported only its
witnesses, so the seven non-witnesses vanished without saying why. Five are
excluded on the stated rule (their stage-1 drift was above the 0.02 percent
criterion, so they had not converged under the stage-1 factors and any later
movement would be convergence rather than a change of answer). **Two —
`Ra1e5_m128` and `Ra1e6_m192` — were excluded for a different reason that the
report did not distinguish: they have no row in `stage1_values.json` at all.**
`Ra1e5_m128` was the pilot for the accelerated continuation and was continued
before the snapshot was taken; `Ra1e6_m192` was rebuilt from scratch after the
watcher race and never had a stage-1 leg under those factors. Neither is data
loss, and neither is a poweroff casualty — the file was written at 16:20:50,
forty minutes before the 17:45:14 poweroff, parses cleanly and is byte-identical
to its committed blob.

**`Ra1e5_m128` carries a graded row, so this was settled by execution rather
than by argument.** `stage1_values.json` is read in exactly one place in
`analyse_k0c.py`, inside the C5 block, and feeds only the witness list. With the
file renamed away, that case's entire gate row re-measures **bit for bit** —
Nu_avg 4.531017, Nu_max 7.763917, Nu_min 0.727163, u1max 34.755242,
u2max 68.652353, every delta 0.00e+00, every verdict unchanged. **The gate row
never came from that file.** Its stage-1 figures are recoverable anyway: the
4.67 percent quoted throughout this document recomputes to 4.66904 percent from
the case's committed solver log alone, by a route method-controlled against the
four cases that do have snapshot rows, which it reproduces to better than 1e-06.
And `Ra1e5_m128` would have been excluded as a witness even with its row present,
because 4.669 percent is far above the 0.02 percent admission rule.

C5 now reports every non-witness with its reason and asserts the arithmetic
`witnesses + excluded == cases` (**4 + 7 = 11**). That reporting is
mutation-proven, not assumed: removing a genuine witness from the snapshot moves
it into `excluded` with the "absent" reason and drops the witness count to three,
so the report is driven by the data rather than printing the same thing whatever
it is finding. A filter nobody can see is a filter nobody can question.

## The controls' preamble, kept where it belongs

Predictions were registered with a timestamp in
`K0c_runs/CONTROL_PREDICTIONS.txt` **before any control result was read**, and
the whole file is reproduced verbatim into `K0c_runs/gate_k0c.json`, so the
prediction and the outcome travel together and neither can be quietly adjusted
to fit the other.

*Reachability* below means: the FAIL branch of this check is reachable at all —
the band is not decorative. *Recognition* means: the check tells a physically
wrong answer from a right one, at the magnitude the gate cares about.

## Core stratification — MEASURED, UNGRADED

Repeated here because it is the one thing that must not drift into a pass. The
specification records the laminar core stratification reference as **NOT
OBTAINED**. No read source tabulates it; de Vahl Davis (1983) and Le Quere
(1991) are both paywalled, `is_oa: false` on both DOIs, checked 2026-08-17.
**These are measurements with nothing to compare them to, and they grade
nothing.** S is the non-dimensional vertical temperature gradient of the core,
d(theta)/d(y/L) with theta = (T - T_cold)/dT, fitted by least squares over the
middle 25 percent of the height at mid-width; the central-difference value at
the geometric centre is given beside it as a robustness check.

| Ra | fine mesh | S (least squares) | S (central difference) | coarse mesh S | status |
| ---: | --- | ---: | ---: | ---: | --- |
| 1e+03 | Ra1e3_m64 | +0.5187 | +0.5311 | +0.5198 | **UNGRADED** |
| 1e+04 | Ra1e4_m80 | +0.8369 | +0.8359 | +0.8399 | **UNGRADED** |
| 1e+05 | Ra1e5_m128 | +1.0368 | +1.0702 | +1.0407 | **UNGRADED** |
| 1e+06 | Ra1e6_m192 | +0.9298 | +0.9150 | +0.9324 | **UNGRADED** |

The two estimators agree to within 0.02 to 0.035 across the ladder and the
coarse and fine meshes agree to within 0.005, so the numbers are stable
measurements rather than mesh artefacts. Pure conduction gives S = 0 exactly,
so they are also not identities. **None of that makes them a pass**, and no
part of this rung's verdict rests on them. To close the gap: obtain de Vahl
Davis (1983) or Le Quere (1991) through the MIT access route
(`docs/research/MIT_ACCESS_DOCKET.md` pattern) and extend the specification's
Section 1.3 by addendum. Until then this row stays ungraded whatever a solve
produces.

The same applies, outside this rung, to the **turbulent-rung Nusselt
reference**, also NOT OBTAINED. The turbulent rung was not run.

## The K0b mesh-sensitivity pair

Run under the second half of the authorization, at the 15 core-minutes proposal
P2 costed on a measured basis. Two new legs, 32x32 and 128x128, completing the
triple with the committed 64x64 leg at `183c91c0`. Exactly one line differs
between the legs — the cell counts in `blockMeshDict` — and `build_and_run.sh`
refuses if any other dictionary differs byte-for-byte from the committed case.
K0b's Pr = 0.706814 and its `limitedLinear`/`linearUpwind` schemes are kept
deliberately, so **the de Vahl Davis values do not apply to these cases and are
not used**: K0b is a capability rung graded against no published datum and this
does not change that.

| quantity | 32x32 | 64x64 (committed) | 128x128 | change 64 to 128 | observed order p | GCI on the fine pair |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Nu_avg_hot | 4.6497 | 4.5538 | 4.5288 | 0.552 percent | 1.94 | 0.243 percent |
| Nu_max_hot | 8.2613 | 7.8726 | 7.7573 | 1.487 percent | 1.75 | 0.784 percent |
| Nu_min_hot | 0.7172 | 0.7257 | 0.7276 | 0.269 percent | 2.12 | 0.100 percent |
| V_star_max | 66.4840 | 68.3723 | 68.6112 | 0.348 percent | 2.98 | 0.063 percent |
| U_star_max | 35.3073 | 34.8814 | 34.7968 | 0.243 percent | 2.33 | 0.075 percent |
| stratification_S_leastsq_mid25pct | 1.0551 | 1.0413 | 1.0374 | 0.372 percent | 1.84 | 0.180 percent |

**What this says about K0b's published numbers.** They are mesh-sensitive at
the sub-percent level and they were quoted from a single mesh. K0b reported
Nu = 4.5538; the Richardson limit of the triple is
4.520, so the single-mesh number was
0.75 percent high. Observed orders land between
1.75 and 2.98, which is
second-order behaviour, and every GCI is below
0.78 percent. P2's premise — "a single-mesh number
is not a converged number" — is confirmed, and the size of the effect is now a
number rather than a worry.

**Cost: 12.818 core-minutes against 15 authorized.** Only the two new
legs are charged; the 64x64 leg was paid for at `183c91c0` and is re-measured
in place, not re-run.

## Cost

Single-core solves throughout, so core-minutes is the sum of the per-case wall
clocks. **No monetary figure appears anywhere in this document**: there is no
verified rate for this machine and inventing one would be an underived number.

| | core-minutes |
| --- | ---: |
| K0c, the eleven cases that produced the table above | **41.73** |
| K0c, discarded and re-run (reconstructed below) | **~44.3** |
| K0b mesh-sensitivity pair | **12.82** (authorized 15) |
| **total charged to this session** | **~98.9** |

Per-case figures are in `K0c_runs/GATE_TABLE.md` and in each case's `COST.txt`.
Wall clock for the whole session was far shorter than the core-minutes total
because up to ten cases ran concurrently on a 16-core machine; the longest
single case, `Ra1e6_m192`, took 18.0 core-minutes across its two stages.

**The 44.3 discarded core-minutes are reconstructed, not measured**, because
the processes that spent them were killed and never wrote their `COST.txt`
lines. The reconstruction uses this machine's own measured per-iteration cost
for the same case (407.745 s for 4000 iterations of the 192x192 mesh = 0.102
s/iteration in stage 1; 673.914 s for 3885 iterations = 0.173 s/iteration in
stage 2) applied to iteration counts read out of the discarded logs before they
were deleted: 12000 + 8271 stage-1 iterations from the contaminated pair
(2068 s) and about 3400 abandoned stage-2 iterations (588 s). It is labelled an
estimate because it is one.

## What did not work

Recorded because a rung that hides its failures teaches nothing, and because
three of these five changed the result.

**1. Every fine mesh was under-converged, and the convergence criterion is what
caught it.** Under K0b's relaxation factors (U 0.3, p_rgh 0.7, T 0.5) every
coarse mesh met the criterion and every fine mesh missed it by two to three
orders of magnitude: 2.19, 3.98 and 4.67 percent of drift in Nu_avg against a
0.02 percent criterion, and 14.65 percent on the g = 0 control. The cause is
that an under-relaxed SIMPLE outer loop moves the smooth modes at a rate that
falls off like 1/N^2, so doubling the mesh needs roughly four times the
iterations. **Had this gate graded on "the residuals stopped moving", the
Ra = 1e3 pair would have reported a FINE mesh further from the benchmark than
its own COARSE mesh** — 1.0940 against 1.1191 — and the rung would have failed
on iteration error while calling it a mesh result. The g = 0 control is the
clean demonstration: its exact answer is Nu = 1 and after 3000 iterations it
was still at 1.328, with the core sitting near its initial 300 K. Every case
was continued from `latestTime` under accelerated factors; C5 above establishes
that this changed the path and not the answer.

**2. The snGrad cross-check disagreed at 5.8e-05, and the cause was not the
trap.** The wall flux built from raw T cells and the same integral recomputed
by `scripts/heat_balance.py` differed by 0.0058 percent at Ra = 1e3 — small,
but far above the 1e-6 the check demands and with no physical cause on an
orthogonal mesh. The first guess, ASCII write precision, was wrong: rewriting
the fields at `writePrecision 16` did not move the number by a digit. The
actual cause is that **stage 1 wrote its restart file at `writePrecision 10`,
truncating the hot-wall boundary value from 300.005440811 to 300.0054408, and
stage 2 restarted from that file** — so from stage 2 onward the solver held a
dT 1.1e-08 K below the intended one, while the analyser was still reading the
intended value out of `0.orig`. The arithmetic closes exactly: 32 faces x 640
1/m x 1.1e-08 K x 3.125e-05 m^2 = 7.0e-09 against an integral of 1.218e-04, is
5.78e-05. Reading the wall value **the solver actually held, at the analysed
time** took the cross-check to 2e-16 — machine precision — across all eleven
cases. The wrong first guess is recorded alongside the right answer because the
wrong guess is the instructive part: a plausible cause that survives one test
and dies on a second is worth more than a cause that was never tested.

**3. I raced my own watcher and destroyed a case.** A background script was
armed to continue `Ra1e6_m192` as soon as its first stage finished. Its wait
condition — a `pgrep` piped into a `grep` for the case directory — returned a
false negative on one poll, so it started a **second** solver in the same case
directory, from time 0, while the first was still running. Both wrote the same
files. The case was discarded and rebuilt from `build_cases.py` (which grew a
case selector for exactly this repair, so that fixing one case did not throw
away eight good solves) and re-run clean. Roughly 34.5 core-minutes were burned
producing nothing. The transferable lesson is narrow and concrete: **a
liveness check that can return a false negative is not a lock**, and the cost
of getting it wrong is not a stale read but a corrupted case.

**4. `writeInterval` equal to `endTime` meant a long run had nothing to show
for itself.** `Ra1e6_m192` met the convergence criterion at iteration 6400 but
its only scheduled write was at 24000, and this build has
`writeNowSignal -1` so the running solver could not be asked to write. The
choice was to wait roughly 50 minutes for `residualControl`, or to kill it and
lose everything since the last write. It was killed and re-run with
`writeInterval 1000`, which cost about 9.8 core-minutes to redo and would have
cost nothing to have set in the first place. **A long solve with one write at
the end is a solve with a single point of failure.**

**5. `scripts/heat_balance.py` reports `nan` for the imbalance when no patch
carries heat inward.** On the C3 planted-source case every wall carries heat
*out*, so the denominator of `imbalance% = 100 |sum Q| / sum(Q > 0)` is zero.
The script **fails safe** — `nan` fails its own comparison, so it returned exit
1 and refused the case, which is the correct verdict — but the percentage it
prints is `nan` rather than a number. **This was not patched.** It is a
standing check other rungs depend on, its failure mode here is conservative,
and changing it is outside this rung's scope. It is recorded as a proposal
below.

## Proposals, not actions

**P1. Give `heat_balance.py` a defined imbalance when all patches are outward.**
Normalising by `max(sum(Q>0), |sum(Q<0)|)` would give C3 a real percentage
instead of `nan` without changing any existing answer, since the two are equal
whenever both signs are present. Script work, no compute. Needs a mutation test
that the existing calibration cases are unmoved.

**P2. The laminar stratification row stays open.** It is the only part of this
gate's laminar mandate that cannot be closed by compute. Acquisition, not
solving, is the blocker.

## What was NOT run, and remains unauthorized

The K0c **turbulent** rung (Betts and Bokhari, ERCOFTAC Case 079), **K0d**,
**K2b**, the **rack-row module**, and any **turbulent SST** case. None of these
was run and none is authorized; each needs the owner's word with a cost
estimate. Nothing in this document should be read as evidence about any of
them, and the trust tier this rung supports is capped at TREND ONLY by the
specification's own Section 2.5 because no experimental comparison was made.

---

## Addendum, 2026-08-17 — P1 is closed, and its remedy was refused

Appended rather than inserted: citations reach this file by line number, and
rewriting section "Proposals, not actions" in place would move every line under
it. Nothing above this rule is altered.

**P1 as filed above** asked for `scripts/heat_balance.py` to report a defined
imbalance when every patch carries heat outward, by normalising with
`max(sum(Q>0), |sum(Q<0)|)`, "without changing any existing answer".

**Closed at rung K1c: the complaint is adopted, the remedy is rejected.** With
no inward patch, `sum(Q<0)` *is* the net, so the proposed ratio is
|net| / |net| = **1 exactly** — it would print 100.0000 % for every such case
whatever the source size. That is a second identity, and by this campaign's own
W-2 finding an identity cannot gate anything. Measured rather than argued: plant
the mirror defect, a **sink** instead of a source, so that every patch carries
heat *in* and `Q_out` is zero, and the **existing** code already prints
`100.000000000 %` (K1c control `KC2_sink_5mW`).

The same measurement found a second failure P1 did not anticipate: at
intermediate iterations of a planted case, an adiabatic patch carrying
**+7.94e-24 W** of floating-point residue made `Q_in > 0` true and the reported
imbalance **6.25e+22 %**. A denominator of residue is not a denominator.

**Adopted instead:** the ratio is declared UNDEFINED whenever `Q_in <= 0` or
`Q_in < |Q_net|`, with a named reason and the net leak in watts, and the case
fails. Proved not more permissive by running HEAD's script and the patched one
over the same 13 sets of fields: **0 exit-code changes, 0 pre-existing JSON keys
moved.** C3's verdict is unchanged — exit 1, plant witnessed in the solver log.

**P2 remains open**, unchanged: the laminar stratification row still needs
acquisition, not solving.

Two further findings from that rung touch cases in this tree and are filed to
the docket rather than acted on here: **D350** (this rung's `C3_Ra1e5_m64_source`
reads 0.123720 % against the 0.02 % criterion this rung established — the same
figure the convergence table above prints, on a case this rung did not grade)
and **D351** (a planted defect moves the Rayleigh number the auditor reports).

Full record: `docs/campaigns/F14-cooling-ladder/K1_STANDING_THERMAL_CHECKS.md`.
