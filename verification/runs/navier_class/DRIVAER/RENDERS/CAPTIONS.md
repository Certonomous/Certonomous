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
