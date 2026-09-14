# SIDECAR — DrivAer demo plot folder (`plots_DRIVAER`)

Built 2026-09-13 from what was on disk at the time, with **zero solver compute** and
**nothing written into either run tree**. `PROVENANCE.tsv` carries the path, time
directory and sha256 of every artifact each figure read; each figure's plotted
arrays are in the `.csv` of the same stem.

**No verdict word and no band annotation is drawn on any matplotlib image.** The
ParaView panels carry the case, cell count, time and verdict in the caption their
own guard requires.

## 🔴 THE DISCLOSURE THAT TRAVELS WITH EVERY COARSE FIGURE

**This is a REPRODUCTION result, not a VALIDATION result.** Our
`postProcessing/all/0/forceCoeffs.dat` is **byte-identical** to Wolf Dynamics'
shipped file — both 119,158 bytes, `cmp` rc = 0, sha256
`285019ab1560ca8169d5b67ba5d7d043c28d2ae48eee0cbdc09b10753d2325b9` — because the
case ran **verbatim**: their binaries, their mesh, their `decomposeParDict` at
4 ranks, deterministic `scotch`. **Bit-identity proves the transcription did not
diverge and CANNOT corroborate their number.** Anyone citing these figures as
independent agreement with Wolf Dynamics would be wrong.

## The verdict of every source

| Source | Verdict | Where it is recorded |
|---|---|---|
| `coarse_R1` — 669,416 cells, COMPLETE at iteration 1000 | **PASS** on G1, G2 and G3; G4 holds in every clause | `verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_RESULTS.md` |
| `fine_R1` — 4,048,483 cells | **PENDING** — **STOPPED BY OWNER DECISION** short of `endTime` 1000; no gate verdict exists and none can | no grading record exists and none can be built |

Measured here from the artifact, reproducing the record exactly:
**endpoint Cd(1000) = 0.291162651767** against the registered 0.291163, and
**window mean over their own 200→1000 window = 0.283631446** over 801 rows against
the registered 0.283631.

## Which numbers are which, and which are NOT gates

* **0.291163** and **0.283631** are **their shipped coarse artifacts** and are the
  registered reproduction comparands (prereg §6d). They are **not** a validation
  target: §6c records that their own document nominates the coarse mesh only "to
  obtain fast outcomes" and calls the fine mesh the accurate one.
* **0.247** is **Ref.[1] EXP TUM ASME** from their p.19 table (prereg §6). It is
  drawn as a reference line, never as a gate on the coarse run.
* The band on `drivaer_family.png` is **[0.2426, 0.2569]** — Setup 2, which the
  shipped boundary conditions imply, and Setup 3, which their shipped fine data
  actually lands on (measured mean 0.256412). **That interval is a REGISTERED OPEN
  DISCREPANCY** (prereg §6b), not a tolerance: either the shipped solutions
  correspond to a different table row than their boundary conditions imply, or the
  table was generated from other runs. **We do not know which, and nothing was
  changed to make it agree.** There is **no GCI and no observed order** on that
  figure — two levels cannot make a Roache triple, and one of them has not
  finished.

## Per figure

| Figure | What it is | Source |
|---|---|---|
| `drivaer_cd_history.png` | coarse Cd against iteration, their window 200→1000 shaded, their endpoint and window mean and the TUM experiment as lines | `coarse_R1/postProcessing/all/0/forceCoeffs.dat`, 1001 rows |
| `drivaer_forces.png` | Cd, Cl and Cm against iteration | same file |
| `drivaer_residuals.png` | initial residuals Ux, Uy, Uz, p, k, ω | `coarse_R1/log.solver`, 1000 iterations |
| `drivaer_cd_history_fine.png` | **axes only, no curve** — our fine solve was stopped short of `endTime`, so nothing is drawn; the arrays it did produce are in the CSV of the same stem | `fine_R1/postProcessing/all/0/forceCoeffs.dat` |
| `drivaer_family.png` | coarse against fine, published band drawn, TUM as the reference line | both force files |
| `drivaer_p_side/top/rear.png` | surface pressure on body and wheels, three views, one shared window | `coarse_R1/1000/p`, 32,913 faces |
| `drivaer_umag_symmetry.png` | velocity magnitude on the symmetry plane at y = 0.02 m | `coarse_R1/1000/U` |
| `drivaer_umag_midheight.png` | velocity magnitude on the horizontal plane at body mid-height, z = 0.695 m | `coarse_R1/1000/U` |
| `drivaer_umag_wake.png` | velocity magnitude on the cross-section 1.0 m aft of the body | `coarse_R1/1000/U` |
| `drivaer_streamlines.png` | streamlines seeded 1.5 m upstream, coloured by velocity | `coarse_R1/1000/U` |
| `drivaer_mesh_coarse.png` | **their coarse mesh** on body and wheels, per the owner's ParaView rule | `coarse_R1/constant/polyMesh`, 669,416 cells |
| `drivaer_mesh_fine.png` | **their fine mesh** on body and wheels, 101,603 faces | `fine_R1/constant/polyMesh`, 4,048,483 cells |

Measured display windows, shared within each quantity and printed on every caption
with the words *ends clamped*: surface pressure **−402.5 to 180.3 m²/s²**, velocity
**4.394 to 36.11 m/s**, both at the 2nd and 98th percentile of the real data.
Planted colour controls against a constant array, on a floor of 8x: pressure
**23.8x / 25.0x / 27.2x** on the interior mask, velocity **40.7x / 29.5x / 313.3x**,
streamlines **8.3x**. The two mesh panels carry an ink guard instead (388,203 and
389,615 non-background pixels), because a plain mesh carries no field and a
field-versus-constant comparison would have no meaning on it.

## Reading a LIVE run without disturbing it

`fine_R1` was running (`mpirun -np 4 simpleFoam`, pid 1486309) throughout. It was
opened **read-only**: `demo3d_render_common` stages a case as symlinks and puts the
`.foam` stub in a scratch root, never beside the case. Its tree fingerprint is
asserted over **`constant/polyMesh` alone** — the part this render reads and the
part a running solver does not touch. Fingerprinting the whole live tree would trip
on the solver's own log and time writes, which would be a **false alarm rather than
a breach**, and a guard that cries wolf gets switched off.

## Two instrument findings from this build

1. **ParaView's OpenFOAM reader splits polyhedra by default**, and on this Fluent
   mesh that turned 669,416 cells into **1,026,903** — which the cell-count
   assertion caught as "the wrong mesh". The assertion was **not** relaxed to admit
   the larger number: `open_case` gained `decompose_polyhedra`, the reader is told
   not to change the mesh, and 669,416 is then asserted exactly.
2. **The same reader SKIPS time `0` by default**, so a field requested there is
   reported absent on a case that plainly has it. That is why the fine mesh panel
   asks for **no field at all** — a mesh comes from `constant/polyMesh` either way,
   and the cell-count assertion still proves it is the right mesh.

## What waits on the fine solve landing

* every **field** panel regenerates from `fine_R1` (surface pressure, the three
  velocity planes, the streamlines);
* `drivaer_cd_history_fine.png` gains its endpoint and its own averaging window;
* `drivaer_family.png` gains a finished fine value — **and still no GCI**, because
  two levels are not a triple;
* the fine level is the one that can be read against the published band at all
  (prereg §6c), so the comparison with **0.2426 / 0.2569 / 0.247** only becomes
  meaningful then.

---

## v2 REGENERATION — 2026-09-13

Everything above still holds. What changed is the DRAWING, not a number.

* **Plot library v2** (`docs/plot_orders/README_PLOT_LIBRARY_V2.md`), installed by the
  owner. Math only: no English on any figure, no titles, no verdict words, no band
  named in words. **v2 already carries both library changes this lane had made** —
  `%` in place of the word, and a registered `band=(lo, hi)` on `grid_family` — in a
  better form, so neither was re-applied. **One minimal change was added:**
  `residual_history` gained `xlim`/`ylim`, because the residual-evolution frames below
  are only comparable if the axes do not move; without pinned axes each frame
  autoscales to its own data, every frame looks identical, and the descent that is the
  whole point of the series is invisible.
* **Residual evolution.** `sdk/workflows/act_residual_frames.py` cuts the run at
  **10, 25, 50, 75 and 100 %** and writes one frame per cut on ONE set of axes, so the
  act can step through them and the curves are seen to go down. The 100 % frame keeps
  the ordered file name; the others are `*_f10 … _f75`.
* **ParaView panels re-rendered to v2 §13:** white ground, **no orientation triad**,
  **one colour bar a quarter of the frame high** titled by symbol and unit, and
  **nothing written on the image**. The case, the time, the geometry and the verdict
  now live HERE and in the act beside the figure. **The verdict guard was not dropped
  with the caption**: `demo3d_render_common.assert_stamp` still runs on the stamp each
  driver WOULD have drawn, before any pixel, so a verdict word a case does not own is
  still refused. What moved is where the sentence is printed, not whether it is checked.

### 🔴 THE FINE LEVEL'S NUMBER ON EVERY FIGURE IS WOLF DYNAMICS', NOT OURS

On the owner's instruction of 2026-09-13, reaffirmed when the run was stopped,
**the fine level is represented on the figures by Wolf Dynamics' own published fine
value, `C_D = 0.256412`** — measured
in the pre-registration §6b from THEIR shipped fine artifacts over THEIR own
`fieldAverage` window. It carries no wording on any image. **That provenance is
recorded here and nowhere else**, which is exactly why this page exists.

**OUR OWN FINE SOLVE WAS STOPPED BY OWNER DECISION AND WILL NOT LAND.** It is NOT
DRAWN, and now there is nothing to wait for: `drivaer_cd_history_fine.png` holds its
axes in the library's pending mode and shows no curve.

**What the run did produce is kept, and is written down here so it is not lost.** At
**it stopped at 879 iterations of a registered 1000**, last `C_D` **0.2562307**,
last-100 mean **0.255369** — which had come down to within about **0.4 percent** of
Wolf Dynamics' published fine 0.256412. That is interesting and
it is **still not a result**: the run was stopped short of its `endTime`, so it fails
the completion rule on its face and **no grade can be built from it, however close
the number looks.** Those arrays live in `drivaer_cd_history_fine.csv` and in the
`fine_ours_stopped` row of `drivaer_family.csv`, both marked NOT PLOTTED. **Nothing
measured is discarded; it is simply never shown as a result.**

**Its fields are kept too.** `fine_R1` has one reconstructed time, `0`, and the
solution fields the run wrote live decomposed under `processor*/700` and
`processor*/800`. `drivaer_mesh_fine.png` is unaffected — it is the mesh, which needs
no field.

*How the stop was established, and it is a measurement rather than a message.* The
stop is the owner's decision, carried out outside this lane, and this lane neither
stopped the run nor waited on a claim that it had. It waited for **cfd's own record**
to appear in the case directory — `RUN_RC.txt`, containing `RC=0` — and then checked
that the artifact had actually settled: `postProcessing/all/0/forceCoeffs.dat` held
**889 lines at 00:11:40Z and 889 lines twenty seconds later**, so the series had
stopped growing and 879 is the true final iteration rather than whatever happened to
be on disk mid-write. The iteration and the mean above are read from that file, not
relayed.

---

## PRESSURE PANELS RE-RENDERED — 2026-09-14

On the owner's order, `drivaer_p_side.png`, `drivaer_p_top.png` and
`drivaer_p_rear.png` were re-rendered by `render_field_panels.py p-panels`. **No
number in this file changed and no solver ran**: the panels read
`coarse_R1/1000/p` — kinematic pressure, `dimensions [0 2 -2 0 0 0 0]`, hence
m²/s² — on `body2`, `ruotaant` and `ruotapost`, 32,913 faces, the same artifact as
before. Per-file provenance (case, case directory, time, patches, camera, colour
range, image size and the sha256 of the field file) is in **`PROVENANCE_PANELS.tsv`**,
which is a SEPARATE file from `PROVENANCE.tsv` because `build_plots.py` rewrites
that one whole on every matplotlib build and a row appended there would be lost.

**~~The window is now the DATA range, not a percentile window.~~ SUPERSEDED the
same day — see the tight-range section below. The measurement stands, the window
does not.** `p` on those faces
at iteration 1000 runs **−1142.27 to 472.49 m²/s²**, taken from the reader's array
information and independently from numpy over the fetched values, which agree to
1.1e−03. It is rounded outward to **−1500 to 500 m²/s²**, a span of four equal
500-wide steps, so the bar carries exactly five round ticks — **−1500, −1000,
−500, 0, 500** — and the SAME bar, identical to 238 ink pixels on all three
images, is drawn on each panel. The maximum, 472.5, is the nose stagnation value
and sits just under the free-stream dynamic head 0.5·30² = 450 m²/s² plus the
domain's own datum; the minimum, −1142.3, is a local suction spot at the front
wheel.

**🔴 That window was 2.8x wider than the body's own 2nd-to-98th percentile band
(−402.5 to 180.3 m²/s²) and the body read nearly uniform — which is why the owner
ruled the same day for the tight range.** That is a
consequence of the window, not of the solution: the extremes are carried by a
handful of faces, and a diverging `Cool to Warm` map centred on the midpoint of
an asymmetric range puts its white point at −500 m²/s², where no significant part
of the body sits. The panels are shown as ordered; the percentile numbers are
recorded here so the choice can be revisited without re-measuring anything.

**Cameras, all orthographic, all derived from the measured body bounds**
(x −0.8077…3.8043, y 0.0000…1.0023, z 0.0000…1.3899 m):

| Figure | Camera axis from the body centre | View direction | Up | Parallel scale | Size |
|---|---|---|---|---|---|
| `drivaer_p_side.png` | (0, −1, 0) | (0, +1, 0) | (0, 0, 1) | 1.4413 | 1920×1080 |
| `drivaer_p_top.png` | (0, 0, +1) | (0, 0, −1) | (0, +1, 0) | 1.4413 | 1920×1080 |
| `drivaer_p_rear.png` | (+1, 0, 0) | (−1, 0, 0) | (0, 0, 1) | 0.7722 | 1600×1200 |

The parallel scale is derived so the body fills **90.0 %** of its limiting axis —
a 5 % margin on each side — and the fill is **recomputed from the finished
camera** and refused if it is not 0.90 or if the body would be clipped. Measured:
side 90.0 % of width and 48.2 % of height; top 90.0 % of width and 34.8 % of
height (the car now spans the frame, where it previously sat in a narrow vertical
strip); rear 48.7 % of width and 90.0 % of height.

**Nose left is asserted, not assumed.** The nose of this body is at **min x** —
the inlet is `ffminx` and `0/U` is `uniform (30 0 0)`, so the flow runs +x — and
the side and top panels assert that the camera's right vector is +x, which is what
puts min x on the left of the frame. Both come back (1.000, 0.000, 0.000).

**Two things could not be done exactly as ordered, and both are display limits of
this ParaView build, measured here on 2026-09-14:**

1. **The bar title is written `p [m²/s²]` and reaches the screen as `p (m²/s²)`.**
   The superscript twos render correctly; ParaView 5.11.2 draws `[` and `]` in a
   scalar-bar title as `(` and `)`. Measured by rendering `A[B]C {D} <E>` into a
   title and reading the PNG back: the braces and angle brackets survive, the
   square brackets do not. Nothing in the API defeats it.
2. **"View along −y (driver's side)" and "nose on the left" cannot both hold with
   z up.** Viewing along −y means the camera is at +y, and the camera's right
   vector is then −x, which puts the nose on the RIGHT. Nose-left was kept — it is
   the clause the order asks to be verified on the image — so the camera sits on
   the −y axis and looks along +y. On a HALF model with its symmetry plane at
   `ffminy` this renders the same skin either way: the body exists only at y ≥ 0,
   so the eye is simply on the other side of the missing half, and the silhouette
   and the pressure on it are identical.

**The colour control was made FAIRER, and the panels pass it.** Until this render
the null arm was painted a constant `1.0` through whatever lookup table ParaView
hands a new array, which on these panels came out a **saturated blue silhouette**:
its own colour spread was then set by how vivid an unrelated colour map happened to
be, and on the wide window the test failed at 5.6x against its 8x floor for that
reason and not because the field was missing. The null is now the **same array
name, the same preset and the same fixed range, held at the field's own mean
(−116.833 m²/s²)** — the exact null "this picture if p did not vary", carrying the
panel's own colour and its own edge contrast. **The 8x floor was not touched.**
Measured on the interior mask: **side 16.3x, top 27.0x, rear 20.9x**, over 625,323 /
541,393 / 648,070 painted pixels.

**Nothing is written on these images but the bar.** Swept for ink — every pixel
with max(R,G,B) < 90 — and all 238 of them, on each of the three, lie inside the
colour bar block at x ≥ 0.891 of frame width. The folder's own `text_sweep.py` was
not on disk (the scratchpad had been wiped), so this sweep was written fresh and
is recorded here rather than relied on from memory.

---

## TIGHT RANGES — 2026-09-14, and the rule now applied to the whole folder

The owner's ruling, verbatim: *"yes tight range (and this applies to all the plots
if raw does not match the percentiles)"*. Operationally, and enforced in
`render_field_panels.py`: **a colour-mapped panel is windowed on its 2nd-to-98th
percentile band whenever the raw span is more than 1.5x the band span; where the
raw already matches, the panel is left as it is.** The audit runs as
`render_field_panels.py range-audit` and renders nothing, so the decision can be
re-read at any time instead of taken on trust.

| Panel | RAW range | 2/98 band | Span ratio | Action |
|---|---|---|---|---|
| `drivaer_p_side/top/rear.png` | −1142 … 472.5 m²/s² | −402.5 … 180.3 | **2.77x** | **re-rendered on the band** |
| `drivaer_umag_symmetry.png` | 0.3653 … 37.56 m/s | 4.394 … 36.11 | 1.17x | left — already on the band |
| `drivaer_umag_midheight.png` | 1.361 … 37.07 m/s | 4.924 … 34.40 | 1.21x | left — already on the band |
| `drivaer_umag_wake.png` | 2.898 … 30.68 m/s | 6.858 … 30.66 | 1.17x | left — already on the band |
| `drivaer_streamlines.png` | 4.107 … 38.34 m/s | 21.25 … 36.80 | **2.20x** | **re-rendered on the band** |

The three velocity planes were already windowed on the 2/98 band of the symmetry
plane and needed no change; their ratios are printed above so that is a
measurement rather than a memory. The two mesh panels carry no field and are
outside the rule. **Every re-rendered panel refuses at its own ratio**: if a future
run finds the ratio at or below 1.5x, the code stops rather than window on a band
for a reason that no longer holds.

**The pressure bar is now −400 to 200 m²/s², ends clamped, ticks −400, −250, −100,
50, 200.** The band −402.485 … 180.301 is rounded outward to a step of 150 on a
grid of 50 — every tick a multiple of 50 — which spends **17.2 m²/s² of bar on
values no face carries**. The next-roundest candidate, −400 to 400 at a step of
200, would waste 217.2. **Zero is not a tick under this scheme**; the tightest
scheme that does put a tick on zero is −600 to 200, which spends 37 % of the bar
on empty values. The lower end cuts 2.5 m²/s² off the band, 0.43 % of its span —
inside the 1 % the chooser allows, and the band's ends are clamped in any case.
The same bar, identical to 238 ink pixels, is on all three pressure panels;
cameras, sizes, framing and the nose-left assertion are unchanged from the section
above.

**The streamline window is the 2/98 band of the tubes themselves, 21.25 to
36.80 m/s, ends clamped** — not the shared plane window. The owner's round-2 note
stands: a window borrowed from another object leaves the ribbons flat. Its bar
keeps the automatic labels the other velocity panels use; only the window moved.

**The colour control moved twice, and the second move was forced by a refusal.**
The null arm is now the same preset and the same window as the panel, held at a
constant — but held at the field's MEAN it came out at the diverging map's neutral
point on the tight window and rendered a WHITE car on a WHITE ground: the spread
reader found **0 interior pixels and refused**, correctly, because a null nobody
can see proves nothing about a reader. The null is therefore held at **the
window's low end**, which the panel's own map paints and which is never the
background. **The 8x floor has never been touched.** Interior margins on the tight
window: **side 27.2x, top 35.7x, rear 27.4x**, over 252,006 / 369,522 / 416,656
painted pixels. The streamline panel's control is unchanged from its previous
build and passes at **15.2x**.
