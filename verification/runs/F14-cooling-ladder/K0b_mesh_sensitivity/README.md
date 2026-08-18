# K0b mesh sensitivity — F14 cooling ladder

Executes proposal **P2** of `verification/campaign/THERMAL_K0_RESULTS.md` (R21;
it was `demo-output/website/campaign/THERMAL_K0_RESULTS.md` when this rung was
written, and naming the old spelling here is D403's defect in the instruction
document rather than in the code):

> Every K0b number above is from a single 64x64 mesh. A single-mesh number is
> not a converged number.

P2 costed a 32/64/128 triple at 4.85 core-minutes on a measured basis and asked
for 15 core-minutes with this lab's 3x planning multiplier. The 64x64 leg was
run and paid for at `183c91c0`; this directory runs the two new legs and
re-measures the third in place, which is the pair the authorisation covers.

## What is here

| Path | What it is |
| --- | --- |
| `build_and_run.sh` | Copies the committed K0b case twice, changes **only** the cell counts in `blockMeshDict`, and refuses if any other dictionary differs from the source byte-for-byte. Then meshes and solves both, **and continues any leg that did not stop itself on `residualControl`** to `endTime 16000` (see *What did change, and why*). |
| `analyse_k0b_mesh.py` | Measures all three legs through one code path, reports the observed order of convergence, the Richardson extrapolate and the Roache GCI, and writes `k0b_mesh_sensitivity.json`. |
| `K0b_m32/`, `K0b_m128/` | The two new legs. |

The third leg is read in place from `verification/runs/THERMAL_K0_runs/K0b_cavity_Ra1e5`
and is not copied, so there is one copy of it in the repository and it is the
committed one. Neither the script nor the analysis spells that path out: both
ask `lab_paths.run_archive("THERMAL_K0_runs")` for it by name, which is why
they survived R20 (D403). This paragraph named the pre-R20 spelling until the
D406 repair; the directory it named had not existed since batch 7.

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

### That continuation is a step of the script, and until 2026-08-18 it was not

**D406.** The paragraph above described a step performed **by hand**. Nothing
executable performed it: `build_and_run.sh` ran every leg to `endTime 4000` and
stopped, and its copy step overwrote `system/controlDict` from the source case
on every invocation, so the hand edit could not have survived a re-run of the
script that was supposed to have produced the result.

Measured during the D403 re-run rather than argued: running the two commands
below, in the order they are given, produced `Nu_avg_hot` 4.3254648850 against
the published 4.5288167412 — **4.490 % low** — with five of six observed orders
negative and the sixth non-monotone. The rung's numbers were never in doubt;
its executability without an undocumented human step was.

`build_and_run.sh` now performs the continuation itself. It reads each leg's
**stopping reason** from the solver's own `SIMPLE solution converged in N
iterations` line, continues only a leg that ran out at `endTime`, and derives
the second-stage `controlDict` from the source case's own dictionary every
invocation — `startFrom latestTime`, `endTime 16000`, `writeInterval 2000`, and
a guard that no other line moved. The stage-1 dictionary is preserved as
`system/controlDict.4000` **by the script**, as an output rather than as an
input, so there is no hand edit left for the copy step to clobber.

The 32x32 leg stops itself at t = 1386 on `residualControl` and is therefore
**not** continued; continuing a converged leg would move its written times and
change a published number for no reason.

## How to run it

```bash
bash build_and_run.sh          # both new legs, continuation included
python3 analyse_k0b_mesh.py    # writes k0b_mesh_sensitivity.json
```

Those two commands reproduce the published table with no manual step. Proved
once, from a clean start, in
`verification/runs/F14-cooling-ladder/K0b_D406_repair/`; the record is
`docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_RESULTS.md`.

**Run it somewhere else, not here.** `build_and_run.sh` opens each leg with
`rm -rf "$dst"`, and `K0b_m32/` and `K0b_m128/` hold 36 tracked files —
both `COST.txt`, every solver log, `system/controlDict.4000`. Running it in
this directory destroys the published record of the rung. Copy the two files to
a scratch tree and run them there; both find the 64x64 archive by name, so they
work from anywhere under the repository.

## Cost

Measured, single core, on this machine: reported by `analyse_k0b_mesh.py` under
`cost.NEW_LEGS_TOTAL`. No monetary figure — there is no verified rate for this
machine and inventing one would be an underived number.
