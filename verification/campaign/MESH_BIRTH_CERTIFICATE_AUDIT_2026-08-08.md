# Mesh birth-certificate audit — 2026-08-08

Filed by the mesh-archive auditor under Katie's AUDIT ORDER 2 of 2026-08-08,
executing Verification Charter v1.5 §9's mesh birth-certificate clause ("born
clean or it does not enter; a mesh whose birth certificate is missing is
quarantined from new work until checkMesh is run and attached") and LESSONS.md
L-40's companion paragraph. Trigger specimens: the A3 ONERA M6 vcoarse mesh
(`demo-output/website/dafoam/A3_SUBLU_RESULT.md`, commit 54a2f2ff) and the TMR
NACA 0012 pyHyp generator finding
(`demo-output/website/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`).

## Verdict up front

**The pathology did NOT strike more than the two known times among reachable
meshes.** One mesh in the whole reachable archive is born broken — the already
-indicted A3 vcoarse specimen — and its defect cluster is exactly the pyHyp
tip-collapse signature. Every other pyHyp mesh on disk checks clean. 47
previously uncertified meshes were certified clean this sweep; 3 TMR-family
meshes carry a high-aspect-ratio flag that matches the lab's own certified
NASA-grid signature (not the pyHyp pathology); 41 mesh instances referenced
from records are no longer on disk (38 of them with retained certificates).

## Method

- Inventory: `find /home/ubuntu/certonomous-runs -type d -name polyMesh` →
  **5,303 polyMesh directories**, of which **4,430 are `processor*`
  decomposition duplicates (skipped as a class — see "Skipped classes")** and
  **873 are case-level instances**.
- Dedupe: md5 of each instance's `points` file → **178 unique meshes** (e.g.
  the 106 `study-b52-*` cases share one cached mesh; 90 `act7-ahmed_25-*`
  share one; 94 `act6-nasa_hump-*`/S1 share one).
- Certificate search: any `*checkMesh*` record beside a member case (case dir,
  its `logs/`, or a parent `logs/` naming the case) → **105 of 178 groups
  already certified**; the other 73 had no record anywhere.
- checkMesh: serial, `-allGeometry`, on a **copy** of the mesh in a scratch
  shell case (never in the archive — an early smoke test showed checkMesh
  writes `sets/` through a symlink, so all production runs used copies; the
  archive received zero writes, verified by mtime sweep). **No flow solver was
  run.**
- Compute log: 72 sweep runs, 63.5 s total wall; 21 snapshot re-runs on base
  topology, 12.9 s; 5 certificate spot-checks, 7.6 s; 1 smoke run, 0.5 s.
  **Total ≈ 85 s of serial checkMesh (≈ 1.4 core-min).** Per-run wall times
  are in the retained logs' companion sweep log lines; every issued
  certificate is retained under
  `demo-output/website/campaign/MESH_AUDIT_runs/2026-08-08/` (78 logs, one per
  shell, named `<case-path-with-__>.log.checkMesh`), per L-27.

## Counts

| class | unique meshes | instances |
|---|---|---|
| CERTIFIED before this audit (record verified present) | 105 | 655 |
| BORN CLEAN — certified this sweep | 47 | 65 |
| DERIVED points-only snapshots — checked on base topology, no hard errors | 17 | 129 |
| HIGH-AR FLAG ONLY (TMR/NASA-grid family signature, not the pyHyp pathology) | 3 | 6 |
| **BORN BROKEN** | **1** | **1** |
| Per-processor points-only backups (skipped class; serial base checked clean) | 4 | 12 |
| Not a mesh as archived (`points_orig` only, vendored IDWarp example) | 1 | 2 |
| Referenced but no longer on disk (UNREACHABLE) | — | 41+2 |

Verdict basis: hard checkMesh errors = negative volumes, wrong-oriented face
pyramids, non-orthogonality errors, skewness errors, flagged aspect ratio.
`-allGeometry` advisories (concave cells, small determinant, low-quality
decomposition tets, small interpolation weights) appear on nearly every
accepted snappyHexMesh/structured mesh in the lab's own pre-existing
certificates and do not indict a mesh; they are listed in the retained logs.

## The born-broken list (chief's reopen list input)

**1. `A3-onera-m6-adjoint-vcoarse/constant/polyMesh`** — pyHyp
(`genWingMesh.py`), generated 2026-07-28. Reproduced this sweep, 0.5 s wall:
max aspect ratio 2.07741e+95 (25 cells), 23 negative-volume cells (min
−3.30275e-09), 43 non-orthogonality errors (max 135.3°), 144 wrong-oriented
face pyramids, max skewness 55.38 — bit-identical to the A3_SUBLU_RESULT
figures.

**Cluster signature (independently recomputed from the cell sets this sweep):
all 23 negative-volume cells and all 25 high-AR cells sit in one clump at
x∈[1.1318,1.1449], y≈0, z∈[1.1934,1.1976] — the wing TIP trailing-edge corner
(M6 tip z≈1.196, TE x≈1.14) — in a domain spanning x∈[−8.7,11.4],
z∈[0,10.1].** This is the pyHyp extremity-collapse signature on a 4×-coarsened
surface, matching the A3 record's own localization exactly.

Archived conclusions that used this mesh (search: every record referencing
"vcoarse"; the chief reopens, this audit does not rewrite):

- `demo-output/website/dafoam/ladder-a/A3_onera_m6.md` + `.json` — the vcoarse
  rung entries (attempts 7–8, the July-28 "SEGV / corrupted-field-read"
  claims; already re-diagnosed by A3_SUBLU_RESULT as clean decomposePar
  failure + mesh-gate rejection, but the rung entries still stand as written).
- `demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` — vcoarse rung status lines.
- `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`
  entry 8 — resolved by A3_SUBLU_RESULT ("NOT EVALUABLE AT THE VCOARSE RUNG");
  cross-reference only.
- `demo-output/website/campaign/NOT_PASSING_REGISTER.md` — vcoarse entry.
- `demo-output/website/agenda/docket.json` and
  `agenda/proposals/a3-m6-vcoarse-adjoint-sub-lu-arm.json` — docket items
  naming the rung.
- `demo-output/website/dafoam/A3_SUBLU_PREREGISTRATION.md`,
  `A3_SUBLU_SWEEP_PREREGISTRATION.md`, `ladder-b/S1_FIML_FIELD_INVERSION.md` —
  reference the rung; no numeric conclusion rests on the mesh.

No OTHER archived conclusion anywhere in the records rests on this mesh: it
never completed a primal or adjoint solve (the A3 record proved the rung "as
archived, has never been a runnable case").

## The pyHyp tip/collapse signature check (Part A.3)

Every reachable pyHyp-generated mesh, checked or certified this sweep:

| mesh | cells | max AR | flagged cells | verdict |
|---|---|---|---|---|
| A3-onera-m6-adjoint-vcoarse | 24,960 | 2.08e+95 | 23 neg-vol + 25 AR, one clump at tip TE corner | **BORN BROKEN** |
| A3-onera-m6-adjoint-coarse | 99,840 | 608.2 | none | BORN CLEAN |
| A3-onera-m6-adjoint-probe80k | 79,560 | 608.2 | none | BORN CLEAN |
| A3-onera-m6-sweep-n8_10920 | 10,920 | 608.2 | none | BORN CLEAN |
| A3-onera-m6-sweep-n15_21840 (= W4-m6-reordering ×3) | 21,840 | 608.2 | none | BORN CLEAN |
| A3-onera-m6-sweep-n28_42120 | 42,120 | 608.2 | none | BORN CLEAN |
| .mesh-cache/onera_m6 (×4 incl. A3 2× mesh) | 399,360 | 222.4 | none | BORN CLEAN |
| act9-crm_wingbody constant (×40, incl. A6-crm-wing) | — | — | — | CERTIFIED (dpw5 A6ref log) |
| adjwall/A1_4032 (×15, incl. W5 a1 cases) | 4,032 | 97.9 | none | BORN CLEAN |
| adjwall/N16k…N400k (7 rungs) | 14k–400k | 110.8→195.3 | none | BORN CLEAN |
| ladder-a1-naca0012-sweep12k/25k/50k | 10k–41k | 96.2/95.0/94.3 | none | BORN CLEAN |

Two observations the Infra family should keep: (a) the M6 family's max AR is
pinned at 608.2 across 10,920→42,120 cells — the generator's far-field
stretching, benign but characteristic; (b) the adjwall airfoil ladder shows
max AR RISING under refinement (110.8 at N16k → 195.3 at N400k), the exact
GENERATOR_FINDING behaviour (fixed pyHyp smoothing vs refined sampling),
still below any failure threshold at these resolutions. The collapse became
geometric breakage only on the 4×-coarsened M6 tip.

## HIGH-AR FLAG ONLY — not the pathology, matches certified family signature

Three uncertified meshes fail checkMesh's aspect-ratio check (threshold 1000)
with NO other hard error. The lab's own pre-existing certificates accept the
identical signature on the same family: `tmr-flatplate-finer/log.checkMesh`
(65,468), `tmr-bump-finer/log.checkMesh` (2.23e+06), `w1-bump-nasa-grids/
medium/log.checkMesh` (5,210) all read "***High aspect ratio … Failed 1 mesh
checks" and entered service. Cluster check this sweep: the flagged cells are
distributed far-field/wall-normal stretching (tmr-naca a10: 1,822 cells
extending from the TE to 453 chords downstream, median 24 chords from the
airfoil; tmr-proof: first wall-normal layers along the whole plate) — the
opposite of a localized extremity collapse. Root cause of the huge numbers:
wall-resolved 2D grids (y+ spacing ~1e-7 chord) carried as unit-span 3D
OpenFOAM meshes.

- `tmr-naca-t-a10-medium` (= `-seeded` = `tmr-naca-a10-medium-regen` =
  `C4-naca-t-a10-medium-confirm`, 4 instances) — plot3dToFoam of NASA's TMR
  C-grid. Max AR 2.64e+07, 1,822/14,336 cells. Used by
  `demo-output/website/tmr/C4_naca0012_closure.md`/`.json` (the family-N
  regrade); the R12 flag machinery already prints the mesh-gate caveat beside
  that band — flag noted, no reopen demanded by this audit.
- `tmr-naca-t-a0-coarse` — same family. Max AR 2.07e+07, 454/3,584 cells.
- `tmr-proof/coarse` — blockMesh per the TMR recipe. Max AR 74,041, 146/816
  cells.

The MODEL_FORM_runs N_* retained certificates carry the same family flag;
`model_form_batch.py` already gates on non-ortho/skewness with the AR flag on
its face (its §"no number, no exemption" discipline).

## Unreachable (referenced in records, not on disk — listed, not guessed)

- **38 `modelform-*` case dirs** (families B/H/P/N × 4 turbulence models,
  cited throughout `campaign/MODEL_FORM_*`/DMR records). Meshes gone from
  `certonomous-runs`; **their birth certificates are retained** at
  `demo-output/website/campaign/MODEL_FORM_runs/<case>/log.checkMesh` (all 39
  cases have one; `modelform-H_re10595_SpalartAllmaras` reappeared on disk
  during this audit — an active batch is rebuilding them, its mesh carries the
  retained certificate).
- **`tmr-naca-a0-coarse`, `tmr-naca-a10-coarse`, `tmr-naca-a15-coarse`**
  (pre-"t" naming, cited in `campaign/W3_NACA4412_LAYERED_REPLICATES.md`,
  `campaign/W3_MESH_QUALITY_GATE_TWO_VALUES.md`, MODEL_FORM logs) — gone;
  superseded by the `tmr-naca-t-*` family and the MODEL_FORM_runs N_* cases.
- **The two GENERATOR_FINDING pyHyp meshes**
  (`work/NACA0012_Airfoil_Incompressible` and `work_refined/…_refined`) — not
  found anywhere under /home/ubuntu. The measured figures (max AR 97.9 →
  167.5 under refinement) survive only in the finding itself.
  `adjwall/A1_4032` (max AR 97.87, checked clean this sweep) is the same
  generator recipe at the coarse setting and remains reachable.

## Skipped classes (no silent truncation)

- **4,430 `processor*` polyMesh dirs** — decomposition duplicates of case
  meshes. Includes the A3 vcoarse `_stale_processor_dirs_run1/` preserved
  copies, which A3_SUBLU_RESULT already proved bit-identical to the broken
  serial mesh (23 negative cells, min −3.302748e-09 on processor1).
- **4 per-processor points-only backups** —
  `A3-onera-m6-sweep-n15_21840/_prior_state_backup_20260808/p{0..3}_*` (6,495
  points each vs 23,925 serial): processor-local deformed-points snapshots,
  not standalone meshes. Their serial base mesh checked BORN CLEAN this sweep.
- **17 whole-domain points-only snapshots** (act9 `1000/polyMesh` ×39
  identical + W4 FD-step time dirs) — deformed-points overlays on their cases'
  constant topology; each was checked as base topology + snapshot points: no
  hard errors (advisories only; act9: 422 low-quality tet faces + small
  determinants on 579,072 cells — same advisory class as its certified base).
- **`W5-patch/idwarp/examples/AhmedBodyCoarse`** (2 instances) — vendored
  IDWarp example carrying `points_orig` but no `points`: not a mesh as
  archived; `run_warp.py` writes the points at use time.
- **CGNS/plot3d generator artifacts** (`surfaceMesh.cgns`,
  `m6_surfaceMesh_fine.cgns`, `volumeMesh.xyz` in the A3/A2 dirs) — pyHyp
  intermediate products, not OpenFOAM meshes; noted as reachable provenance
  for the M6 family, not separately checked.
- **`/home/ubuntu/dafoam-tutorials/**`** — upstream vendor tree, not lab
  archive; out of scope.

## Certificate spot-checks (Part A.5) — 5 of 105, all match

| certificate | archived headline | this sweep | match |
|---|---|---|---|
| `validation-scratch/b52/log.checkMesh` | 193,880 cells, AR 6.5204479, nonOrtho 54.329, skew 3.9118 | identical to shown digits | YES |
| `w3-naca0012_wing-family/r3/log.checkMesh` | 358,430 cells, AR 4.9088747, nonOrtho 44.040, skew 2.0070 | identical | YES |
| `credential-repair-naca4412-medium/log.checkMesh` | 263,359 cells, AR 53.501908, nonOrtho 58.374, skew 1.1072 | identical | YES |
| `A2-mach-wing/checkMesh.log` | 38,304 cells, AR 684.4022, nonOrtho 66.965, skew 1.3393 | identical | YES |
| `tmr-flatplate-finer/log.checkMesh` | 52,224 cells, AR 65,467.85 flagged (8,415 cells) | identical | YES |

(The only differences are `-allGeometry` advisory lines absent from the
plain-checkMesh archived logs — instrument-mode difference, not mesh drift.)

## Part B — the standing rule's mechanics (filed as proposal, not implemented)

Filed: `demo-output/website/agenda/proposals/a-mesh-enters-with-its-birth-certificate-or-not-at-all.json`
(criterion: instrument-check, 0 core-min beyond this sweep). Summary of the
proposed mechanics — Infra family to adopt with their own verification:

1. **Where the certificate lives**: `log.checkMesh` committed beside the case
   (the existing convention in the 105 certified groups and MODEL_FORM_runs),
   PLUS a one-line `birth_certificate.json` beside every `.mesh-cache` entry:
   `{points_sha256, verdict, cells, maxAR, maxNonOrtho, maxSkew, generator,
   created_at}` so the certificate travels with the mesh and is hash-bound to
   it.
2. **Insertion points** (file:symbol, current line refs):
   - `sdk/chief_engineer/head_engineer.py` — `save_mesh_to_cache` (~1006):
     write the certificate beside `polyMesh` at cache-save;
     `cached_mesh_available` (~971): a cache entry without a matching-hash
     certificate reports NOT cached (= the charter's quarantine);
     `restore_cached_mesh` (~986): assert-at-entry on hash+verdict, and copy
     the certificate into the case so every run dir carries `log.checkMesh`
     (today 400+ act6/act7/act9/study run dirs carry the mesh with no record
     beside it — the single biggest certificate gap this sweep found).
   - `sdk/chief_engineer/docker_dafoam.py` — the mesh-cache mirror
     (`_mesh_cache_dir` ~216, save/restore ~223–250): identical mechanics.
     This is the pyHyp entry path — the pathology's generator — and the A3
     vcoarse mesh entered here uncertified.
   - `sdk/workflows/geometry_study.py` — the quality gate already runs
     checkMesh (`mesh_quality_reading` ~455, `retry_mesh_quality` ~590, rung
     builder ~1388–1402) but its reading is transient; persist the judged log
     into the case dir and hand it to `save_mesh_to_cache` (L-40: the gate
     that ran must be provable from the artifact, not inferred).
   - `sdk/scripts/model_form_batch.py` — already the exemplar (retains
     `log.checkMesh` per case, hard gates at `mesh_verdict` ~569 /
     `apply_mesh_gate` ~600, "no number, no exemption" ~101); add
     assert-at-entry so an absent/unreadable `log.checkMesh` refuses the
     SOLVER LAUNCH rather than surfacing as a post-hoc exclusion.
3. **Registry side**: any pre-registration or docket item naming a mesh rung
   carries the mesh's `points_sha256` + certificate verdict, so a
   born-broken mesh cannot re-enter under a new case name (the A3 vcoarse
   failure mode: same mesh, three case reconstructions).

## Return summary

- Unique meshes: 178 (873 case-level instances; 4,430 processor duplicates).
- Certified pre-existing: 105 (5 spot-checked, all match). Certified clean
  this sweep: 47 (+17 derived snapshots, +3 high-AR-flag-only TMR).
- **BORN BROKEN: 1 — A3-onera-m6-adjoint-vcoarse (pyHyp tip-TE collapse
  clump, reproduced and localized).** Reopen-list input above.
- UNREACHABLE: 41 case meshes (38 with retained certificates) + 2
  GENERATOR_FINDING work meshes.
- Issued certificates retained: `campaign/MESH_AUDIT_runs/2026-08-08/` (78
  logs). Proposal:
  `agenda/proposals/a-mesh-enters-with-its-birth-certificate-or-not-at-all.json`.

## Full inventory table

One row per unique mesh (group representative shown; `members` = bit-identical
instances). Paths relative to `/home/ubuntu/certonomous-runs/`.

| mesh (group representative) | members | generator | birth certificate | verdict |
|---|---|---|---|---|
| `.mesh-cache/ahmed_25/polyMesh` | 90 | blockMesh; snappyHexMesh | yes (w3-published-rung-ahmed_25/a/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/ahmed_35-rung-medium-s23/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 2.95502, 45813 cells; advisory flags only) |
| `.mesh-cache/ahmed_35/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 4.1041, 79778 cells; advisory flags only) |
| `.mesh-cache/airliner_wing_span52-rung-medium-s23/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 1.8607, 22754 cells; advisory flags only) |
| `.mesh-cache/airliner_wing_span52/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 5.75214, 32385 cells; advisory flags only) |
| `.mesh-cache/b52/polyMesh` | 106 | no generation log on disk | yes (validation-scratch/b52/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/cube/polyMesh` | 4 | blockMesh; snappyHexMesh | yes (w3-cube-settle/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `.mesh-cache/hyp-cylinder-M8-coarse/polyMesh` | 2 | blockMesh | yes (hypersonic-cylinder/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/hyp-cylinder-M8-fine/polyMesh` | 2 | blockMesh | yes (hypersonic-cylinder/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/hyp-cylinder-M8-medium/polyMesh` | 2 | blockMesh | yes (hypersonic-cylinder/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/motorBike/polyMesh` | 3 | no generation log on disk | yes (validation-scratch/motorBike/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/naca0012_wing-rung-medium-s23/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 4.73581, 67356 cells; advisory flags only) |
| `.mesh-cache/naca0012_wing/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 4.29153, 140580 cells; advisory flags only) |
| `.mesh-cache/naca0015_sail/polyMesh` | 3 | blockMesh; snappyHexMesh | yes (w3-published-rung-naca0015_sail/a/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/naca4412_wing-rung-medium-s23/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 3.33997, 67826 cells; advisory flags only) |
| `.mesh-cache/naca4412_wing/polyMesh` | 3 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r1/log.checkMesh) | CERTIFIED (pre-existing record) |
| `.mesh-cache/onera_m6/polyMesh` | 4 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 222.355, 399360 cells; advisory flags only) |
| `A2-mach-wing/constant/polyMesh` | 10 | pyHyp (genWingMesh.py) | yes (A2-mach-wing/checkMesh.log) | CERTIFIED (pre-existing record) |
| `A3-onera-m6-adjoint-coarse/constant/polyMesh` | 1 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 608.207, 99840 cells; advisory flags only) |
| `A3-onera-m6-adjoint-probe80k/constant/polyMesh` | 1 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 608.21, 79560 cells; advisory flags only) |
| `A3-onera-m6-adjoint-vcoarse/constant/polyMesh` | 1 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN BROKEN: High aspect ratio cells found, Max aspect ratio: 2.07741e+95, number of cells 25; Zero or negative cell volume detected.  Minimum negative volume: -3.30275e-09, Number of negative volume cells: 23; Number of non-orthogonality errors: 43.; Error in face pyramids: 144 faces are incorrectly oriented.; Max skewness = 55.378, 3 highly skew faces detected which may impair the quality of the results; Fac |
| `A3-onera-m6-sweep-n15_21840/_prior_state_backup_20260808/p0_1000/polyMesh` | 3 | no generation log on disk | none | PER-PROCESSOR points-only snapshot -- skipped as duplicate class; serial base mesh (A3-onera-m6-sweep-n15_21840/constant) checked BORN CLEAN this sweep |
| `A3-onera-m6-sweep-n15_21840/_prior_state_backup_20260808/p1_1000/polyMesh` | 3 | no generation log on disk | none | PER-PROCESSOR points-only snapshot -- skipped as duplicate class; serial base mesh (A3-onera-m6-sweep-n15_21840/constant) checked BORN CLEAN this sweep |
| `A3-onera-m6-sweep-n15_21840/_prior_state_backup_20260808/p2_1000/polyMesh` | 3 | no generation log on disk | none | PER-PROCESSOR points-only snapshot -- skipped as duplicate class; serial base mesh (A3-onera-m6-sweep-n15_21840/constant) checked BORN CLEAN this sweep |
| `A3-onera-m6-sweep-n15_21840/_prior_state_backup_20260808/p3_1000/polyMesh` | 3 | no generation log on disk | none | PER-PROCESSOR points-only snapshot -- skipped as duplicate class; serial base mesh (A3-onera-m6-sweep-n15_21840/constant) checked BORN CLEAN this sweep |
| `A3-onera-m6-sweep-n28_42120/constant/polyMesh` | 1 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 608.215, 42120 cells; advisory flags only) |
| `A3-onera-m6-sweep-n8_10920/constant/polyMesh` | 1 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 608.215, 10920 cells; advisory flags only) |
| `A4-ahmed-body/fine/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | none -> issued this sweep | BORN CLEAN (maxAR 3.19739, 45760 cells; advisory flags only) |
| `A6-crm-wing/constant/polyMesh` | 40 | pyHyp (genWingMesh.py) | yes (dpw5-committee-probe/logs/A6ref_checkMesh.log) | CERTIFIED (pre-existing record) |
| `S1-fiml/hump/constant/polyMesh` | 94 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 12131.6, 51626 cells; advisory flags only) |
| `S1-fiml/ramp_kw/c2/constant/polyMesh` | 26 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 250.973, 5000 cells; advisory flags only) |
| `W4-a1-rank/a1_np1/0.0001/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-a1-rank/a1_np1/219/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-a4-du0check/du0_np1/500/polyMesh` | 16 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-a4-stepsweep/a4_dcddxv/500/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-a4-stepsweep/a4_np1_stock/500/polyMesh` | 3 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-reach/a35_np1/0.0001/polyMesh` | 5 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-reach/a35_np1/500/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-reach/a35_np1/constant/polyMesh` | 10 | blockMesh; snappyHexMesh | yes (W4-defect-reach/a35_mesh/log.checkMesh) | CERTIFIED (pre-existing record) |
| `W4-defect-reach/a35_np1_h1e-2/500/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-reach/a35_np1_h3e-3/500/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1fs_np1/0.0001/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1fs_np1/251/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1lim_np1/0.0001/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1lim_np1/242/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1lim_np1_h3e3/276/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1limdef_np1/0.0001/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a1limdef_np1/232/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 1 mesh checks.) |
| `W4-defect-robustness/a4_medium_mesh/constant/polyMesh` | 3 | blockMesh; snappyHexMesh | yes (W4-defect-robustness/a4_medium_mesh/log.checkMesh) | CERTIFIED (pre-existing record) |
| `W4-defect-robustness/a4conf_np4scotch/constant/polyMesh` | 2 | blockMesh; snappyHexMesh | yes (W4-defect-robustness/a4_conformal_mesh/log.checkMesh) | CERTIFIED (pre-existing record) |
| `W4-idx16/case/constant/polyMesh` | 11 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 69.0829, 4800 cells; advisory flags only) |
| `W4-m6-reordering/m6_rcm/constant/polyMesh` | 3 | pyHyp (genWingMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 608.215, 21840 cells; advisory flags only) |
| `W4-upstream-repro/tutorials/PeriodicHill/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 71.7288, 3500 cells; advisory flags only) |
| `W4-verify-sweep/cbfs_fd/constant/polyMesh` | 19 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 14.7588, 21000 cells; advisory flags only) |
| `W5-patch/accept/input_files/ahmedBodyMesh/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 10.6837, 17588 cells; advisory flags only) |
| `W5-patch/idwarp/examples/AhmedBodyCoarse/constant/polyMesh` | 2 | no generation log on disk | none | NOT A MESH AS ARCHIVED (points_orig only; vendored IDWarp example) |
| `W5-regrade/a4_stock/constant/polyMesh` | 61 | blockMesh; snappyHexMesh | yes (A4-ahmed-body/coarse/log.checkMesh +2 more) | CERTIFIED (pre-existing record) |
| `W5-regrade/sail_stock/constant/polyMesh` | 4 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 4.32232, 63920 cells; advisory flags only) |
| `act9-crm_wingbody-cc6667/1000/polyMesh` | 39 | pyHyp (genWingMesh.py) | none -> issued this sweep | DERIVED points-only snapshot, checked on base topology: no hard errors (advisories only: Failed 2 mesh checks.) |
| `adjwall/A1_4032/constant/polyMesh` | 15 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 97.8722, 4032 cells; advisory flags only) |
| `adjwall/N100k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 170.553, 100224 cells; advisory flags only) |
| `adjwall/N16k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 110.782, 14464 cells; advisory flags only) |
| `adjwall/N200k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 185.517, 199892 cells; advisory flags only) |
| `adjwall/N30k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 142.998, 29992 cells; advisory flags only) |
| `adjwall/N400k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 195.254, 399730 cells; advisory flags only) |
| `adjwall/N51k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 156.533, 51546 cells; advisory flags only) |
| `adjwall/N64k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 162.126, 63784 cells; advisory flags only) |
| `credential-repair-naca4412-fine/constant/polyMesh` | 2 | blockMesh; snappyHexMesh | yes (credential-repair-naca4412-fine/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `credential-repair-naca4412-finer/constant/polyMesh` | 2 | blockMesh; snappyHexMesh | yes (credential-repair-naca4412-finer/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `credential-repair-naca4412-finer_relayered/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (credential-repair-naca4412-finer_relayered/log.checkMesh) | CERTIFIED (pre-existing record) |
| `credential-repair-naca4412-finer_relayered_ngrow0/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (credential-repair-naca4412-finer_relayered_ngrow0/log.checkMesh) | CERTIFIED (pre-existing record) |
| `credential-repair-naca4412-medium/constant/polyMesh` | 2 | blockMesh; snappyHexMesh | yes (credential-repair-naca4412-medium/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `diamond-airfoil/coarse/constant/polyMesh` | 2 | blockMesh | yes (diamond-airfoil/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `diamond-airfoil/fine/constant/polyMesh` | 2 | blockMesh | yes (diamond-airfoil/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `diamond-airfoil/medium/constant/polyMesh` | 2 | blockMesh | yes (diamond-airfoil/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `dpw5-committee-probe/case_hex/constant/polyMesh` | 30 | no generation log on disk | yes (dpw5-committee-probe/logs/DPW5_hex_checkMesh.log +2 more) | CERTIFIED (pre-existing record) |
| `f11-cavity-ladder/probe_re5000_n256/constant/polyMesh` | 1 | blockMesh | yes (f11-cavity-ladder/probe_re5000_n256/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f11-cavity-ladder/re100_n128/constant/polyMesh` | 2 | blockMesh | yes (f11-cavity-ladder/re1000_n128/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `f11-cavity-ladder/re100_n64/constant/polyMesh` | 2 | blockMesh | yes (f11-cavity-ladder/re1000_n64/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/f5b_re1000_3d_pilot/constant/polyMesh` | 2 | blockMesh | yes (f5a-cylinder-ladder/f5b_re1000_3d_pilot/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/f5b_re1000_3d_reference_stage/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/f5b_re1000_3d_reference_stage/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/f5b_re1000_3d_referenceclean_stage/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/f5b_re1000_3d_referenceclean_stage/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re1000/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re1000/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re10000/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re10000/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re1000_coarsespacing/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re1000_coarsespacing/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re2000/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re2000/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re3900/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re3900/log.checkMesh) | CERTIFIED (pre-existing record) |
| `f5a-cylinder-ladder/re3900_correctedspacing/constant/polyMesh` | 1 | blockMesh | yes (f5a-cylinder-ladder/re3900_correctedspacing/log.checkMesh) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/case_C1/constant/polyMesh` | 2 | no generation log on disk | yes (hlpw6-memory-probe/logs/C1_checkMesh.log +1 more) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/case_C3/constant/polyMesh` | 2 | no generation log on disk | yes (hlpw6-memory-probe/logs/C3_checkMesh.log +1 more) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/case_HLPW6/constant/polyMesh` | 1 | no generation log on disk | yes (hlpw6-memory-probe/logs/HLPW6_checkMesh.log) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/case_P2/constant/polyMesh` | 1 | no generation log on disk | yes (hlpw6-memory-probe/logs/P2_checkMesh.log) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/case_P4/constant/polyMesh` | 2 | no generation log on disk | yes (hlpw6-memory-probe/logs/C4_checkMesh.log +1 more) | CERTIFIED (pre-existing record) |
| `hlpw6-memory-probe/smoke/constant/polyMesh` | 2 | blockMesh | yes (hlpw6-memory-probe/smoke/log.checkMesh) | CERTIFIED (pre-existing record) |
| `ladder-a1-naca0012-sweep12k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 96.2441, 10640 cells; advisory flags only) |
| `ladder-a1-naca0012-sweep25k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 94.9898, 21484 cells; advisory flags only) |
| `ladder-a1-naca0012-sweep50k/constant/polyMesh` | 1 | pyHyp (genAirFoilMesh.py) | none -> issued this sweep | BORN CLEAN (maxAR 94.2511, 41528 cells; advisory flags only) |
| `mb-iterfix/coarse/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (mb-iterfix/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `mb-iterfix/medium/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (mb-iterfix/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `r2-plate-uq/_probe/constant/polyMesh` | 58 | blockMesh | yes (tmr-flatplate-valcheck-fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/coarse/constant/polyMesh` | 1 | blockMesh | yes (rae2822-meshcheck/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/fine/constant/polyMesh` | 1 | blockMesh | yes (rae2822-meshcheck/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/medium/constant/polyMesh` | 1 | blockMesh | yes (rae2822-meshcheck/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/og-coarse/constant/polyMesh` | 1 | no generation log on disk | yes (rae2822-meshcheck/og-coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/og-fine/constant/polyMesh` | 1 | no generation log on disk | yes (rae2822-meshcheck/og-fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/og-medium/constant/polyMesh` | 1 | no generation log on disk | yes (rae2822-meshcheck/og-medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `rae2822-meshcheck/ogrid-coarse/constant/polyMesh` | 1 | no generation log on disk | yes (rae2822-meshcheck/ogrid-coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-ahmed_25-coarse-40aacb/constant/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 3.19881, 20621 cells; advisory flags only) |
| `study-ahmed_25-medium-b37e86/constant/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 3.19731, 45753 cells; advisory flags only) |
| `study-ahmed_35-coarse-186b41/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 2.48795, 20425 cells; advisory flags only) |
| `study-airliner_wing_span52-coarse-1f61fe/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 1.83932, 9639 cells; advisory flags only) |
| `study-b52-fine-uq/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (study-b52-fine-uq/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-b52-finer2-uq/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (study-b52-finer2-uq/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-b52-rung7-uq/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (study-b52-rung7-uq/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-b52-rung7b-uq/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (study-b52-rung7b-uq/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-b52-rung8-uq/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (study-b52-rung8-uq/log.checkMesh) | CERTIFIED (pre-existing record) |
| `study-naca0012_wing-coarse-09bec1/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 4.73436, 27265 cells; advisory flags only) |
| `study-naca4412_wing-coarse-a6c5e0/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 3.92028, 27237 cells; advisory flags only) |
| `supersonic-cone/coarse/constant/polyMesh` | 2 | no generation log on disk | yes (supersonic-cone/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `supersonic-cone/fine/constant/polyMesh` | 2 | blockMesh | yes (supersonic-cone/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `supersonic-cone/medium/constant/polyMesh` | 2 | blockMesh | yes (supersonic-cone/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `supersonic-wedge/coarse/constant/polyMesh` | 2 | no generation log on disk | yes (supersonic-wedge/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `supersonic-wedge/fine/constant/polyMesh` | 2 | blockMesh | yes (supersonic-wedge/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `supersonic-wedge/medium/constant/polyMesh` | 2 | blockMesh | yes (supersonic-wedge/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `tmr-bump-finer/constant/polyMesh` | 1 | blockMesh | yes (tmr-bump-finer/log.checkMesh) | CERTIFIED (pre-existing record) |
| `tmr-flatplate-finer/constant/polyMesh` | 1 | blockMesh | yes (tmr-flatplate-finer/log.checkMesh) | CERTIFIED (pre-existing record) |
| `tmr-flatplate-finest/constant/polyMesh` | 1 | blockMesh | yes (tmr-flatplate-finest/log.checkMesh) | CERTIFIED (pre-existing record) |
| `tmr-naca-t-a0-coarse/constant/polyMesh` | 1 | plot3dToFoam (external grid) | none -> issued this sweep | HIGH-AR FLAG ONLY: High aspect ratio cells found, Max aspect ratio: 2.06508e+07, number of cells 454 -- matches the certified TMR/NASA-grid family signature (certified peers flag up to 2.2e6); no negative volumes, no pyramid/non-ortho/skewness errors; flagged cells are distributed far-field/wall-normal stretching, not extremity collapse |
| `tmr-naca-t-a10-medium/constant/polyMesh` | 4 | plot3dToFoam (external grid) | none -> issued this sweep | HIGH-AR FLAG ONLY: High aspect ratio cells found, Max aspect ratio: 2.64462e+07, number of cells 1822 -- matches the certified TMR/NASA-grid family signature (certified peers flag up to 2.2e6); no negative volumes, no pyramid/non-ortho/skewness errors; flagged cells are distributed far-field/wall-normal stretching, not extremity collapse |
| `tmr-proof/coarse/constant/polyMesh` | 1 | blockMesh | none -> issued this sweep | HIGH-AR FLAG ONLY: High aspect ratio cells found, Max aspect ratio: 74041, number of cells 146 -- matches the certified TMR/NASA-grid family signature (certified peers flag up to 2.2e6); no negative volumes, no pyramid/non-ortho/skewness errors; flagged cells are distributed far-field/wall-normal stretching, not extremity collapse |
| `unsteady-cylinder/Re100/coarse/constant/polyMesh` | 2 | blockMesh | yes (unsteady-cylinder/Re100/coarse/log.checkMesh) | CERTIFIED (pre-existing record) |
| `unsteady-cylinder/Re100/fine/constant/polyMesh` | 2 | blockMesh | yes (unsteady-cylinder/Re100/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `unsteady-cylinder/Re100/medium/constant/polyMesh` | 2 | blockMesh | yes (unsteady-cylinder/Re100/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `unsteady-cylinder/cyl-re100/constant/polyMesh` | 2 | blockMesh | yes (unsteady-cylinder/cyl-re100/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w1-bump-nasa-grids/coarse/constant/polyMesh` | 2 | plot3dToFoam (external grid) | yes (w1-bump-nasa-grids/coarse/log.checkMesh +1 more) | CERTIFIED (pre-existing record) |
| `w1-bump-nasa-grids/fine/constant/polyMesh` | 1 | plot3dToFoam (external grid) | yes (w1-bump-nasa-grids/fine/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w1-bump-nasa-grids/medium/constant/polyMesh` | 1 | plot3dToFoam (external grid) | yes (w1-bump-nasa-grids/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w1-bump-nasa-grids/plot3d_crosscheck/medium/constant/polyMesh` | 1 | plot3dToFoam (external grid) | yes (w1-bump-nasa-grids/plot3d_crosscheck/medium/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r1/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r1/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r1b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r1b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r1c/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r1c/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r1d/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r1d/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r2/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r2/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r2b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r2b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r3/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r3/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r3b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r3b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r3c/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r3c/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r3d/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r3d/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r4/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r4/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca0012_wing-family/r4b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca0012_wing-family/r4b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/B/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/B/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/C/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/C/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/D/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | none -> issued this sweep | BORN CLEAN (maxAR 1.08588, 40600 cells) |
| `w3-naca4412-layered-replicates/E/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/E/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r3/B/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r3/B/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r3/C/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r3/C/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r3/E/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r3/E/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r5/B/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r5/B/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r5/C/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r5/C/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412-layered-replicates/r5/E/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412-layered-replicates/r5/E/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r1b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r1b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r2/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r2/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r2b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r2b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r3/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r3/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r3b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r3b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r4/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r4/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-naca4412_wing-family/r4b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-naca4412_wing-family/r4b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-published-rung-ahmed_25/b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-published-rung-ahmed_25/b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-published-rung-cube/b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-published-rung-cube/b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-published-rung-naca0015_sail/b/constant/polyMesh` | 1 | blockMesh; snappyHexMesh | yes (w3-published-rung-naca0015_sail/b/log.checkMesh) | CERTIFIED (pre-existing record) |
| `w3-qcr-duct/AR_10_Ret_180_sst/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 22090 cells; advisory flags only) |
| `w3-qcr-duct/AR_3_Ret_180_qcr/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 6627 cells; advisory flags only) |
| `w3-qcr-duct/AR_5_Ret_180_sst/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 11045 cells; advisory flags only) |
| `w3-qcr-duct/sst/constant/polyMesh` | 3 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 2209 cells; advisory flags only) |
| `w3-qcr-rank1/AR_14_Ret_180_qcr/constant/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 31819 cells; advisory flags only) |
| `w3-qcr-rank1/AR_1_Ret_360_qcr/constant/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 1880.59, 3025 cells; advisory flags only) |
| `w3-qcr-rank1/AR_3_Ret_360_qcr/constant/polyMesh` | 1 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 1708.72, 8748 cells; advisory flags only) |
| `w3-qcr-rank1/AR_7_Ret_180_qcr/constant/polyMesh` | 2 | no generation log on disk | none -> issued this sweep | BORN CLEAN (maxAR 871.975, 15463 cells; advisory flags only) |

---

## AMENDMENT, 2026-08-10 — **"CERTIFIED (pre-existing record)" means a LOG exists, not a certificate. The measured number is 0 of 105.**

Ordered by the chief after the ladder-scatter retrofit found that neither the `cube` nor the
`naca0015_sail` mesh carried a certificate despite both appearing in this audit's certified
column. Treated as a claim to be re-measured, not as a wording tidy-up, because this is the class
of defect this audit was written to catch.

### The two readings, stated side by side

- **What the column says:** `CERTIFIED (pre-existing record)`, contributing **105** to the summary
  row *"CERTIFIED before this audit (record verified present) | 105 | 655"* (`:52`).
- **What it means:** a **`log.checkMesh` was found** for that mesh — in its own directory, its
  `logs/`, or a parent naming the case (`:33`). That is genuine evidence the check *ran*.
- **What it does NOT mean:** that a `birth_certificate.json` exists. The certificate is the
  artifact the Mesh Standard v1.1 gate actually requires, and this audit never wrote one — its own
  proposal to do so (`:228`) was never executed.

### The measurement

Every one of the 105 rows was resolved to its mesh root on disk and checked for a certificate
file beside its `polyMesh`:

| | count |
|---|---|
| rows marked `CERTIFIED (pre-existing record)` | **105** |
| paths that resolve on disk | **105** (all) |
| **carrying an actual `birth_certificate.json`** | **0** |
| carrying a `log.checkMesh` only | **105** |

Corroborating from the other direction: **33** `birth_certificate.json` files exist anywhere under
`certonomous-runs/` and `Certonomous/`, of which **29 were written today (2026-08-10)** — so only
**4 predate today, and none of them is among these 105.**

### The operational consequence, which is the part that matters

**Mesh Standard v1.1's own checker refuses all 105.** `certificate_admits()` requires a
certificate file, a `points_sha256` matching the mesh actually present, and an accepted verdict; a
`log.checkMesh` satisfies none of those. So every mesh in this column is **quarantined at the v1.1
gate** — which is exactly what happened, unprompted, to both ONERA M6 members certified during
today's A3 work and to both of the retrofit ladders.

**The honest restatement of this audit's headline:** its 105 are **CHECKED BUT UNCERTIFIED** —
the evidence exists, the artifact does not. **The certificate coverage the lab believes it has
from this audit is notional.** Nothing here says those meshes are bad: the audit's verdict rule
(hard errors read from the log) is sound and its BORN CLEAN findings stand. What is wrong is that
the word "CERTIFIED" names an artifact that was never written, and downstream machinery believes
the word.

### The fix, priced and offered rather than executed

Minting is mechanical and needs **no solver**: `sdk/chief_engineer/mesh_certificate.write_certificate`
already accepts a checkMesh log (`check_log_text=`), parses it with this audit's own verdict rule,
and hash-binds the result to the points file present. A scripted pass over the 105 would mint from
the logs this audit already located — **~0 core-min of compute, one agent-session of file IO**,
with per-mesh failures (log unparseable, points file since changed, hash mismatch) reported rather
than papered over, since a certificate is a record of a check that ran and a mesh whose points
have changed since its log must be re-checked, not certified from stale evidence.

**Not executed here.** These meshes belong to other families and the audit's own proposal for this
is filed at `:228`; the retrofit agent measured the gap and is reporting it, not unilaterally
writing 105 files into other families' cases. Recommended owner: Infra, alongside the launcher
resource-cap item already routed there.

---

## AMENDMENT, 2026-08-10 — "CERTIFIED (pre-existing record)" named an artifact that did not exist

Added by the Infrastructure/Standards family at the chief's direction. **No
verdict in this audit is revised and no mesh is impugned.** The BORN CLEAN
findings stand. What is corrected is a word: 105 rows were marked `CERTIFIED
(pre-existing record)` on the strength of a `log.checkMesh`, and a coverage
check on 2026-08-10 found that **105 of 105 carried the log and 0 of 105
carried a `birth_certificate.json`.** Only four certificates in the whole tree
predated that day and none was among the 105.

The consequence was not theoretical. `mesh_certificate.certificate_admits()`
requires the FILE, a `points_sha256` matching the mesh actually present, and
an accepted verdict — so every one of the 105 was quarantined from new work,
which is what happened unprompted to two M6 members and two retrofit ladders
that day. The evidence existed; the artifact did not; and downstream machinery
believed the word. **The honest reading of the original row is CHECKED BUT
UNCERTIFIED.**

### What was done

A scripted pass (`scripts/mint_retrospective_certificates.py`, 0 core-min)
minted certificates from the checkMesh logs this audit had already located.
Every mint had to pass two gates: the log must parse to a real checkMesh
record, and **the log's cell count must equal the mesh's own `nCells`** read
from the polyMesh `owner` header. The second gate is what stops a certificate
drifting onto a different mesh — the failure the hash binding exists to
prevent, which would otherwise reappear in the act of back-filling it.

| outcome | rows |
|---|---|
| **MINTED** and now admitted by `certificate_admits()` | **95** |
| DISCREPANCY: this audit's own cited log parses `broken` | 7 |
| mesh states no `nCells` of its own, so the cross-check cannot run | 3 |

Verified after the fact: 95 admitted, **0 minted-but-refused**, 10 still
uncertified — the 7 + 3 above.

### The 7 discrepancies, for this audit's owner to rule on

These rows are marked `CERTIFIED (pre-existing record)` here, and the log each
one cites parses to hard errors under **this audit's own verdict rule**
(negative volumes, wrong-oriented face pyramids, non-orthogonality errors,
skewness errors, or a flagged aspect ratio in the pyHyp range):

- `rae2822-meshcheck/og-fine`, `og-medium`, `ogrid-coarse` — **negative-volume
  cells**, plus wrong-oriented face pyramids, non-orthogonality and skewness
  errors
- `dpw5-committee-probe/case_hex` — wrong-oriented face pyramids, skewness
  errors, flagged aspect ratio (max AR 1.44e4)
- `hlpw6-memory-probe/case_HLPW6` — skewness errors, flagged AR (2.29e3)
- `rae2822-meshcheck/og-coarse` — skewness errors, flagged AR (6.09e3)
- `tmr-bump-finer` — flagged aspect ratio at **2.23e6**, above the 1e6
  pyHyp-pathology threshold and far above the 6.6e4–7.4e4 NASA-grid signature
  this audit documents as a flag rather than an error

**No certificate was written for these.** Minting one would quarantine another
family's mesh on the strength of a parser, and an absent certificate already
quarantines it — so the conservative action and the honest one are the same
action, and the decision stays with the owner.

### RULED, 2026-08-10 — four of those rows are WRONG, confirmed by fresh measurement

**Chief-routed to this audit's owner and ruled (`MESH_CERT_RULINGS_2026-08-10/RULINGS.md`,
`8845be5f`). The discriminator was re-running `checkMesh`, which nobody had done:
the rows were refused at the verdict gate before any cross-check.** All seven
fresh parses agree with their cited log **exactly** — verdict, cell count,
aspect ratio and the full hard-error list — so **the stale-log hypothesis is
eliminated and the ROWS are what is wrong, not the logs.**

**Frame, stated first:** this covers **exactly the seven rows routed to this
family**, judged against **the meshes as they exist on disk at 2026-08-10
19:19 UTC**. It says nothing about the other three refusals, the 95 minted rows,
or the ~73 rows outside the 105.

**The four wrong rows are wrong in TWO DIFFERENT WAYS, and the difference is part
of the finding:**

**(a) Three meshes carry genuine GEOMETRIC errors** — `rae2822-meshcheck/og-fine`
(327 680 cells), `og-medium` (81 920), `ogrid-coarse` (20 480). Fresh `checkMesh`
reproduces on all three: **negative-volume cells**, **wrong-oriented face
pyramids**, non-orthogonality errors and skewness errors. These are broken meshes
that this audit marked `CERTIFIED`.

**(b) One mesh fails a THRESHOLD, with no geometric error at all** —
`tmr-bump-finer` (225 280 cells), max aspect ratio **2 230 928.97**, above the
1e6 pyHyp-pathology threshold and far above the 6.6e4–7.4e4 NASA-grid signature
**this audit itself documents as a flag rather than an error**. It has **no
negative volumes and no wrong-oriented pyramids.** The standard's own
aspect-ratio rule is doing the work here, not a geometric defect.

**These two are deliberately not merged into one sentence.** (b) is a weaker
failure than (a), and the weaker failure being weaker is part of what was found.
A reader who takes "four rows are wrong" as "four meshes have negative volumes"
would be wrong about three quarters of it.

**Why no `broken` certificate was written for any of the four.** The next reader
will ask, so: **an absent certificate already quarantines the mesh.** Writing a
`broken` one buys no additional protection and would assert a verdict the
standard does not require. The conservative action and the honest action
coincide, which is why the minting pass left the ruling to this audit's owner
rather than imposing one. **The four meshes remain uncertified and therefore
remain quarantined.**

**The remaining three refusals were EXONERATED and are now certified.**
`w1-bump-nasa-grids` coarse / medium / fine were refused because the mesh states
no `nCells` in its `polyMesh/owner` header — verified, and expected, since these
are `plot3dToFoam` conversions of NASA's grids rather than OpenFOAM-generated
meshes. **Re-running `checkMesh` performed that cross-check by a different
route — counting the mesh directly instead of reading a note about it** — and
returned 3 520 / 14 080 / 56 320, matching the cited logs exactly. Verdict
`flagged` (AR 4.8e3–5.3e3), an accepted verdict under Mesh Standard 3.3.
Certificates minted **from the fresh run**, not from the archived log.

**No verdict elsewhere in this audit is revised by this amendment, and the
original row text above is retained unedited.**

### Provenance: these are not birth certificates

A certificate minted from an archived log is a weaker fact than one written at
creation, and it says so. Each carries
`"provenance": "retrospective-from-archived-log"`, the log path, both mtimes,
and the cell-count cross-check result. **6 of the 95 rest on a log written
BEFORE the points file** (`.mesh-cache/b52`, `.mesh-cache/motorBike`,
`W4-defect-reach/a35_np1`, `W4-defect-robustness/a4conf_np4scotch` among
them); the cell count agrees in every case, so the mesh size is unchanged, but
mtime ordering is recorded rather than relied on. A reader can tell a birth
certificate from a retrospective one, which is the point: the mesh standard's
guarantee is not quietly widened to cover something it never promised.
