# DEFECT — `render_openfoam_3d_paraview.py --field` IS A SILENT NO-OP ON THIS CASE

**These two PNGs are NOT field renders. They are duplicate MESH renders produced by a run
that was asked for `--field p` and silently ignored it.** They are kept as the evidence,
in a clearly-named directory, rather than deleted or left among the deliverables.

**MEASURED, NOT EYEBALLED.** The `--field p` output and the plain mesh output were compared
by hue histogram over body pixels (background `(82,87,110)` excluded, saturated pixels only,
12 bins):

```
mesh render : [6844, 4, 5, 0, 5, 0, 0, 22, 19, 0, 1, 5]   -> 1 of 12 bins carries >2 %
--field p   : [6844, 4, 5, 0, 5, 0, 0, 22, 19, 0, 1, 5]   -> 1 of 12 bins carries >2 %
```

**Identical, and both carry a SINGLE hue** — the default orange surface colour with lighting
shading. A pressure field on a blue-to-red colormap spreads across the range. The md5s differ
(`34feb8ce…` vs `89c5a572…`) so the files are not byte-identical, which is why a hash check
would NOT have caught this and a hue measurement did.

**CAUSE, READ FROM THE SCRIPT:** `scripts/render_openfoam_3d_paraview.py:588-590` does
`ColorBy(d, ("POINTS", a.field))`. OpenFOAM writes `p` as a **CELL** field; if the reader
does not expose a POINTS array of that name, `ColorBy` leaves the default solid colour and
**raises nothing**.

🔴 **WHY THE FILE'S OWN GUARD DID NOT CATCH IT, AND THIS IS NOT A CRITICISM OF THE GUARD.**
The guard asserts a **per-patch face-count identity** — `rendered[p] == nFaces[p]` — and it
did its job: `17780 faces, guard PASS`. **Colouring is not a geometry property, so a
face-count identity is blind to it by construction.** The script's own header says the guard
exists because *"a renderer that draws a decimated, clipped or WRONG case still produces a
confident-looking picture"*; this is the same class of failure in the one dimension that
guard does not cover.

**CONSEQUENCE FOR THE STANDING RENDER DIRECTIVE:** the **mesh** render path is verified and
is what is delivered. **No field render is claimed for DrivAer until this is fixed**, because
a picture captioned "surface pressure" that is actually a flat-shaded body is exactly the kind
of confident-looking wrong artifact the guard was written to prevent.

**SUGGESTED FIX, not applied here** (the script is shared tooling and this lane did not edit
it mid-directive): try `CELLS` before `POINTS`, or run `CellDatatoPointData`, and **assert the
array exists and that the rendered image carries more than one hue bin** — a colouring guard
to sit beside the geometry guard.

*Recorded by a cfd `lab-lane`, 2026-09-12.*
