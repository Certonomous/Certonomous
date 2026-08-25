# F12 attempt 2 — mesh birth certificates

Every level records how it was built: the generating dictionary and its sha256,
the command, the UTC stamp, the cell count and the `checkMesh` result. A mesh
whose provenance is not recorded is not admissible evidence.

**Builder:** `build_ladder_attempt2.py`, sha256 `ac77bb9fa1c7f1fd…`, committed at `117d8adc`.
**Frozen pre-registration blob asserted before the build:** `080303c57aee52849bb625579565a84ca5469717`.
**UTC stamp:** `2026-08-25T16:42:27Z`.  **loadavg at launch:** 5.33, 4.79, 2.87.
**OpenFOAM:** `openfoam2606` (`OPENFOAM_RUN_PREFIX`), native, ranks = 1.

## coarse

| field | value |
| --- | --- |
| generating dictionary | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/coarse/system/blockMeshDict` |
| dictionary sha256 | `d47f5b9c5e9718cc155b4173f2a898cfe26ce3b9be9c881fe201ce5c116ff637` |
| dictionary bytes | 244727 |
| command | `blockMesh` then `checkMesh` |
| blockMesh rc | **0** |
| checkMesh rc | **0** |
| cells built | **23040** |
| max non-orthogonality | **51.1237°** (gate ≤ 70°) |
| faces > 70° | **0** |
| max skewness | **0.957230** (gate ≤ 4) |
| max aspect ratio | < 1000, not printed (advisory, not gated) |
| wall-normal first cell | 2e-06 chord |
| y+ (full first-cell height) | 0.4660 |
| decomposition | `hierarchical`, 4 subdomains, seed-free |
| partition cell counts, run 1 | [5760, 5760, 5760, 5760] |
| partition cell counts, run 2 | [5760, 5760, 5760, 5760] |
| identical across two runs | **True** |
| **admission gate A** | **`PASS`** |
| checkMesh log | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/coarse/log.checkMesh` |

## medium

| field | value |
| --- | --- |
| generating dictionary | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/medium/system/blockMeshDict` |
| dictionary sha256 | `7364b20f9d556452dbab451ae792cb621ce311395feff34312e8aa3a9486b276` |
| dictionary bytes | 244751 |
| command | `blockMesh` then `checkMesh` |
| blockMesh rc | **0** |
| checkMesh rc | **0** |
| cells built | **92160** |
| max non-orthogonality | **51.5250°** (gate ≤ 70°) |
| faces > 70° | **0** |
| max skewness | **0.956899** (gate ≤ 4) |
| max aspect ratio | < 1000, not printed (advisory, not gated) |
| wall-normal first cell | 1e-06 chord |
| y+ (full first-cell height) | 0.2330 |
| decomposition | `hierarchical`, 4 subdomains, seed-free |
| partition cell counts, run 1 | [23040, 23040, 23040, 23040] |
| partition cell counts, run 2 | [23040, 23040, 23040, 23040] |
| identical across two runs | **True** |
| **admission gate A** | **`PASS`** |
| checkMesh log | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/medium/log.checkMesh` |

## fine

| field | value |
| --- | --- |
| generating dictionary | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/fine/system/blockMeshDict` |
| dictionary sha256 | `00b1fb36fc91f9b08c1d4a098eb5c4a2c38290d982fc27cef7f447e77bbe4982` |
| dictionary bytes | 244759 |
| command | `blockMesh` then `checkMesh` |
| blockMesh rc | **0** |
| checkMesh rc | **0** |
| cells built | **368640** |
| max non-orthogonality | **51.9261°** (gate ≤ 70°) |
| faces > 70° | **0** |
| max skewness | **0.956588** (gate ≤ 4) |
| max aspect ratio | < 1000, not printed (advisory, not gated) |
| wall-normal first cell | 5e-07 chord |
| y+ (full first-cell height) | 0.1165 |
| decomposition | `hierarchical`, 4 subdomains, seed-free |
| partition cell counts, run 1 | [92160, 92160, 92160, 92160] |
| partition cell counts, run 2 | [92160, 92160, 92160, 92160] |
| identical across two runs | **True** |
| **admission gate A** | **`PASS`** |
| checkMesh log | `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/fine/log.checkMesh` |
