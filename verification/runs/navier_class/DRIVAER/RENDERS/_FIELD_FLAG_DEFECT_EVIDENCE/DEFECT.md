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

---

## ADDENDUM — 2026-09-12 — **TWO FIX ATTEMPTS, BOTH FAILED, AND THE FIRST DIAGNOSIS WAS WRONG**

**`lines whose number changed above this section: 0.**

### The first diagnosis was WRONG

The section above blames `ColorBy(d, ("POINTS", field))` against a field OpenFOAM writes on
**CELLS**. **That is not the cause.** Probed directly on the rendered surface:

```
POINTS present: ['k', 'nut', 'omega', 'p', 'U']
CELLS  present: ['k', 'nut', 'omega', 'p', 'U']
```

**`p` is present on BOTH associations.** The original code was already colouring by an array
that exists.

### Attempt 1 — association repair. **DID NOT WORK.**

A repair was applied that selects `POINTS` or `CELLS` by probing which carries the array. It
reported `field 'p' coloured by POINTS association` and **still rendered flat**, measured:

| | mesh render | `--field p` render |
|---|---|---|
| body RGB mean | [121.9, 69.8, 53.0] | **[121.9, 69.8, 53.0]** |
| body RGB std | [58.5, 34.2, 25.9] | **[58.5, 34.2, 25.9]** |
| body pixels differing by >30 | — | **39 of 256,226 (0.015 %)** |

**Identical. The cause remains UNIDENTIFIED and is not claimed to be fixed.**

### Attempt 2 — a colouring guard. **REMOVED, BECAUSE IT COULD NOT BE SHOWN ABLE TO FAIL.**

A guard was added asserting the saved image carries hue variation when `--field` is requested.
**It passed the known-flat render.** Measured: the flat `--field p` image scores **0.062752** on
the hue-std statistic — **and so does the plain mesh render, 0.062752.** A flat orange body plus
black cell edges and the axes widget already spreads hue that far. **The threshold guessed
(0.06) sat BELOW the failing case, so the guard passed the exact artifact it was written to
catch.**

🔴 **AND IT CANNOT BE CALIBRATED YET.** A discriminating threshold needs a **known-good coloured
render as a positive control**, and none can exist while this path is broken. **A guard that
cannot be shown able to FAIL is not a guard**, so it was **removed rather than shipped** —
shipping it would have advertised a protection that does not exist, which is worse than no
guard at all.

### What WAS kept, and it is proven

**An ABSENT-FIELD REFUSAL.** `--field NoSuchField__` now exits 2 with the arrays it did find,
instead of silently drawing a flat body. **Driven as a negative control and shown to refuse.**
The 12-limb geometry selftest still passes **12/12** after both edits, including the swap and
decimation controls.

### Also added: `--zoom` (camera only)

`--zoom` defaults to **1.0, which reproduces the previous framing exactly**, so no existing
render changes. Lower values move the camera closer for long thin bodies. CRM wing-alone reads
ink **0.0546 at 1.0** and **0.0621 at 0.45**. **Camera only — no data touched, guard unaffected.**

**STILL OWED: the actual cause of the `--field` no-op.** Until it is found and a positive
control exists, **no field render is claimed by any cfd deliverable.**
