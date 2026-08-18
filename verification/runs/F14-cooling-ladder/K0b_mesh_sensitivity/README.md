# K0b mesh sensitivity — F14 cooling ladder

Executes proposal **P2** of `demo-output/website/campaign/THERMAL_K0_RESULTS.md`:

> Every K0b number above is from a single 64x64 mesh. A single-mesh number is
> not a converged number.

P2 costed a 32/64/128 triple at 4.85 core-minutes on a measured basis and asked
for 15 core-minutes with this lab's 3x planning multiplier. The 64x64 leg was
run and paid for at `183c91c0`; this directory runs the two new legs and
re-measures the third in place, which is the pair the authorisation covers.

## What is here

| Path | What it is |
| --- | --- |
| `build_and_run.sh` | Copies the committed K0b case twice, changes **only** the cell counts in `blockMeshDict`, and refuses if any other dictionary differs from the source byte-for-byte. Then meshes and solves both. |
| `analyse_k0b_mesh.py` | Measures all three legs through one code path, reports the observed order of convergence, the Richardson extrapolate and the Roache GCI, and writes `k0b_mesh_sensitivity.json`. |
| `K0b_m32/`, `K0b_m128/` | The two new legs. |

The third leg is read in place from
`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5` and is not
copied, so there is one copy of it in the repository and it is the committed
one.

## What deliberately does not change

Pr stays at K0b's 0.706814, the schemes stay `limitedLinear`/`linearUpwind`,
the relaxation, `residualControl` and `0.orig` fields are the committed ones.
A mesh study that also changes the scheme is not a mesh study. In particular
these cases do **not** adopt the central-difference schemes or the Pr = 0.71 of
the K0c gate next door, and the de Vahl Davis reference values are not applied
to them: K0b is a capability rung graded against no published datum, and this
work does not change that.

## What did change, and why

The 128x128 leg was first run at K0b's `endTime 4000` and came out of it with
initial residuals of 5.3e-05 on T and 8.7e-05 on U, against 9.6e-08 for the
64x64 leg. It was not converged, and taken at face value it made the triple
look *divergent* under refinement — Nu_avg 4.6497 / 4.5538 / 4.3255, with an
observed order of −1.25. That is iteration error wearing a mesh study's
clothes. The leg was continued to 16000 iterations, reaching 2.5e-08, and the
triple then behaves: 4.6497 / 4.5538 / 4.5288, observed order 1.94, GCI 0.24
percent. Iteration count is not a discretisation parameter, so extending it is
not a change to the study.

## Cost

Measured, single core, on this machine: reported by `analyse_k0b_mesh.py` under
`cost.NEW_LEGS_TOTAL`. No monetary figure — there is no verified rate for this
machine and inventing one would be an underived number.
