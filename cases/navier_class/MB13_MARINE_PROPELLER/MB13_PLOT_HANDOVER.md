# MB13 MARINE PROPELLER — PLOT-LANE HANDOVER

**Version 1.0 — 2026-09-14. Written by a `lab-lane` under `cfd-supervisor`, PREPARATION ONLY,
read-only on the live run.**

**Purpose.** A plot lane should be able to act on this file without reading the MB13 case from
scratch. Every path below is either **on disk now** (marked `EXISTS`) or is stated as **`WILL
APPEAR AT <path>`** with the condition that creates it. Nothing here is a verdict, and nothing
here authorises one.

**Governing registration (frozen, gates CLOSED after first compute):**
`cases/navier_class/MB13_MARINE_PROPELLER/MB13_PREREGISTRATION.md`
freeze `64195e9b`, addenda `cf67f8d7`, `524fef08`, `76595a22c` (Addendum B1).

**The run this handover describes:**
`/home/ubuntu/certonomous-runs/MB13_MARINE_PROPELLER/nref1_n32` — OpenFOAM **v2606**
(`_481094f-20260618`), 32 ranks, 4,073,817 cells.
Stage now: `rhoSimpleFoam` MRF steady precursor, `endTime 5000` iterations.
Then `system/replace.sh` hands off to `rhoPimpleFoam` LES, `endTime 2.5 s`, `deltaT 1e-4`,
**25,000 time steps**.

**Upstream licence.** The case, its `figures/` and its `README.md` are ESI-Group,
CC BY-SA 4.0 (`COPYING` in the run directory). Anything re-used from `figures/` carries that.

---

## 0. THE FOUR RULES THAT BIND THE PLOTS THEMSELVES — READ BEFORE RENDERING ANYTHING

1. **Demo images carry no caveats.** Sanaa's standing rule (2026-09-13): no stamps, no
   annotations, no watermarks, no "reference"/"preliminary"/"not validated" wording burned into
   a demo PNG. **Provenance goes in a sidecar file, never on the image.** Presentation is
   Sanaa's. Do not argue the point in the sidecar either.
2. **Every figure gets a sidecar** beside it, naming: the **source artifact path**, the
   **iteration or time window** used, and for every number on the figure whether it is
   **measured** (read from a solver artifact), **digitised** (read by eye off a published
   figure), or **derived** (computed from measured or digitised inputs).
3. **A plot of a quantity is not a verdict.** The gates below are graded by the registered
   comparators in `MB13_PREREGISTRATION.md` §3 through readers **R2** (force/moment) and **R3**
   (spectrum), each of which must pass **both** planted-zero limbs in the same invocation that
   produced the number. **Agreement seen on a plot is not `PASS`.** Never write `PASS`,
   `GATE FAIL` or `NOT A RESULT` into a figure, a filename or a sidecar.
4. **No plot may be made from a window that does not exist yet.** §6 states the minimum
   transient duration each figure needs. A figure drawn from a shorter record is not a
   preliminary version of the real figure; it is a different figure, and must not carry the
   real figure's name.

---

## 1. FORCE HISTORY — THRUST AND TORQUE

### 1.1 Where it lands

| | |
|---|---|
| Function-object name | **`forces_all`**, type `forces`, `libs ("libforces.so")` |
| Declared in | `system/forces` (the whole file is one FO block) |
| Included by | `system/controlDict.tr` line `#include "forces"` — **the TRANSIENT controlDict only** |
| Output directory | `postProcessing/forces_all/<startTime>/` — `<startTime>` is **`0`** for the transient |
| Files | **`force.dat`** and **`moment.dat`** |
| Write frequency | `writeControl timeStep; writeInterval 1` → **every time step, 25,000 rows** |
| Patches integrated | `propellerStem1` (480 faces), `propellerStem2` (5,528), `propellerTip` (49,940) — face counts from `log.checkMesh` |
| `rho` | `rho` — the live density field, so `force.dat` is in **newtons**, not m⁴/s² |
| `rhoInf` | `997` — **inert here.** It is used only when `rho` is the literal word `rhoInf` |
| `pRef` | `101325` Pa — **NOT inert.** See §1.4 |
| `CofR` | `(0 0 0)` — moments are about the origin, which is the propeller axis point |
| `pitchAxis` | `(0 1 0)` — an entry consumed by `forceCoeffs`, not by `forces`; it does not rotate these columns |

**Current status: `WILL APPEAR AT postProcessing/forces_all/0/force.dat` and
`.../moment.dat` when `rhoPimpleFoam` starts.** They do **not** exist now, and they will
**never** exist for the steady precursor — the live `system/controlDict` is a byte copy of
`system/controlDict.st`, which declares only `fieldMinMax` and `fieldAverage1` and does **not**
`#include "forces"`. **The case's published `figures/Force_history.png` and
`figures/Moment_history.png` cannot be reproduced from the MRF precursor at all.** Do not go
looking for a precursor force history; there is none.

### 1.2 The exact header, and the column mapping — RESOLVE BY HEADER NAME

`force.dat` opens with four `#` lines. The fourth is the column line. Verified by reading the
writer, not by pattern-matching a past file:
`/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/forces/forces.C:418-443`
(`writeIntegratedDataFileHeader`) and `:463-483` (`writeIntegratedDataFile`), with the
formatting primitives at
`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/db/functionObjects/writeFile/writeFileTemplates.C:44-56`.

```
# Force
# CofR              : (0 0 0)
#
# Time              	total_x total_y total_z	pressure_x pressure_y pressure_z	viscous_x viscous_y viscous_z
```

`moment.dat` is identical except the first line reads `# Moment`.

**Column mapping (1-based), for both files:**

| col | name | meaning |
|---|---|---|
| 1 | `Time` | s |
| 2 | `total_x` | total = pressure + viscous (+ porous, absent here) |
| 3 | **`total_y`** | **THE THRUST column in `force.dat`; THE TORQUE column in `moment.dat`** |
| 4 | `total_z` | |
| 5–7 | `pressure_x`, `pressure_y`, `pressure_z` | pressure contribution |
| 8–10 | `viscous_x`, `viscous_y`, `viscous_z` | viscous contribution |

**Resolve these by header name, not by position.** The writer emits the three groups
tab-separated, and inside each group the three names are space-separated; strip the leading
`#`, split the fourth header line on whitespace, and you get exactly ten names in column order.
Assert that the parsed name list equals the ten names above before reading a single data row,
and **refuse** if it does not. The data rows themselves are **space-separated bare scalars with
no parentheses** (`writeValue` writes `' ' << component` per component) — ten numeric fields per
row. **A porous contribution would add columns 11–13**; `porosity` is not set in `system/forces`,
so it is absent, but the name assertion catches it if that ever changes.

> **Why by name.** Earlier in this act a `coefficient.dat` header was read by position and
> `Cd(f)` / `Cd(r)` was taken for a pressure/viscous split when it is a **front/rear axle**
> split. A force column read by position is a silent error — it produces a plausible number
> from the wrong physics and nothing in the output says so. The shipped `plot_spectrum` script
> in the run directory reads `using 1:3` positionally; that happens to be correct here, and it
> is **not** a licence to copy the habit.

### 1.3 Which component is thrust, and why

- MRF/solid-body axis is **y**: `constant/MRFProperties` `axis (0 1 0)`,
  `constant/dynamicMeshDict` `axis (0 1 0)`, `omega 157.14 rad/s`.
- Inlet velocity is `(0 -5 0)` (`0.orig/U`, `Uinlet`), so the free stream runs in **−y** and the
  wake is downstream in **−y**.
- Therefore **`total_y` in `force.dat` is the axial thrust** and **`total_y` in `moment.dat` is
  the shaft torque about the rotation axis**. `total_x` and `total_z` are the side loads and
  should hover near zero on a four-bladed rotor once settled — a useful sanity trace, not a gate.
- **Derived, not measured:** shaft rate `n = 157.14 / 2π = 25.0097 rev/s`; one revolution is
  `0.039984 s = 399.8 time steps`; the 2.5 s transient is **62.5 revolutions**.

### 1.4 `pRef` is load-bearing — do not describe it as redundant

`system/forces` carries the comment `// Redundant for incompressible`. For **this** compressible
stack it is not redundant. `forces.C:721-731` computes the pressure force as
`rhoRef * Sf * (p - pRef)` with `rhoRef = 1` whenever `p` carries pressure dimensions
(`forces.C:337-341`). The three force patches are an **open** surface (blades plus stem, with
`propellerStem_outlet` excluded from the patch list), so a uniform pressure offset does **not**
cancel: without `pRef = 101325` the reported force would be dominated by ambient pressure times
projected area. If a figure ever needs to say what the reference is, the sidecar says
"gauge-referenced to 101,325 Pa" — the image says nothing.

### 1.5 An independent, published bound on the expected magnitudes

The shipped `plot_spectrum` gnuplot script (run directory root) sets, for the published nref=1
result, `set yrange [300:400]` on the Fy history and `set yrange [-30:-10]` on the My history.
That is a **published artifact of the case**, not an eye-digitisation, and it independently
brackets the registered centres. It is a **bound, not a value**: it does not replace the
digitised centres in §5 and it is not a gate. Note the **sign**: the published My axis is
negative, and the registered gate is on **|My|**.

---

## 2. PROBES AND ACOUSTICS

### 2.1 The probe signal — the only source of BPF

| | |
|---|---|
| FO name | **`probes_pGauge`**, type `probes`, `libs ("libsampling.so")` |
| Declared in | `system/controlDict.tr` — **TRANSIENT ONLY** |
| Field sampled | **`pGauge`** = `p - 101325` Pa, created in-memory by the `gaugePressure` `exprField` FO in `system/derivedPressureFields`; that FO is `writeControl none`, so `pGauge` is never written as a field |
| Output file | **`postProcessing/probes_pGauge/0/pGauge`** (plain text) |
| Write frequency | `writeControl runTime; writeInterval 1e-4` with `deltaT 1e-4` → **every time step** |
| Sample rate | **f_s = 10,000 Hz**; Nyquist **5,000 Hz** |

**Probe locations in physical coordinates** (`system/controlDict.tr`, `probeLocations`). All five
lie in the plane **x = 0** at radius **4.48 m = 20 D** from the origin, spanning 180° from −y
through +z to +y. The rotation axis is y, so p1 and p5 are **on-axis** and p3 is the **90°
sideline**:

| file column | noise `componentColumns` | probe index in file header | position (m) | orientation |
|---|---|---|---|---|
| 2 | 1 | `# Probe 0` | `(0, −4.48, 0)` | **on-axis, downstream — in the wake** |
| 3 | 2 | `# Probe 1` | `(0, −3.1678, 3.1678)` | 45° aft |
| 4 | 3 | `# Probe 2` | `(0, 0, 4.48)` | 90° sideline |
| 5 | 4 | `# Probe 3` | `(0, 3.1678, 3.1678)` | 45° forward |
| 6 | 5 | `# Probe 4` | `(0, 4.48, 0)` | on-axis, upstream |

`Allrun.noise` calls `evaluateProbe 1 … 5`, each setting
`pointNoiseCoeffs.componentColumns (N)` and `outputPrefix pressurePointN`. **`componentColumns`
is 1-based over the data columns after the time column**, so `pressurePoint1` is
`# Probe 0` at `(0, −4.48, 0)` — the **wake** probe the README singles out as
turbulence-contaminated at 100 Hz. Carry that identification into any per-probe figure; the
off-by-one here is easy and would mislabel five plots at once.

**File layout** (writer read at
`/usr/lib/openfoam/openfoam2606/src/sampling/probes/Probes/Probes.C:105-147`):
**6 header lines** — five `# Probe <i> (x y z)` lines, then one
`# Time   0   1   2   3   4` line — followed by one row per written time, `Time` then five
values, whitespace-separated in fixed-width columns.

**`system/noiseDict-points` sets `nHeaderLine 15007`.** With a 6-line header that skips 15,001
data rows, which is self-consistent **only if the probes file carries a `t = 0` row**
(6 + 25,001 = 25,007 total lines; 25,007 − 15,007 = exactly the `N 10000` the dict asks for).
**Verify this with `wc -l` on the finished file before running `noise`.** If the count is
25,006 rather than 25,007, `nHeaderLine` is one too large and the window is short by one sample
— **fix `nHeaderLine`, never `N`**, because `N` is the frequency-resolution parameter and
changing it changes the comparator (see §2.3).

**Current status: `WILL APPEAR AT postProcessing/probes_pGauge/0/pGauge` when
`rhoPimpleFoam` starts.** It does not exist now. **There is no probe signal of any kind from
the steady MRF precursor** — `probes_pGauge` appears only in `controlDict.tr`.

### 2.2 How BPF = 100 Hz is obtained from the signal

It is **derived from the rotation rate, not fitted to the spectrum**:

```
n   = omega / 2*pi = 157.14 / 6.283185 = 25.0097 rev/s      (constant/dynamicMeshDict)
BPF = n * (number of blades) = 25.0097 * 4 = 100.04 Hz
```

The README reaches 100 Hz the same way but routes it through `J = U/(nD) = 0.892` with
`D = 0.224 m`. **Use the omega route.** `constant/triSurface/propellerTip.obj.gz` has a
tip-to-tip extent of **0.1949 m** in both x and z, i.e. **D = 0.195 m, not the 0.224 m the
README states** — measured here by scanning the vertex list. BPF does not depend on D and is
unaffected; anything that does depend on D is. **Do not label a view "D = 0.224 m"**: the
shipped geometry contradicts it. This is an observation about the published case, not a
correction to it, and it touches no gate (see §5 on KT/KQ).

### 2.3 The spectrum: window length, resolution, and what a record must contain

`Allrun.noise` runs the `noise` utility five times against `system/noiseDict-points`
(`noiseModel pointNoise`, `windowModel Hanning`, 50 % overlap, symmetric, extended,
`N 10000`, `rhoRef 1`, `fl 2`). Defaults read at
`/usr/lib/openfoam/openfoam2606/src/randomProcesses/noise/noiseModels/noiseModel/noiseModel.C:307-320, 621-671`:

- `N` is the **window length in samples** = 10,000 → **window duration 1.000 s**.
- **Frequency resolution `Δf = 1/(N·Δt) = 1/(10000 × 1e-4) = 1.000 Hz`** — the same 1 Hz the
  shipped `plot_spectrum` title announces. BPF lands on bin 100.
- `fl 2` sets the lower bound to 2 Hz. The upper bound defaults to 10,000 Hz and is in practice
  capped by Nyquist at 5,000 Hz.
- SPL reference is the standard **2e-5 Pa** (`dBRef_`, not set in the dict).
- With exactly 10,000 samples available and `N 10000`, there is **one** window — no averaging.

**Window length needed:**

| purpose | minimum record | why |
|---|---|---|
| see a 100 Hz peak at all | ~0.05 s (5 cycles) | qualitative only, never a gate |
| resolve the registered **±3 Hz** band | **≥ 0.334 s** (`Δf ≤ 3 Hz` ⇒ `N ≥ 3334`) | `Δf = 1/(N·Δt)` |
| **reproduce the registered G6 comparator** | **the full 2.5 s run** | the comparator is the case's own `noiseDict`: `nHeaderLine 15007` + `N 10000` = the published **t ∈ [1.5, 2.5] s** window, which only exists when all 25,000 steps are done |

A spectrum from any shorter window is a **different figure** and must not be given the
registered figure's name or compared to the 100 ± 3 Hz band.

**Noise output paths** (from the shipped `plot_spectrum`, which is the authority on where the
utility puts them):
`WILL APPEAR AT postProcessing/noise/pressurePoint<1..5>/pointNoise/input0/pGauge/SPL_dB_f.xy`
— two columns, **col 1 = frequency [Hz]**, **col 2 = SPL [dB re 2e-5 Pa]**. These appear only
after `Allrun.noise` is run, which is after `rhoPimpleFoam` completes.

### 2.4 The `curle` FO cannot give you BPF — do not try

`system/derivedPressureFields` also declares a `Curle` FO (`c0 1500 m/s`, the same five observer
positions, patches `propellerStem1 propellerStem2 propellerTip propellerStem_outlet`). It writes
`WILL APPEAR AT postProcessing/curle/0/observer<0..4>.dat`, header `# Time   p(Curle)`, two
columns (writer at `/usr/lib/openfoam/openfoam2606/src/functionObjects/field/Curle/Curle.C:136-146`).

**But its `writeControl` is `writeTime`**, and the transient's write times are 2.5e-2 s apart
(`controlDict.tr`, as amended — Addendum B1 D3). With `timeStart 0.1` that is roughly **96
samples at f_s ≈ 40 Hz, Nyquist ≈ 20 Hz**. **100 Hz is far above Nyquist and will alias.** The
Curle series is usable as a slow pressure trace and for nothing spectral. **G6 is graded from
the probe signal via reader R3, never from `curle`.**

---

## 3. WAKE PLANES — AND THE DISK ARITHMETIC

### 3.1 Definition

| | |
|---|---|
| FO name | **`cuttingPlane`**, type `surfaces`, `libs ("libsampling.so")` |
| Declared in | `system/cuttingPlane`, included by `system/controlDict.tr` — **TRANSIENT ONLY** |
| Surfaces | one, named **`xNormal_0`**, `type cuttingPlane`, `planeType pointAndNormal` |
| Plane | **point `(0 0 0)`, normal `(1 0 0)`** — the plane **x = 0** |
| Restriction | `zone v_fluid_tunnel`, `exposedPatchName inlet` |
| Fields | **`p`, `pGauge`, `U`** |
| Options | `interpolate false` (face values), `triangulate false` (general polygons), `mergeTol 1e-15` |
| Format | **ensight, binary, `collateTimes true`** |
| Write frequency | `writeControl runTime; writeInterval 2.0e-04` with `deltaT 1e-4` → **every second time step, 12,500 writes** |

**Orientation, which matters for framing a view.** The rotation axis is **y** and the free
stream runs **−y**, so the plane x = 0 **contains the axis**: it is a **meridional slice showing
the slipstream running downstream in −y**, not a disk-plane cut. Frame the view in the y–z
plane, y increasing upstream.

**There is a hole where the propeller is.** `zone v_fluid_tunnel` selects the 3,438,798
non-rotating cells and **excludes the 635,019-cell rotor zone**, whose bounding box is
`(−0.12, −0.08, −0.12)` to `(0.12, 0.06, 0.12)` m (`log.checkMesh`, cellZone table). The cut
therefore carries a **blank rectangle 0.24 m (z) × 0.14 m (y) centred on the origin** — exactly
over the blades. That is the published setup, not a defect, and a plot lane must expect it
rather than treat it as a failed sample. `exposedPatchName inlet` names a patch that does not
exist in this mesh (`log.checkMesh` lists `freestream`, `propellerStem1`, `propellerStem2`,
`propellerStem_outlet`, `propellerTip`, `AMI1`, `AMI1_rotor`, `AMI2`, `AMI2_rotor`); the lookup
returns −1 and the exposed faces fall to the default internal patch. Harmless, and it is theirs.

### 3.2 Output layout

Collated ensight, from
`/usr/lib/openfoam/openfoam2606/src/surfMesh/writers/ensight/ensightSurfaceWriter_collated.cxx:56-190`
and the output root at
`/usr/lib/openfoam/openfoam2606/src/sampling/sampledSurface/sampledSurfaces/sampledSurfaces.C:196-203`:

```
WILL APPEAR AT postProcessing/cuttingPlane/xNormal_0/xNormal_0.case
               postProcessing/cuttingPlane/xNormal_0/data/<8-digit index>/geometry
               postProcessing/cuttingPlane/xNormal_0/data/<8-digit index>/p
               postProcessing/cuttingPlane/xNormal_0/data/<8-digit index>/pGauge
               postProcessing/cuttingPlane/xNormal_0/data/<8-digit index>/U
```

Open the `.case` file, not the `data/` tree, in any reader.

### 3.3 On-disk volume so far, and the growth rate

**On disk so far: ZERO bytes. `postProcessing/` contains one directory, `fieldMinMax/`.**
The `cuttingPlane` FO is declared only in `system/controlDict.tr`; the live `system/controlDict`
is a byte copy of `controlDict.st` and contains no `surfaces` FO. **Growth rate so far: zero.**
Growth starts at the second time step of the transient and not before. Free space on
`/dev/root` at the time of writing: **968 G total, 751 G used, 218 G available, 78 % used.**

**The projection, stated as arithmetic so it can be attacked.**

*Cut-face count, estimated — this is the weak number.* The `freestream` patch is the r = 0.3 m
sphere carrying **16,416 faces** (`log.checkMesh`). A great circle across a quasi-uniform
sphere mesh of N faces crosses `sqrt(pi*N) = sqrt(pi*16416) ≈ 227` of them. `extrudeMesh` then
adds **36 + 150 = 186** radial layers out to r = 600 m (`system/extrudeMeshDict.step1/.step2`),
and a radial extrusion preserves surface topology, so the extruded shell contributes
`227 × 186 ≈ 42,200` cut faces. Consistency check: `186 × 16,416 = 3,053,376` extruded cells,
leaving `3,438,798 − 3,053,376 = 385,422` tunnel cells inside r = 0.3 m. Those sit at
refinement level 2 (`h = 0.03/4 = 0.0075 m`, from `snappyHexMeshDict` `refinementRegions`) over
a cut area of `pi*0.3^2 − 0.24*0.14 = 0.249 m²`, giving `≈ 4,400` more.
**Estimate `N_faces ≈ 47,000`; band adopted here 40,000 – 70,000. NOT MEASURED.**

*Bytes per write.* Element data is float32: `p` + `pGauge` + 3 components of `U` = **20 bytes per
face per write** ≈ 0.94 MB. The geometry is **re-emitted on every write**: `geomChanged` is
`(!upToDate_)` (`ensightSurfaceWriter_collated.cxx:52`) and a `dynamicMotionSolverFvMesh`
expires the sampled surface every step, so the writer re-emits even though the tunnel-zone cut is
geometrically unchanged. Geometry ≈ points (3 × float32) + polygon connectivity ≈ **1.7 MB**.
**Total ≈ 2.6 MB per write.**

*Full-run projection.* `12,500 × 2.6 MB ≈ **32 GB**`; across the face band, **27 – 47 GB**.

**Conclusion against the registered stop: on this arithmetic the cutting plane does NOT
threaten the 60 GB stop.** Headroom today is `218 − 60 = 158 GB`, roughly 3–5× the projection,
and the transient's own field checkpoints add only ~2 GB (100 write times, `purgeWrite 2`). The
registration's relayed estimate of **50–80 GB** (§A2.4) sits above this projection but inside the
same order and also inside the headroom. **This projection rests on an inferred face count and
is not a measurement**, and `/dev/root` is shared with other campaigns, so it is not left as a
prediction:

> **MEASUREMENT AND TRIGGER, to be run once the transient has produced 10 writes
> (t = 0.002 s, about 20 time steps):**
> `du -sb /home/ubuntu/certonomous-runs/MB13_MARINE_PROPELLER/nref1_n32/postProcessing/cuttingPlane`
> **Ceiling: 118 MB.** It comes from `(218 GB free − 60 GB stop − 10 GB allowance) / 12,500
> writes = 11.8 MB per write`, times 10. **If the reading exceeds 118 MB, the full-run
> projection breaches the registered 60 GB stop; report it to `cfd-supervisor` immediately and
> do not absorb it.** Re-check at 1,000 writes against a 11.8 GB ceiling.

**The disk stop is `BLOCKED`, not `GATE FAIL`.** It is a disk condition registered before first
compute (`MB13_PREREGISTRATION.md` §A2.4) and it can only stop the act. Directive #17 stands:
**no run here is stopped by a time or a budget cap.**

---

## 4. GEOMETRY FOR CONTEXT

Surfaces are gzipped **Wavefront OBJ** in
`/home/ubuntu/certonomous-runs/MB13_MARINE_PROPELLER/nref1_n32/constant/triSurface/` —
all `EXISTS` now. Bounding boxes measured here by scanning each vertex list:

| file | verts | faces | bbox min (m) | bbox max (m) | what it is |
|---|---|---|---|---|---|
| `propellerTip.obj.gz` | 16,785 | 33,432 | `(−0.0975, −0.0610, −0.0975)` | `(0.0975, 0.0490, 0.0975)` | **the four blades** — the hero surface |
| `propellerStem1.obj.gz` | 544 | 816 | `(−0.0264, 0.0490, −0.0264)` | `(0.0264, 0.0600, 0.0264)` | hub collar, rotating |
| `propellerStem2.obj.gz` | 816 | 1,494 | `(−0.0264, 0.0600, −0.0264)` | `(0.0264, 0.1900, 0.0264)` | shaft |
| `propellerStem3.obj.gz` | 952 | 1,632 | `(−0.0264, 0.1000, −0.0264)` | `(0.0264, 0.2000, 0.0264)` | **commented out of `snappyHexMeshDict`; NOT a patch in this mesh.** Do not render it as part of the wetted body |
| `innerCylinderSmall.obj.gz` | 20,572 | 41,140 | `(−0.1200, −0.0800, −0.1200)` | `(0.1200, 0.0600, 0.1200)` | **the rotating-zone boundary (AMI)** — draw it as a translucent shell to show the zone |
| `innerSphere.obj.gz` | 4,034 | 8,064 | `(−0.2, −0.2, −0.2)` | `(0.2, 0.2, 0.2)` | level-2 refinement region |
| `outerSphere.obj.gz` | 4,034 | 8,064 | `(−0.3, −0.3, −0.3)` | `(0.3, 0.3, 0.3)` | edge of the snappy core; becomes the `freestream` patch |
| `outerCylinder.obj.gz` | 14,655 | 29,306 | `(−0.3, −0.8, −0.3)` | `(0.3, 0.2, 0.3)` | unused by `snappyHexMeshDict` |
| `innerCylinder.obj.gz` | 100 | 196 | `(−0.16, −0.6, −0.16)` | `(0.16, 0.1, 0.16)` | unused by `snappyHexMeshDict` |

**Zone extents, from `log.checkMesh` (`EXISTS`, the cellZone table):**

| zone | cells | volume (m³) | bounding box (m) |
|---|---|---|---|
| `v_fluid_rotor` | 635,019 | 0.00601178 | `(−0.12, −0.08, −0.12)` → `(0.12, 0.06, 0.12)` |
| `v_fluid_tunnel` | 3,438,798 | 9.04435e+08 | `(−600, −600, −600)` → `(600, 600, 600)` |

**Framing advice.** The domain is a 600 m sphere and the propeller is 0.2 m. **Never frame on
the domain bounds.** A useful wake view is roughly `y ∈ [−1.5, 0.5] m`, `z ∈ [−0.5, 0.5] m`; a
blade view is `±0.15 m` about the origin. Axis y is the rotation axis, flow runs −y, and the
probe ring sits at r = 4.48 m in the plane x = 0 — an order of magnitude outside any blade view,
so a "probe positions" figure needs its own scale.

---

## 5. WHAT IS NOT PLOTTABLE YET, AND WHY

### 5.1 The registered comparison quantities — all three are on the TRANSIENT axis

| gate | quantity | registered band | axis | source of the band |
|---|---|---|---|---|
| **G4** | time-mean **Fy** over `t ∈ [1.5, 2.5] s` | **325 ± 20 N** (305–345) | **transient** | **eye-digitised** from `figures/Force_history.png`, read uncertainty ±3 N |
| **G5** | time-mean **\|My\|** over `t ∈ [1.5, 2.5] s` | **18.0 ± 1.5 N·m** (16.5–19.5) | **transient** | **eye-digitised** from `figures/Moment_history.png`, read uncertainty ±0.4 N·m |
| **G6** | largest spectral peak below 250 Hz, each probe | **100 ± 3 Hz**, graded ≥ 4 of 5 probes | **transient** | derived from `omega` and blade count; the README states 100 Hz |

**The centres 325 N and 18.0 N·m were read by eye off the case's own two published figures,
before any compute, and frozen.** `MB13_PREREGISTRATION.md` §3 records this where the numbers
are used. **No table of thrust, torque, KT, KQ or efficiency exists anywhere in the 72
published files** — the bands could not have come from a table because there is no table. A
sidecar that cites these numbers says **digitised**, never measured. A figure that shows them
says nothing about where they came from — that is the sidecar's job (§0 rule 1).

### 5.2 KT and KQ are BARRED from any verdict in this act

`MB13_PREREGISTRATION.md` §1.6 and §12 are explicit: **"No KT/KQ gate is registered and no KT/KQ
number will be reported as a verdict."** The orientation values that appear in the registration
(KT ≈ 0.207, 10·KQ ≈ 0.512, eta_O ≈ 0.574) are orientation only. **Do not plot KT, KQ, J or
eta_O as a result, do not put them on an axis, and do not put them in a figure title.** The
diameter discrepancy in §2.2 (shipped 0.195 m against a README 0.224 m) is a second, independent
reason not to: every one of those coefficients is a function of D, and the two available values
of D differ by 15 %.

### 5.3 Nothing from the steady MRF precursor is comparable to those bands

The precursor is `rhoSimpleFoam` with `simulationType RAS`, MRF **on**, acoustic damping
**off**, an iteration axis (`endTime 5000`, `deltaT 1`) and **no force, probe or surface output
at all**. The transient is `rhoPimpleFoam` with `simulationType LES`, MRF **off**, sliding mesh
**on**, acoustic damping **on**, on a physical-time axis. **A converged precursor number is not
a low-fidelity version of the gated number; it is a different quantity on a different axis.**
Any precursor figure must be captioned in its sidecar as the MRF precursor and must never be
placed on the same axes as a G4/G5/G6 band.

### 5.4 What exists on disk right now, and what it is good for

| path | status | good for |
|---|---|---|
| `postProcessing/fieldMinMax/0/fieldMinMax.dat` | **EXISTS** | precursor convergence / stability trace only |
| `log.rhoSimpleFoam` | **EXISTS** | residual histories, `ExecutionTime` per iteration |
| `log.checkMesh`, `log.snappyHexMesh*`, `log.extrudeMesh.*` | **EXISTS** | mesh-quality and build figures |
| `constant/polyMesh/`, `constant/triSurface/*.obj.gz` | **EXISTS** | geometry and mesh renders |
| `figures/*.png` | **EXISTS** | the **published** ESI figures, CC BY-SA 4.0 — the source of the digitised bands. **Not lab results**; do not republish one as a lab figure |

`fieldMinMax.dat` is **TAB-separated and in long format** — one row per field per time, cycling
`T`, `mag(U)`, `p`, `rho` (`mode magnitude`, so `U` appears as `mag(U)`). Columns:
`Time`, `field`, `min`, `location(min)`, `processor`, `max`, `location(max)`, `processor`.
**The `location(...)` columns contain parenthesised vectors with embedded spaces**, so splitting
a row on whitespace produces twelve tokens, not eight. **Split on tab.** Group by the `field`
column before plotting anything.

### 5.5 Minimum transient duration per figure

| figure | needs | earliest possible |
|---|---|---|
| Fy / My running history (progress only, **milestone, not a gate**) | any steps | first write of `force.dat` |
| wake plane single frame | 2 steps | first `cuttingPlane` write |
| wake plane animation, one revolution | **400 steps = 0.04 s** | — |
| probe pressure history | any steps | first probe row |
| spectrum resolving ±3 Hz at all | **3,334 steps = 0.3334 s** | — |
| **the registered G6 spectrum** | **all 25,000 steps = 2.5 s** | run complete |
| **the registered G4/G5 means** | **steps 15,001–25,000, i.e. t ∈ [1.5, 2.5] s** | run complete |

The registration also names a **milestone, explicitly not a gate and carrying no verdict**: at
`t = 1.0 s` the running Fy and |My| are reported for progress. A figure at that milestone is
allowed; a verdict from it is not.

---

## 6. TWO THINGS THAT WOULD STOP A PLOT LANE COLD

### 6.1 `startFrom latestTime` may resolve to **4500**, not 0, and produce a silent empty transient

**This is the most serious finding in this handover and it is not a plot-lane matter to fix.**

Addendum B1 deviation **D3** changed `system/controlDict.st` from `writeInterval 5000;
purgeWrite 0` to **`writeInterval 500; purgeWrite 2`**. `purgeWrite` retains the last N
**written** times and never touches the start-time directory
(`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/db/Time/TimeIO.C:561-580`), so at iteration 5000
each `processorN/` will hold **`0`, `4500`, and `5000`** — where upstream, with `purgeWrite 0`
and one write, it held only `0` and `5000`.

`system/replace.sh` renames `5000` to `5000_steadyState`, deletes `0`, and symlinks
`0 -> 5000_steadyState`. **It does not touch `4500`.** `system/controlDict.tr` then says
`startFrom latestTime`. OpenFOAM's time scan keeps only directory names that parse as a scalar,
so `5000_steadyState` is invisible and the candidates are `{0, 4500}` — **`latestTime` resolves
to 4500**, against `endTime 2.5`.

**Predicted consequence:** `rhoPimpleFoam` constructs successfully (the 4500 directory holds
`U p T k omega nut alphat`, and `pMean`/`UMean` too, since `fieldAverage1` has `timeStart 4000`),
runs **zero** time steps because `run()` tests `value() < endTime`, writes an `End` line, and
**exits rc = 0**. No `force.dat`, no probe file, no cutting planes, no `Allrun.noise` input —
and a naive completion check sees `rc = 0` plus an `End` line and calls it done. Every figure in
this handover would have nothing behind it.

**Status of this finding: DERIVED BY READING, NOT OBSERVED.** It comes from `TimeIO.C`, the
`Allrun`/`replace.sh` sequence and Addendum B1's D3, and it has not been executed. It is
consistent with what is on disk now: `processor0/` currently holds `0` and `500` at iteration
~977, exactly as `writeInterval 500; purgeWrite 2` predicts.

**Decisive check, one command, read-only, to be run after the steady stage ends and before
`rhoPimpleFoam` is allowed to start:**
`ls /home/ubuntu/certonomous-runs/MB13_MARINE_PROPELLER/nref1_n32/processor0/`
If a numeric directory other than `0` is present, `latestTime` will not be 0.

**This is `cfd-supervisor`'s call, and it belongs to the lane that owns the run and the
`replace.sh` handoff — not to a plot lane and not to this lane.** The two obvious repairs are to
rename the leftover checkpoint out of the numeric namespace (preserving it, as `replace.sh`
already does for 5000) or to set `startFrom startTime; startTime 0` in `controlDict.tr`. Either
is a dictionary change **after first compute** and must be recorded as a further addendum, not
applied quietly. The existing `mb13_handoff_watch.sh` instrument records the retained
directories in its `BEFORE RETAINED` row but **does not act on them**, so this is not currently
covered by anything.

### 6.2 `readFields` hard-requires `pMean` and `UMean` in the start-time directory

`system/controlDict.tr` declares `readFields { fields (pMean UMean); }`. Those fields are
produced by the precursor's `fieldAverage1` (`timeStart 4000`, `writeControl writeTime`), so they
exist at 4500 and 5000 and survive the rename into `5000_steadyState`. **If the precursor stops
before iteration 4000, or if `fieldAverage1` writes nothing, `rhoPimpleFoam` FATALs at
construction and the transient never starts.** Nothing in `controlDict.tr` consumes `pMean` or
`UMean` — the FO is vestigial — but it is a hard dependency all the same. The existing
`mb13_handoff_watch.sh` already samples `pMean`/`UMean` presence in its `BEFORE MEANS` row.

---

## 7. WHAT THIS LANE COULD NOT VERIFY

- **The cut-face count in §3.3 is inferred, not measured.** It is built from the `freestream`
  patch face count, the extrusion layer counts and the refinement levels. Measuring it properly
  would mean cutting the plane, which needs a solver process this lane will not start while 32
  ranks are running. The §3.3 trigger exists precisely because of this.
- **Whether the ensight writer re-emits geometry on every write** is read from
  `geomChanged = (!upToDate_)` plus the fact that the mesh is a `dynamicMotionSolverFvMesh`. It
  has not been observed. It is the larger half of the projected volume; the §3.3 measurement
  settles it at the first ten writes without any further reasoning.
- **§6.1 is derived from source and dictionaries, not observed.** It has not happened yet.
- **The exact probe-file line count** (25,006 vs 25,007), which decides whether
  `nHeaderLine 15007` leaves exactly `N = 10000` samples, depends on whether `probes` emits a
  `t = 0` row. The self-consistency of the upstream number implies it does; `wc -l` settles it
  in one command once the file exists.
- **The ESI figures were not re-digitised here.** The 325 N and 18.0 N·m centres are taken from
  the frozen registration, where they are labelled digitised. This lane independently noted only
  that the shipped `plot_spectrum` axis ranges bracket them (§1.5).

---

## 8. ONE-PAGE PATH SUMMARY

Root: `/home/ubuntu/certonomous-runs/MB13_MARINE_PROPELLER/nref1_n32`

| what | path (relative to root) | status |
|---|---|---|
| thrust history | `postProcessing/forces_all/0/force.dat`, col 3 = `total_y` | WILL APPEAR (transient) |
| torque history | `postProcessing/forces_all/0/moment.dat`, col 3 = `total_y` | WILL APPEAR (transient) |
| probe pressures | `postProcessing/probes_pGauge/0/pGauge`, cols 2–6 = p1–p5 | WILL APPEAR (transient) |
| SPL spectra | `postProcessing/noise/pressurePoint<1..5>/pointNoise/input0/pGauge/SPL_dB_f.xy` | WILL APPEAR (after `Allrun.noise`) |
| Curle observers | `postProcessing/curle/0/observer<0..4>.dat` — **aliased, not spectral** | WILL APPEAR (transient) |
| wake plane | `postProcessing/cuttingPlane/xNormal_0/xNormal_0.case` | WILL APPEAR (transient) |
| y+ | `postProcessing/yPlus/...` | WILL APPEAR (precursor post-process stage) |
| precursor min/max | `postProcessing/fieldMinMax/0/fieldMinMax.dat` | **EXISTS** |
| geometry | `constant/triSurface/*.obj.gz` | **EXISTS** |
| mesh | `constant/polyMesh/` | **EXISTS** |
| published figures | `figures/*.png` (ESI, CC BY-SA 4.0) | **EXISTS** |

