# K2e runs — Boussinesq against variable density at fixed Ra

F14 rung K2e. Pre-registration: `../K2e_PREREGISTRATION.md`. Result:
`../K2e_RESULTS.md`. Tier **SOLVER-BACKED** — a model-to-model comparison with
no experimental reference, and it cannot reach VALIDATED.

## What is here

| path | what |
|---|---|
| `build_cases.py` | writes all 30 cases from one table. Ra is held at 1e5 and only `eps = beta.dT` moves; `nu` moves with `dT` to keep Ra fixed. |
| `run_cases.sh` | meshes and solves one case. Reads the application out of the case's own `controlDict`, so one script runs both solvers. |
| `archive_cases.sh` | copies the committable part of a solved tree (this directory's `m48_*` / `m96_*`). |
| `analyse_k2e.py` | grades the sweep against the pre-registered thresholds and writes `GATE_TABLE.md` and `gate_k2e.json`. |
| `m48_*`, `m96_*` | the 30 archived cases. |
| `GATE_TABLE.md` | generated. Do not hand-edit. |

Each archived case carries `0.orig/`, `constant/` (without `polyMesh`,
regenerated exactly by `blockMesh`), `system/`, `COST.txt`, the mesh logs, the
final `T`, `U` and `alphat`, and `log.<app>.monitor` — a filtered solver log
holding the banner, every `Time =` line and every function-object output line.
`scripts/check_convergence.py --monitor-regex` reads that file directly and
reproduces the convergence gate from it.

## Reproduce the numbers WITHOUT re-solving

Everything `GATE_TABLE.md` reports is re-derivable from the archive:

```sh
cd /home/ubuntu/Certonomous
python3 docs/campaigns/F14-cooling-ladder/K2e_runs/analyse_k2e.py \
        docs/campaigns/F14-cooling-ladder/K2e_runs \
        --md /tmp/K2e_GATE_TABLE.md --json /tmp/gate_k2e.json
diff /tmp/K2e_GATE_TABLE.md docs/campaigns/F14-cooling-ladder/K2e_runs/GATE_TABLE.md
```

`analyse_k2e.py` refuses to grade at all if its thresholds have drifted from the
pre-registration's; that check runs first, before any case is read.

## Reproduce the convergence gate with the campaign's own instrument

```sh
cd /home/ubuntu/Certonomous
for d in docs/campaigns/F14-cooling-ladder/K2e_runs/m*/; do
  python3 scripts/check_convergence.py "$d"/log.buoyant*.monitor \
    --monitor-regex 'areaNormalIntegrate\(hotWall\) of k2eGradT = ([-\d.eE+]+)' --oneline
done
```

All 30 must print CONVERGED. Read that script's own exit status, never a
pipeline's.

## Re-solve from scratch

Takes about 21 core-minutes; single-core per case, so run several in parallel.

```sh
REPO=/home/ubuntu/Certonomous
WORK=$(mktemp -d)
python3 $REPO/docs/campaigns/F14-cooling-ladder/K2e_runs/build_cases.py "$WORK"
cd "$WORK" && ls -d m48_* | xargs -P 8 -n 1 \
    $REPO/docs/campaigns/F14-cooling-ladder/K2e_runs/run_cases.sh
cd "$WORK" && ls -d m96_* | xargs -P 6 -n 1 \
    $REPO/docs/campaigns/F14-cooling-ladder/K2e_runs/run_cases.sh
python3 $REPO/docs/campaigns/F14-cooling-ladder/K2e_runs/analyse_k2e.py "$WORK" \
    --md "$WORK"/GATE_TABLE.md
```

Requires OpenFOAM v2606 at `/usr/lib/openfoam/openfoam2606`, which ships both
`buoyantBoussinesqSimpleFoam` and `buoyantSimpleFoam`; neither is a lab build
and `docs/OPENFOAM_SOLVER_BUILD.md` is not needed for this rung.

## What was actually verified of the three recipes above

All three were run verbatim from a `mktemp -d` **after** this file was written,
because three documents in this campaign have shipped recipes that could not be
followed. The first two ran in full and passed: the gate table came back
`diff`-clean and all 30 cases returned CONVERGED. The third was run **partially**
to stay inside the rung's compute authorisation — `build_cases.py` was run in
full and all 30 case definitions came out byte-identical to the archived ones
(90 directory comparisons, 0 differences), and two cases at eps = 0.1, one under
each solver, were re-solved and came back bit-identical in `Nu_h` and in the
final `T` and `U`. The other 28 solves were not repeated.

## One thing that will bite you

`scripts/heat_balance.py` deletes `<case>/postProcessing` (line 770) before its
own postProcess pass. Audit a case in place and its function-object history is
gone — which is why `analyse_k2e.py` audits a COPY and why the convergence
evidence archived here is a filtered LOG and not a `postProcessing` tree.
