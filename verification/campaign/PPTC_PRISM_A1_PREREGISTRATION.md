# PPTC VP1304 — PRISM-LAYER DEFECT, RUNG PRISM-A1 PRE-REGISTRATION

Case family: PPTC VP1304 open water (`cases/PPTC_VP1304/`).
Scope: the prism-layer defect ONLY. No solver is run. No queue entry is armed.
Frozen: 2026-09-13, BEFORE any compute for this rung. The run directory named in
§5 does not exist at the moment of this commit; that is how the freeze is checked.

---

## 1. THE DEFECT BEING EXPLAINED

`snappyHexMesh` on the PPTC meshes reports, with `rc=0`:

    Extruding 0 out of 724711 faces (0%). Removed extrusion at 0 faces.
    Added 0 out of 4348266 cells (0%).
      -- /home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse/log.snappyHexMesh:3314-3315

and the same on the 72-degree sector at 76,465 faces
(`.../L1_prod7s/log.snappyHexMesh.layersBladesOnly:483-484`).
Zero prism layers, reported as success.

## 2. THE CAUSE THIS RUNG TESTS (ruled in from the log, the dictionaries and the
   OpenFOAM-2606 source, before this run)

`addLayersControls { relativeSizes true; }` makes every layer thickness a
multiple of `edgeLen = level0EdgeLength()/2^pointLevel`
(`snappyLayerDriver.C:1564-1567`, `:1622-1625` — exactly four fields are scaled:
firstLayerThickness, finalLayerThickness, thickness, minThickness).

`hexRef8::getLevel0EdgeLength()` returns the **global minimum** level-0 edge in
the mesh, not a representative one — `typEdgeLenSqr[eLevel] = min(...)`, with the
source comment *"Note minimum so if cells are not cubic we use the smallest edge
side"* (`dynamicMesh/lnInclude/hexRef8.C`).

In this mesh that global minimum is the azimuthal chord of the level-0 cell on
the r = 2 mm axis rod:  2 · 0.002 · sin(pi/60) = **2.09343825e-04 m**,
which is `constant/polyMesh/level0Edge` = **2.0934383e-04** to eight figures.

The blade surface cell is **6.25e-04 m** (`log.makeSnappy:3`, "blades level 5 ->
surface cell 0.6250 mm", from a 20.00 mm near-field background). snappy's model
of that same cell is 2.0934383e-04/2^5 = 6.5420e-06 m — **95.54x too small**.

Predicted consequence, already observed: first layer 1.79e-06 m instead of
1.2559e-04 m; the resulting prisms give 5,613,625 faces with pyramid volume below
`minVol 1e-13` (73.2% of the 7,674,028 illegal faces at layer iteration 0,
`log.snappyHexMesh:3170-3180` sum), `checkAndUnmark` removes the extrusion, and
iteration 1 finds nothing to extrude.

## 3. THE SINGLE REGISTERED CHANGE

**The layer sizing basis moves from relative to absolute. Nothing else moves.**

    relativeSizes   false;                 // was true
    finalLayerThickness 3.125e-4;          // metres = 0.5  x 0.625 mm (was 0.5 relative)
    minThickness        3.125e-5;          // metres = 0.05 x 0.625 mm (was 0.05 relative)
    expansionRatio      1.2;               // UNCHANGED
    nSurfaceLayers      6;                 // UNCHANGED

The registered layer specification of the pre-registration §6.3 — six layers at
growth ratio 1.2, final layer half the local surface cell, minimum five percent
of it — is preserved exactly; only the unit changes, from multiples of a length
snappy computes wrongly to metres.

`minThickness` MUST be converted in the same edit: left at `0.05` under
`relativeSizes false` it means 0.05 **metres** = 50 mm and would refuse every
layer in the mesh. It is one change with coupled numbers, not two changes.

## 4. PREDICTIONS, REGISTERED BEFORE THE RUN

Run: `snappyHexMesh -overwrite` with `castellatedMesh false; snap false;
addLayers true;` on a COPY of the existing L1_prod7s snapped mesh, blades only,
dictionary otherwise byte-identical to the one that produced the zero.

| id | quantity | instrument | threshold | verdict if met |
|---|---|---|---|---|
| P1 | blades near-wall thickness in snappy's own request table | the log's `avg thickness[m]` table | **>= 1.00e-04 m** (now 1.79e-06) | the length-scale collapse is cured |
| P2 | final `Extruding A out of B faces` after the last `Outer iteration` | `read_layer_achievement.py` | **A/B > 25%** (now 0%) | the collapse was the DOMINANT cause |
| P3 | presence of the achievement table (`Mesh with layers :` + `target mesh [m] [%]`) | `read_layer_achievement.py`, route == `table` | present | layers were actually added |

- **P1 met and P2 met** -> `GATE REACHED`: one registered change is sufficient
  to obtain prism layers, and the rung proceeds to the 360-degree mesh.
- **P1 met and P2 NOT met** -> `GATE FAIL` on P2, and the honest reading is that
  the length scale is necessary but not sufficient; the remaining illegal-face
  population (hub/blade-root snapping, 316 negative-volume cells) becomes a
  SECOND registered change and this becomes a ladder. That decision is the
  supervisor's, not this lane's.
- **P1 NOT met** -> the cause in §2 is refuted and this rung is `NOT A RESULT`
  for the purpose of the fix; the analysis is reopened.

P2's 25% floor is deliberately conservative: the base mesh carries 18,408 illegal
faces before any layer (`log.snappyHexMesh.layersBladesOnly:507`) and those will
suppress extrusion locally whatever the thickness. A result between 0% and 25% is
a GATE FAIL that still refutes nothing about §2 and will be reported as such.

## 5. COST, AND THE RUN DIRECTORY THAT DOES NOT YET EXIST

Run directory: `/home/ubuntu/certonomous-runs/PPTC_VP1304/PRISM_A1_absthick`
— **it does not exist at this commit.** That is the freeze check.

| item | basis | estimate |
|---|---|---|
| copy of the L1_prod7s case (2.5 GB) | I/O, 1 rank | 2 core-min |
| `snappyHexMesh -overwrite`, layers only, 1 rank | the same run at `relativeSizes true` took 438.91 s wall serial (`log.snappyHexMesh.layersBladesOnly:508`) | 8 core-min |
| **cap** | overrun STOPS the run (CLAUDE.md rule 12) | **20 core-min** |

Ranks: 1. Reserve used: 1 of the 16 allocated to PPTC. Rate for the derived
dollar figure: c7a.4xlarge at $0.0513/core-h, **reported-by-owner, not
measured** — the box cannot read its own billing. 20 core-min = 0.333 core-h
= **$0.017 derived**.

## 6. WHAT THIS RUNG MAY NOT DO

No solver. No queue entry. No edit to
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` or any other
frozen document. No change to `F360_coarse/`, which another lane holds.

---

## ADDENDUM 1 — 2026-09-13, AFTER first compute. TWO CITATION LINE NUMBERS CORRECTED. NO GATE, THRESHOLD, CAP OR LABEL IS ALTERED.

Version 1.1. Lines whose number changed above this section: 0.

Section 2 cited the layer-iteration-0 quality block as
`log.snappyHexMesh:3170-3180`. The correct range in
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse/log.snappyHexMesh`
is **3251-3259**, with the summing line `Detected 7674028 illegal faces` at
**3260** and `Extruding 0 out of 724711 faces (0%)` at **3261**. The struck
citation is left in place above, unedited; this is the correction.

The nine counts at 3251-3259 sum to exactly 7,674,028, which is the figure the
log prints at 3260 — so "illegal faces" there is the sum of the mesh-quality
block, not a separate narrower test. The dominant term, `faces with face pyramid
volume < 1e-13 : 5613625` at 3252, is 73.2% of it.

The rung's §5 cost cap of 20 core-min, the three thresholds of §4 and the labels
of §4 are untouched by this addendum.
