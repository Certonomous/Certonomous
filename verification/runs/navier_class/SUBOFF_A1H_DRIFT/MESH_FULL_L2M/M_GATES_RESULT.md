# SUBOFF A1h — MESH ADMISSION GATES M-1…M-7, MEASURED

Gates frozen in `verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md`
§2.1 at commit `79b4de868e1e8bbf08e14cd6db3c1d6acb3240df`, **before this mesh existed**.
Measured 2026-09-13. Artifacts beside this file: `log.mirrorMesh`,
`log.checkMesh.FULLFLAG`, `M7_SEAM_MEASUREMENT.json`.

## VERDICT: **GATE REACHED** — all seven clauses pass; the mesh is ADMITTED for A1h.

| # | gate | threshold | measured | |
|---|---|---|---|---|
| M-1 | `nCells` | exactly 18,242,474 | **18,242,474** | PASS |
| M-2 | patch `symm` | nFaces == 0 | **0 faces, 0 points, "ok (empty)"** | PASS |
| M-3 | z bounding box symmetric to 1e-6 | ±2.9927629 | **(−2.9927629, +2.9927629)**, sum 0 | PASS |
| M-4 | topology closed, no boundary errors | closed | **`".*"` ok (closed singly connected)** | PASS |
| M-5 | max non-orthogonality | ≤ 70° | **64.90583165°** (avg 6.386686081) | PASS |
| M-6 | max skewness, boundary faces included | ≤ 4 | **3.125838012** | PASS |
| M-7 | **THE SEAM** | min vol > 0; seam non-ortho ≤ 70° **and** ≤ whole-mesh max | **min vol 9.56232599e-14 m³; seam non-ortho 63.70247604°** | PASS |

## M-7, THE GATE THIS CASE EXISTS TO PASS

261,024 seam cells of 18,242,474, carrying 136,316 seam points of 19,632,596.

| quantity | seam | whole mesh | reading |
|---|---|---|---|
| min `cellVolume` | **9.56232599e-14 m³** | 5.166831581e-14 m³ | the smallest cell in the mesh is **NOT** at the seam |
| max `nonOrthoAngle` | **63.70247604°** | 64.90583165° | the worst non-orthogonality is **NOT** at the seam |

**The seam is better than the mesh as a whole on both metrics.** `mirrorMesh` did not
create a sliver layer at z = 0 — which is the failure M-7 was written to catch, and
which M-1…M-6 would have missed among 18 million cells.

## THE MIRROR'S SYMMETRY, READ FROM THE GEOMETRY — NOT FROM CELL COUNTS MATCHING

A doubled cell count is consistent with a mirror that duplicated the seam instead of
merging it. The point and face arithmetic is not:

| quantity | L2 (half) | 2 × L2 | A1h (full) | difference | what the difference IS |
|---|---|---|---|---|---|
| points | 9,884,456 | 19,768,912 | **19,632,596** | **136,316** | exactly the seam points — **counted once, not twice** |
| faces | 28,106,791 | 56,213,582 | **56,083,012** | **130,570** | exactly L2's `symm` face count — **became interior** |
| cells | 9,121,237 | 18,242,474 | **18,242,474** | 0 | — |

**136,316 is also exactly the point count L2's `checkMesh` reports for its `symm`
patch**, found here independently by a vertex test on the mirrored mesh with no
knowledge of the old patch. Two readers, two meshes, one number.

The mirror is an isometry, and the invariants say so: max non-orthogonality
**64.90583165° on both meshes**, max skewness **3.125838012 on both**.

## DISCLOSED, NOT GATED

`checkMesh` reports **263,456 concave cells = exactly 2 × L2's 131,728**, the same
1.444 % fraction — the two-tier standard's disclosed item (§2.1), governed by
`SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md` and unmeasured on this mesh.
Faces with non-consecutive shared points: **2, exactly 2 × L2's 1**. Every disclosed
figure doubles, as a faithful mirror requires.

`checkMesh` prints "Failed 1 mesh checks" — that failure **is** the concave-cell
geometry check above. `MESH_STANDARD` §14 governs: non-orthogonality is read from the
reported maximum, **never from `checkMesh`'s verdict line**. No gate is read from that
line here.

## THE SEAM READER WAS PLANTED BEFORE IT WAS BELIEVED

- **S-A, the selector**: run at the registered plane and at an impossible one. Found
  **136,316 points at z = 0** and **0 at |z − 1e9| < 1e-6**. A selector returning the
  same answer for both is not selecting.
- **S-B, the reducer**: a bad value planted at a known seam cell must come back as the
  reported extremum. Planted −9.87e-30 into `cellVolume` → returned −9.87e-30; planted
  123.456 into `nonOrthoAngle` → returned 123.456.
- **The cell count was cross-checked, not asserted**: derived from `owner`/`neighbour`
  connectivity as 18,242,474, against `checkMesh`'s independently printed 18,242,474.
  Disagreement would have refused.

## TWO DEFECTS FOUND WHILE MEASURING THESE GATES, BOTH RECORDED

1. **`set -u` killed the build wrapper inside OpenFOAM's own `bashrc`** (it reads
   `WM_PROJECT_DIR` before setting it, line 184). The shell died **before reaching the
   line that writes the wrapper's rc file**, leaving an empty status, no rc, no log and
   no process — *indistinguishable from never having been launched*. A wrapper whose
   job is to capture its own rc must not use a shell option that can kill it first.
2. **The field reader refused an 18-million-value list as "unparsable uniform"**:
   `"uniform"` is a **suffix of `"nonuniform"`**, so a bare substring test is true for
   every nonuniform field. Same trap as the numeric prefix that made
   `grep -F '3.343886'` match `3.3438861e-05`. Both were caught by refusal rather than
   by producing a wrong number, and the repaired reader was planted both ways.

A third is disclosed against this act's own tooling: the first build wrapper recorded
`checkMesh_rc=1` and still wrote `rc=0`. It has been repaired so a failed `checkMesh`
fails the wrapper.
