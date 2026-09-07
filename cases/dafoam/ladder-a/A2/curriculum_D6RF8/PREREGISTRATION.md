# Curriculum D6RF8 — A2-wing convergence probe `P_conv`, the RE-MESH successor to D6RF7 (NOT A RESULT / G-CONV GATE FAIL)

Supersedes: **D6RF7** — A2-wing convergence probe `P_conv`, overall **`NOT A RESULT`** with a substantive
**`G-CONV GATE FAIL`** inside. D6RF7 measured, on the D4 base mesh, that Fix #1 (`Gauss linear limited
corrected 0.333`) **+** Fix #2 (`nNonOrthogonalCorrectors 3`) do **NOT** bring `p`'s first uncorrected solve
under the `1.0e-05` accept floor: `p_first_uncorrected initRes 1.625570732e-05` = **1.626×** the floor
(graded leg L1); the F5 falsifier at D6RF4's original scheme gave `1.658e-05` = 1.658×, AS PREDICTED.
Verdict json: `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF7-a2-wing-convergence-probe/d6rf7_official_verdict.json`
(freeze `347976d2`); RESULTS beside the case at `curriculum_D6RF7/RESULTS.md`.

Under rule 2, D6RF7 has COMPUTED — its gates are closed and its frozen files are not edited. Its NOT A RESULT
record stands. **The fix is a SUCCESSOR** (this item, D6RF8), not an edit to a frozen D6RF7 file.

**PERMISSION = NOT_FROZEN.** This is a lane's prediction-first proposal. Nothing here is a registration until
the dafoam-supervisor replaces the `PERMISSION` placeholder in `d6rf8_run_arm.sh` with a pre-registration sha
(CLAUDE.md rule 2), after the supervisor's non-delegable check-1 **and** after the re-mesh has been generated
and its `MD5_REF_MESH` fixpointed (§4, §7). The freeze, the mesh-gen go, and the enqueue belong to the
supervisor and are not taken here.
**No gate, threshold, cap, band or label below may be altered after first compute** (rule 2); D6RF8 is a NEW
item, so **its gates are OPEN pre-compute** — before first compute this file is amendable, and any amendment
must state the condition and how it was checked.

**Single-point by design.** Multipoint is mandatory lab-wide, but this A2 **convergence probe** is single-arm
`P_conv` by design (as D6RF3→D6RF7); it exists to measure whether the primal reaches its own accept floor, not
to optimise. It buys no F_mp / REF_off arm, so the FD/CD/off-design/price gates read want-of-input exactly as
in D6RF7. The multipoint SHIPPED row is NAMED-UNBOUGHT and priced (§5), not bought here.

---

## 0. WHY A SUCCESSOR AT ALL — the mesh is the diagnosed common cause

D6RF7's finding is not a null: it is a **measured** demonstration that scheme-side aids are insufficient. The
binding residual is `p`'s uncorrected first solve, mechanistically the **magnitude of the explicit
non-orthogonal correction term** carried lagged into each outer iteration's first pressure assembly
(`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:56-66`). `checkMesh` on the D4/D6RF7 base measured **max
non-orthogonality 71.48°** (`… :56-58`, `Mesh non-orthogonality Max: 71.47582467`), which **exceeds DAFoam's
own default `maxNonOrth: 70.0`** (DAFoam FAQ, fetched — `… :58-59`). That correction term is irreducible at
fixed mesh and fixed scheme — which is exactly why "run longer", "tighten relTol", the limited scheme, and 3
correctors all already failed. The one un-tried lever that attacks the mechanism directly is **RANK 7 — a
re-mesh below the non-orthogonality limit** (`… §3 RANK 7`, `… §4` basis 2). The `1.0e-05` accept floor
**stays**; widening it (DAFoam's own two documented remedies) is forbidden (N-D43; Sanaa 2026-09-04).

## 1. THE ONE CLASS OF DELTA — the mesh, and nothing else

D6RF8 changes **exactly one thing: the volume mesh.** Everything else is carried forward from D6RF7
byte-identical in logic:

- **The mesh (the DELTA).** A re-meshed A2-wing volume mesh with **max non-orthogonality < 70.0°** (hard
  acceptance; the mesh-gen aims lower — see §7 — for margin, RANK 7 names ~40°). The re-mesh replaces
  `constant/polyMesh/` of the run base. The **FFD control box** (`FFD/wingFFD.xyz`), the boundary/patch
  topology, the `0/` initial fields, `constant/` transport/turbulence, and `system/` (fvSchemes, fvSolution,
  controlDict) are carried **unchanged** — the design-variable parameterisation and the discretisation are
  not the lever.
- **The scheme is carried forward UNCHANGED.** `d6rf8_fvSchemes_LIMITED` (`Gauss linear limited corrected
  0.333`), `d6rf8_fvSchemes_D6RF4_ORIGINAL`, and the fvSolution `nNonOrthogonalCorrectors 3` are byte-identical
  to their D6RF7 counterparts. This is deliberate: holding the scheme fixed isolates the mesh as the single
  independent variable, so a G-CONV flip is attributable to the mesh alone.
- **The D6RF7 grader fix is carried forward UNCHANGED.** The entire grading-path-survives-present-but-empty
  machinery (D6RF7 §1, the 12-site table + the two fixture-exposed read-path fixes A/B, the single detector
  `cdc.points_empty_by_primal_raise`, fail-closed) is carried into `d6rf8_grade.py` / `d6rf8_cd_plant_control.py`
  **logic-identical**. It must survive the failure path in case the re-mesh does NOT clear the floor (see the
  falsifier, §2). The only byte changes to these files are the `d6rf7_→d6rf8_` renames and the `D6RF7_→D6RF8_`
  marker strings — no gate, threshold, band, cap, accept-floor or scheme changes (N-D43, T25).
- **The cap is carried forward at 186.00 — and the D6RF8 stager carries 186.00 FROM THE START.** D6RF8's
  `d6rf8_grade.py` registers `CAPS = {"P_conv": 186.00}` (D6RF7 `d6rf7_grade.py:200`, PREREGISTRATION §5 est
  62.0 / cap 186.0, MAX form). The D6RF8 stager `d6rf8_stage_root.sh` MUST be authored with
  `ITEM_CEILING_CORE_MIN = ARM_CAP_CORE_MIN = 186.00` from the start — **never the stale 54.00** that the
  inherited D6RF7 stager carried before its 2026-09-07 cap reconciliation. This is a registered constraint on
  the clone.

## 2. THE REGISTERED PREDICTION and its FALSIFIER

**Primary prediction — the rung that could reach a PASS: `G-CONV PASS` on L1.** On a mesh with max
non-orthogonality **< 70°**, the explicit non-orthogonal-correction magnitude falls, and the hypothesis is
that `p_first_uncorrected initRes` drops **below** the `1.0e-05` accept floor at the final iteration —
`G-CONV = PASS`. This would be the **first PASS on the A2 convergence probe** and would confirm the mesh as the
diagnosed cause, unblocking the A2 optimisation ladder. `nuTilda` (D6RF7 L1 `1.408e-05`, also over floor) is
predicted to fall under the floor on the same mechanism; it is graded per-field alongside `p`.

**Overall verdict caveat (unchanged ladder, NOT widened).** Because `P_conv` is a single-arm probe that buys
no FD/CD arm, the CD-dependent gates (G-FD, G-OFF, G-PRICE) and G-DVL's REF_off arm read **NOT A RESULT for
want of an input** exactly as in D6RF7 — but now the reason is `ARM_NOT_REGISTERED_AT_THIS_FREEZE` / the
P_conv-takes-no-FD-step branch, **not** `ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY` (the primal is predicted to
CONVERGE, not raise). The **overall verdict therefore remains `NOT A RESULT` at ladder rung 6** even on a
G-CONV PASS, with the substantive win disclosed as **G-CONV PASS** in the per-gate breakdown. The ladder
(rule 5) is unaltered and not widened; a want-of-input NOT A RESULT can only turn a PASS/GATE FAIL INTO a
NOT A RESULT, never the reverse. (Whether a future item should register the full arm set to grade the whole
ladder to an overall PASS is a design decision reserved to the supervisor; it is NOT taken here and would be
the multipoint SHIPPED row, not this single-point probe.)

**The FALSIFIER — and it is the scientifically load-bearing branch.** If, on a mesh whose `checkMesh`
max non-orthogonality is **verified < 70°**, `p_first_uncorrected initRes` is **still ≥ `1.0e-05`** at the
final iteration → **`G-CONV GATE FAIL`**, and then, per `docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:294-301`,
the exhaustion of RANK 1 (limited 0.333) + RANK 2 (3 correctors) + RANK 7 (re-mesh below the limit) makes a
**DAFoam capability-gap claim WARRANTED — and only then, filed with that measurement.** D6RF8 is the item that
either clears the floor or earns that claim. The accept floor stays `1.0e-05` in either branch. `d6rf8_grade.py`
carrying the D6RF7 failure-path fix is what lets the GATE FAIL branch produce a graded verdict rather than
crashing.

**Falsifier F5 (carried forward).** The identical primal at D6RF4's ORIGINAL scheme (leg L3) is predicted to
`GATE FAIL` its named gate at the re-meshed geometry unless the mesh alone clears even the 1-corrector scheme;
its withdrawal clause is carried forward unchanged (if the WRONG setting ALSO passes G-CONV, G-CONV is not
measuring the stopping rule and its verdict withdraws).

## 3. FIXTURE VALIDATION — what can and cannot be proven before the re-mesh

Unlike D6RF7 (whose entire DELTA was grading-side and was fully fixture-validated off the D6RF6 log with NO
re-solve), **D6RF8's DELTA is the mesh, and a new mesh cannot be fixture-validated from an old log** — the
residuals it must produce do not exist until the re-meshed primal runs. Therefore:

- **Grader-logic carry-forward** IS fixture-validatable NOW, before mesh-gen: re-running `d6rf8_grade.py`
  (logic-identical to D6RF7) against the D6RF7 run root must reproduce D6RF7's verdict byte-for-byte (G-CONV
  GATE FAIL, the four want-of-input gates, controls, overall NOT A RESULT). This proves the rename introduced
  no logic drift. **[TO RUN at clone time — grader is read-only, no solver.]**
- **The G-CONV verdict on the re-meshed geometry** is NOT provable without the re-mesh + the official re-run.
  It is registered as a prediction with a falsifier (§2), to be graded by the supervisor's freeze + run.

## 4. PIN FIXPOINT — plan and the ONE pin that cannot close pre-mesh

**`ALL_PINS_MATCH` is NOT asserted in this document and must NOT be, because the mesh anchor does not yet
exist.** Asserting a pin fixpoint against an absent mesh would be a planted zero (CLAUDE.md rule 3). The
fixpoint closes in TWO stages:

- **Stage 1 (clone time, mesh-independent, before mesh-gen or after):** every owned instrument is cloned
  `d6rf7_*→d6rf8_*`, its internal self-references and `D6RF7_→D6RF8_` markers renamed, and every **file-vs-file**
  md5 pin re-derived to a fixpoint (`MD5_RUNSCRIPT`, `MD5_LOCUS`, `MD5_FVSCHEMES_LIMITED`,
  `MD5_FVSCHEMES_ORIG`, `MD5_FVSOL`, `MD5_EXTRACT`, `MD5_PHYS`, `MD5_FD`, `MD5_UNITS`, `MD5_ANCHOR_GATE`, and
  the grader's internal `FVSCHEMES_MD5`). These do not depend on the mesh and CAN reach `ALL_FILE_PINS_MATCH`.
- **Stage 2 (after the approved mesh-gen):** `MD5_REF_MESH` in `d6rf8_run_arm.sh` is set to the md5 of the
  **new** `constant/polyMesh/points.gz`, and the D6RF8 stager's derivation re-verifies it against the staged
  base. Only after Stage 2 may `ALL_PINS_MATCH = TRUE` be asserted, and only then is the item freezable.

`MD5_REF_MESH` is currently **PENDING mesh-gen**. `D4_BASE_SRC` (the base the stager copies) re-points from
the D4 base to the **re-meshed D6RF8 base** (path fixed at mesh-gen).

## 5. COST — costed est / cap (rule 12), mesh-generation stated SEPARATELY

**(a) The graded primal re-run.** Registered at **est 62.0 / cap 186.0 core-min**, carried forward from
D6RF7/D6RF6 unchanged (single-point deterministic same-scheme re-run; the cap is the MAX form
max(3.0·62.0, 1.6667·62.0) = 186.0). Realised is small: D6RF6 measured **12.133** core-min, D6RF7 measured
**13.6** core-min, both at ~38k cells running to endTime 1000. D6RF8's re-meshed base is expected to be of
comparable scale, so realised is expected **~12–18 core-min**; a re-mesh that CONVERGES (primal does not raise)
runs the full iteration count as D6RF7 already did (it reached time 1000), so no large change is expected.
**Flagged uncertainty:** if the re-mesh materially changes the cell count or the iterations-to-converge, the
realised cost moves — this is reported, not absorbed.

**(b) Mesh generation — SEPARATE line, held for supervisor approval.** The A2 base is a **blockMesh** mesh
(`…/CURRICULUM-D4-a2-wing-cdmin/base/system/blockMeshDict`), **38,304 cells / 40,209 points** (`owner.gz`
header). One `blockMesh` + `checkMesh` (+ `renumberMesh`) pass on ~38k cells is **single-core and trivial
(~0.2–0.4 core-min per attempt)**. Driving max non-orthogonality below 70° requires **blockMeshDict topology /
grading edits, iterated against `checkMesh`**. Estimate for the full tuning loop:
**est ~5 core-min / cap 15 core-min** (single-core blockMesh; a generous ~15–40 attempts). All well under $25
and single-core, but per the lane brief and the "no compute" instruction this is **HELD — mesh-gen does not
start until the supervisor approves this line.**
**Toolchain risk (UNVERIFIED):** whether max non-orthogonality < 70° is achievable on this wing geometry with
`blockMesh` alone is not established — curved leading/trailing edges concentrate non-orthogonality, and an
O-grid/C-grid re-topology or a switch to `snappyHexMesh` / `pyHyp` (higher cost, tens of core-min) may be
needed. If blockMesh cannot reach the target, the mesh-gen line is re-estimated before proceeding.

Cost is derived at the recorded c7a.4xlarge rate ($0.0513/core-h) and is **reported-by-owner, not measured**
(the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5). Estimate-vs-actual calibration lands in
`docs/COST_CALIBRATION.md` at process completion (rule 12), for BOTH lines separately.

## 6. TWO-ROW RULE

This is a **ONE-ROW, PATCHED-ROW** item, as D6RF7: the graded row is the patched-IDWarp `P_conv` probe. The
multipoint **SHIPPED** row (stock IDWarp) is **NAMED-UNBOUGHT** and carried forward priced at **155.70
core-min** (F_mp's registered estimate) so a successor can buy it; it is not bought here. This item is **NOT** a
full `DAFOAM_CHARTER.md` §6 verdict about DAFoam and must not be reported as one.

## 7. WHAT I COULD NOT VERIFY / WHAT IS HELD (honest gaps)

- **The re-mesh itself is not generated** (mesh-gen is compute; the lane brief forbids running it). Therefore
  **max non-orthogonality achieved = PENDING** (target < 70°, aim lower for margin). `MD5_REF_MESH` = PENDING.
  `ALL_PINS_MATCH` is deliberately NOT asserted (§4; asserting it now would be a planted zero, rule 3).
- **The instrument clone (`d6rf7_*→d6rf8_*`) + Stage-1 file-pin fixpoint is HELD**, not authored into a
  half-pinned tree, because the mesh anchor cannot close and a half-open staging layer is the dropped-layer
  defect this family repeatedly pays for (`d6rf8_stage_root.sh` will be authored, with 186.00 from the start,
  as part of the post-approval clone). The clone + Stage-1 fixpoint + the grader carry-forward fixture check
  (§3) is the immediate next step once the supervisor approves the mesh-gen line.
- **Real-run G-CONV** on the re-meshed geometry is a prediction, not a measurement (§2); the official verdict
  requires the supervisor's freeze + re-run after mesh-gen.
- **Delivered-gradient / FD-vs-adjoint:** a single-point convergence probe buys no FD arm, so D6RF8 needs no
  FD-vs-adjoint verification. But any DOWNSTREAM optimisation item built on this re-meshed base **does** —
  RANK 7 changes the delivered gradient (`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:305-313`). Flagged for the
  ladder, not resolved here.

---

## AMENDMENT 2026-09-07 — the A2 base is a pyHyp mesh, NOT a blockMesh mesh; re-mesh METHOD escalated to the chief (PENDING)

**Status: pre-compute amendment (CLAUDE.md rule 2).** D6RF8 is NOT_FROZEN and has NOT computed, so this
amendment is legal; it states the CONDITION corrected and HOW it was checked. Nothing above this section is
rewritten — the false lines are **STRUCK** here and corrected here (rule 2, "originals are struck, never
rewritten"). No line number above this section changed.

**Condition corrected.** §5(b) and the §5/§7 mesh-gen framing rest on a FALSE PREMISE: that the A2 base is a
`blockMesh` mesh. It is not.

**How it was checked.** The dafoam-supervisor's APPROVED bounded mesh-gen probe (single-core blockMesh + checkMesh,
cap 15 core-min, 2026-09-07). blockMesh was run on `…/CURRICULUM-D4-a2-wing-cdmin/base/system/blockMeshDict`: it
produced a **4,400-cell U-bend DUCT** (patches `inlet/outlet/ubend`, boundingBox `(0 -0.0945 0)–(0.8445 0.0945
0.075)`), rc 0, 0.10 wall s — **the wrong geometry entirely.** The registered A2 base has **38,304 cells** and
patches **`wing` (wall, 1008 faces) / `inout` / `sym`**. EVERY blockMeshDict in the D4 run tree is the same stale
U-bend leftover; there is NO `snappyHexMeshDict`, STL, pyHyp input or CGNS in that tree. Cross-checked against
`cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:28-30` and `cases/dafoam/actd_reproduce_a2_grid.py:6-7,67`.

**The corrected finding (MEASURED / cited).** The A2 wing mesh is built by a **pyHyp hyperbolic-extrusion
pipeline**, not blockMesh: `cgns_utils coarsen → genWingMesh.py (pyHyp) → plot3dToFoam → autoPatch → createPatch
→ renumberMesh`, giving **38,304 cells = 1008 surface faces × 38 cell layers** (`A2_GC_…:28-30`;
`A2_mesh_time.json` `measured_cells: 38304`, `mesher: "pyHyp hyperbolic extrusion from a CGNS surface mesh …"`).

**STRUCK lines (§5(b)), replaced by this amendment:**
- ~~"The A2 base is a **blockMesh** mesh (`…/base/system/blockMeshDict`) … One `blockMesh` + `checkMesh` (+
  `renumberMesh`) pass on ~38k cells is single-core and trivial (~0.2–0.4 core-min per attempt). Driving max
  non-orthogonality below 70° requires blockMeshDict topology / grading edits … est ~5 core-min / cap 15
  core-min (single-core blockMesh; ~15–40 attempts)."~~ — **STRUCK: false premise.** blockMesh does not and
  cannot produce this mesh; there is no A2-wing blockMeshDict.
- ~~"Toolchain risk (UNVERIFIED): whether max non-orthogonality < 70° is achievable … with `blockMesh` alone …
  a switch to `snappyHexMesh` / `pyHyp` … may be needed."~~ — **STRUCK: mis-framed.** pyHyp is not a "switch"
  or a fallback; it is the mesh's ONLY toolchain.

**STRUCK framing (§7), corrected here:** the §7 references to "the mesh-gen line" and "once the supervisor
approves the mesh-gen line" assumed the blockMesh line above. They are re-read against the pyHyp finding:
`MD5_REF_MESH` and `max non-orthogonality achieved` remain **PENDING**, now pending a **chief decision on the
pyHyp re-extrusion**, not a blockMesh attempt.

**Re-mesh METHOD — PENDING a chief decision (NOT re-registered here).** Reducing the A2 wing's max
non-orthogonality below 70° requires a **pyHyp re-extrusion with adjusted marching / `s0` / smoothing
parameters**. This produces a **NEW mesh identity** (a new `MD5_REF_MESH`) and a **NEW CD baseline** (the primal,
CD and delivered gradient all shift on the new mesh). Per the supervisor's hard stop, a pyHyp re-mesh is the
**chief's / supervisor's call, not a lane's**, and is **ESCALATED**. No specific pyHyp approach is registered as
decided; this amendment records only that the method is pyHyp and the decision is the chief's.

**Corrected mesh-gen COST (rule 12) — replaces the STRUCK blockMesh est/cap.**
- **Per-pipeline-pass cost — MEASURED**, from `cases/dafoam/ladder-a/A2_mesh_time.json` (pre-registered
  `6e911354`, identity-asserted 38,304 cells): the full serial pipeline (coarsen 0.225 s, **pyHyp 5.547 s**,
  plot3dToFoam 0.506 s, autoPatch 0.551 s, createPatch 0.571 s, renumberMesh 0.622 s, checkMesh 0.227 s) =
  **8.774 container wall s** → **0.1462 core-min at 1 rank executing / 0.5849 core-min on the 4-core reserved
  quota** the recorded A2 run used (the pipeline is serial; the quota reserves 4 cores).
- **Iteration count to reach < 70° with margin — REASONED, not measured:** the base is only ~1.48° over the 70°
  default (71.48°), so modest pyHyp smoothing increases may suffice, but a comfortable margin (aim < 65°) on a
  wing whose LE/TE curvature concentrates non-orthogonality could need more. **est ~15 passes / cap ~40 passes.**
- **Re-mesh tuning-loop est / cap (4-core reserved basis, matching the A2 container — conservative):**
  **est ~9 core-min ($0.0077 DERIVED) / cap 25 core-min ($0.0214 DERIVED).** On the 1-rank-executing basis:
  est ~2.2 / cap ~5.9 core-min. Dollars DERIVED at $0.0513/core-h, reported-by-owner, not measured
  (COMPUTE_BUDGET_CHARTER §5). Trivial, well under $25.
- **Not guaranteed:** this costs the ATTEMPT, not a success. Whether pyHyp CAN reach < 70° on this geometry is
  not established; if it cannot at cap, that is itself a measured finding to report.

**Unchanged by this amendment:** every gate, threshold, band, accept-floor (`1.0e-05`, N-D43) and the cap
(186.00). The graded-primal cost line §5(a) (est 62.0 / cap 186.0) is unchanged. `ALL_PINS_MATCH` remains NOT
asserted (§4). The single physics lever remains the mesh; only its GENERATION METHOD is corrected (pyHyp) and
its DECISION escalated.
