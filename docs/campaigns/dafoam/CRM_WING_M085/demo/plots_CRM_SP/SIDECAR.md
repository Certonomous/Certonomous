# SIDECAR — CRM wing, Mach 0.85 (`plots_CRM_SP`)

Built 2026-09-14 with **zero solver compute** and nothing written into the run tree.
Plot library **v2**: math only on every figure, no titles, no verdict words, no
annotations — the words live here and in the act.

## 🔴 NO OPTIMISATION RAN. ZERO DESIGN ITERATIONS HAVE EVER COMPLETED.

The request that commissioned this folder asked for "the single point transonic CRM
Mach 0.85 **optimization**". **There is no such thing on disk.** There is no
CD-versus-design-iteration history, no optimised geometry, no drag-reduction number,
and the only geometry in the tree is the **baseline**. Nothing in this folder is
labelled optimisation, optimised, before/after or improvement, and none of it may be
described that way.

One line if the act needs a status: **"baseline established and verified against the
published result; the optimisation has not yet completed a design iteration."**

## What is here, and it is worth showing

**Case identity.** The published DAFoam `CRM_Wing` tutorial, **M = 0.8497**
(U₀ 295 m/s, T₀ 300 K), `DARhoSimpleCFoam`, wall functions, **579,072 cells**,
extrusion N = 53 / s0 1.0e-4 / marchDist 93.954, FFD `FFD/wingFFD.xyz`.
Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/`.

### 1. The verbatim baseline primal — and a three-way agreement

`P00/`, log `P00_20260913T192711Z.log`: the tutorial **exactly as shipped**, no lab
wrapper, `-task run_model`, converged, `rc = 0`, 28 ranks, 155.400 core-min.

| source | C_D |
|---|---|
| **this run** | **0.02090109066417552** |
| DAFoam's published figure | 0.02090 |
| an independent prior lab run | 0.02090143421526141 |

**Agreement to five significant figures, on a mesh rebuilt from the published
recipe.** That is a *validation* result, and it is the honest headline of this folder.
`C_L = 0.5000136952243076` against the tutorial's 0.500 lift constraint.

**Every number above was re-derived here from the log itself**, not transcribed from
the message that supplied them — the build script parses the log and printed
`0.02090109066417552` and `0.5000136952243076` independently.

**The history is 21 checkpoints, not 2000 points, and the figures show 21.** The log
records `Time = 0, 1, 100, 200 … 2000`, each with six per-equation `initRes` values
and one C_D/C_L pair. Nothing is interpolated up to look denser than the record is.

### 2. The multipoint trim — **iteration ZERO and nothing more**

`MP_R1/`, log `MP_R1_20260913T215100Z.log`, 20 ranks, 3,183.0 core-min, `rc = 1`.
**The run died in its first adjoint, on a PETSc −9 at `cl06`, before any design step.**
What it did establish is the trim: three angles of attack separating from a **common**
2.11031707° onto three lift targets.

| condition | α trimmed [deg] | C_D | C_L | target |
|---|---|---|---|---|
| cl04 | 1.32496937 | 0.0161737418278086 | 0.39999899 | 0.400 |
| cl05 | 2.11023869 | 0.02090147414115444 | 0.50000008 | 0.500 |
| cl06 | 2.88211463 | 0.02823517860146243 | 0.59999588 | 0.600 |

**`J0 = 0.25·C_D(cl04) + 0.50·C_D(cl05) + 0.25·C_D(cl06) = 0.021552967`**, computed in
the build script from the three measured values. The **74.6 % drag spread** across the
three conditions is the physics worth pointing at — and it is a property of the
**baseline** geometry at three lift coefficients, not of any design change.

**Measured, not relayed:** the three converged C_D values are found by reading the
log's C_D/C_L pairs and taking the last pair whose C_L is within 1e-3 of each target;
the four angles are **asserted to appear as literal strings in the log** before they
are drawn, so a number the run never printed cannot reach a figure.

### 3. The decomposition sweep — a real graded result

`DECOMP_N{08,20,28}`, graded `PASS` each, rollup `DECOMP_SWEEP_ROLLUP.json`, 849.667
core-min. Against DAFoam's threshold of **1.0e-06**:

| ranks | position 1 | position 2 | |
|---|---|---|---|
| 8 | 1.233169580459589e-07 | 1.981968888016819e-06 | over threshold |
| **20** | **4.265593605364853e-08** | **bit-identical to position 1** | under |
| 28 | 1.194718885139746e-07 | 1.757696578179007e-06 | over threshold |

**Two identical physical problems giving different answers at 8 and 28 ranks, and
identical ones at 20.** That is the finding, and the figure is floor against rank
count with the threshold drawn.

## Per figure

| Figure | What it is |
|---|---|
| `crm_cd_history.png` | C_D across the 21 primal checkpoints, published 0.02090 drawn as a line |
| `crm_cl_history.png` | C_L across the same, the 0.500 lift constraint drawn |
| `crm_residuals.png`, `_f10 … _f75` | the residual-evolution series, six equations on pinned axes |
| `crm_trim_cd.png` | converged C_D at each lift target — **baseline geometry, three conditions** |
| `crm_trim_alpha.png` | the common starting α and the three trimmed α |
| `crm_decomposition.png` | max residual against rank count, threshold 1e-06 drawn |

## Not built, and why

**No ParaView panel yet** — surface C_p on the wing, the FFD box over the wing, and
the mesh panel. The material exists (`P00/surfMesh.cgns`, `P00/FFD/wingFFD.xyz`,
`P00/constant/polyMesh` and `processor*`) and these are the first things to add; they
were not built in this pass. **No baseline-versus-optimised section shapes**, at any
span station, ever: there is no deformed geometry, because there was no design step.
