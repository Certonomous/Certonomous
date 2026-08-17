# K0c run tree — F14 cooling ladder, laminar differentially heated cavity

Everything under this directory executes
`../K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`, Section 1. The specification was
written first, by a different agent, at zero compute; nothing here edits it.

## What is here

| Path | What it is |
| --- | --- |
| `build_cases.py` | Writes every case directory from one table. Run it with no arguments to rebuild all, or with case names to rebuild only those. Prints the Ra, dT, `beta.dT` and cell Peclet number of each case at build time. |
| `run_cases.sh` | Stage 1: `blockMesh`, `checkMesh`, solve. One core per case. |
| `continue_cases.sh` | Stage 2: continue from `latestTime` with an accelerated SIMPLE outer loop. Its docstring carries the measurement that forced it. |
| `rewrite_precision.sh` | Stage 3: rewrite the converged fields at `writePrecision 16`. Its docstring carries the measurement that forced *it*. |
| `analyse_k0c.py` | Grades the rung. Reads the reference values and the pass bands **out of the specification file**, not from a copy of its own. Writes `gate_k0c.json`. |
| `CONTROL_PREDICTIONS.txt` | The control predictions, registered with a timestamp before any control result was read. |
| `stage1_values.json` | Snapshot of every case's stage-1 measurement, taken before stage 2 overwrote the fields. It is the evidence base for control C5. |
| `gate_k0c.json` | The graded result, every deviation as a number, with the controls and the cost. |
| `audit/` | `scripts/heat_balance.py` output per case: the JSON and the printed report, including its exit status. |
| `<case>/` | One OpenFOAM case each. `0.orig/`, `constant/`, `system/` and every `log.*` travel; time directories, `postProcessing/` and `constant/polyMesh/` are gitignored and are rebuilt from the dictionaries. |
| `<case>/CASE.txt` | The case's own statement of what it is: target Ra, dT, wall temperatures, gravity, planted source, mesh. |
| `<case>/COST.txt` | Wall clock per stage, single core. Core-minutes is the same number over sixty; there is no monetary figure because there is no verified rate for this machine. |

## The cases

Eight graded cases, four Ra on a mandatory two-mesh pair each, plus three
control twins:

| Ra | coarse | fine | refinement ratio |
| --- | --- | --- | --- |
| 1e3 | `Ra1e3_m32` | `Ra1e3_m64` | 2.0 |
| 1e4 | `Ra1e4_m40` | `Ra1e4_m80` | 2.0 |
| 1e5 | `Ra1e5_m64` | `Ra1e5_m128` | 2.0 |
| 1e6 | `Ra1e6_m128` | `Ra1e6_m192` | 1.5 |

| Control | What is planted | Kind |
| --- | --- | --- |
| `C1_Ra1e5_m128_g0` | gravity set to zero | recognition (gross), and reachability |
| `C2_Ra1e5_m128_dT110` | dT, hence Ra, raised by exactly 10 percent | recognition at the gate's own scale |
| `C3_Ra1e5_m64_source` | a 5.000e-03 W uniform volumetric heat source | reachability of the energy-balance row |
| C4 (no case) | the comparator's own inputs, in `analyse_k0c.py` | reachability of every band, one at a time |
| C5 (no case) | nothing; it compares stage 1 against stage 2 | recognition of a relaxation confound |

## Rebuilding from scratch

```
python3 build_cases.py
./run_cases.sh Ra1e3_m32            # and each other case
./continue_cases.sh 30000 Ra1e3_m32 # stage 2
./rewrite_precision.sh Ra1e3_m32    # stage 3
python3 analyse_k0c.py
```

`Ra1e6_m192` is the exception: it takes `endTime 4000` at stage 1 and
`./continue_cases.sh 24000` at stage 2.

## One warning that is not decoration

Do not clean these cases with `rm -rf <case>/[0-9]*`. That glob matches
`0.orig`, and one such loop deleted every initial-condition directory in the
K0b tree before a hygiene check caught it. Every script here uses
`foamListTimes -rm`, which enumerates parseable time values and therefore
cannot see `0.orig` at all.
