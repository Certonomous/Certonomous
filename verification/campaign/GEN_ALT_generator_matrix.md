# GEN_ALT — alternative-generator matrix for the pyHyp aspect-ratio pathology

Campaign-level record of an arm that is **COMPLETE and GRADED**. This page
transcribes an existing verdict to where verdicts live; it does not re-grade
anything and no compute was spent producing it. The full pre-registration,
its frozen prediction set, and the appended outcome are at

- `verification/runs/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md`

and are **cited, not duplicated** here.

Owner: cfd team (written 2026-08-08 by the then Cases family supervisor).
Standing finding under test: `cases/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`.

---

## 1. What the arm asked

`genAirFoilMesh.py`'s pyHyp hyperbolic extrusion lets **max cell aspect ratio
worsen under refinement** — measured, on the record: coarse 4,032 cells max AR
97.87 → refined 14,720 cells max AR 167.50, a factor **×1.71**, with max
non-orthogonality also worsening 22.7° → 27.0°.

The question was whether that behaviour belongs to **the tool** or to **the
recipe/geometry**. The arm built the lab's own analytic-NACA0012 **blockMesh
C-grid** (the F2/F5b proven topology) at **exactly matched cell counts**
(4,032 and 14,720), applying the **same user-facing refinement moves** pyHyp
received: ≈2× surface points, 2× wall-normal layers, ½ first wall spacing.

**The primary measure is the TREND, not the level.** The pre-registration
states explicitly that the AR *level* is out of scope — a C-grid to 25 chords
carries large far-field in-plane stretching — so only the refinement **factor**,
plus the near-wall band informationally, decide the verdict.

## 2. The pre-declared verdict rule

Fixed in the pre-registration before any mesh of this arm existed
(`GEN_ALT_PREREGISTRATION.md` §"The question and the verdict rule,
pre-declared"). These are **the arm's own pre-registered labels** and are kept
verbatim; they are not the standing gate vocabulary and are not translated
into it.

| Label | Condition, pre-declared |
| --- | --- |
| **GENERATOR-OWNED** | alternative pair's max-AR refinement factor **≤ 1.0** while pyHyp's measured ×1.71 stands → the mesh-generation family unblocks on the alternative generator |
| **RECIPE/GEOMETRY-OWNED** | alternative pair's max AR also worsens by a comparable factor **≥ 1.3** → the finding is not pyHyp's alone and must be re-scoped |
| **PARTIAL** | factor between 1.0 and 1.3 → reported as measured, no unblock claimed |

## 3. Verdict: **GENERATOR-OWNED**

| | pyHyp (measured, standing finding) | blockMesh C-grid (this arm) |
| --- | --- | --- |
| coarse | 4,032 cells, max AR 97.87 | **4,032 cells** (exact), max AR 240.21, non-ortho 70.13°, skew 0.57 |
| refined | 14,720 cells, max AR 167.50 | **14,720 cells** (exact), max AR 227.04, non-ortho 70.11°, skew 0.69 |
| **max-AR refinement factor** | **×1.71 (worsens)** | **×0.945 (improves)** |
| near-wall band (≤1 chord) max AR | 87.6-class (4G measurement) | **37.4** on the refined mesh |

The identical refinement moves that worsen pyHyp's worst cell by ×1.71
**improve** the structured C-grid's worst cell (×0.945 ≤ 1.0). The pathology
belongs to pyHyp's unscaled-smoothing hyperbolic march, not to the recipe and
not to the geometry.

Level caveat, as pre-declared: the alternative meshes' *global* max AR (240 /
227) exceeds pyHyp's level and does not touch the verdict — the trend decides.
The aspect-ratio figures carry the note `"advisory only per Mesh Standard 3.3;
never a lone rejection"` in `quality_matrix.json`.

## 4. Predictions scored

- **G1 — HELD.** blockMesh pair's max-AR refinement factor ≤ 1.0: measured
  **0.945**.
- **G2 — HELD, favourably.** Near-wall (≤1 chord) max AR predicted within ~3×
  of pyHyp's 87.6-class same-band value; measured **37.4**, i.e. **0.43×**, well
  inside the band rather than merely inside it.
- **G3 — REFUSED BY THE BORN-CLEAN GATE.** The smoke solve was predicted to
  complete 500 iterations clean. It never launched. The refined mesh's max
  non-orthogonality is **70.11°** (coarse 70.13°), breaching the **70° hard
  gate** of `docs/standards/MESH_STANDARD.md` §3.1 by 0.16%, and
  `assert_mesh_certified_at_entry` refused the solve **pre-launch**. The
  standard worked as adopted, on its second day, against its own author's arm.
  **No post-hoc mesh tuning was done to sneak under the gate**, and the
  prediction is scored as refused rather than quietly dropped.

**This is a mesh-only arm: no solve ever ran.** No solver credential, band or
validation claim follows from it, and none is made.

## 5. Cost

≈ **0.4 core-min** of the ~20 approved (mesh + `checkMesh` only; the ~1–2
core-min budgeted for the smoke solve was never spent, because the gate refused
the launch). At the c7a.4xlarge rate of $0.0513/core-h that is ≈ **$0.0003**.

`cost_basis`: **reported-by-owner, not measured** — the box cannot read its own
billing (CLAUDE.md rule 12, `COMPUTE_BUDGET_CHARTER.md` §5).

## 6. Freeze chain

Supervisor-verified, and the reason this record can be trusted at all: the
verdict rule above was committed **before** the answer existed.

| Step | Commit | When | What |
| --- | --- | --- | --- |
| Freeze | **`9c4fbef4`** | 2026-08-08 23:16:04Z | pre-registration committed at **95 lines, no outcome section**, under its original `demo-output` path — before any mesh of this arm was built |
| Outcome | **`41f0e1df`** | 2026-08-08 23:19:01Z | outcome appended (*"Entry 10 answered at four hundredths of its budget"*) |
| Move | **`a1fbe127`** | 2026-08-18 | file relocated to `verification/runs/GEN_ALT_runs/` in MOVE_MAP batch 7 |

The driver's own first mesh line is stamped `2026-08-08T23:16:13Z`
(`driver.log`), after the freeze commit.

## 7. Artifacts, all under `verification/runs/GEN_ALT_runs/`

| Path | What it holds |
| --- | --- |
| `GEN_ALT_PREREGISTRATION.md` | the frozen pre-registration + appended outcome (the authority; this page is a pointer to it) |
| `quality_matrix.json` | the matrix itself — both generators, both levels, both refinement factors, near-wall band, and the per-mesh `breaches` list naming the 70° non-orthogonality breach |
| `run_gen_alt.py` | the driver, committed with the pre-registration |
| `driver.log` | the run trace, including the two driver defects found and fixed in the act at zero solver cost |
| `alt_coarse/{record.json,log.checkMesh,log.blockMesh}` | coarse mesh record and birth certificate |
| `alt_refined/{record.json,log.checkMesh,log.blockMesh}` | refined mesh record and birth certificate |
| `alt_refined_smoke/{log.checkMesh,log.blockMesh}` | the smoke case as far as it got — mesh and certificate, **no `record.json`**, because the gate refused before the solver |

Both meshes carry `levers_verified_active` in their records, and the refusal was
enforced from the birth certificate rather than from a later reading.

## 8. Consequence on record

- The **mesh-generation family unblocks on the alternative generator**.
- `CAPABILITY_STRATEGY` §2's *"pyHyp pathology characterized +
  alternative-generator matrix"* now has **both halves**: the characterization
  was the standing finding, and `quality_matrix.json` is the matrix.
- A **gate-compliant re-parameterization** for the smoke-solve capability proof
  (more far-field cells, or a relaxed arc grading, to clear 70° non-orthogonality
  at these counts) is a **successor arm with its own pre-registration**. It has
  not been run, and nothing here anticipates its result. The entry-10 question
  did not require it.
