# 🔴 COMMIT HAZARD — 0.77 GB UNDER THIS DIRECTORY IS **NOT** GITIGNORED

`.gitignore:66` covers `**/constant/polyMesh/`, so the 1.995 GB of `polyMesh` data is safe.
**The Plot3D volume meshes are NOT covered.** Measured with `git check-ignore` over every file here:

| not ignored | bytes |
|---|---|
| `L3/volumeMesh.xyz` | **645,035,449** |
| `L2/volumeMesh.xyz` | 84,948,361 |
| `TRIAGE_L1_s0/s0_2.0e-4/volumeMesh.xyz` | 11,746,705 |
| `TRIAGE_L1_s0/s0_1.0e-4/volumeMesh.xyz` | 11,746,705 |
| `L1/volumeMesh.xyz` + `*/surfMesh.cgns` + records | remainder |
| **69 files, total** | **0.77 GB** |

**A `git add` of this directory would commit 742 MB of mesh into the repository.** Rule 10 forbids
`git add -A` / `git add .` / pathspec sweeps anyway, so the standing rules already prevent it — this
note exists so the hazard is known rather than merely not-yet-triggered.

**This lane staged nothing and committed nothing.** The records here are the deliverable; whether any
of them is committed, and whether `.gitignore` should grow a `*.xyz` rule, is the supervisor's call —
`.gitignore` is a shared file and this lane did not touch it.

**If a commit is made, commit the `.md` records and the `.py`/`.sh` instruments by EXPLICIT PATH
only**, never the directory.
