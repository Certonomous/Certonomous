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
