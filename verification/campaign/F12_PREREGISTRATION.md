# F12 pre-registration: RAE 2822, AGARD AR-138 Case 9

**Written 2026-07-30, before any solver was launched on this case.** Nothing
below is edited after the fact. If the result falsifies the prediction, the
prediction stays as written and the record says so, exactly as F6b's did.

## The case

RAE 2822 aerofoil, AGARD AR-138 Case 9. Re = 6.5e6 on chord, transonic,
shock-bearing, attached (Case 10 is the separated one; this is not that).

**Conditions solved.** Two, because the published corrected conditions for this
case do not agree and picking one silently is the classic way to be confidently
wrong here.

| Convention | Mach | alpha (deg) | Where it comes from |
| --- | --- | --- | --- |
| Workshop (primary) | 0.734 | 2.79 | International Workshop on High-Order CFD Methods, case C2.2 / ADIGMA MTC5 |
| Tape | 0.730 | 2.79 | The reference data's own record: measured Mach, corrected incidence |

The incidence correction, 3.19 deg geometric to 2.79 deg corrected, is common
to both and is carried by the reference data itself. Only the Mach differs, by
0.004. The primary grade is at the workshop condition; the tape condition is
solved at one mesh level so the sensitivity to the disagreement is measured.

A third convention, M = 0.734 with alpha = 2.54 deg, circulates in the
literature and is **not** used: 2.54 deg is the tape's corrected incidence for
Case 6, not Case 9.

## The reference

Cook, P.H., McDonald, M.A., Firmin, M.C.P., "Aerofoil RAE 2822 - Pressure
Distributions and Boundary Layer and Wake Measurements", AGARD AR-138 (1979).
Digitised as AFOSR-HTTM/Stanford flow case 8621 (evaluator R. E. Melnik, 1981),
hosted by the NASA Turbulence Modeling Resource. Secondary but authoritative:
it is a transcription made by the experiment's own AGARD evaluator, not the
AR-138 document itself, and it is labelled secondary everywhere it is used.

Measured quantities graded against: 52 upper-surface and 50 lower-surface
pressure taps, CN = 0.803, CM = -0.099, CD = 0.0168. The experimenters quote
their tap uncertainty as Cp to within +/- 0.0026 at this Reynolds number.

## Gates, declared now

A run is admitted as evidence only if the mesh gate and the convergence gate
both pass. The physics gates are then graded on the **finest mesh at the
workshop condition**.

**Admission gate A, mesh.** Every mesh in the ladder: max non-orthogonality
<= 70 degrees and max skewness <= 4, boundary faces included, per
`docs/standards/MESH_STANDARD.md`. Aspect ratio is advisory there and is
recorded with its alignment justification, not gated.

**Admission gate B, convergence.** The solver must print its own convergence
statement. A small-looking residual is not a substitute (LESSONS L-14, L-15).
A run that does not converge is not a result and is not graded.

**Gate 1, surface pressure (primary).** RMS deviation of the computed Cp from
the measured taps, CFD interpolated onto the tap stations:

- upper surface RMS <= **0.08**
- lower surface RMS <= **0.04**

Basis for the numbers: F1 (ONERA M6, 3D, 399k cells) was recorded GATE REACHED
at upper-surface RMS 0.049 to 0.114 with pressure-side 0.013 to 0.027. This is
a two-dimensional, wall-resolved case with far more surface resolution per
chord, so the bar is set inside F1's achieved band rather than at it.

**Gate 2, shock location.** |x_shock(CFD) - x_shock(experiment)| <= **0.020**
chord, both measured by the same definition: the chordwise station where
upper-surface Cp crosses the critical (sonic) value from below on the
recompression, linearly interpolated between bracketing points.

Why this definition and not steepest-gradient: F2's record documents that a
steepest-gradient detector can only return values on the sample lattice, that
its resolution there was 0.052 chord, and that a deviation smaller than one
lattice step was wrongly narrated as a physical shift. The sonic crossing is
continuous in x, is identically defined on the experimental taps and the CFD,
and does not quantise. Steepest-gradient is also recorded, with its own
resolution quoted beside it, and is never quoted alone.

Basis for 0.020: the experimental tap spacing through the shock is 0.025 chord,
so the reference's own shock position is resolved to roughly +/- 0.0125. A
tolerance of 0.020 is a little over one tap interval and cannot be met by luck.

**Gate 3, normal force.** |CN - 0.803| / 0.803 <= **5%**.

**Gate 4, drag.** |CD - 0.0168| / 0.0168 <= **20%**. Declared generous, and
declared generous *now* rather than after seeing the number: the reference CD
is a wake-traverse total drag from a tunnel, and the comparison is against a
fully turbulent, free-air, finite-domain RANS. It is a one-sided comparison and
20% is the honest width for it.

**Reported, not gated: CM.** The measured CM is -0.099. Pitching moment on this
section is dominated by the aft-loaded lower surface and by the trailing-edge
closure, both of which are interpolation-sensitive on a 65-station coordinate
table. It is reported with its deviation and it does not decide the verdict.
Saying so in advance is the point.

**Overall verdict.** PASS requires admission gates A and B plus Gates 1, 2, 3
and 4, all on the fine mesh at the workshop condition. Anything less is
recorded as a documented failure in the campaign record and does not become a
filmed act, per the standing no-failures-on-camera rule.

## Mesh study

Three levels, factor two in every direction, so an observed order of
convergence is meaningful:

| Level | surface cells per quarter | wake | wall-normal | cells |
| --- | --- | --- | --- | --- |
| coarse | 48 | 48 | 80 | 23,040 |
| medium | 96 | 96 | 160 | 92,160 |
| fine | 192 | 192 | 320 | 368,640 |

Wall-normal first cell 2e-6 chord, targeting y+ below 1 so the boundary layer
is resolved rather than bridged. Reported for every level: cells, mesh quality,
convergence statement, CN, CD, CM, both shock measures and both Cp RMS values.
A single-mesh result is not shipped.

Two further runs, both at medium: the tape condition (M = 0.730) to measure the
correction-convention sensitivity, and a doubled far-field radius to measure
the domain-size sensitivity of a lifting transonic case.

## Prediction, recorded before the data is seen

1. The shock will sit **downstream** of the measured position, by 0.01 to 0.03
   chord. Linear eddy-viscosity closures under-predict the shock-induced
   thickening of the boundary layer, which is what pushes the shock forward;
   the same one-sided bias is already on this lab's record as F6a's +13.95%
   reattachment and F6b's +63% to +66%.
2. CN will be **over-predicted** by 0 to 4%, for the same reason.
3. CD will be **under-predicted**, by 5 to 20%, because a fully turbulent
   free-air RANS omits both the tripped laminar run and the tunnel's own
   contributions to the measured wake momentum deficit.
4. Upper-surface Cp RMS will be dominated by a small number of taps inside the
   shock foot, not spread evenly along the chord.

If the shock lands upstream of experiment, prediction 1 is falsified and the
record will say so in those words.

---

## COSTED ADDENDUM — 2026-08-23

**Document version 1.0 (2026-07-30, unversioned original) -> 1.1.**

**lines whose number changed above this section: 0**

Nothing above this line is struck, rewritten, renumbered or reworded. This
addendum adds **cost and only cost**. It alters no gate, no threshold, no cap
declared above (none was), no label, no mesh level, no condition, no prediction
and no verdict rule. Gates A, B, 1, 2, 3 and 4, the CM reporting clause and the
overall PASS rule stand exactly as written on 2026-07-30.

### 1. Why this amendment is legal, and how that was checked

Standing rule 2: *"Before first compute, amendments are legal and must state the
condition and how it was checked (name the run directory that does not exist)."*

The condition is that **no compute has ever been spent on F12**. It was checked
on 2026-08-23 at 19:56 UTC by reading the disk, not by recalling the record:

```
$ date -u
Sun Aug 23 19:56:13 UTC 2026

$ find verification/runs/F12_runs/ | sort
verification/runs/F12_runs/
verification/runs/F12_runs/reference
verification/runs/F12_runs/reference/decode_tape.py
verification/runs/F12_runs/reference/f8621.txt
verification/runs/F12_runs/reference/nparc_geom.txt
verification/runs/F12_runs/reference/nparc_yl.pts
verification/runs/F12_runs/reference/nparc_yu.pts
verification/runs/F12_runs/reference/rae2822_case9_cp_lower.dat
verification/runs/F12_runs/reference/rae2822_case9_cp_upper.dat
verification/runs/F12_runs/reference/rae2822_coordinates.dat

$ find verification/runs/ -iname '*F12*' | sort
verification/runs/F12_runs
```

`verification/runs/F12_runs/` contains exactly one subdirectory, `reference/`,
holding eight digitised reference files and the decoder that produced them. It
contains **no case tree**: there is no `0/`, no `constant/`, no `system/`, no
time directory, no `log.*`, no `postProcessing/`, no `DONE.*` marker and no
`result.json`. The second sweep is the one that matters — across the whole of
`verification/runs/`, the **only** path whose name contains `F12` is the
directory `verification/runs/F12_runs` itself, so no F12 case or run directory
exists anywhere under `verification/runs/` under any other spelling.

**The run directories that do not exist**, named explicitly as rule 2 requires:

- `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/`
- `verification/runs/F12_runs/medium_workshop_M0.734_a2.79/`
- `verification/runs/F12_runs/fine_workshop_M0.734_a2.79/`
- `verification/runs/F12_runs/medium_tape_M0.730_a2.79/`
- `verification/runs/F12_runs/medium_farfield2x_M0.734_a2.79/`

None of these five paths exists. No solver has been launched on this case. The
lab's own records agree and were not the basis of this check, only a corroborant:
`verification/campaign/CALIBRATION_SCORECARD_2026-08.md:264` counts F12 an
**ORPHANED pre-registration**, and `docs/VALIDATION_INVENTORY.md:343` records
**no results file exists**.

The pre-amendment content of this file is git blob
`8b6cc4c09ecb5207a60150194f62e7fff48998ea`, which was also the blob at HEAD when
this addendum was written — the file had no uncommitted drift to fold in.

### 2. What compute this pre-registration actually registers

The document above registers **five solver runs**: the three mesh levels of the
mesh study (§"Mesh study"), plus the two further medium runs it names — the tape
condition and the doubled far-field radius.

| # | Rung | Condition | Cells (registered above) |
| --- | --- | --- | --- |
| 1 | coarse | workshop, M = 0.734, alpha = 2.79 | 23,040 |
| 2 | medium | workshop | 92,160 |
| 3 | fine | workshop | 368,640 |
| 4 | medium, tape | tape, M = 0.730, alpha = 2.79 | 92,160 |
| 5 | medium, 2x far-field | workshop | 92,160 |

**Two quantities the frozen text does not fix, disclosed rather than assumed.**
The pre-registration above names neither a solver nor an iteration count. Both
are fixed by the implementing workflow, `sdk/workflows/rae2822_case9.py`:

- **Solver: `rhoSimpleFoam`** with k-omega SST — `sdk/workflows/rae2822_case9.py:577`
  (`application     rhoSimpleFoam;`), and the solve step at :957.
- **Iterations: 6,000** — the `iterations: int = 6000` default of both
  `build_case` (:894) and `run_case` (:927).
- **Ranks: 1** — `run_case`'s `ranks: int = 1` default (:929). The parallel
  branch exists but is not the default.

Costing below is at **6,000 iterations, 1 rank**. Naming these here changes
nothing above: it records what the registered compute *is*, so that a cost can
be attached to it. If a launch later chooses a different solver, iteration count
or rank count, the caps in §5 still bind, because they are stated in
core-minutes and core-minutes is rank-invariant to first order.

### 3. The measured analogs, named, with their artifacts

No rate is invented here. Two analogs measured **on this box** are used, and
both artifacts were confirmed present on disk on 2026-08-23 before being cited.

**Basis A — same solver, and one run at F12's own freestream condition.**
`verification/runs/F2_runs/F2_reproduction_2026-07-30.json` (the F2 transonic
NACA0012 reproduction of 2026-07-30, recorded at
`verification/campaign/F2_transonic_naca0012.md:83-94`). Both of its runs are
`rhoSimpleFoam` + k-omega SST on a 2D transonic aerofoil, single rank, from the
same `sdk/workflows` family that implements F12:

| Record key | M | alpha | Re | cells | iters | `timings.rhoSimpleFoam` |
| --- | --- | --- | --- | --- | --- | --- |
| `primary_M0.8_a1.25_Re6e6` | 0.800 | 1.25 | 6.0e6 | 3,584 | 2,000 | **33.7 s** |
| `secondary_M0.734_a2.79_Re6.5e6` | 0.734 | 2.79 | 6.5e6 | 3,584 | 2,000 | **25.8 s** |

The secondary run is at **exactly F12's workshop condition** — M = 0.734,
alpha = 2.79 deg, Re = 6.5e6 — on a different section (NACA0012, not RAE 2822).
That is the closest analog this lab holds. Its rate is
25.8 / (3584 x 2000) = **3.599e-6 s per cell-iteration**; the primary's is
33.7 / (3584 x 2000) = **4.7015e-6 s per cell-iteration**.
**The slower of the two (4.7015e-6) is used**, so the estimate is not built on
the more favourable of two available numbers.

**Basis B — cross-solver upper bound, disclosed because it disagrees.**
`verification/runs/DPW8_V2_runs/run_L3_physics/result.json`
(`t_run_s = 1696.1329329013824`, `meta.ncells = 12288`, `latest_time = 3000`),
recorded at `verification/campaign/DPW8_V2_joukowski.md:69`. Rate
1696.133 / (12288 x 3000) = **4.6011e-5 s per cell-iteration**.

Basis B is a **different solver** — `simpleFoam`, incompressible, on a conformal
O-grid — and it is **9.79x slower per cell-iteration** than Basis A on the same
box. That disagreement is not smoothed over: it is the single largest source of
uncertainty in every figure below, it is why both columns are carried, and it is
why the caps in §5 are set off Basis B at the first rung rather than off Basis A.

**Refinement exponent, taken from measurement not from theory.** Cost is not
exactly linear in cells. The only clean same-solver, same-iteration-count,
same-box refinement pair on the record is DPW8_V2's own L1/L3:

```
L1: 768 cells,   3000 iters,  t_run_s =   92.25288462638855   (run_L1_feasibility/result.json)
L3: 12,288 cells, 3000 iters, t_run_s = 1696.1329329013824    (run_L3_physics/result.json)

p = ln(1696.1329 / 92.2529) / ln(12288 / 768)
  = ln(18.3857) / ln(16)
  = 2.91161 / 2.77259
  = 1.05013
```

**p = 1.050** is used for both bases. It is derived from Basis B's solver and
applied to Basis A as well; that is an assumption, stated as one.

### 4. Per-rung cost — ESTIMATED, both bases

Model, applied per rung: `t = t_ref x (N / N_ref)^1.05013 x (I / I_ref)`,
then core-minutes = wall s x ranks / 60, with ranks = 1.

Worked example, the fine rung on Basis A:

```
(368640 / 3584)^1.05013 = 102.857^1.05013 = 129.7
t = 33.7 s x 129.7 x (6000 / 2000) = 33.7 x 129.7 x 3 = 13,117.6 s
core-min = 13,117.6 x 1 / 60 = 218.6
$ = (218.6 / 60) core-h x $0.0513/core-h = $0.187
```

**Every figure in this table is ESTIMATED. None is measured.**

| # | Rung | Cells | **Basis A (ESTIMATED, F2 `rhoSimpleFoam` 33.7 s / 3,584 cells / 2,000 it)** | **Basis B (ESTIMATED, DPW8_V2 L3 `simpleFoam` 1,696.1 s / 12,288 cells / 3,000 it)** |
| --- | --- | --- | --- | --- |
| 1 | coarse | 23,040 | 713.5 s = **11.9 core-min** ($0.010) | 6,564 s = **109.4 core-min** ($0.094) |
| 2 | medium | 92,160 | 3,059.2 s = **51.0 core-min** ($0.044) | 28,146 s = **469.1 core-min** ($0.401) |
| 3 | fine | 368,640 | 13,117.6 s = **218.6 core-min** ($0.187) | 120,686 s = **2,011.4 core-min** ($1.720) |
| 4 | medium, tape | 92,160 | 3,059.2 s = **51.0 core-min** ($0.044) | 28,146 s = **469.1 core-min** ($0.401) |
| 5 | medium, 2x far-field | 92,160 | 3,059.2 s = **51.0 core-min** ($0.044) | 28,146 s = **469.1 core-min** ($0.401) |
| | **TOTAL, five runs** | | **383.5 core-min = 6.391 core-h = $0.328** | **3,528.1 core-min = 58.802 core-h = $3.017** |

**Meshing, counted not waved away.** `blockMesh` + `checkMesh` took 0.6 s at
3,584 cells in the F2 secondary record (`timings` = 0.3 s + 0.3 s). Scaled
linearly in cells across all five cases: 111.9 s = **1.9 core-min ESTIMATED**
(~0.5% of the Basis A total, ~$0.002). It is inside the §5 headroom and is not
given its own cap.

**Rung 5 costs the same as rung 2 by construction**, not by oversight: doubling
the far-field radius changes `farfield_r` only, and the cell count is fixed by
the grid level (`blockmesh_dict(section, level, farfield_r=...)`,
`sdk/workflows/rae2822_case9.py:903`). The mesh is stretched, not enlarged. The
real risk there is *slower convergence at equal cell count*, which the cap
catches.

**`cost_basis`: reported-by-owner, not measured.** The rate $0.0513/core-h
(c7a.4xlarge) is owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. This box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure above is
**reported-by-owner**. Every core-minute figure above is **ESTIMATED** from the
named analogs; the analogs' own wall times are measured, the extrapolation to
F12 is not.

### 5. Caps, declared now — an overrun stops the run

**An overrun stops the run. It does not get a new budget** (standing rule 12).

| # | Rung | **CAP (core-min)** | Cap in $ | Cap vs Basis A | Cap vs Basis B |
| --- | --- | --- | --- | --- | --- |
| 1 | coarse | **120** | $0.103 | 10.1x | 1.10x |
| 2 | medium | **160** | $0.137 | 3.14x | 0.34x |
| 3 | fine | **700** | $0.599 | 3.20x | 0.35x |
| 4 | medium, tape | **160** | $0.137 | 3.14x | 0.34x |
| 5 | medium, 2x far-field | **160** | $0.137 | 3.14x | 0.34x |
| | **TOTAL CAP** | **1,300 core-min** | **$1.111** | 3.39x | 0.37x |

**The coarse rung is the rate-calibration rung, and its cap is set deliberately
above BOTH bases.** At 120 core-min it covers Basis B's 109.4, so rung 1
completes on either rate and returns a *measured* `rhoSimpleFoam` cost per
cell-iteration on the actual F12 mesh. That measured rate then replaces both
estimates before rungs 2-5 are considered. Rungs 2-5 are capped off Basis A with
~3.2x headroom, which means: **if the true rate turns out to be Basis B's, the
medium rung blows its cap and stops.** That is the designed behaviour, not a
mis-set cap. A 9.8x miss on the rate is exactly the condition under which a run
should stop and be re-read rather than run on.

**A wall-clock trap, flagged now.** `run_case`'s solver-step timeout defaults to
`timeout: float = 7200.0` seconds (`sdk/workflows/rae2822_case9.py:930`). The
fine rung's Basis A estimate is **13,117.6 s at ranks = 1** — 1.8x that timeout.
On the default settings the fine rung would be killed by its own timeout before
it reached 6,000 iterations, and would then fail admission gate B rather than
produce a result. This is recorded as an implementation fact for whoever
schedules F12. It changes no gate: gate B still reads exactly as written above.

**Scope of the $25 pre-authorisation.** The total cap, $1.11, and the Basis B
total, $3.02, both sit under the $25 per-run pre-authorisation. Under standing
rule 9 that blanket is **not** a per-item reading and is not treated as one here.
This is CPU compute on the existing box; **no GPU is involved**, so the separate
GPU costing regime of rule 12 does not apply.

### 6. This addendum does not authorize a launch

**F12 remains `PENDING`.** Nothing in this addendum schedules, approves or
authorizes any run. It repairs one defect and one only: the pre-registration
carried no core-minute cost, which under standing rule 12 disqualified it as a
proposal. It is now costed. It is not now approved.

Any launch of F12 needs, separately from this document:

1. its own reading by the responsible supervisor, against these caps;
2. the supervisor's **personal** check that this pre-registration is committed
   and frozen before compute — one of the four checks that may never be
   delegated (`CLAUDE.md`, TEAM ROSTER; `SUPERVISION_CHARTER.md` §3);
3. verification that the frozen file that ran hashes to the committed blob
   (standing rule 2).

No agent message authorizes a launch, and this addendum is an agent's work
product, not consent (standing rule 9).

*Written 2026-08-23 by a `lab-lane` worker for the cfd team, on a chief-directed
zero-compute task. No solver was launched in producing it.*
