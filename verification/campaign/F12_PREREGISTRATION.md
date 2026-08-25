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

---

## MESH-SIMILARITY AMENDMENT — 2026-08-25

**Document version 1.1 (COSTED ADDENDUM, 2026-08-23) -> 1.2.**

**lines whose number changed above this section: 0**

Nothing above this line is struck, rewritten, renumbered or reworded. This
addendum resolves **one ambiguity in the frozen §"Mesh study"** and reports one
consequence of resolving it. It alters **no gate, no threshold, no cap and no
label**. Gates A, B, 1, 2, 3 and 4, the CM reporting clause, the overall PASS
rule, the three mesh levels and their cell counts, the two conditions, the two
further medium runs, the four predictions, and every core-minute estimate and
cap in the 2026-08-23 addendum §4 and §5, all stand exactly as written.

### 1. Why this amendment is legal, and how that was checked

Standing rule 2: *"Before first compute, amendments are legal and must state the
condition and how it was checked (name the run directory that does not exist)."*

The condition is that **no compute has ever been spent on F12**. It was
re-checked on **2026-08-25 at 00:19 UTC**, on the disk, in the same shell
invocation that committed this amendment, by `test -e` on each of the five run
directories the 2026-08-23 addendum §1 named, plus a name sweep of the whole of
`verification/runs/`:

- `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/` — **does not exist**
- `verification/runs/F12_runs/medium_workshop_M0.734_a2.79/` — **does not exist**
- `verification/runs/F12_runs/fine_workshop_M0.734_a2.79/` — **does not exist**
- `verification/runs/F12_runs/medium_tape_M0.730_a2.79/` — **does not exist**
- `verification/runs/F12_runs/medium_farfield2x_M0.734_a2.79/` — **does not exist**

`verification/runs/F12_runs/` still holds exactly one subdirectory, `reference/`,
with the same eight files listed in the 2026-08-23 addendum and nothing else: no
`0/`, no `constant/`, no `system/`, no time directory, no `log.*`, no
`postProcessing/`, no `DONE.*`, no `result.json`. A sweep of the entire
`verification/runs/` tree for any path whose name contains `F12` returns exactly
one path, the directory `verification/runs/F12_runs` itself, so no F12 case
exists under any other spelling. F12 is **UNFIRED**.

The pre-amendment content of this file is git blob
`7e84b5d35e4b07f511dd41dca465c4724d9b4566`, which was the blob at HEAD when this
addendum was written; the worktree copy had no uncommitted drift. This addendum
is a pure append: insertions only, no line above it moved.

### 2. The ambiguity, stated before it is resolved

§"Mesh study" registers three levels at a clean factor two in every direction —
coarse 48/48/80 = 23,040 cells, medium 96/96/160 = 92,160, fine 192/192/320 =
368,640 — and then says, **once, for the ladder as a whole**:

> "Wall-normal first cell 2e-6 chord, targeting y+ below 1 so the boundary layer
> is resolved rather than bridged."

The table has **no per-level first-cell column**. The frozen text therefore does
not say whether 2e-6 chord is the **fine** level's first cell, or a value held
**fixed** on all three. That single unstated word decides whether the ladder is
gradeable as a Roache triple at all.

**Why.** If the first cell is held fixed at 2e-6 while the wall-normal count
goes 80 -> 160 -> 320 over the same 50-chord radial extent, the wall-normal
**expansion ratio changes between levels** and the three meshes are not a
geometrically similar family. That is `VERIFICATION_CHARTER.md` §3.2's second
failure mode — an order fitted across a change of mesh recipe. It also silently
defeats the representative-h convention `h = (N_ref/N)**(1/dim)`, which assumes
uniform refinement and would otherwise return an `h` that no region of the mesh
actually has. `scripts/roache_triple.py` **cannot detect this**; its own
docstring says the caller establishes similarity and the file cannot. The
observed order would come back monotone, plausible and worthless.

This is not a hypothetical failure mode in this lab. The cfd supervisor verified
from the dictionaries on 2026-08-24 that the **Ahmed ladder** carries exactly
it: `study-ahmed_25` at 45,753 cells and `act7-ahmed_25` at 79,439 cells refine
`body { level (2 3); }` to `level (3 4); }` while **both carry the identical
background block `hex (60 13 36)` = 28,080 cells**. Refinement there was local to
the wetted surface, the far field never changed, and the stored `observed_order`
of 1.95 is worthless. (A lesson recording that finding is being landed by a peer
lane; as of this writing the highest lesson on `docs/LESSONS.md` is **L-263**,
which is a different subject, so no lesson number is cited here rather than a
guessed one.)

### 3. What the generator actually does — the prose is not the authority, the code is

F12's mesh is built by `sdk/workflows/rae2822_case9.py`. Read on 2026-08-25:

- **`FIRST_CELL = 2.0e-6`** is a module-level constant at **:254**, with the
  comment *"wall-normal first cell in chords; y+ ~ 0.5 at Re 6.5e6"*.
- It appears as a **keyword default only**, on `blockmesh_dict(..., first_cell:
  float = FIRST_CELL)` at **:269**. Those two lines are its only two occurrences
  in the entire repository; nothing overrides it anywhere.
- **`build_case` does not expose `first_cell` at all** (**:892-894**), and its
  call to the generator at **:903** is
  `blockmesh_dict(section, level, farfield_r=farfield_r, wake_len=wake_len)` —
  the first-cell argument is not passed. `run_case` (**:925**) likewise has no
  such parameter.

**Therefore the code, as it stands, fixes the wall-normal first cell at 2.0e-6
chord on ALL THREE LEVELS, and there is no argument by which a launch could
choose otherwise.** The ambiguity in the prose is resolved **against**
similarity by the implementation. The frozen ladder as it would actually be
built is **not a geometrically similar family**.

### 4. How far from similar — the numbers

The generator sets the wall-normal grading as
`r_y = ratio_for_first_cell(R, level.ny, first_cell)` at **:281**, with
`R = FARFIELD_R = 50.0` chords. `ratio_for_first_cell`
(`sdk/workflows/tmr_verification.py:184`) returns the blockMesh **total**
expansion ratio (last cell / first cell) that puts `level.ny` geometric cells
across `R` with the requested first cell.

**The similarity invariant of a geometric wall-normal distribution is that total
expansion ratio.** Under a similar refinement every cell in the column halves,
so last/first is preserved. Evaluated with the repository's own function:

| Level | ny | **As the code stands** (first cell fixed 2e-6) | | **Similar family** (first cell scales) | |
| --- | --- | --- | --- | --- | --- |
| | | total expansion | cell-to-cell r | total expansion | cell-to-cell r |
| coarse | 80 | 4.4011e6 | 1.213656 | 4.4011e6 | 1.213656 |
| medium | 160 | 2.1935e6 | 1.096179 | 4.5989e6 | 1.101295 |
| fine | 320 | 1.0643e6 | 1.044464 | 4.7020e6 | 1.049340 |

As the code stands the total expansion ratio **falls by a factor of 4.135**
across the ladder and the near-wall cell-to-cell growth rate falls from **21.4%
per cell to 4.4% per cell**. The coarse and fine meshes are not the same mesh at
two resolutions; they are two different wall-normal recipes. In the similar
family (right-hand columns, anchored per §7 below) the invariant is held to
within **6.8%** across the three levels, and the cell-to-cell ratios stand in the
square-root relation a factor-two refinement requires: `1.213656**0.5 = 1.1017`
against a built 1.101295, `1.101295**0.5 = 1.0494` against a built 1.049340.

### 5. A SECOND non-similarity, found while checking the first, and reported not repaired

`blockmesh_dict` also sets, at **:282**,

    r_y_far = ratio_for_first_cell(R, level.ny, min(0.3, 0.3 * farfield_r / 25.0))

which is the far-side wall-normal grading of the two wake blocks (**:328-334**,
inside their `edgeGrading` entries). At `farfield_r = 50` the requested first
cell is `min(0.3, 0.6) = 0.3` **chord**, an absolute length with **no dependence
on the level**. Evaluated:

| Level | ny | 50/ny | requested first cell | total expansion returned |
| --- | --- | --- | --- | --- |
| coarse | 80 | 0.625 | 0.3 | 3.747165 |
| medium | 160 | 0.3125 | 0.3 | 1.084468 |
| fine | 320 | **0.15625** | 0.3 | **1.000000** |

At the fine level the requested first cell **exceeds the uniform spacing**
`length / n`, so `ratio_for_first_cell`'s guard
(`if first_cell >= length / n: return 1.0`,
`sdk/workflows/tmr_verification.py:189-190`) fires and the fine level's wake
blocks get a **uniform** far-side distribution where the coarse level's are
graded 3.75:1. That is not a gradual drift of recipe across the ladder; it is a
**branch flip**, and it is a second change of experiment across the levels,
independent of and unfixed by §7.

This is reported, **not repaired**. It is read from the dictionary-writing code,
not from a built mesh — no mesh was built for this amendment — and the precise
geometric role of that edge should be confirmed against a built `blockMeshDict`
by whoever repairs it. **It is a pre-launch blocker on F12's triple** (§8).

### 6. The y+ consequence, worked

`Re = 6.5e6` on chord. For a wall distance `y/c`,
`y+ = (y/c) * Re * sqrt(cf/2)`. Three standard flat-plate correlations at
`Re_c = 6.5e6` give:

    Schlichting 1/5-power  cf = 0.0592 Re^-0.2      = 0.002569  -> y+ per chord = 2.330e5
    1/7-power              cf = 0.0576 Re^-0.2      = 0.002500  -> y+ per chord = 2.298e5
    Prandtl-Schlichting    cf = 0.455/ln(0.06 Re)^2 = 0.002750  -> y+ per chord = 2.408e5

**2.330e5 per chord** is carried below. It reproduces the generator's own stated
figure — `2.0e-6 * 2.330e5 = 0.466`, against the `# y+ ~ 0.5` comment at
`rae2822_case9.py:254` and the *"first cell sits at y+ ~ 0.5"* note at **:692** —
which fixes the convention the generator used: **y+ quoted on the FULL first-cell
height**, not on the cell centre. Both conventions are tabulated; the cell-centre
figure is exactly half.

| first cell (chord) | y+ (full height) | y+ (cell centre) | y+ (full height) x LE factor 1.71 |
| --- | --- | --- | --- |
| 5.0e-7 | 0.116 | 0.058 | 0.20 |
| 1.0e-6 | 0.233 | 0.116 | 0.40 |
| **2.0e-6** | **0.466** | 0.233 | 0.80 |
| 4.0e-6 | 0.932 | 0.466 | 1.59 |
| 8.0e-6 | **1.864** | 0.932 | **3.19** |

**The LE factor is why a chord-Reynolds flat-plate number is a floor, not a
bound.** Near the suction peak the local edge velocity and the thinner local
boundary layer both raise y+. With `U_e/U_inf = 1.30` at `x/c = 0.05` (consistent
with this case's measured `Cp_min`) and `cf_x = 0.0592 Re_x^-0.2` at
`Re_x = U_e/U_inf * Re * x/c = 4.225e5`, the local-to-chord-Reynolds ratio is
`(U_e/U_inf) * sqrt(cf_x/cf_c) = 1.30 * sqrt(0.004438/0.002569) = 1.709`. The
same estimate gives 1.59 at `x/c = 0.10`, 1.33 at 0.30 and 1.12 at 0.50. **The
1.71 column is ESTIMATED, from a flat-plate correlation with an assumed edge
velocity; it is not measured and it is not a gate.**

**Consequence for the two candidate anchorings.**

- **Anchored at the FINE level** (fine 2e-6, medium 4e-6, coarse 8e-6): the
  coarse level's first cell reaches `y+ = 1.86` on the generator's own
  convention, and `~3.2` near the suction peak. That crosses the frozen text's
  own *"y+ below 1"* clause and moves the coarse level from **resolved** to
  **bridged** wall treatment — which is itself a change of experiment across the
  ladder, and it would put a wall-function-regime coarse rung into a triple with
  two wall-resolved rungs. Under this anchoring the ladder **cannot** be both
  similar and y+ < 1 at every level.
- **Anchored at the COARSE level** (coarse 2e-6, medium 1e-6, fine 5e-7): y+ =
  0.47 / 0.23 / 0.12 on the full-height convention, 0.23 / 0.12 / 0.06 on the
  cell-centre convention, and 0.80 / 0.40 / 0.20 with the 1.71 leading-edge
  factor applied to the full-height figure. **Every level is below 1 under every
  convention tabulated here**, and the family is similar (§4, right-hand columns).

### 7. The resolution

The cfd supervisor's ruling, which this amendment implements and does not
re-decide: *a mesh ladder is admissible as a Roache ladder only if the refinement
is geometrically similar — the first cell height and the expansion ratio scale
WITH the mesh, and the refinement recipe is otherwise held FIXED.*

Applied to F12, the frozen sentence is read as a whole, and its **second** clause
selects the anchoring its first clause left open:

> **The wall-normal first cell of 2e-6 chord named in §"Mesh study" is the
> COARSE level's first cell. The medium level's is 1e-6 chord and the fine
> level's is 5e-7 chord — the first cell halves with each factor-two refinement,
> as every other spacing in the ladder does.**

This is not a free choice between two readings. The frozen sentence says *"2e-6
chord, targeting y+ below 1"*. Once similarity is required, 2e-6 can attach to
exactly one level, and **only the coarse anchoring satisfies the second half of
the same frozen sentence at all three levels** (§6). Anchoring at the fine level
would leave the coarse level at y+ 1.86, in contradiction with the text being
interpreted. The frozen document therefore determines its own reading; this
amendment records that reading rather than supplying one.

**What must change in the implementation before F12 may be launched.** These are
recorded as pre-launch blockers and are **not made here** — this amendment is a
zero-compute record and touches no code:

1. `sdk/workflows/rae2822_case9.py` must carry a **per-level** first cell —
   2.0e-6 / 1.0e-6 / 5.0e-7 chord for coarse / medium / fine — and `build_case`
   (**:892**) and `run_case` (**:925**) must thread it through to
   `blockmesh_dict` (**:903**), which today they do not. Until they do, a launch
   silently builds the non-similar ladder of §3-§4.
2. The `r_y_far` level-independence of §5 must be repaired, so the wake blocks'
   far-side distribution refines with the ladder instead of flipping to uniform
   at the fine level.
3. Both repairs are changes to a **grading path**. Standing rule 2 fixes the
   grading path at the pre-registration commit; the repaired generator must be
   committed, and hashed against its committed blob, **before** the first solver
   starts, exactly as the comparator freeze requires.

**A record, not an authorisation.** Neither this amendment nor these three items
schedules, approves or authorizes any run. F12 remains **PENDING**, on the same
three conditions the 2026-08-23 addendum §6 already stated.

### 8. What this amendment changes, and what it does not

**It does not change:** any gate (A, B, 1, 2, 3, 4), any threshold (0.08, 0.04,
0.020 chord, 5%, 20%), any cap (§5 of the 2026-08-23 addendum: 120 / 160 / 700 /
160 / 160, total 1,300 core-min), any label, any of the three cell counts
(23,040 / 92,160 / 368,640), either condition, either of the two further medium
runs, the CM reporting clause, the overall PASS rule, or any of the four
predictions. The first-cell height does not enter the cell count, so **every
core-minute figure in the 2026-08-23 addendum §4 and every cap in its §5 stands
verbatim**.

**It changes:** the per-level wall-normal first cell, from a value the frozen text
left unstated per level (and the code fixed at 2e-6 on all three) to 2.0e-6 /
1.0e-6 / 5.0e-7 chord. That is a resolution of an ambiguity in a construction
parameter, not an alteration of a gate, threshold, cap or label. **If the
verification supervisor rules otherwise — that fixing a per-level construction
parameter is itself a gate change — this amendment is the record of the
ambiguity and the ruling stands over it; F12 has not been fired and nothing is
lost by re-freezing.**

**Two consequences carried forward honestly, neither of them a gate change.**
The coarse-anchored fine mesh has a steeper total expansion (4.70e6 against the
1.06e6 the code would have built) and a much higher near-wall cell aspect ratio.
Gate A gates max non-orthogonality <= 70 degrees and max skewness <= 4 and
records **aspect ratio as advisory, not gated** — that clause is unchanged and is
what carries this. And a steeper near-wall grading can slow convergence at equal
cell count; the 2026-08-23 addendum §5 already states that a rate miss is caught
by the cap and that stopping is the designed behaviour. Neither figure is
measured; no mesh was built.

### 9. Rule 15 on the primary reference — reported, not repaired, and not papered over

§"The reference" already discloses that F12's reference data is *"a transcription
made by the experiment's own AGARD evaluator, not the AR-138 document itself,
and it is labelled secondary everywhere it is used."* Checked on 2026-08-25:
**no AGARD AR-138 document exists anywhere under `docs/papers/`.** A full-text
sweep of that library returns three files that merely **cite** AR-138 in their
own reference lists — `docs/papers/uncertainty_quantification/schaefer_2017_uq_closure_transonic.txt`,
`docs/papers/uncertainty_quantification/schaefer_2017_uq_sa_model.txt` and
`docs/papers/turbulence_models/spalart_allmaras_1992_turbulence_model.txt` — and
no copy of the report.

**Standing rule 15 title-page verification of F12's primary is therefore
currently IMPOSSIBLE**, because the primary is not held. The strongest honest
statement available about F12's P is:

> F12's reference values are taken from the AFOSR-HTTM/Stanford digitisation,
> flow case 8621, evaluator R. E. Melnik (1981), retained on disk at
> `verification/runs/F12_runs/reference/f8621.txt` with the decoder that produced
> the graded `.dat` files beside it. That artifact is **secondary**, it is
> **title-page-verified against nothing**, and Cook, McDonald and Firmin, AGARD
> AR-138 (1979), the primary it transcribes, **is not held by this lab and has
> not been opened by it.**

Whether a secondary transcription can support a P at all is
`VERIFICATION_CHARTER.md`'s rubric — a **verification-team ruling**. It is
neither this lane's call nor the cfd supervisor's, it is not decided here, and no
wording in this document should be read as having decided it.

### 10. What this amendment refused to decide

- Whether a secondary transcription can support a P (§9) — referred to
  verification.
- Whether resolving a per-level construction parameter counts as a gate change
  (§8) — referred to verification; the amendment states its own reading and does
  not insist on it.
- The repair of `r_y_far` (§5) — reported as a pre-launch blocker; its geometric
  role is stated from the dictionary-writing code and should be confirmed against
  a built `blockMeshDict` before anyone edits it.
- Any change to `sdk/workflows/rae2822_case9.py` — named precisely (§7) and not
  made.

*Written 2026-08-25 by a `lab-lane` worker for the cfd team, on a
supervisor-directed **ZERO-COMPUTE** task. No solver was launched, no mesh was
built and no case directory was created in producing it. Every mesh-grading and
y+ number above is arithmetic evaluated with this repository's own
`ratio_for_first_cell` and with named flat-plate correlations; all of it is
ESTIMATED and none of it is measured.*

---

## CAP-ENFORCEMENT ADDENDUM — 2026-08-25 (POST-COMPUTE)

**Document version 1.2 (MESH-SIMILARITY AMENDMENT, 2026-08-25) -> 1.3.**

**lines whose number changed above this section: 0**

Nothing above this line is struck, rewritten, renumbered or reworded.

**THIS ADDENDUM IS POST-COMPUTE AND IT KNOWS IT.** F12 rung 1 fired at
**2026-08-25T01:03:06.630Z** and aborted at **01:03:34.350Z**. Under standing
rule 2 the gates are therefore **CLOSED**, and this addendum **alters no gate,
no threshold, no cap and no label**. Gates A, B, 1, 2, 3 and 4, the CM reporting
clause, the overall PASS rule, the three mesh levels and their cell counts, the
two conditions, the two further medium runs, the four predictions, the
per-level first-cell resolution of the 2026-08-25 MESH-SIMILARITY AMENDMENT §7,
and **every core-minute estimate in the 2026-08-23 COSTED ADDENDUM §4 and every
cap in its §5** all stand exactly as written.

**What it adds is arithmetic derived from the caps that are already frozen**: how
many seconds of wall clock a core-minute cap is worth. It defines no new row, no
new quantity and no new gate. It is recorded here because the caps in §5 above
are denominated in one unit and were, in the grading path, enforced in another.

### 1. The defect, stated in one line

**A wall-clock `timeout` is not a core-minute cap. The two coincide only at
1 rank.** The correct conversion, which this addendum records and does not
invent:

    timeout_seconds = cap_core_min * 60 / ranks

**The finding belongs to the `ansys-verification` team and is cited as theirs.**
They measured it on their own launcher and disclosed it at
`cases/ansys_verification/VMFL051/RESULTS.md` §7.1, under the heading *"the cap
unit and the enforcement unit are not the same unit"*, and carried the same
formula forward into `cases/ansys_verification/VMFL045/PREREGISTRATION.md` §9.1
as *"the cap-as-timeout instrument trap"*. **It is cited, not adopted, and no
lesson is assigned from it here** — it is not the cfd team's finding to number.

### 2. What each frozen cap is worth in seconds, at ranks = 1

Derived from §5 above by the formula in §1. **These are conversions of the frozen
caps, not new caps.** At ranks = 1 the two units coincide exactly, so the
conversion is `cap_core_min x 60`:

| # | Rung | **CAP (core-min), frozen in §5 above** | timeout_s at ranks = 1 | timeout_s at ranks = 4 | timeout_s at ranks = 8 |
| --- | --- | --- | --- | --- | --- |
| 1 | coarse | 120 | **7,200** | 1,800 | 900 |
| 2 | medium | 160 | **9,600** | 2,400 | 1,200 |
| 3 | fine | 700 | **42,000** | 10,500 | 5,250 |
| 4 | medium, tape | 160 | **9,600** | 2,400 | 1,200 |
| 5 | medium, 2x far-field | 160 | **9,600** | 2,400 | 1,200 |

**A timeout of `cap_core_min x 60` seconds on an 8-rank job would permit 8x the
registered budget before firing.** That is the failure the formula prevents.

### 3. Where the defect is in the grading path

Read from `sdk/workflows/rae2822_case9.py`, blob
`a18314f77160b7a58f443073850a44b4d8fada7d` — the blob that ran, recorded in
`verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/result.json`:

- **`:1145`** — `run_case`'s signature carries `ranks: int = 1, timeout: float =
  7200.0`. The default is a **bare wall-clock number with no rank term**.
- **`:1175-1177`** — the parallel branch passes that **unscaled** `timeout`
  straight to `["mpirun", "-np", str(ranks), "rhoSimpleFoam", "-parallel"]`. The
  rank count is in the command and **not** in the limit.
- **`:1180`** — the serial branch passes the same `timeout` to a single-rank
  `rhoSimpleFoam`, where it is correct by coincidence.

**The module's 7,200 s default measured against the frozen caps of §2:**

- **75.0 %** of rung 2's, rung 4's and rung 5's cap (7,200 / 9,600);
- **17.14 %** of rung 3's cap (7,200 / 42,000).

**On the default settings the fine rung is bounded at 17 % of its own registered
budget.** The 2026-08-23 COSTED ADDENDUM §5 already flagged the 7,200 s default
as a wall-clock trap for the fine rung, against a Basis A estimate of 13,117.6 s;
this addendum states the general form of the same defect and its arithmetic.

**The ACCOUNTING is right where the ENFORCEMENT is wrong.** At **`:1229-1232`**
the returned record computes

    "wall_seconds": sum(timings.values()),
    "core_seconds": sum(v for k, v in timings.items()
                        if k != "rhoSimpleFoam") + timings.get(
                            "rhoSimpleFoam", 0.0) * ranks,

which **correctly multiplies solver wall time by the rank count** and correctly
leaves the serial pre- and post-processing steps unmultiplied. So the module
**reports** core-seconds in the charter's unit and **enforces** a limit in a
different one. A reader of the record would see the right number; a run
approaching its cap would not be stopped at the right place.

### 4. What actually happened on F12, stated so this addendum does not misdescribe its own case

**F12 rung 1 did NOT exercise this defect, for two independent reasons, and both
are recorded rather than the more dramatic one alone:**

1. **F12 ran serial.** `run_f12_rung.py` sets `RANKS = 1`, and `result.json`
   records `"ranks": 1`. At 1 rank the two units coincide and **no overspend was
   possible**.
2. **F12's own driver already implements the §1 formula.** `run_f12_rung.py`
   computes `cap_wall_s = spec["cap_core_min"] * 60.0 / RANKS` and then
   `solver_timeout = cap_wall_s - MESH_RESERVE_S` with `MESH_RESERVE_S = 60.0`,
   giving **7,140 s** for rung 1 — recorded as `"solver_timeout_s": 7140.0` in
   `result.json`. The driver **never passed the module's unscaled 7,200 s
   default**, and it reserved 60 s of the cap for `blockMesh` and `checkMesh`
   rather than letting meshing eat into the solver's limit.

**The defect is therefore in the module's default and in its parallel branch, and
it was never reached by this case.** It is recorded here because §5's caps are
this document's, because the module is this document's frozen grading path, and
because a future parallel F12 launched through `run_case` directly — rather than
through this driver — would hit it.

**No repair is made here.** This addendum is a record; changing
`sdk/workflows/rae2822_case9.py` is not this document's business and the grading
path that ran is frozen (standing rule 2). The disposition is the cfd
supervisor's.

### 5. What this addendum changes, and what it does not

**It does not change:** any gate (A, B, 1, 2, 3, 4), any threshold (0.08, 0.04,
0.020 chord, 5 %, 20 %, 70 degrees, skewness 4), **any cap** (120 / 160 / 700 /
160 / 160, total 1,300 core-min), any label, any cell count, either condition,
either of the two further medium runs, the CM reporting clause, the overall PASS
rule, the per-level first-cell resolution, or any of the four predictions.

**It adds:** the seconds-equivalent of caps that were already frozen, at three
rank counts, and the location of the enforcement defect in the frozen grading
path. **A conversion of a frozen number into a different unit is not a new
number.** Nothing in §2 may be read as authorising a run: F12 has fired and
**nothing further launches on this pre-registration** (see
`verification/campaign/F12_RESULTS.md`, which grades the case `GATE FAIL` and
tiers it `NOT HELD`, and rules that a next F12 needs a fresh pre-registration
because this ladder fails admission gate A at all three levels).

**Pure append, proven three ways in the committing shell invocation:**
`git diff-tree --stat` against the parent tree **before** `commit-tree`, showing
only this path; `--numstat` showing **insertions only and zero deletions**; and
the pre-addendum blob `41ec748a06b513414101dca9780107f08a25ddec` verified to be
a **byte prefix** of this file. No line above this section moved.

*Written 2026-08-25 by a `lab-lane` worker for the cfd team, on a
supervisor-directed **ZERO-COMPUTE** task. No solver was launched, no mesh was
built and no case directory was created in producing it. Every line number and
every value above was read from the named blob by this lane. The wall-clock
finding is `ansys-verification`'s and is cited as theirs.*

---

## LAUNCHER ADDENDUM — 2026-08-25 (POST-COMPUTE)

**Document version 1.3 (CAP-ENFORCEMENT ADDENDUM, 2026-08-25) -> 1.4.**
**Lines whose number changed above this section: 0.** This addendum is
INSERTIONS ONLY, appended at the foot. Verified by diff against the immediately
preceding blob: 0 deletions, and every line above this heading byte-identical.

**This addendum alters NO gate, NO threshold, NO cap and NO label.** Admission
gate A (`<= 70` degrees, `<= 4` skewness), admission gate B, Gates 1, 2, 3 and 4
and their thresholds (0.08, 0.04, 0.020 chord, 5 %, 20 %), the CM-reported-not-
gated clause, the overall PASS rule, the §5 caps (120 / 160 / 700 / 160 / 160,
total 1,300 core-min), the three cell counts, both conditions, the two further
medium runs and all four predictions stand **exactly as frozen 2026-07-30**.

### 1. Why this addendum is legal, and what it is

**It is post-compute and it says so.** Rung 1 fired on 2026-08-25 (`cd1ac21a`),
so `VERIFICATION_CHARTER.md` §2d is **live**. The pre-compute grounds that
carried the earlier `REFERENCE_DIR` repair — that F12 had never run — **have
expired and are not cited here.**

**The authority is the owner's, and it is explicit.** Sanaa's instruction of
2026-08-25: *"Build a fresh three-level mesh ladder that passes the admission
gate at every level … mesh instrument replaced, gate unchanged. Then run
RAE 2822 / AGARD Case 9 against the unchanged criteria."* **Replacing the mesh
instrument after first compute is an owner ruling and only she can make it.**
Her approval is of the new ladder against unchanged criteria and **nothing
wider** (standing rule 9); this addendum takes nothing beyond it.

**What this addendum discloses is a LAUNCHER, not a grading path.** The
replacement ladder cannot be fired by `run_case`, which writes
`system/blockMeshDict` from `sdk/workflows/rae2822_case9.py`'s own
`blockmesh_dict` and offers hooks for spacings only, never topology. A launcher
that can write the new dictionary is **instrumental to what was authorised, not
an expansion of it.**

**And there is an independent reason the old path cannot fire a gate run at
all:** `run_case` writes `method scotch;` into `decomposeParDict`
(`sdk/workflows/rae2822_case9.py`, the `ranks > 1` branch), which is
non-compliant with the parallel-gate doctrine ratified 2026-08-25. It also runs
the solver in the foreground under a subprocess timeout, with no `setsid` and
**no `rc` written to disk**, so standing rule 4's `rc` limb cannot be measured
through it — only inferred, which rule 4 forbids.

### 2. How "launcher, not grading path" is ENFORCED and not merely asserted

The launcher is `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/`
`launch_f12_rung.py`. It does not contain, and may not contain, any code that
turns a solve into a number. Every graded quantity is produced by calling the
**unchanged** frozen functions, and the launcher **asserts their bytes at run
time and fails closed**:

1. `sdk/workflows/rae2822_case9.py` is hashed whole against its pinned committed
   blob. Any difference is an ABORT before anything is written.
2. Every downstream grading function is hashed **individually**, by
   `inspect.getsource`, against a sha256 pinned in the launcher — across all
   three modules the grading path spans (`rae2822_case9`, `tmr_verification`,
   `chief_engineer.head_engineer`). A function-level pin survives an unrelated
   edit elsewhere in a shared file and still fails closed if a graded function
   changes.
3. The launcher **contains no comparator of its own.** `mesh_gate`,
   `solver_converged`, `split_surfaces`, `shock_location`, `cp_deviation`,
   `final_coefficient`, `parse_force_split` and `parse_coefficient_history` are
   imported and called, never reimplemented.
4. The only substitution is `system/blockMeshDict`, overwritten from the
   **committed** attempt-2 dictionary and asserted sha256-equal to its blob
   before the mesh is built. The assertion fails closed.

**The single mesh substitution is the entire delta.** Fields, thermophysical and
turbulence properties, `fvSchemes`, `fvSolution` and `controlDict` — including
the `forceCoeffs1`, `surfaceP`, `yPlus` and `MachNo` function objects that
produce every graded quantity — are written by the frozen `build_case`,
unchanged and byte-asserted.

### 3. Run directories registered by name, and asserted ABSENT before launch

Attempt 1 fired into `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/`,
which **exists** and is preserved undeleted and unrenamed. Standing rule 4's
guard refuses a case where `0` or a time directory already exists, so attempt 2
uses new directories, registered here:

| # | rung | run directory (under `verification/runs/F12_runs/`) | cap |
| --- | --- | --- | --- |
| 1 | coarse, workshop | `attempt2_coarse_workshop_M0.734_a2.79` | **120 core-min** |
| 2 | medium, workshop | `attempt2_medium_workshop_M0.734_a2.79` | **160 core-min** |
| 3 | fine, workshop | `attempt2_fine_workshop_M0.734_a2.79` | **700 core-min** |
| 4 | medium, tape | `attempt2_medium_tape_M0.730_a2.79` | **160 core-min** |
| 5 | medium, 2x far-field | `attempt2_medium_farfield2x_M0.734_a2.79` | **160 core-min** |

The caps are the §5 caps **verbatim**; this table converts nothing and relaxes
nothing. The launcher asserts the target directory ABSENT by `os.path.exists` in
its own invocation and aborts if it is not.

### 4. `rc`, detachment and the sampler — rule 4's limbs made measurable

- The solver is launched under **`setsid`**, so it is a session leader and
  survives the launching agent. Its `rc` is captured **immediately** into a shell
  variable, written raw to `RC.txt`, `sync`'d, and **read back from the file**.
  A missing, empty or non-integer `RC.txt` is **REFUSED, never inferred.**
- An **external sampler**, also detached, appends a sample every 15 s carrying
  the UTC stamp, elapsed wall seconds, accumulated core-minutes, the cap, the
  latest solver iteration, and **`loadavg` in EVERY sample** — not only at
  launch. This team has measured that the contention allowance is **bimodal**; a
  run that records only its launch load has measured the wrong thing.
- **Cap breach STOPS the rung.** The sampler signals the solver's process group
  when accumulated core-minutes exceed the frozen cap and records the stop. An
  overrun stops the run; it does not get a new budget (standing rule 12).
- A **resume record** is written into the run directory carrying the pid, the
  process-group id, the case path, the cap and the stamp, so the run does not
  depend on the agent that started it.

### 5. What this addendum does NOT do

**It does not authorise a launch.** The launcher is committed **UNFIRED**. Firing
needs, separately: the cfd supervisor's personal reading of the launcher as a
diff (`SUPERVISION_CHARTER.md` §3, check 1, which may never be delegated), and
the supervisor's personal check that this pre-registration is committed and
frozen before compute. No agent message authorises a launch, and this addendum is
an agent's work product, not consent (standing rule 9).

**It does not re-open `build_ladder_attempt2.py`.** That builder pins the
**pre-addendum** blob `080303c57aee52849bb625579565a84ca5469717` and will
therefore REFUSE to run against this file from now on. That is intended and is
disclosed rather than repaired: the pin records the exact bytes the mesh ladder
was graded against, and the ladder's gate-A verdict is already on record at
`d26f5bdc`. Re-running it would require a new dated record of its own.

**It does not touch the mesh verdict.** Admission gate A `PASS` at 51.1237 /
51.5250 / 51.9261 degrees, zero faces over 70 at every level, stands on the
record already committed and is not restated as a new claim here.

*Written 2026-08-25 by a `lab-lane` worker for the cfd team, on a supervisor-
authorised task. **No solver was launched in producing it.** The launcher it
discloses is committed unfired.*
