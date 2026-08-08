# A3 FD-verification arm (charter §7) — 3-component FD vs the converged M6 gradient: PRE-REGISTRATION

Filed 2026-08-08T22:33Z by the DAFoam solver agent, chief ruling 2 of the entry-8 epilogue
(14d57c8e). Until this passes, the TPC1 gradient is an existence proof, not a number anyone
may use (the converged arm's own scope note, binding). Committed BEFORE launch. ~30 core-min.

## 1. Configuration

Same case and converged-arm configuration (`runScript_tpc1.py` lineage: `transonicPCOption 1`,
stock ILU, env unset, 4 ranks, same partition/coloring cache), cold-started by the standing
repair (the control arm's leftovers moved to backup, `decomposePar -fields` from pristine
serial `0/`). New script `runScript_fd3.py`, exactly three functional changes from
`runScript_tpc1.py`:

1. `primalMinResTol: 1.0e-6 -> 1.0e-8` — S1's tight-primal discipline, per the ruling.
2. `primalMinResTolDiff: (default 100) -> 1.0e4` — keeps DAFoam's hard-fail gate at the
   record's effective 1e-4 so an unreachable 1e-8 target reports a shallow plateau instead of
   fabricating a crash. The achieved primal depth is measured operationally (see §4 noise
   floor) and reported.
3. A new task `fd3` implementing the protocol of §3 (baseline, adjoint, central FD at two
   steps, repeat-baseline drift).

## 2. Component choice and the index-mapping check (the S1 lesson)

Three components, one per DV group, selection basis pre-stated: **largest |adjoint gradient
component| within each group** from the converged arm's totals (maximum signal-to-FD-noise);
no cell/serial mapping is involved (these are FFD/global/patch DVs, not field cells), and the
mapping hazard is closed BY CONSTRUCTION: perturbations are applied through the same
`om.Problem` DV vectors that produced the totals dict columns, and the script logs, for each
component, the DV value before/after perturbation AND the adjoint component it reads at that
index, so the pairing is verifiable in the log.

| component | index | converged-arm adjoint value (reference) |
|---|---|---|
| `patchV[1]` (AoA) | 1 of 2 | 0.00764612 |
| `twist[1]` | 1 of 5 | 0.00173254 |
| `shape[5]` | 5 of 10 | −0.12418968 |

Objective: CD (`scenario1.aero_post.CD`), the family's standing FD class. The arm's
comparison is FD vs THIS ARM'S OWN adjoint (recomputed at the 1e-8-target primal); the
converged arm's values above are recorded to also report gradient drift vs primal depth.

## 3. FD protocol

Central differences, absolute steps, two step sizes per component (the `A_stepsize_study`
pattern): h = 1e-3 and 2h = 2e-3, in each component's native units (deg for AoA/twist, FFD
displacement for shape). Sequence: baseline `run_model` → `compute_totals` (adjoint; the
wrapper renames solutions 0.0001/0.0002 — leftovers cleared pre-run so no collision) → for
each component and step, ±h `run_model` pairs (warm restarts from the neighboring converged
state — standard and desirable for FD; disclosed, not hidden) → DV restore → repeat-baseline
`run_model`. 14 primal evaluations + 2 adjoint solves total.

## 4. Pre-registered acceptance bands (the family's standing bands)

- **Noise floor**: baseline CD drift |CD_base2 − CD_base1| is the operational plateau noise;
  a component is EVALUABLE only if |CD(+h) − CD(−h)| > 10x that drift.
- **Step-consistency**: |FD(h) − FD(2h)| / |FD(h)| < 1% required for the component to be
  evaluable; violation = noise-dominated, reported as such, no verdict from that component.
- **Verdict per evaluable component** (adjoint vs FD(h) relative error): **PASS < 5%**,
  **CONDITIONAL 5–15%** (the standing single-component band), **FAIL > 15% or sign flip**.
- **Arm verdict**: PASS = all evaluable components PASS and >= 2 components evaluable;
  CONDITIONAL = any evaluable component in 5–15% with none failing; FAIL = any FAIL;
  NOT EVALUABLE = < 2 evaluable components (reported with the noise measurements).
- Until the arm returns PASS, the M6 gradient remains an existence proof — binding
  regardless of outcome wording.

## 5. Mechanics

`dafoam-subpclu:v1`, env unset, `--cpus=4 --memory=10g` (ILU envelope), setsid +
`.t0/.rc/.t1` ledger via `run_arm_fd3.sh`, log `fd3_run.log`, polled inline (explicit
handoff if the turn ends mid-run). Host re-checked at launch (S1/Cases agents resuming on
the box). Budget ~30 core-min (14 warm primals at the ~10–30 s scale + 2 adjoint solves at
~110 s record). Result appended to `A3_SUBLU_RESULT.md`; docket entry updated inline, own
entry only.
