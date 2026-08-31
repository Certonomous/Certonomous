# T22_CHTb_L1 — FEASIBILITY NOTE

## THIS IS NOT A PRE-REGISTRATION AND MUST NEVER BE CITED AS ONE

**T22 IS UNREGISTERED.** No `T22_PREREGISTRATION.md` exists, in the working tree
or at any commit — checked, not assumed: `git ls-files | grep -i T22` returns
nothing, and `docs/campaigns/T-family/` holds `T19`, `T19b`, `T20` and `T21`
pre-registrations and no `T22`. This file **does not become** that document by
being cited in a queue entry's `prereg_path` field.

**It fixes no gate, no threshold, no band, no cap on a graded quantity and no
label. It is not frozen. It could be rewritten tomorrow and nothing evidentiary
would be lost, because it carries no evidentiary content** — which is exactly
what distinguishes it from a pre-registration, whose freeze *is* its entire
evidentiary content (`CLAUDE.md` rule 2, `VERIFICATION_CHARTER.md` §2b).

## The run this note describes produces NO VERDICT

The queue entry that cites this file carries `prereg_commit: "FEASIBILITY"`, the
exact tag Sanaa ruled queue-legal on 2026-08-31
(`etc/sessions/2026-08-31T1551Z_sanaa_queue_ruling_yes_yes.md`, verbatim:
*"Unregistered feasibility and physics rungs are queue-legal, tagged
prereg=FEASIBILITY or prereg=PHYSICS; the runner accepts them and their outputs
are never gradeable as verdicts."*), enforced as an exact-match membership test
at `scripts/queue_entry_check.py:114`.

Consequently, and stated here on the run's own face rather than left to be
inferred from a tag:

- **This run produces no graded value.** No number it emits may be quoted as a
  measured result, a deviation, or a comparison against any reference.
- **It reaches no band.** None is declared, so none can be met or missed.
- **It needs no comparator.** `analyse_t22.py` does not exist and is not
  required to exist for this run to have served its purpose.
- **Its verdict vocabulary entry is none of PASS / GATE REACHED / GATE FAIL /
  NOT A RESULT.** Those five grade a registered gate. There is no gate here.
  The run either answers the question below or it does not.
- **Nothing it produces may be carried into a future graded T22 rung.** If T22
  is ever registered, that registration re-measures under its own frozen gates
  on its own runs.

## THE ONE QUESTION

A feasibility rung exists to answer exactly one question that reading the source
cannot answer (`VERIFICATION_CHARTER.md` §3, rung 1: *"It runs, it does not
crash, residuals fall."*). For `T22_CHTb_L1` that question is:

> **Does `chtMultiRegionSimpleFoam` advance this THREE-REGION 5-degree WEDGE
> case — `fluid` + `housing` + `core`, TWO conjugate `mappedWall` interfaces,
> and a sector-scaled volumetric source in the innermost solid — from its
> `0.orig` state without dying, and do its residuals fall?**

**Why source inspection cannot answer it.** The case combines a wedge
(axisymmetric) mesh with a *two-solid* conjugate stack. The lab's only measured
`chtMultiRegionSimpleFoam` precedent, `T5_CUBE_m` / `T5_CUBE_f`, is **Cartesian
with a single solid region**. Whether the solver's runtime handling of wedge
front/back patches survives at *two* region-coupled interfaces is a property of
the solver's execution, not of `build_t22.py`, and no amount of reading either
settles it. The mesh already passed `checkMesh` on all three regions (below);
that is a statement about the mesh, not about the solver on it.

**The question is answered by ANY outcome.** Clean completion, a cap at the
3000 s timeout, or a crash each answer it — a crash most informatively of all,
and a crash is a finding until triage says otherwise
(`SUPERVISION_CHARTER.md` §3). That is what makes this a feasibility rung and
not a graded one.

## No solver has run in this tree — MEASURED, with a planted control

Measured 2026-08-31T16:28Z in
`verification/runs/T-family/T22_runs/T22_CHTb_L1/`:

| artifact a solve would leave | count found |
| --- | --- |
| `0/` directory (`run_t22.sh` creates it by copying `0.orig`) | **absent** |
| numeric time directories | **0** |
| `log.solve*` | **0** |
| `STATUS.*` / `START.*` | **0** |
| `postProcessing/` | **0** |
| `processor*/` | **0** |

**Planted control (standing rule 3): the sweep was shown able to see a
non-zero.** The identical `find` predicates were run against a synthetic case
directory carrying a `500/` time directory, a `log.solve` and a `STATUS.PLANT`,
and returned 1, 1 and 1. A zero from a reader not shown able to see a non-zero
is not evidence; this zero was.

The only logs present are the four build/inspection logs — `log.blockMesh`,
`log.splitMeshRegions`, `log.checkMesh.{fluid,core,housing}`. `build_t22.py`
carries a hard refusal on solver names and drives meshing utilities only; the
launch lives in the separate `run_t22.sh` by design, so that a builder can never
launch.

## Mesh quality, MEASURED from the three checkMesh logs

Gates from `docs/standards/MESH_STANDARD.md` §3.1 (non-orthogonality hard gate
**70 deg**, warning band 65–70), §3.2 (skewness hard gate **4**), §3.3 (aspect
ratio advisory: above **1000** requires an alignment justification on the
record).

| region | cells | max non-ortho | max skewness | min cell volume | max aspect ratio | checkMesh |
| --- | --- | --- | --- | --- | --- | --- |
| `fluid` | 35,200 | **0** | **0.109152072608** | 6.73948906288e-11 | 162.627654918 | Mesh OK |
| `core` | 3,360 | **0** | **0.103363600467** | 5.86080893703e-10 | 1.26018522089 | Mesh OK |
| `housing` | 1,120 | **0** | **0.108291019105** | 1.31317246204e-09 | 1.80065562436 | Mesh OK |
| **total** | **39,680** | | | | | |

**Negative volumes: ZERO in all three regions.** Read as the direct quantity
rather than as an absence of a warning: every region's reported **minimum** cell
volume is strictly positive (6.74e-11, 5.86e-10, 1.31e-09 m^3), and checkMesh
reports `Cell volumes OK` for each.

**The mesh passes its own gate, with margin.** Non-orthogonality is 0 against a
70-degree gate — the mesh is an orthogonal graded wedge, so this is expected and
is reported, not gated on as if it were informative. Skewness is at most 0.109
against a gate of 4, a factor of 37. Maximum aspect ratio 162.6 in `fluid` is
below the 1000 advisory threshold and needs no alignment justification; it comes
from the deliberate near-wall grading (`GR_BL_IN = 40`, `GR_BL_OUT = 1/40`) and
sits alongside non-orthogonality 0 and skewness 0.109, i.e. nowhere near §3.3's
combined flag (AR > 1000 *with* non-ortho > 60 or skew > 2).

An earlier build put the `core` block on the axis with a collapsed edge and
`checkMesh -region core` returned three failures including
`Max skewness = 9.2966987286e+146` on 140 zero-area axis faces. That build was
replaced by the 6 mm shaft bore now in `build_t22.py:R_BORE`. **The obvious mesh
for this case did not pass and was measured failing before it was fixed** — the
figures above are the fixed mesh's.

## What runs, and what it costs

- **Launcher:** `verification/runs/T-family/T22_runs/T22_CHTb_L1/run_t22.sh`,
  which takes no arguments. Solver `chtMultiRegionSimpleFoam`, serial, 1 rank,
  `endTime 5000` iterations, `writeInterval 5000`.
- **CAP: 50.0 core-min**, REGISTERED here and hard-coded as `TIMEOUT_S=3000` at
  1 rank in `run_t22.sh` (`cap_core_min = TIMEOUT_S * RANKS / 60`). An overrun
  **stops the run**; it does not get a new budget (`CLAUDE.md` rule 12,
  `COMPUTE_BUDGET_CHARTER.md`:197). The `timeout` in the wrapper is what enacts
  that; the queue runner's `CAP_OVERRUN.txt` only *reports*.
- **POINT ESTIMATE: 15.4 core-min**, DERIVED from two MEASURED lab anchors, not
  guessed:

  | anchor | solver | cells | iterations | ExecutionTime | s per cell-iteration |
  | --- | --- | --- | --- | --- | --- |
  | `T5_runs/T5_CUBE_m` | chtMultiRegionSimpleFoam, 1 rank | 216,214 | 5,000 | 4,490.88 s | 4.1541e-06 |
  | `T5b_runs/T5_CUBE_f` | chtMultiRegionSimpleFoam, 1 rank | 896,531 | 5,000 | 20,833.54 s | 4.6476e-06 |

  Applied to T22's 39,680 cells × 5,000 iterations = 1.984e08 cell-iterations:
  **824 s (13.74 core-min)** at the `_m` rate, **922 s (15.37 core-min)** at the
  `_f` rate. The registered point is the conservative end of that measured
  bracket, **15.4 core-min**; the cap sits **3.25×** above it.

  **Named mismatches between anchor and case, disclosed rather than absorbed:**
  the anchors are Cartesian with ONE solid region and no volumetric source;
  T22 is a wedge with TWO solids and a source. T22 also runs on a contended box
  (two T19b solvers live at filing time), and contention inflates wall time,
  which is why the cap carries 3.25× headroom rather than 1.2×.

- **DERIVED, NOT MEASURED — the box cannot read its own billing**
  (`COMPUTE_BUDGET_CHARTER.md` §5): at the owner-stated c7a.4xlarge rate of
  **$0.0513/core-h** (REPORTED-BY-OWNER, 2026-08-21/22), the point estimate is
  **$0.0132** and the cap is **$0.0428**. Both are far under the $25
  pre-authorisation, and a blanket authorisation is not a per-item reading
  (`CLAUDE.md` rule 9).

## Age guard

`run_t22.sh` refuses if `$CASE/0` or any `[1-9]*` time directory exists, copies
`0.orig` to `0`, and **touches `0/housing/T` last**, so that file dates the run
allowed to produce the answer. `scripts/queue_entry_check.py`'s AGE-GUARD makes
the same check at filing time. Both were clean at filing.

## Authority, and what is NOT claimed

Filed by a heat-transfer `lab-lane` at the heat-transfer-supervisor's dispatch,
under Sanaa's 2026-08-31T15:51Z queue ruling and her 2026-08-31T16:15Z answer
*"1. Yes file"* to the question of whether heat-transfer files the T22 queue
entry (`etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md`).

**Enqueueing is not authorisation.** `SUPERVISION_CHARTER.md` §3 check 4 —
pre-registration committed before compute — is the supervisor's own and is **not
claimed as performed here**. For this entry that check has an unusual and
explicit answer: *there is no pre-registration, by design, and that is precisely
why the run can produce nothing gradeable.* The FEASIBILITY tag is Sanaa's route
for the **unregistered** case and **does not license a graded run without its
committed freeze** — a graded T22 would still need one, frozen first.

No agent's message is Sanaa's consent (`CLAUDE.md` rule 9); the two session
files above are the chief's verbatim capture of her own words and are cited as
such.
