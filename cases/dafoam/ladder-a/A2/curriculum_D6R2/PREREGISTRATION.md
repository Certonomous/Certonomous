# Curriculum D6R2 — the 3D transonic MULTIPOINT optimisation, run to a budget it can reach, with nothing left to kill it on the clock

**Item id:** `D6R2` (dafoam curriculum successor to `D6R`; the A2 MACH wing multipoint
optimisation named mandatory by Sanaa 2026-09-07, `etc/sessions/2026-09-07T0330Z_sanaa_dafoam_multipoint_mandatory.md`).
**Version 1.0 — FROZEN 2026-09-12 by dafoam `lab-lane` for `dafoam-supervisor`.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze sha is the commit that
introduces this file. Permission for detached launches: **`bc0e687e`**. **Nothing here is sent,
filed, uploaded, registered, posted or commented** (rule 7). **No frozen file is edited** (rule 6).
**This item has burned 0 core-min and started no container at freeze.**

> **ID-NAMESPACE WARNING.** `docs/DOCKET.md` carries fleet-defect rows numbered D6. Every `D<n>`
> here is the **curriculum** item.

## 0. The two failures this item exists to repair, both MEASURED

**FAIL-1 — D6's `O_mp` was killed by its own clock.** Ledger row
`/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint/ledger.txt`:
`rc=124 wall_s=30008 ranks=4 core_min=2000.533 cap_core_min=2000.0`. The chain closed
`STOPPED_AT_FIRST_NONZERO arm=O_mp rc=124`; three arms never ran. Item verdict `NOT A RESULT`.

**FAIL-2 — D6R's `O_mp` ran to completion of nothing: IPOPT died on an evaluation error.**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp/opt_IPOPT.txt` closes:

```
Number of Iterations....: 73
EXIT: Invalid number in NLP function or derivative detected.
```

preceded by repeated `Warning: Cutting back alpha due to evaluation error` and
`Warning: Evaluation error during soft restoration phase step.`. The arm recorded `rc=0` (the
container exited cleanly) but **the optimiser did not terminate itself — it crashed** at major 73
against its registered `max_iter: 80`. The first `Primal solution failed!` is at log line 20,959 of
264,607, so primal failures ran through the whole optimisation and the line search absorbed them
until it could not. **D6R's `O_mp` is a completed container around a failed optimisation, and it is
not a result about multipoint optimisation.** Its `ACC_mp` arm then hit `rc=124` — the clock again.

**What D6R nonetheless MEASURED, and this item reuses as its anchor.** The weighted multipoint
objective fell from `obj.J = 0.03064163` at the first evaluation to `obj.J = 0.0222388` at the
crash — **27.4 % of the weighted mean drag, across three lift points, on 96 FFD + 7 twist design
variables** — with all three CL constraints held (`0.39997369 / 0.49993216 / 0.59985632` against
targets `0.4 / 0.5 / 0.6`, worst miss `1.44e-4`) and `volcon = 1.00221414`. The optimisation works.
What failed was (a) letting it run past the point where its line search collapses, and (b) a clock
that kills.

## 1. What changes from D6R, and ONLY this

The four science instruments are D6R's bytes with the `d6r_` → `d6r2_` rename; the diffs are
`d6r2_opt_runScript_DELTAS_from_d6r.diff` and `d6r2_run_arm_DELTAS_from_d6r.diff` beside this file.

| | D6R | D6R2 |
|---|---|---|
| case, mesh (9,504 cells), np=4, FFD 6×2×8 (96 DVs), twist (7), three scenarios `cl04`/`cl05`/`cl06`, CL targets 0.4/0.5/0.6, weights **w = (0.25, 0.50, 0.25)**, composite `J = Σ wᵢ·CDᵢ`, thickness/volume/LE-radius constraints, `findFeasibleDesign` trim, solver `DARhoSimpleFoam`, `primalMinResTol 1e-8`, image `dafoam-idwarp-rot:v1` @ `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` (PATCHED row only) | as D6 | **identical, byte-for-byte** |
| **IPOPT `max_iter`** | `80` — **not reachable**: the line search collapsed at 73 | **`25`** — a BUDGET the measured run demonstrably reaches, so IPOPT terminates ITSELF and prints `EXIT: Maximum Number of Iterations Exceeded.` |
| **in-container clock kill** | `timeout -k 60 $TMO` at the registered cap wall — the mechanism that produced D6's `rc=124` and D6R-`ACC_mp`'s `rc=124` | **REMOVED.** Sanaa's NO-CAP ruling (`6f3abf8a3`): nothing dafoam owns kills on spend or clock. The container runs to the optimiser's own exit. |
| **runaway CEILING** | `4 × CAP`, `action=HARD_STOP` (`docker stop`) | **REPORTS, never stops** (`D4S_CEILING_CROSSED … REPORTED_RUN_CONTINUES`), same ruling |
| run root | `CURRICULUM-D6R-a2-wing-multipoint` | `CURRICULUM-D6R2-a2-wing-multipoint-transonic`; D6R's and D6RACC2's roots added to `FORBIDDEN_ROOTS` so this launcher can never stage over a graded row |
| arms | chain `O_mp → ACC_mp → F_mp → REF_off` | **`O_mp` ALONE.** The gradient-verification arms are a separate item; this item's deliverable is a completed multipoint optimisation with saved results. |

**Why `25` and not more.** `31.258 core-min/major` is the MEASURED multipoint rate (C-188 `8262f123`,
from D6's `2000.533 / 64 majors`). D6R reached major 73 in 34,200 wall s at 4 ranks. 25 majors is
inside every measured envelope, and D6R's own trajectory shows `obj.J` already at `0.02513271` by
its fifth objective print. **The iteration count is a budget, not a promise** — the lab's own demo
language for exactly this case (`docs/dafoam/demo/ACT_D_multipoint_optimisation_script.md`).

## 2. THE GATES, FROZEN. The threshold, the cap, the label.

Graded on the arm's own log, `opt_IPOPT.txt`, `OptView.hst` and the arm directory, all read AFTER
the container exits.

- **G1 — THE OPTIMISER TERMINATED ITSELF.** `rc = 0`, `opt_IPOPT.txt` present and newer than the
  age datum, carrying `Number of Iterations....: 25` and
  `EXIT: Maximum Number of Iterations Exceeded.`. Any other `EXIT:` line — in particular
  `Invalid number in NLP function or derivative detected` — **FAILS G1**. `rc = 124`, `137` or any
  non-zero **FAILS G1**.
- **G2 — THE PHYSICS GATE, WITH ITS BAND.** `J0` = the FIRST `obj.J` printed by THIS run;
  `Jf` = the LAST. **PASS requires `Jf ≤ 0.90 × J0`** — at least a **10 %** reduction in the
  weighted mean drag coefficient across the three lift points. (D6R measured 27.4 % at major 73 and
  ~18 % by its fifth print; 10 % at 25 majors is a bar this case can miss and is not a formality.)
- **G3 — THE LIFT CONSTRAINTS ARE HELD AT THE FINAL DESIGN.**
  `max_i |CL_i − target_i| ≤ 1.0e-3` over `cl04 / cl05 / cl06`. (D6R's measured worst miss: `1.44e-4`.)
- **G4 — THE RESULTS ARE SAVED, AND THEY ARE THIS RUN'S.** All present in the arm directory and
  **strictly newer than the age datum `0/U`**: `OptView.hst`, `opt_IPOPT.txt`, and field data at
  time `1000` under `mp04/`, `mp05/` and `mp06/` `processor*`. A run whose results were not written
  is not showable and is not a result.

**LABELS.**
- `PASS` — G1 ∧ G2 ∧ G3 ∧ G4.
- `GATE FAIL` — G1 ∧ G4 hold, and G2 or G3 misses. The value, `J0`, `Jf`, the ratio and the three
  CL misses are printed beside it.
- `NOT A RESULT` — G1 or G4 fails. No number from this run is quoted as a result.
- No other label. No synonyms (rule 1).

**A Roache triple is NOT claimed and no GCI is quoted.** This item is a single-grid optimisation;
rule 5 does not apply to it and nothing here will be dressed as grid convergence.

## 3. COST, in core-minutes, BEFORE the run (rule 12)

| | figure | basis |
|---|---|---|
| predicted compute | **781.5 core-min** | 25 majors × **31.258 core-min/major**, the MEASURED multipoint rate (C-188 `8262f123`) |
| staging + container preamble | **~5 core-min** | D6R measured preamble ≤ 3.3 s (D4S-F3S) |
| **REGISTERED PREDICTION** | **786 core-min** | sum of the two above |
| reported ceiling (**reports, never stops**) | 3144 core-min | 4 × the 786 figure, ledger row only, NO-CAP ruling `6f3abf8a3` |
| derived dollars | **$0.67** | 786/60 h × 4-rank-hour price … at $0.0513/core-h. **DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Contention caveat, registered in advance.** The 31.258 anchor was measured at
`delivered_cores_mean ≈ 3.98` of 4 requested. At freeze this box carries `load1 ≈ 40` on 16 cores
with cfd and heat-transfer solving. `core_min = wall_s × ranks / 60` therefore **inflates with
contention at identical compute work**. A recorded figure above 786 core-min attributable to
delivered-core starvation is **REPORTED with the measured `delivered_cores_mean`, and is not a gate
and not a stop** (rule 12: waste is named, never absorbed; NO-CAP: nothing kills on spend).

## 4. Placement, ranks, memory

`RANKS=4`, `CPUSET=2,3,4,14` (D6R's registered placement, carried unchanged), `--memory=20g`.
An OOM kill (`rc=137`) is a registered outcome and fails G1 as `NOT A RESULT`.

## 5. What this item does NOT claim

It does not verify the gradient (that is the `F_mp` / FD family, and D6RF3's `F_mp` closed `rc=1`).
It does not claim the primal reaches the A2 accept floor of `1.0e-5` — D6RF10 measured that the
`DARhoSimpleFoam` config used here does **not** (`p_first_uncorrected = 1.681e-05`, `GATE FAIL`)
and that the `DARhoSimpleCFoam`/nNonOrth-12/relax_p-0.70 config **does** (`6.323e-06`, binding
`PASS`, `R3_autograde.json`). **That solver change is a separate registered successor (`D6R3`) and
is deliberately NOT taken here**, because its adjoint has never been exercised on this case and an
untested adjoint is not what an overnight run to a demo should carry. This item reuses the primal
that is proven through 73 IPOPT majors and their adjoints.
