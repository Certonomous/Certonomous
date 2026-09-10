# Ahmed body, 25° slant — which Cd is which, and why they differ

**Date:** 2026-07-30
**Why this document exists:** an act-survey audit flagged that "the Ahmed act
reports Cd 0.3041 against a reference of 0.285, while the A4 ladder record
reports 0.2510 and 0.3219", and asked whether these disagree. **They do not
disagree.** They are three different measurements that were never in conflict,
but no single document said so, and the risk the audit correctly identified is
real: someone narrating over the act's footage could reach for A4's numbers, or
worse for A4's **10.04% CONDITIONAL** gradient grade, and attach either to the
wrong thing. This document is the one place that settles it.

**Nothing here is withdrawn or newly measured.** Every value below already
existed in the record; what was missing was the relationship between them.

---

## The short answer

| # | Cd (frontal basis) | What it is | Mesh | Code | Where it belongs |
|---|---|---|---|---|---|
| 1 | **0.3041** | The **act's** production result — what is on camera | **79,439 cells** (snappyHexMesh castellated refinement **3**) | `simpleFoam`, SIMPLEC | `NINE_ACT_GATE_TABLE.md`, `FILMING_COMMANDS.md` |
| 2 | **0.3219** | The **pre-existing validated baseline** that A4 *reused* — not an A4 result | **45,753 cells** (refinement **2**) | `simpleFoam`, SIMPLEC | `A4_ahmed_body.md`, `wall.json` credential, F10 family |
| 3 | **0.2510** | A4's **DAFoam primal** — **WITHDRAWN**, do not cite | 45,760 cells (refinement 2) | DAFoam `DASimpleFoam`, plain SIMPLE | `A4_ahmed_body.md`; withdrawal in `ACTIVE_RESEARCH.md` and `NOT_PASSING_REGISTER.md` |

Reference for all three: Cd 0.285, Ahmed, Ramm & Faltin 1984, SAE 840300,
±15% band, defined once in `models/curriculum/ahmed_25/reference.yaml`.

**1 and 2 are two rungs of a single grid-refinement ladder that the act itself
ran and published.** 3 is a different code and is off the board.

## Why 0.3041 and 0.3219 differ: one knob, and only one

The two case directories were compared field by field:

- **Identical:** the STL (`md5 ec3abd312d3e3e9d15340b95365ff62f` on both
  `mission-output/ahmed-body/act7-ahmed_25/case/constant/triSurface/ahmed_25.stl`
  and `mission-output/geometry-study/study-ahmed_25/case/constant/triSurface/ahmed_25.stl`),
  `system/fvSchemes`, `system/fvSolution` (including `SIMPLE { consistent yes; }`,
  i.e. SIMPLEC, and `residualControl` 1e-4 on p/U/k/omega), `system/blockMeshDict`,
  `constant/transportProperties` (`nu 1.5e-05`), `constant/turbulenceProperties`
  (`RASModel kOmegaSST`), the `0/` fields (`U uniform (40 0 0)`, `k 0.24`,
  `omega 8.56731`, wall functions), and the `forceCoeffs` block
  (`magUInf 40; lRef 1.044; Aref 0.401696; rhoInf 1.225`).
- **Different:** snappyHexMesh castellated refinement — **3** for the act
  (`sdk/workflows/geometry_study.py`, `refinement = int(params.get("refinement", 3))`)
  versus **2** for the baseline (`system/snappyHexMeshDict`: `body { level (2 3); }`).
  Cell counts from each case's own `log.checkMesh`: **79,439** and **45,753**.
- Secondary: iteration cap 300 vs 250, and the act ran on 6 subdomains while the
  baseline ran serial.

So none of the usual explanations apply. Same slant angle, same solver, same
closure, same Reynolds number (U=40, L=1.044, ν=1.5e-5 → Re ≈ 2.8e6), same
reference areas, same rebasing, same experiment. **Mesh density is the whole
difference.**

## The act's own ladder proves it

`mission-output/ahmed-body/transcript.txt` publishes the refinement study
during the act:

| rung | cells | Cd (planform) | Cd (frontal, × 0.401696/0.112) |
|---|---|---|---|
| coarse | 20,621 | 0.1010 | 0.3622 |
| **middle** | **45,753** | **0.0898** | **0.3220** |
| production | 79,439 | 0.0848 | 0.3041 |

**The act's own middle rung *is* the A4 baseline mesh**, and reproduces its
number: 0.0898 against the baseline's 0.08978, a 0.02% match. Machine record:
`models/curriculum/uq-studies/ahmed_25.json` (`"updated_utc": "2026-07-30T16:01:02Z"`),
which also carries `"conclusive": false`, `"observed_order": 1.95`,
`"band_abs": 0.0202`, and the method string *"Richardson-extrapolated value
falls outside the measured range; ladder not in the asymptotic range."*

That band — ±0.0202 on planform Cd, i.e. **±0.072 on frontal Cd** — is more
than five times the 0.018 gap between 0.3041 and 0.3219. **The two numbers are
inside each other's numerical uncertainty.** There is nothing to reconcile
beyond saying which mesh each came from.

## What may and may not be said on camera

- **May:** "Cd 0.3041 against the published 0.285, 6.7% off, inside the ±15%
  band." That is the act's own gate line, and it is what
  `NINE_ACT_GATE_TABLE.md` records.
- **May:** "solver-backed, not validated — the grid-refinement study for this
  setup came back inconclusive." The act says exactly this itself in its
  conclusion, and the credential in `demo-output/website/wall/wall.json` already
  carries `"finest_rung": false`. The honesty is already on the record; keep it
  there.
- **Must not:** narrate **A4's 10.04% gradient** over this footage. A4's
  10.04% is an adjoint-vs-finite-difference agreement check on a **2,777-cell**
  mesh — a different mesh from all three above, used only for the gradient — and
  it is graded **CONDITIONAL** under the current standard
  (`DAFOAM_CASE_STATUS.md`, `NOT_PASSING_REGISTER.md`). It is not a drag
  accuracy figure at all and has no relationship to 0.3041.
- **Must not:** cite **0.2510**. Withdrawn — the 45,760-cell DAFoam primal's
  omega field diverged while its normalised residual read as converged, and the
  drag was computed from that state (`ACTIVE_RESEARCH.md`,
  `NOT_PASSING_REGISTER.md`).

## The A4 record is not wrong — it is scoped, and the scope is easy to over-read

`demo-output/website/dafoam/ladder-a/A4_ahmed_body.md` never claims to report
"the" Ahmed drag. It states in its own text that it *found and reused* the
existing validated case ("`grep -ril ahmed` ... turned up a real,
already-validated Ahmed body case ... It is **not** a rebuild from scratch"),
and its comparison table exists to put `simpleFoam` beside `DASimpleFoam` **on
one fixed mesh recipe**. It never mentions the 79,439-cell mesh and never claims
0.3219 is the finest available result. Any reading of A4 as "the lab's Ahmed
number" over-reads it.

## Open items this reconciliation surfaced (not fixed here)

1. **`ACTIVE_RESEARCH.md` contradicts itself on 0.2510**, 29 lines apart: the
   A4 row withdraws the primal drag, and a later paragraph still quotes 0.2510
   as sitting inside the experimental band. Corrected in that file on
   2026-07-30 alongside this document.
2. **`10.04%` is labelled PASS in the A4 files and CONDITIONAL elsewhere.**
   `A4_ahmed_body.md` and `A4_ahmed_body.json` (both 2026-07-28) still say PASS
   under the retired 1–12% band; `DAFOAM_CASE_STATUS.md`,
   `NOT_PASSING_REGISTER.md` and `ACTIVE_RESEARCH.md` say CONDITIONAL under the
   current standard. The A4 files were never updated. Flagged, not edited —
   ladder-A grading is another owner's call.
3. **`DAFOAM_CASE_STATUS.md` names the wrong turbulence model** for the A4
   comparison ("SA on the DAFoam side"). The solver log says otherwise:
   `logs_A4/A4_fine_primal_par4.log` prints `Selecting RAS turbulence model
   kOmegaSST`, and `A4_ahmed_body.json` records `"kOmegaSST (RAS, wall
   functions)"`. **Both sides were kOmegaSST**; the differing knob was SIMPLE vs
   SIMPLEC. Attributing any part of the gap to SA would be wrong. Flagged, not
   edited.
4. **Forward risk in F10.** `F10_YPLUS_FIX.md` promotes refinement 2→3 for
   Re ≥ 2.8e6. Refinement 3 *is* the 79,439-cell mesh, which by the act's own
   measurement yields Cd ≈ 0.3041, not 0.3219 — about 5.5% lower. All 52
   `simplefoam-ahmed-3d-viscous` ledger rows are refinement 2 (45,760 / 45,813
   cells); no refinement-3 row has a Cd at all. The F10 family headline
   ("13.28% off") will need restating once refinement-3 rows land. Flagged for
   the F10 owner.

## Scale note, for anyone tempted to blame Reynolds number

Across the 25 successful 25°-slant ledger rows spanning Re 1.53e6–3.13e6 at
fixed refinement 2, frontal Cd ranges **0.32171 to 0.32287** — a spread of
0.0012, or 0.36%. Changing refinement from 2 to 3 moves it by **5.5%**. Mesh
dominates Reynolds number here by more than an order of magnitude.

## Primary evidence

- Act: `mission-output/ahmed-body/transcript.txt` (gate block and refinement
  ladder), `mission-output/ahmed-body/act7-ahmed_25/log.simpleFoam`
  (`Cd: 0.084801705`, `SIMPLE solution converged in 154 iterations`),
  `.../coefficient.dat` (final `8.48017045e-02`), `.../log.checkMesh` (79,439
  cells), `.../log.snappyHexMesh` (refinement level 2/3 in `nearBody`/features),
  `.../report.md`.
- Baseline: `mission-output/geometry-study/study-ahmed_25/report.md`
  (Cd 0.08978, 45,753 cells), `.../log.simpleFoam` (runs to `Time = 250`, **no**
  convergence sentence), `.../coefficient.dat` (final `8.97763675e-02`),
  `.../case/system/snappyHexMeshDict` (`body { level (2 3); }`),
  `models/curriculum/results/ahmed_25.json` (`"tier": "VALIDATED"`,
  `"finished_at": "2026-07-23T04:23:19+00:00"`).
- Ladder: `models/curriculum/uq-studies/ahmed_25.json`.
- Credential: `demo-output/website/wall/wall.json` (`"finest_rung": false`).
- A4: `demo-output/website/dafoam/ladder-a/A4_ahmed_body.md` / `.json`,
  `demo-output/website/dafoam/ladder-a/logs_A4/` (`A4_fine_primal_par4.log`,
  `A4_compute_totals_run1.log`, `A4_check_totals_run1.log`).
- Reference: `models/curriculum/ahmed_25/reference.yaml`.
- Batch: `demo-output/website/mega-batch/ledger.jsonl`, 52 rows with
  `"solver": "simplefoam-ahmed-3d-viscous"`, indices 206351–206963,
  2026-07-29T02:12:45Z → 11:16:13Z (35 ok, 17 y+ gate failures).

---

## ADDENDUM 1 — 2026-09-10, cfd-supervisor (Opus 5). A FOURTH Cd BASIS EXISTS, AND IT IS THIS DOCUMENT'S JOB TO CATCH IT.

**lines whose number changed above this section: 0.** Nothing above is edited, withdrawn or
renumbered. The three-row table above stands exactly as written and every value in it is unchanged.

**Why this addendum exists.** This document was written to stop a narrator attaching the wrong Cd to
the footage. It reconciles **three** numbers — 0.3041, 0.3219, 0.2510 — and states that all three are
on the **frontal-area basis** against the 0.285 reference. **There is a fourth set of Ahmed Cd values
in this lab, on a DIFFERENT basis, and this document did not cover them.** They are the R4 asymptotic
ladder's, in `verification/campaign/R4_ASYMPTOTIC_RESULTS.md`, and they read **0.0848 → 0.0750** —
about a quarter of the reference. A narrator holding that table beside the 0.285 reference would be
out by a factor of three and a half.

### A1.1 THE FACTOR, AND THE MEASUREMENT THAT VERIFIES IT

The R4 cases report on the **planform** area — `Aref 0.401696`, read from
`verification/runs/R4_runs/c4b/system/controlDict` — while the published reference is on the
**frontal** area **0.1120 m²** (`models/curriculum/ahmed_25/reference.yaml`, `area_basis: frontal`,
0.389 × 0.288). The rebase factor is

    Aref / A_frontal  =  0.401696 / 0.1120  =  3.586571

**This is verified, not assumed, and the verification is a coincidence of meshes that makes it
checkable.** R4's coarsest rung `c1` is background divisions (60 13 36) = **79,439 cells**, raw
Cd **0.084801801**. Rebased: 0.084801801 × 3.586571 = **0.30415**. **The table at the head of this
document independently records row 1 — the act's on-camera production result — as Cd 0.3041 at
79,439 cells.** Same mesh, four significant figures, arrived at from opposite directions and from
records written six weeks apart. **The R4 ladder and the act's headline number are the same family.**

### A1.2 THE R4 LADDER, REBASED ONTO THIS DOCUMENT'S BASIS

Every row below is on the **frontal basis**, so it is directly comparable with the three-row table
above and with the 0.285 reference (±15 % band **[0.24225, 0.32775]**):

| rung | cells | raw Cd (planform `Aref` 0.401696) | **frontal basis** | final-window 2σ, as % of value |
|---|---:|---:|---:|---:|
| c1 | 79,439 | 0.084801801 | **0.30415** | 0.01 % |
| c2 | 144,240 | 0.079359699 | **0.28463** | 0.07 % |
| c3 | 254,911 | 0.073992743 | **0.26538** | 0.10 % |
| c4 | 454,691 | 0.074882228 | **0.26857** | 0.02 % |
| c4b *(replicate control)* | 468,509 | 0.074979080 | **0.26892** | 0.03 % |
| ~~c5~~ | ~~834,351~~ | ~~0.082466071~~ | ~~0.29577~~ | **6.31 % — REFUSED** |

**Every converged level lands inside the band.**

### A1.3 TWO THINGS A NARRATOR MUST NOT DO WITH THIS TABLE

**Do not cite c5.** `c5` (834,351 cells) is **`NOT A RESULT`** and is struck through here for the same
reason `R4_ASYMPTOTIC_RESULTS.md` strikes it: it ran to `endTime` 4,000 **without `residualControl`
ever firing**, and its final-window 2σ is **5.2e-03 — 6.31 % of its own value — against the lab's 5 %
ceiling**. Rule 5 clause 1: a level not iteratively converged is `NOT A RESULT` whatever its value.
**This matters more than it looks, because rebased, c5 is the SECOND-CLOSEST level to the reference
at 0.29577.** The most flattering number in the ladder is the one the lab refuses. **The settled
level to show is `c4b`, 468,509 cells, frontal-basis 0.26892, 2σ 0.03 % of value.**

**Do not say the c3→c4 turn is a finding.** The **+8.895e-4 increment from c3 to c4 is WITHDRAWN as a
FEATURE** — chief ruling 2026-08-10, recorded at `8f5bf878`, canonical record
`verification/campaign/R4_AHMED_TURN_WITHDRAWAL_2026-08-10.md`. It is a withdrawn feature between two
coarser levels. **It is not a verdict on the Ahmed case, and it has nothing to do with c5.**

### A1.4 WHERE THE REBASE WAS, AND WHY THAT WAS NOT ENOUGH

`models/curriculum/ahmed_25/reference.yaml` **already documented** the rebasing, in its `notes`:
*"The published drag is referenced to frontal area (0.112 m²); the solver reports on measured planform
area, so the comparison rebases by the ratio…"*. **So this was never undocumented — it was documented
in the one place a narrator does not read.** The two documents on the filming path — this one and
`R4_ASYMPTOTIC_RESULTS.md` — both omitted it. **A mitigation that lives outside the path it protects
is not a mitigation**, and that, rather than the arithmetic, is the finding worth keeping.
