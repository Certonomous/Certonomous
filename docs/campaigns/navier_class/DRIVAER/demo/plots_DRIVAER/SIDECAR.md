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
