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

---

## 2026-09-11 — RULING APPLIED: **THE FILES STAY.** And the gap is NOT this rung's.

cfd-supervisor's criterion: *"grep every graded record and gate table for a path citing the `.xyz`.
If NOTHING cites them, move them to `/home/ubuntu/certonomous-runs/`... If ANY record cites them by
path, they stay where they are and `COMMIT_HAZARD.md` stands as the record."*

**Checked, with a positive control** — the grep was first shown able to find `nonOrthoFaces`, a path
that IS cited, so a null result would have been evidence rather than a blind read.

**The condition FIRED. Records cite them by path, so THE FILES STAY and nothing was moved.**

| citing record | line | nature of the citation |
|---|---|---|
| `GATE_TABLE.md` | 46 | *"written while `L3/volumeMesh.xyz` did not exist"* |
| `L3_PREDICTION_BEFORE_RUN.md` | 3 | same — an **absence-at-a-time** claim |
| `PGRIDRATIO_FINDING.md` | 10 | *"`L3/volumeMesh.xyz` does not exist"* — the rc=0 finding rests on it |
| `COMMIT_HAZARD.md` | 8–12 | this file's own hazard inventory |

🔴 **A DISTINCTION FOR THE SUPERVISOR TO RULE ON, SURFACED RATHER THAN USED.** Every hit above is
either an **absence-claim** (the path being *empty* is the point) or this file's inventory. **No
verdict cites the CONTENT of any `.xyz`** — the graded numbers come from `log.checkMesh` and
`pyhyp.log`, both now committed, so the evidence chain for every verdict is already in git.

**The supervisor's stated REASON** — *"an artifact a verdict cites is not bulk"* — would therefore
point to MOVE, while his stated CRITERION points to STAY. **This lane took STAY**, because that is
what the criterion literally says and because re-reading a supervisor's criterion until it yields the
other answer is not a lane's call. **The distinction is reported, not acted on.**

## 🔴 AND THE GAP IS PRE-EXISTING AND LAB-WIDE, NOT THIS RUNG'S

Measured while checking this directory:

**`verification/runs/CRM_M085_runs/PYHYP_ROUTE_PROBE/work/volumeMesh.xyz` — 163,573,897 bytes,
NOT gitignored, untracked, sitting under `verification/runs/` since 18:00 today.**

`.gitignore:66` covers `**/constant/polyMesh/` and **nothing covers `*.xyz`**. So this is not a
CRM-wing-alone problem — **any pyHyp rung that writes a Plot3D mesh under `verification/runs/`
leaves un-ignored bulk**, and one already had, hours before this ladder was built.
**`.gitignore` is shared config and this lane did not touch it.**
