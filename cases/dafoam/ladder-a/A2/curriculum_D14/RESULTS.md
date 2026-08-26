# CURRICULUM D14-M — RESULTS: **`PASS`** — THE pyHyp TOOLCHAIN REPRODUCES D4's MESH BIT-FOR-BIT, AND THE GENERATOR FINDING DOES NOT CONTAMINATE AN UNREFINED RE-MESH

**Dated 2026-08-26.** Lane: dafoam `lab-lane` (Q2). Supervisor: `dafoam-supervisor`. Pre-registration frozen at **`dd6c808e`** (`PREREGISTRATION.md` v1.0, this directory), before the run root existed (asserted absent 17:36:36Z). **Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7). Permission for the detached launch: `bc0e687e`; launched by `scripts/queue_runner.py` from `verification/queue/dafoam/D14M.json` at **17:40:32Z** (pid 307428, `runner.log`), not by an agent.

## 1. Verdict

**`PASS`.** Composed by the frozen comparator `d14m_grade.py` (blob `2835b729`, md5 asserted by the driver before launch) from the artifacts on disk — `/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh/D14M_grade_20260826T174136Z_307430.json` — under the composition §6 registered: G14-1 completion+age `PASS`, G14-2 identity `PASS`, G14-3 non-ortho `PASS`, G14-3 skew `PASS`, G14-4 reproduction `PASS`.

| quantity | registered reference (D4 baseline, `A2-mach-wing/checkMesh.log`) | measured on the regenerated mesh (`MESH/checkMesh.log`) | relative departure |
|---|---|---|---|
| cells / points | 38,304 / 40,209 | **38,304 / 40,209** | 0 |
| faces / internal | 116,756 / 113,068 | **116,756 / 113,068** | 0 |
| max aspect ratio | 684.4022128 | **684.4022128** | 0 |
| max non-orthogonality | 66.96543422° (avg 11.48508811°) | **66.96543422°** (avg 11.48508811°) | 0 — inside the 65–70° warning band, reported |
| max skewness | 1.339283343 | **1.339283343** | 0 |
| `points.gz` sha256 | `260e9db7f5a021080a5bc48cacc0874af511fee82e59d33b7832cefde52cbd4e` | **`260e9db7f5a021080a5bc48cacc0874af511fee82e59d33b7832cefde52cbd4e`** | **identical** |

The mesh is **bit-identical** to the one D4 ran on — not merely within the 1e-6 band. Aspect-ratio advisory flag: false; generator-finding-class drift: false.

## 2. Predictions, scored by the comparator

| # | registered | measured | score |
|---|---|---|---|
| P1 | 38,304 / 40,209 exactly | 38,304 / 40,209 | **HIT** |
| P2 | 684.4022128 ± 1e-6 rel | 684.4022128 | **HIT** |
| P3 | 66.96543422° ± 1e-6 rel | 66.96543422° | **HIT** |
| P4 | 1.339283343 ± 1e-6 rel | 1.339283343 | **HIT** |
| P5 | pyHyp cumulative CPU at level 39 ∈ [2.0, 10.0] s, point 4.2 | **4.2 s** (`MESH/logMeshGeneration.txt`, level 39 column) | **HIT** |
| P6 | container wall ≤ 120 s, point 40 s | **11 s** (`StartedAt` 17:41:36.997Z → `FinishedAt` 17:41:45.787Z; in-container stamps: coarsen 0 s, pyHyp 5 s, OpenFOAM utilities 3 s, both `checkMesh` < 1 s) | **HIT** |

**6 of 6 HIT.** P6's point (40 s) overshot the measurement by 3.6× — the container start + `loadDAFoam.sh` overhead priced from D12R2's S0 stage did not materialise on a warm image; recorded, not re-derived.

## 3. Completion and the record (rule 4, L-342 field classes)

Physics-critical, all satisfied: container `d14m_MESH_20260826T174136Z_307430` **rc 0 from `docker inspect`, OOMKilled false**; `checkMesh` rc 0 and `Mesh OK.`; `checkMesh.log` newer than `MESH/AGE_DATUM` (mtime 1787766096, the last host write before launch). Infrastructure: wall 11 s, 0.1833 core-min, MemAvailable 27.87 → 27.81 GiB, H5 window 45/45 above 14.0 GiB, aggregate 0 waits (`MESH_aggregate_series.txt`), G14-0 `PASS` with its planted control fired at 17:40:33Z (`G14-0_20260826T174033Z.json`, this directory), cpuset 14. The container is preserved (no `--rm`); the run root is preserved byte-for-byte.

## 4. Cost (rule 12) — the anchor this rung was cut to produce

**Predicted 0.67 core-min (band [0.3, 2.0]); measured 0.1833 core-min; ratio 0.274.** Gross = cleaned = 0.1833 (one 11 s row; nothing near the 3600 s stall rule). **Waste 0.000 core-min, named separately.** Derived **$0.000157**, reported-by-owner, NOT MEASURED. Attribution: **misprediction of overhead** — the point assumed ~20 s of container start on top of ~15 s of work; the work itself (pyHyp 4.2 s CPU, utilities 3 s) was predicted correctly from the baseline log, so the like-for-like anchor for any future pyHyp regeneration of this wing is **≈ 9 s of in-container wall at np=1, 11 s container wall**. Calibration row: `docs/COST_CALIBRATION.md` (id re-derived from the HEAD blob in the committing invocation).

## 5. What this establishes, and what it does not

**Established:** on image `sha256:9d45679d…f07fc` (pyHyp 2.6.1, cgnsutilities 2.6.0, OpenFOAM v2506) the registered generator (`genWingMesh.py` md5 `dab5e959…`) applied to the registered surface (tarball md5 `92956aa0…`, coarsened once) reproduces D4's 38,304-cell mesh **bit-for-bit**; the pyHyp aspect-ratio finding, whose recipe is a refinement with smoothing unscaled, has no purchase on an unrefined regeneration — G14-0 refused the planted refinement and passed the staged generator. The "single mesh only" caveat on D4's capability cell keeps its meaning (one mesh, no grid family) but its premise — that the mesh could not be regenerated on demand — is retired.

**Not established (§9 of the pre-registration, unchanged):** nothing about D4's optimum or a re-mesh at it (successor rung; `PREREGISTRATION_DRAFT.md` in this directory is that draft); nothing about gradients or CD; nothing about pyHyp's internal mechanism; nothing at np > 1; nothing about the PATCHED row; **no grid family, no GCI**; nothing about the mesh's quality beyond `checkMesh`'s own metrics (66.97° max non-orthogonality is inside `MESH_STANDARD.md` §3.1's warning band, on the baseline exactly as here).

**Capability cell (`068c2bf0`):** 3D · steady · subsonic-compressible — deepened; no gradient verdict moved.
