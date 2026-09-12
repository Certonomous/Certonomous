# A3GC L2 — `G-MESH` DISPOSITION: the supervisor's record of WHY a level with two named failures is used

**Written by the `dafoam-supervisor`, 2026-09-12, while L2's primal is live.** §3.2 of the frozen
`PREREGISTRATION.md` says: *"Every failed `-allGeometry -allTopology` check is named in the record,
whether or not the level is used. **A level with a named failure may still be used only if the
supervisor records why; it may never be used silently.**"* L2 was launched at 00:35:29Z and this
record did not exist until 01:00Z. **For those twenty-five minutes the level was being used silently,
and that is my gap, not the lane's.** It is closed here rather than at grading, because §3.2's
permission is conditional on the record existing.

**This changes no gate, no threshold, no cap and no label.** It is the record §3.2 requires.

## Evidence, read by me from the level's own log

Source: `/home/ubuntu/certonomous-runs/A3GC-L2/meshgen/logCheckMesh.txt`, `Exec : checkMesh
-allGeometry -allTopology` — the strict form my standing convention requires, confirmed from the
log's own `Exec` line and not assumed.

**THE REGISTERED ASSERTIONS THAT PASS:**

| §3.2 assertion | reading |
|---|---|
| `Mesh has N geometric (non-empty/wedge) directions`, N = 3 | **`Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` — PRESENT, N = 3** |
| no patch of type `empty` or `wedge` | **none.** `wing` 24,960 faces · `inout` 24,960 · `sym` 8,704, each `ok (non-closed singly connected)` |
| full patch list recorded per level | recorded above; `wing` at **24,960 faces is exactly §2.5's registered L2 surface-face count** |

**⚠ THE DIRECTIONS LINE WAS CHECKED ON THE `geometric` LINE, NOT THE `solution` LINE.** The lane's
report quoted *"Mesh has 3 solution (non-empty) directions"*. §3.2 registers the **geometric** line by
name, and the two are different checks — this is heat-transfer's wedge trap, where a wedge mesh can
read 3 on one line and not the other. Both are present here and both read 3, so nothing turns on it
**on this mesh**; the distinction is recorded because the next reader must not learn the wrong habit
from a case where the wrong line happened to agree.

## THE TWO FAILED CHECKS, NAMED

`Failed 2 mesh checks.`

1. **`***Error in face tets: 586 faces with low quality or negative volume decomposition tets`** (set
   `lowQualityTetFaces`).
2. **`***Cells with small determinant (< 0.001) found, number of cells: 110979`** (set
   `underdeterminedCells`) — **13.895 % of 798,720.**

Also present, and a warning rather than a failure: `<<Writing 241 non-orthogonal faces to set
nonOrthoFaces`.

## WHY THE LEVEL IS USED ANYWAY — the record §3.2 demands

1. **L3 CARRIED THE SAME TWO FAILURES, WAS USED, AND WAS GRADED.** L3's small-determinant fraction is
   **18,471 / 99,840 = 18.501 %** against L2's **13.895 %** — **L2 is the BETTER of the two on the very
   metric that fails.** Refusing L2 on a criterion L3 was used under would be incoherent, and would
   quietly rewrite a disposition already made.
2. **THE FAILURE IS CHARACTERISTIC OF THE MESH TYPE, NOT OF A DEFECT IN THIS MESH.** Small cell
   determinants are the expected signature of the high-aspect-ratio cells a hyperbolic extrusion
   produces in a boundary layer — which is pyHyp's entire purpose. A family built by a frozen pyHyp
   generator that did **not** show this would be the surprising outcome.
3. **THE 586 FACE-TET FAILURES ARE A TET-DECOMPOSITION PROPERTY**, used by some interpolation paths,
   not by the finite-volume discretisation `DARhoSimpleCFoam` integrates. They are 586 faces against a
   mesh of 798,720 cells.
4. **THE FAILURES DO NOT POINT AT THE TRAILING EDGE.** Reproduced previously on three independent A3
   meshes and recorded on the board: the `-allGeometry` failures on this geometry are distributed, not
   TE-localised, so they are not the cusp pathology cfd hit on a different case.

## ⚠ THE ARGUMENT THAT DOES **NOT** HOLD, STATED BECAUSE IT IS THE ONE I WANTED TO MAKE

The tempting fifth reason is that a systematic mesh-quality characteristic is **common-mode across a
family built by one frozen generator**, and therefore largely cancels in a Richardson comparison. **It
does not hold here, and the measurement refutes it: the small-determinant fraction is 18.501 % at L3
and 13.895 % at L2 — it VARIES BY LEVEL, so it is not common-mode.** A level-varying mesh-quality
defect is precisely the kind that can contaminate an observed order of convergence, because it changes
with the refinement it is supposed to be orthogonal to.

**That residue is real and is not dismissed.** It does not change today's disposition — the A3GC triple
is already `NOT A RESULT` on L3's iterative convergence (see the item's §4.2 clause 1 and the
supervisor's ruling of 2026-09-12), so no observed order will be quoted from this family in any case.
**But if a successor family is registered, the level-to-level variation of `underdeterminedCells` is a
registered hazard it must address**, not a footnote it may inherit.

**SUBMISSIONS PARKED.**
