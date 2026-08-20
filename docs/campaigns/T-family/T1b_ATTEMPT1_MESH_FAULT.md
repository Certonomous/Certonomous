# T1b attempt 1 — NOT A RESULT: the radial grading ran the wrong way

**Rung:** T1b, fully developed turbulent pipe against a two-correlation band
**Verdict:** NOT A RESULT (all 19 cases)
**Cost:** 56.6 core-hours, ~$2.90, 19 cases, all discarded
**Date:** 2026-08-20
**Repaired by:** attempt 2, same design, same frozen comparator, corrected mesh

---

## 1. What happened

Every T1b case was built with

```
hex (0 1 2 3 0 1 5 4) (nx nr 1) simpleGrading (1 expansion 1)
```

with `expansion > 1`.  blockMesh reads a simpleGrading entry as the ratio of the
**last** cell to the **first** cell along that direction, and the radial
direction of this block runs from the **axis** (vertices 0 and 1 at y = 0) to
the **wall** (y = R).  A ratio above one therefore grows the cells from axis to
wall.  The builder computed the correct wall-cell height, and then placed it on
the centreline.

The smallest cell sat where nothing happens.  The largest cell sat against the
wall, where the entire wall flux and the entire wall shear are decided.

Read straight from attempt 1's own `constant/polyMesh/points`, Re = 3e5,
finest level:

| | height |
|---|---|
| cell touching the **axis** | 1.96e-05 m — *the designed wall cell* |
| cell touching the **wall** | 4.11e-03 m — **210× too thick** |
| achieved y+ at the wall | 52.3 — the design asked for 0.625 |

The designed first cell was 1.961777e-05 m.  Recovering the axis cell's height
from its centroid, with the wedge factor of 2/3 for the innermost sector cell,
gives 1.5 × 1.3066e-05 = 1.960e-05 m.  That is the design value to four
significant figures, sitting at the wrong end of the pipe.  There is no
ambiguity about what happened.

## 2. What it did to the answers

Measured by the frozen comparator at x/D = 80, against the pre-committed band
and against Petukhov's friction factor:

| case | y+ achieved | Nu | vs band | f | vs Petukhov |
|---|---:|---:|---:|---:|---:|
| R_10k_c  |   5.67 |  35.71 | **+15.5 %** | 0.03504 | +11.3 % |
| R_10k_m  |   3.35 |  31.41 | **+1.6 %**  | 0.03113 | −1.1 % |
| R_10k_f  |   2.05 |  30.06 | **−2.7 %**  | 0.02958 | −6.0 % |
| R_30k_c  |  17.65 |  48.61 | −34.0 % | 0.01403 | −40.6 % |
| R_30k_m  |  12.91 |  63.25 | −14.2 % | 0.01887 | −20.2 % |
| R_30k_f  |   9.04 |  75.52 | **+2.5 %**  | 0.02337 | −1.1 % |
| R_100k_c |  42.26 |  43.09 | −77.4 % | 0.00354 | −80.3 % |
| R_100k_m |  32.63 |  62.82 | −67.0 % | 0.00524 | −70.9 % |
| R_100k_f |  24.81 |  89.31 | −53.1 % | 0.00759 | −57.8 % |
| R_300k_c |  85.89 |  36.98 | −91.9 % | 0.00102 | −92.9 % |
| R_300k_m |  67.30 |  55.60 | −87.8 % | 0.00153 | −89.4 % |
| R_300k_f |  52.32 |  83.26 | −81.8 % | 0.00230 | −84.1 % |
| W_100k   | 141.94 | 147.32 | −22.6 % | 0.01724 | −4.2 % |
| W_300k   | 131.97 | 402.71 | −11.8 % | 0.01384 | −4.1 % |

## 3. The part that matters: it would have shipped two PASSES

The registered band is the disagreement between Dittus-Boelter and Gnielinski:
±2.84 % at Re = 1e4, ±3.89 % at 3e4, ±5.33 % at 1e5, ±5.75 % at 3e5.

Against that band, on the broken mesh:

* **Re = 10 000, finest level: −2.7 % against ±2.84 % → PASS**
* **Re = 30 000, finest level: +2.5 % against ±3.89 % → PASS**

and the friction rows next to them read −6.0 % and −1.1 %, which is what a
healthy pipe looks like.  Two of the four gate rows would have been reported
as passes, with corroborating friction, on a mesh whose wall cell was 3.4× and
14.6× thicker than designed.

The reason is that the damage scales with the grading ratio, and the grading
ratio scales with the Reynolds number, because a higher Re demands a thinner
wall cell against the same pipe radius:

| Re | axis/wall ratio | worst Nu error |
|---|---:|---:|
| 10 000  |   3.4 |  −2.7 % (finest) |
| 30 000  |  14.6 |  +2.5 % (finest) |
| 100 000 |  61.5 | −53.1 % (finest) |
| 300 000 | 211.4 | −81.8 % (finest) |

A campaign run only at Re = 1e4 would have passed its gate, published a
Nusselt number good to 3 %, and been wrong about its mesh by a factor of three.
**The Reynolds sweep is what exposed this. A single-point validation would not
have.**

## 4. What did diagnose it, and what did not

**Did not:**
* blockMesh — the dictionary is legal and it meshed without a warning.
* checkMesh — every case returned rc = 0.
* The builder's own summary table and every `CASE.txt` — both print the
  *intended* wall cell, because both read it from the same variable the
  dictionary got it from.  Nothing in the chain disagreed with anything else.
* Iterative convergence — most cases converged happily to the wrong answer.
* Cell count — attempt 1 and attempt 2 meshes have **identical** cell counts
  (81 920 at the finest level).  They differ only in grading.

**Did:**
* **The friction row.** The frozen comparator grades Nusselt and *reports*
  friction, on the registered reasoning that "a friction error is a solver or
  mesh fault; a Nusselt error with correct friction is the thermal closure."
  Nu and f failed together and by nearly the same amount at every point
  (−34.0/−40.6, −77.4/−80.3, −91.9/−92.9, −81.8/−84.1).  A thermal-closure
  fault cannot do that: a wrong turbulent Prandtl number moves Nu and leaves f
  alone.  The attribution lever worked exactly as registered, and it pointed at
  momentum, which means the wall.
* **The achieved y+**, which the comparator reads rather than assumes.  A
  "resolved" arm reporting y+ = 52 is not a resolved arm.
* **The written points file.**  In the end the mesh had to be read, not
  inferred from what built it.

## 5. Repair

Attempt 2 emits `simpleGrading (1 1/expansion 1)`.  Reversing a geometric series
does not change its sum, so the mesh still fills R exactly and the wall cell is
the design value by construction.  Verified against the written points before
any solver ran: wall cell 1.959909e-05 m against a designed 1.961777e-05 m, the
0.095 % being the wedge cos(θ/2) factor.

Nothing else changed.  Same 19 cases, same Reynolds numbers, same stations, same
endTime, and the **same frozen comparator** `analyse_t1b.py`, byte-identical to
the version committed in 08732fd6 before any case existed.  The band in
`T1b_band.json` is untouched.  This is a repair under Charter §2d.1, not a
redesign: the fault is in the mesh the design was realised on, not in the design
or in what it will be graded against.

`check_t1b_mesh.py` is new, and runs before any solver.  It reads each case's
written points and asserts the wall cell matches CASE.txt, that it is the
**smallest** radial cell — the specific inversion attempt 1 failed — that the
cells sum to the wall radius, and that the ratio is geometric.  All 19 attempt-2
meshes pass it.

## 6. Attempt 1 is retained

`verification/runs/T-family/T1_runs/attempt1/` holds all 19 case directories,
their logs and their STATUS files.  It is the evidence for this record and it
is not to be deleted.

Two caveats on its contents:

* `P_10k` was still solving when the archive was made and was not graded.
* `R_10k_f` finished after the move.  OpenFOAM writes to the absolute case path
  it resolves at startup, not to the directory its process followed, so its
  final `20000/` was written into the freshly rebuilt attempt-2 case of the
  same name and was moved back here by hand.  See §7.

## 7. A second fault the first one exposed

Archiving a case directory while its solver runs does **not** redirect the
solver's output.  The process follows the moved inode for its working
directory, but OpenFOAM writes fields to the absolute path resolved at startup.
A finished attempt-1 solver therefore dropped a complete, correct-looking
`20000/` — right time, right field list, right length — into the attempt-2 case
rebuilt at the old path.

Because both meshes have the same cell count, **a cell-count check cannot see
this**.  Only the file ages give it away.  Two guards were added:

* `run_one2.sh` refuses any case that already carries a numeric time directory
  other than `0`, before it meshes or solves.  (Its first version used the glob
  `[0-9]*`, which matches `0.orig`, and refused all 18 cases in 45 seconds; the
  guard now uses a numeric regex.  It was tested against a clean case and
  against a contaminated one, and fires only on the latter.)
* `mark_done_t1b.py` refuses to mark a case done if any field in its final time
  directory is older than that case's own `0/T`, which the runner writes at the
  start of the run allowed to produce the answer.

## 8. Blast radius: how far the fault reaches

Swept with `find`, not `grep -r`, because `grep -r` here is ugrep honouring
ignore files and is blind to exactly the gitignored case archives this needed to
read (L-136). Meshes were read from written `constant/polyMesh/points`, never
inferred from the builder that wrote them — that inference is what failed in the
first place.

**Confined to T1b.** Specifically:

* **T1c** (`build_t1c.py`) emits `simpleGrading (1 1 1)`. Read from disk, its
  radial cells are uniform. The apparent 0.75 ratio in a naive centroid check is
  the wedge sector's 2/3 centroid offset for the innermost cell, not grading.
  **T1c's GATE FAIL is not this fault.**
* **The T1 diagnostic ladder** — `D_Pe`, `D_Pe_c`, `D_Pe_m`, `D_wedge`,
  `D_Re25/50/200/400` — all uniform, verified from disk, ratio 1.0000 to four
  decimals. **The Péclet sweep and the Pr ladder are unaffected.**
* **The square cavity ladder** (`K0cG_runs`, `K0cS_runs`, `K0cT_runs`) is
  **correct**, and correct for an instructive reason. It uses blockMesh
  *multi*-grading, `( (0.5 0.5 ex) (0.5 0.5 1/ex) )`, splitting each direction
  into two half-blocks and writing the reciprocal by hand for the second. Read
  from disk: `S_SST_x` has 9.77e-05 m cells at both walls against 1.16e-02 m at
  the centre, a ratio of 119, and `S_KE_c` 2.50e-04 m against 2.93e-02 m, ratio
  117. Fine at both walls, coarse in the middle, which is what a cavity needs.
  Its author had to think about grading direction to write that reciprocal at
  all. T1b's builder had a single direction and never did. **D436 stands.**
* `THERMAL_K0_runs` is uniform throughout.

**Not swept, and named rather than passed over:** the graded meshes outside the
thermal ladders — `F3_runs`, `F4_runs`, `F6b_runs`, `F7_runs`, `F11_runs`,
`DMR_runs`, `R4_runs`, `B52_RUNG6_REPLICATE_runs`, `K2b_runs`, `K2e_runs`,
`KV1_runs`, `cases/hlpw6`, and the `sdk/workflows` templates. Several carry
non-unit gradings such as `(40 1 1)`, `(1 6 1)` and `(0.25 1.6 1)`; the presence
of reciprocals like `0.25` suggests direction was considered there, but that is
an inference from a literal, which is the class of reasoning this record exists
to distrust. **They have not been read from disk and no claim is made about
them.**
