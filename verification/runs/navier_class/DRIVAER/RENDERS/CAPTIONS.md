# DRIVAER RENDERS — CAPTIONS. **USE THESE VERBATIM. A PICTURE TRAVELS FURTHER THAN A VERDICT.**

Produced under Sanaa's standing directive of 2026-09-12 (*"whenever a run completes, i want
the paraview visualization of its mesh saved"*) by `scripts/render_on_completion.sh`, which
refuses any case that is not complete. **No solver time was spent and no graded tree was
touched** — the renderer proves the latter by census hash and says so in its own output.

---

## `r2_coarse_R2_mesh_surface.png`

> **DrivAer notchback — surface mesh, COARSE level (186,709 cells), non-blended control arm.**
> 17,780 rendered faces across 44 vehicle patches, per-patch identity verified against the
> case's own `constant/polyMesh/boundary`.
> **This is the COARSE mesh and the coarse solution is NOT converged** — a coherent limit
> cycle, period ≈ 33 iterations, excursion 3.30× the plateau tolerance and not decaying.
> **No drag coefficient is quoted on this image.** The run's `Cd` is **`NOT A RESULT`** on two
> independent bars: the pre-registered **Y1 mixed-wall-treatment cap** (16.3 % of boundary
> faces carry no usable layer) and the **unconverged solution**.

## `r2c_coarse_blended_R2_mesh_surface.png`

> **DrivAer notchback — surface mesh, COARSE level, blended wall-treatment arm**
> (`nutUSpaldingWallFunction` on the 47 vehicle patches; **identical mesh** to the control,
> one line of difference). 17,780 rendered faces, per-patch identity verified.
> **Same two caveats as the control, unchanged by the wall-treatment swap:** the `Cd` is
> **`NOT A RESULT`**, and gate B2 measured the swap as **`INACTIVE`** — it moved `Cd` by 0.87
> drag counts against a body ripple of ~59 counts, because the whole body sits above the
> y⁺ ≈ 30 crossover where the two wall functions coincide.

---

## 🔴 WHAT MUST NOT BE PUT ON EITHER IMAGE

- **No `Cd` as a validated number.** Both caveats travel with any number that appears at all.
- **No claim of a converged solution.**
- **No claim of validation.** DrivAerML is a **CODE** reference (rank 2), not experiment.

## WHAT IS OWED

- **Sanaa's rule is "coarse mesh, or MEDIUM if the coarse isn't converged". The coarse is not
  converged, so the medium mesh render is owed the moment `r2c_medium_blended_R2` completes**
  (it was mid-run at 764/2000 when these were made). `render_on_completion.sh` produces it
  with the same call and **refuses until the run is actually complete** — proven: it returned
  `REFUSED: carries no rc sidecar` against that very case while it was running.
- **No FIELD render is claimed.** `--field` is a measured silent no-op; see
  `_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md`. Her clause *"all fields should be stored as the
  fine mesh result fields (whenever we have it)"* does not bind yet — **there is no fine
  DrivAer mesh on this box.**

---

# ADDENDUM — 2026-09-12 — **THE OWED MEDIUM RENDER LANDED.** Appended by a cfd `lab-lane`;
nothing above this line is altered.

## `r2c_medium_blended_R2_mesh_surface.png`

> **DrivAer notchback — surface mesh, MEDIUM level (983,106 cells), blended wall-treatment
> arm (`nutUSpaldingWallFunction` on the vehicle patches).**
> **64,228 rendered faces across 44 vehicle patches**, per-patch identity verified against the
> case's own `constant/polyMesh/boundary`; renderer guard **PASS**, graded tree untouched,
> 3-D dimensionality confirmed from `checkMesh` geometric directions.
> **This is the MEDIUM mesh, and that is Sanaa's rule applied, not a substitution:** her
> directive is *"the coarse mesh (or medium mesh if the coarse isnt converged)"*, and the
> coarse level is **not** converged. **No `Cd` is quoted on this image.** The run's `Cd`
> (0.315107) is **`NOT A RESULT`**, and even were the disclosed instrument conflict ruled in
> its favour it would be a **MIXED-WALL-TREATMENT `Cd`** — 16 patches under one prismatic
> layer over **19.65 % of the wetted area** — never a `Cd` on a fully layered body.

### 🔴 THE FACE-COUNT GUARD, DISCHARGED ON THIS IMAGE AND NOT ASSUMED

This lab has previously rendered a car from **3.6 % of itself**. The guard is therefore
checked against arithmetic done independently of the renderer, not taken on the renderer's
word:

| quantity | faces | source |
|---|---:|---|
| layered vehicle patches, medium | 52,489 | `r2_medium/R2_MEASURED.json` |
| unlayered vehicle patches, medium | 12,106 | same |
| all 47 vehicle patches | **64,595** | sum |
| less the three `CTRL_SURFACE_*` patches the selector excludes (235 + 66 + 66) | −367 | `polyMesh/boundary` |
| **expected in the render** | **64,228** | |
| **rendered** | **64,228** | renderer's own count |

**EXACT MATCH. The geometry in the image is the whole body.** Confirmed by eye as well:
body, roof, notchback trunk and C-pillar, both wheel pairs with rims and arches, mirrors,
front fascia and underbody edge all present.

### WHAT IS STILL NOT CLAIMED, UNCHANGED FROM THE HEAD OF THIS FILE

- **No FIELD render.** `--field` remains a measured silent no-op (`_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md`).
- **Her clause *"all fields should be stored as the fine mesh result fields (whenever we have
  it)"* does not bind on DrivAer and now never will**: Sanaa's ~21:00Z ruling caps this family
  at medium with **no fine mesh**. The finest completed level available for this family **is
  the medium**, and it is the level rendered here. Said plainly so no reader infers a missing
  fine-mesh render that was never owed.

---

# ADDENDUM 2 — 2026-09-12 — **ALL THREE IMAGES ABOVE WERE SILENTLY COLOURED BY A SCALAR FIELD WHILE CAPTIONED AS MESHES. RE-RENDERED. AND `--field` WAS NEVER BROKEN.**

Appended, not inserted: **lines whose number changed above this section: 0.**

## A2.1 THE DEFECT RECORD AT `_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md` IS WRONG IN BOTH DIRECTIONS

Measured with `pvbatch`: **immediately after `Show()` and BEFORE any `ColorBy` call,
`d.ColorArrayName` already reads `['POINTS', 'p']`.** ParaView auto-colours by the first
array it finds. Therefore:

1. **`--field` works and always did.** Colouring by `T` instead of `p` moves **7.07 %** of
   frame pixels on a control case; `p` versus a genuinely solid surface moves **6.47 %**.
2. **DEFECT.md's own evidence is explained by this, not by a broken flag.** It compared
   `--field p` against "the plain mesh render" and found them identical — **because the
   plain mesh render was already `p`.** The comparison had no uncoloured arm, so it could
   not have shown a difference whatever the tool did. **The control was not a control.**
3. **The real defect was the half nobody was looking at.** The three images above were
   rendered *without* `--field` and therefore carried an **unlabelled scalar field as their
   surface colour, with no colour bar, under captions calling them mesh renders.** The
   orange body in the earlier `r2_coarse_R2` and `r2c_coarse_blended_R2` images was a field,
   not a surface colour.

**A wrong artifact on disk is worse than a missing one: a missing one announces itself and
a wrong one does not.** All three are re-rendered with ParaView's auto-colouring explicitly
disabled (`25caef4c6`), and are now genuine neutral-grey surfaces with black cell edges.

**The geometry did not change and the guard proves it:** 17,780 / 17,780 / 64,228 faces —
identical to the counts the superseded images carried.

## A2.2 THE FIELD RENDER — HER SECOND CLAUSE, NOW ACTUALLY SATISFIED

Sanaa, ~20:30Z: *"all fields should be stored as the fine mesh result fields (whenever we
have it)."* The head of this file recorded that clause as not binding. **It binds, and it is
now met**, with the level chosen by her own rule:

> **`r2c_medium_blended_R2_field_p_surface.png` — DrivAer notchback, surface KINEMATIC
> pressure, from the MEDIUM level (983,106 cells), 44 vehicle patches, 64,228 faces.**
> `p` on its **CELLS** association, rescaled to range, **with a scalar bar carrying the
> field name and its numbers.** Planted colour control **PASSED at 84.81 %** of body pixels
> moved.
> **UNITS, AND THEY ARE NOT WHAT A READER WILL ASSUME.** `simpleFoam` is incompressible, so
> `p` here is **KINEMATIC pressure in m²/s² — NOT pascals.** Read from the field file's own
> header: `dimensions [0 2 -2 0 0 0 0]`. (The M6I field render beside this family is a
> *compressible* solve, `dimensions [1 -1 -2 ...]`, and its bar genuinely is Pa. Two field
> renders, two different quantities, both called "p".)
> Range **[−3776.6, +809.0] m²/s²**. Against this case's own dynamic pressure
> `q = ½U∞² = 756.2 m²/s²` that is **+1.070 q at the maximum and −4.994 q at the minimum**.
> **The medium IS the finest completed level for this family** — Sanaa's ~21:00Z ruling caps
> DrivAer at coarse + medium with **no fine mesh**, so there is no finer level to wait for
> and this is the final field render for the family, not an interim one.
> 🔴 **EVERY CAVEAT AT THE HEAD OF THIS FILE APPLIES, AND HARDER TO A FIELD PICTURE.** The
> `Cd` is **`NOT A RESULT`**; the wall treatment is **MIXED** — 16 patches under one
> prismatic layer over **19.65 % of the wetted area**; and the mesh is **non-conforming**
> (max skewness 5.450 against a 4.0 standard). **A pressure picture of that body is not a
> validated surface pressure field and must never be captioned as one.**

**TWO THINGS THE IMAGE ITSELF SAYS, BOTH AGAINST THE RUN.**

1. **`Cp_max` = +1.070, AND FOR INCOMPRESSIBLE FLOW THAT IS PHYSICALLY IMPOSSIBLE.** The
   stagnation point is the maximum of `Cp` and it is exactly **1.0**; anything above it is a
   **discretisation overshoot**, here **7 %**. Reported as a diagnostic observation of a
   coarse wall-function RANS, **not** as a result and **not** gated — no band for it is
   registered anywhere in this family.
2. **THE COLOURMAP IS STRETCHED BY ONE OUTLIER AND THE BODY THEREFORE READS NEARLY FLAT.**
   The linear map spans the full **−3776.6 → +809.0**, while almost the whole body sits
   within a few hundred of zero, so the car renders in one narrow band of the scale. **That
   is a LEGIBILITY limit of a full-range linear map over a field with a −5 q spike — it is
   not a uniform pressure field, and must not be read as one.** The scale is left at the
   true data range deliberately: clipping it to a percentile would make a prettier picture
   by hiding the spike, and the spike is the interesting part — it sits on the unlayered
   wheel/arch group that Gate Y2 already caps.

**AND THIS RETROSPECTIVELY EXPLAINS `DEFECT.md`'s OWN MEASUREMENT.** Its hue histogram found
the `--field p` image carrying **one dominant bin of twelve** and read that as "not
coloured". It was coloured — by an **outlier-stretched colormap that compresses the body
into one band.** **The histogram was measuring something real and pointing at the wrong
cause**, which is the same shape as its headline conclusion.

## A2.3 THE REPAIR'S CONTROLS — because a colour claim needs one, and the last attempt was withdrawn for lacking it

| behaviour | result |
|---|---|
| no `--field` | **solid neutral surface**; auto-colouring explicitly disabled |
| `--field p` | CELLS, rescaled, **scalar bar shown** |
| `--field alphat` (range 0, 0) | **REFUSED, exit 2** — a constant field paints one flat colour that reads as a field picture and shows nothing |
| `--field U` on a no-slip wall | **REFUSED, exit 2, and the message says this is CORRECT PHYSICS** — the tool renders boundary patches, `U` on a no-slip wall is exactly zero by boundary condition, and the volume field is not |
| `--field NoSuchField__` | **REFUSED, exit 2**, listing the arrays present |
| **planted colour control** | collapse the colour map to one value, re-render, **read the PNG back off disk**. Varying fields move **96.17 % / 96.58 %** of body pixels; a CONSTANT field moves **0.00 %** — a demonstrated failing case. Floor **10 %**. |
| 12-limb geometry selftest | **12/12**, unchanged |

**A guard that does not discriminate was measured and rejected before shipping:** "does the
field render differ from a solid render" **fails**, because a constant field differs from
solid by **96.24 %** — a constant maps to one *end* of the colormap, nowhere near grey.

## A2.4 THE SUPERSEDED IMAGES ARE KEPT, NOT DELETED

The two auto-coloured `--field p` renders from the original investigation stay in
`_FIELD_FLAG_DEFECT_EVIDENCE/` as the evidence for what the defect looked like. **DEFECT.md
itself is left standing and is corrected by this addendum, not rewritten** — its measurements
were sound and only its conclusion was wrong, which is worth preserving as an example of a
correct number pointing at a wrong cause.

*Appended by a cfd `lab-lane`, 2026-09-12. No solver launched. Alters no gate, threshold,
cap or label. Submissions parked.*

---

# ADDENDUM 3 — 2026-09-12 — **THE FIELD RENDER IN ADDENDUM 2 WAS ITERATION 1750, NOT 2000. `--time` WAS A DECLARED ARGUMENT THAT WAS NEVER READ.**

Appended, not inserted: **lines whose number changed above this section: 0.**

## A3.1 THE DEFECT

`grep -n "a\.time"` in `scripts/render_openfoam_3d_paraview.py` returned **nothing**.
`--time` was declared, documented, passed by every caller, and **never consulted**;
ParaView's OpenFOAM reader used its own default.

**MEASURED, NOT INFERRED.** This case holds times `0 / 1750 / 2000` and the reader lists
`[1750.0, 2000.0]`. The image filed under ADDENDUM 2 reported `p` ∈ [−3776.5985, 809.0353].
Read off disk: **`1750/p` is EXACTLY that**, and `2000/p` is [−3777.3351, 809.5600].

> **THE FIELD IMAGE SHIPPED IN `40eff4e18`, CAPTIONED "the finest completed level", WAS
> ITERATION 1750 OF A RUN WHOSE GRADED `endTime` IS 2000.** It is re-rendered at 2000, and
> this addendum records the error rather than silently replacing the file.

**The three MESH renders are unaffected — geometry does not change with time**, and their
face counts (17,780 / 17,780 / 64,228) are unchanged again.

## A3.2 THE CORRECTED IMAGE, AND IT NOW STATES ITS OWN UNITS

> **`r2c_medium_blended_R2_field_p_surface.png` — DrivAer notchback, surface KINEMATIC
> pressure, MEDIUM level, 44 vehicle patches, 64,228 faces, at `time 2000`.**
> Renderer output, verbatim: `time 2000 loaded (available: [1750.0, 2000.0])` and
> `field 'p' coloured by CELLS association, range [-3777.34, 809.56] m^2/s^2 (KINEMATIC -- not Pa)`.
> Planted colour control **PASSED at 84.48 %** of body pixels moved.
> **THE UNIT ON THE BAR IS DERIVED FROM THE FIELD FILE'S OWN `dimensions` HEADER
> (`[0 2 -2 0 0 0 0]`), NEVER FROM THE FIELD'S NAME.** The M6I field render in the adjacent
> campaign is a *compressible* solve, `dimensions [1 -1 -2 ...]`, and its bar genuinely reads
> **Pa**. Two field renders, two different physical quantities, one one-letter name — and
> the artifact now says which it is instead of leaving the reader to supply a unit.
> Every caveat in ADDENDUM 2 stands unchanged: `Cd` **`NOT A RESULT`**, **MIXED** wall
> treatment over 19.65 % of wetted area, mesh **non-conforming**.

## A3.3 THE THIRD REPAIR, WHICH MATTERS MOST FOR EVERY OTHER TEAM

The staging directory was a **fixed** `<out>/_stage`. Two lanes rendering into one `RENDERS/`
— which is what every team does — staged into the **same path**. Measured when two of this
lane's own checks shared an `--out`: *"per-patch identity failed for 43 of 44 patches"*.

**The guard caught it, which is the only reason it was a nuisance and not a wrong picture.
But a tool that needs its guard to survive normal concurrent use is relying on the guard for
CORRECTNESS instead of for VERIFICATION** — a guard doing routine work has already spent the
margin it was meant to hold in reserve. Now `_stage_<pid>`.

## A3.4 THE HONEST TALLY ON THIS ONE TOOL, IN ONE NIGHT

1. a per-patch face-count guard that passed an image **with no wing in it**;
2. `Show()` auto-colouring, shipping **unlabelled scalar fields captioned as meshes**;
3. a "control" that compared `--field p` against a default that **was already `p`**;
4. `--field` declared broken **while working**;
5. **`--time` declared and never read** — two of these are the same mechanical class, with
   `--min-ink` before them;
6. a stage name that **collides under normal concurrent use**.

**That is not bad luck. It is a tool that had never been read adversarially.** Recorded here
because the next person to trust one of its outputs should know what its history is.

*Appended by a cfd `lab-lane`, 2026-09-12. No solver launched. Alters no gate, threshold,
cap or label. Submissions parked.*
