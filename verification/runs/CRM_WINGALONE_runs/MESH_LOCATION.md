# THE PLOT3D VOLUME MESHES LIVE OUTSIDE GIT — WHERE THEY WENT, AND WHY

**Moved 2026-09-11 on cfd-supervisor's ruling. Moved, never deleted.**

| level | destination | bytes | md5 (unchanged by the move) |
|---|---|---|---|
| L1 | `/home/ubuntu/certonomous-runs/CRM_WINGALONE_meshes/L1/volumeMesh.xyz` | 11,746,705 | `bef6ce07718486e36df3e2f237c43051` |
| L2 | `/home/ubuntu/certonomous-runs/CRM_WINGALONE_meshes/L2/volumeMesh.xyz` | 84,948,361 | `214db528050e347b323951a4bec4c436` |
| L3 | `/home/ubuntu/certonomous-runs/CRM_WINGALONE_meshes/L3/volumeMesh.xyz` | 645,035,449 | `71df4d76fcc3a8e3d275dd39aabb39a6` |
| triage s0=1.0e-4 | `/home/ubuntu/certonomous-runs/CRM_WINGALONE_meshes/TRIAGE_L1_s0/s0_1.0e-4/volumeMesh.xyz` | 11,746,705 | `2538f7ce3da4d5a557c85d3e9a7580ba` |
| triage s0=2.0e-4 | `/home/ubuntu/certonomous-runs/CRM_WINGALONE_meshes/TRIAGE_L1_s0/s0_2.0e-4/volumeMesh.xyz` | 11,746,705 | `2d72440ffc711bb58a4b0207c896abc7` |
| **total** | | **765,223,925** | |

**Integrity proved, not assumed:** all five were md5'd **before** and **after**; every hash matches.
Same filesystem (`st_dev` 66305 both sides), so the move was a **rename** and cost no disk.

**Why they are bulk.** The supervisor's ruling: *"a citation to an artifact's ABSENCE is not a
citation to its CONTENT."* The records cite these paths only to say the file **did not exist** at a
moment — a claim satisfied by the record itself — and `COMMIT_HAZARD.md` cited them as an inventory,
which is what this file now supersedes. **No verdict reads their content.** Every graded number comes
from `log.checkMesh` and `pyhyp.log`, both committed.

**The destination needs no new `LOCATIONS.md` entry:** `/home/ubuntu/certonomous-runs/` is already
enumerated there as §4.1, *"every solver run the lab has executed... outside the repository
entirely."* This directory sits inside that enumerated tree and `ls /home/ubuntu/certonomous-runs/`
reaches it. §4.1's snapshot counts (446 directories, 75.79 GB) are now one directory and 765 MB
stale, but they are stated there **with their re-derivation command** and go stale with every run —
they are not edited here.

**The `surfMesh.cgns` inputs STAY** in the level directories (2.3 MB total). They are small, and the
build record asserts their **md5** as the proof that the right surface was staged — an input whose
hash a record cites is not bulk.
