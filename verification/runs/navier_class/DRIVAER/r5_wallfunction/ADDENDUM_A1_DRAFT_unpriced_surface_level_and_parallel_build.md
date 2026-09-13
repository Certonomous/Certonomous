# ADDENDUM A1 — DATED DISCLOSURE — 2026-09-13

**DRAFT, HANDED TO cfd-supervisor FOR LANDING. NOT APPLIED BY THIS LANE.**
This lane's brief forbids it editing frozen files (CLAUDE.md rule 6), so the
text below is delivered as a file under the run directory it concerns and is
**not** appended to the registration by its author. Landing it is the
supervisor's act.

**Target document:** `verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md`
**Frozen at:** `38aab8e78662d574d1b14b61da7efc5898be5c7e`
**Blob at freeze and at HEAD when this was drafted:** `8f0083d195d8bf03c1afa8f87e683c4b4d5a8fcc` (identical)
**Target document length at drafting:** 438 lines.

**On landing, this section is appended AT THE FOOT and the lander asserts:
`lines whose number changed above this section: 0`, verified by
`cmp -n <original byte length>` between the pre- and post-append files.**

---

## WHAT THIS ADDENDUM DOES AND DOES NOT DO

**It alters NO gate, NO threshold, NO cap and NO label.** L1 stays at ≥ 5.0 of
8 on vehicle patches. L2 stays at ≥ 90 %. M1 stays at 15–20 M. S1 stays at
4.0. P1–P4 stand exactly as frozen. First compute against R5 began at
2026-09-13T18:05:35Z, so the gates are closed and nothing here reopens them.

**What it discloses is an UNPRICED CONDITION** — a fact about the mesh the
registration builds on that the registration did not account for, found before
the graded mesh existed and recorded so that the P1 reading is not quoted as
something it is not.

---

## A1.1 — THIRTEEN VEHICLE PATCHES ARE ALREADY AT SURFACE LEVEL 5 = 12.5 mm

The dictionary R5 inherits — `r2_medium/system/snappyHexMeshDict`, whose
`refinementSurfaces` block R5 leaves **byte-identical** — sets thirteen vehicle
patches to `level (5 5)`:

`BodyDoorhandles`, `BodyHeadlamps`, `BodyRocker`, `ClosedGrillLowerInsert`,
`ClosedGrillUpperInsert`, `ExhaustSystem1`, `ExhaustSystem2`, `ExhaustSystem3`,
`Mirrors1`, `Mirrors2`, `TirePlinthfront`, `TirePlinthrear`.

At the R5 background of `h0 = 0.4 m`, level 5 is a **12.5 mm** surface cell.

**On a 12.5 mm cell the registered 11.859 mm stack is 0.949 local cells —
double the 0.48 ceiling §4.2 itself declares necessary for extrusion.**

The affected population is **10,162 of 64,595 vehicle faces = 15.7 %**
(face counts measured from `r2_medium`'s own post-extrusion table via
`cases/navier_class/DRIVAER/mesh/analyse_layers.py`; the remaining 54,433
faces = 84.3 % are at level 4 = 25.0 mm, where the stack is 0.474 c and the
§4.2 constraint is satisfied).

**§4.2 resolved "do not refine the surface further" and did not notice that
part of the surface is already refined.** That is the honest description of how
the gap got there: **a constraint written against the intended mesh rather than
against the actual dictionary.** It is the same shape as the PRISM-A2 defect
one case over.

## A1.2 — WHY THIS CHANGES HOW P1 MUST BE READ, WITHOUT CHANGING P1

If the 84.3 % at 25 mm reach ~6 layers and the 15.7 % at 12.5 mm reach ~0, the
face-weighted result is

    (6 × 54,433 + 0 × 10,162) / 64,595 = 5.06

against a threshold of **5.0**. **P1 would be decided at the third significant
figure by a condition the registration never priced.**

**A gate decided in its third digit by an unpriced condition is not a gate
anybody should quote. A P1 PASS near 5.0 is therefore UNINFORMATIVE and must
not be reported as evidence that the mechanism of §2.2 was confirmed.**

**THE RESULT IS THE TWO POPULATIONS REPORTED SEPARATELY, EACH WITH ITS FACE
COUNT — coverage on the 54,433 faces at 25 mm, and coverage on the 10,162
faces at 12.5 mm. The blended figure is an artefact of mixing two different
geometric situations and is reported only because the frozen gate is defined
on it.**

## A1.3 — THE BUILD IS PARALLEL WHERE THE FAMILY WAS SERIAL

R5 is built with `mpirun -np 16 snappyHexMesh -parallel`. Every graded mesh in
the R1/R2 family was built **serial**. This is not registered either way.

**It is a live confound on exactly the quantity P1 measures:** parallel snappy
can move layer insertion at processor boundaries, and this act has already
observed parallel snappy rebalance at every feature iteration. Recorded in
`r5_wallfunction/RUN_PIN.txt` and here.

## A1.4 — TWO BUILD CONDITIONS, ONE OF WHICH WOULD HAVE DEFEATED M1

1. **`maxLocalCells` was 6,000,000.** In a serial build that is the binding
   cap and it makes the registered 15–20 M gate **unreachable**. Raised to
   40,000,000 to match `maxGlobalCells`. Disclosed as an enabling limit, not a
   physics change.

2. **The first sizing model was wrong and a castellation-only probe refuted
   it.** `R5_SIZING_PROBE` (castellation only, 16 ranks) returned
   **12,541,747 cells** against a 12.96 M estimate — 3.3 % high, tolerable —
   but it killed the layer-gain assumption. The original sizing carried
   `r2_medium`'s **+31 %** layer gain. Measured on that level's own log,
   **snapping adds ZERO cells (748,658 → 748,658 — it moves points, it does
   not add cells)**, and R5's **surface** refinement is identical to medium's,
   so its wall-face count is too (~80,974 extrudable faces). Layers therefore
   add `faces × extruded_fraction × 8 ≈ 0.58 M` cells — **+4.7 %, not +31 %**.
   The final mesh would have landed at **~13.1 M and MISSED M1 LOW**. The
   volume-refinement box was rescaled from the measured point rather than the
   assumed one; predicted final ~16.9 M.

   **The volume-refinement geometry is authored by the building lane.** The
   registration sets the 15–20 M gate and mandates that the cells come from
   volume refinement, but specifies no geometry. The boxes are recorded in
   `cases/navier_class/DRIVAER/mesh/make_r5_dict.py` and the emitted dict's
   sha256 is pinned in `r5_wallfunction/RUN_PIN.txt`.

## A1.5 — WHAT THE SURFACE LEVELS DID NOT DO

**They did not move.** `refinementSurfaces`, `features`, `snapControls` and
`meshQualityControls` are asserted **byte-identical** to `r2_medium`'s by
`make_r5_dict.py`, which exits 2 if any of them differs. §4.2 forbids touching
surface refinement, and **an arm that changes the mesh *and* the layer spec
measures neither.**

---

*Drafted by a cfd `lab-lane`, 2026-09-13, at the direction of the drafting
lane, for the cfd-supervisor to land. Alters no gate, threshold, cap or label.
Contains no submission and no external communication. Nothing leaves the box.*
