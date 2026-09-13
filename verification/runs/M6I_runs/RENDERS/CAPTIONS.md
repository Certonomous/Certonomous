# M6I RENDERS — CAPTIONS. **USE THESE VERBATIM. A PICTURE TRAVELS FURTHER THAN A VERDICT.**

Produced under Sanaa's standing directive of 2026-09-12 ~20:30Z (*"whenever a run
completes, i want the paraview visualization of its mesh saved … the coarse mesh (or
medium mesh if the coarse isnt converged). But all fields should be stored as the fine
mesh result fields (whenever we have it)"*) by `scripts/render_on_completion.sh`, which
refuses any case that is not complete. **No solver time was spent and no graded tree was
touched** — the renderer proves the latter by census hash in its own output.

---

## `M6I_R1_L3_mesh_surface.png`

> **ONERA M6 wing — surface mesh, level L3 of the M6I import ladder, 15,360 cells,
> 480 wing faces.** Solve `M6I-R1-L3-R3`, `rhoSimpleFoam`, 4 ranks, completed
> 2026-09-12T22:17:26Z with `rc = 0` and an `End` line at iteration 3000.
> 🔴 **THIS RUN CARRIES NO SHOCK AT ALL, AND NOTHING ON OR NEAR THIS IMAGE MAY SUGGEST A
> VALIDATED M6 RESULT.** Measured: `cfd_cp_rise_at_shock` **0.087** against the
> experiment's **0.424** at η = 0.65, and **0.053** against **0.640** at η = 0.90 — an
> order of magnitude short of the registered shock-strength limb S1 (≥ 0.212 and ≥ 0.320).
> Upper-surface `Cp` minimum reaches only **−0.42 to −0.44** across all six AGARD
> stations, where an M6 at M∞ = 0.8395 requires roughly −1.1. **The picture is a mesh and
> a flow field. It is not an agreement with anything.**

### WHAT THIS IMAGE IS, LEVEL BY LEVEL — because her rule has two halves and they differ here

| her clause | what was applied |
|---|---|
| *"the coarse mesh (or medium mesh if the coarse isnt converged)"* | **L3 — and in THIS family L3 is the COARSEST level**, not the finest. The ladder runs L3 (coarse, 15,360 cells) → L2 → L1 (finest). L3 converged, so L3's mesh is what her rule selects. |
| *"all fields should be stored as the fine mesh result fields (whenever we have it)"* | **L3's own fields — because L3 is the ONLY completed level.** `L2` terminated with **`rc = 136` (SIGFPE)** and holds no time directory beyond `0`; `L1` holds no `RC.txt`, no time directory beyond `0`, and no `rhoSimpleFoam` process is live on the box. **The finest completed level available at this time IS L3.** Her rule explicitly anticipates this — it is why she said render *as runs complete* rather than batching — and **this caption is to be updated the moment L2 or L1 lands.** |

### 🔴 THE FACE-COUNT GUARD — DISCHARGED, AND IT FAILED TO CATCH A BAD IMAGE ON THE FIRST ATTEMPT

This lab has previously rendered a car from **3.6 % of itself**, so the count is checked
against arithmetic done independently of the renderer:

| quantity | faces | source |
|---|---:|---|
| `wing` patch | **480** | `constant/polyMesh/boundary`, read directly |
| **rendered** | **480** | renderer's own count |

**EXACT MATCH.** Independently corroborated by geometry that the count alone cannot see:
`cp_extracted.json` reports chord falling 0.9125 → 0.5800 and `x_le` advancing
0.1704 → 0.8181 between η = 0.20 and η = 0.96 — i.e. the taper and sweep of an ONERA M6
planform, visible in the image and measured from a different artifact.

**AND THE PART THAT IS AGAINST THE GUARD.** The first render of this run passed the
face-count guard **exactly** — 1,248 faces = `wing` 480 + `symmetry` 768 — **and the image
showed no wing at all.** The opaque symmetry-plane disc sat between the camera and the
wing and filled the frame. **The guard proves what was LOADED; it does not prove what is
VISIBLE.** It was caught by looking at the picture, which is the only thing that catches
it. Recorded here rather than quietly re-rendered, because a guard trusted past its range
is worse than no guard.

### MESH QUALITY — DISCLOSED, NOT GATED (Sanaa's two-tier ruling)

`checkMesh` on the patched L3 mesh: **max non-orthogonality 87.66**, average 34.63;
**max skewness 2.775 (OK)**. The 87.66 is disclosed as a fact about an imported grid and
is **not** offered as the explanation for the missing shock.

### COMPUTE (rule 12)

Startup 6 s + solve 82 s at 4 ranks = **5.87 core-minutes**, **$0.0050 DERIVED, NOT
MEASURED** at $0.0513/core-h, owner-stated — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). The render itself launched no solver and cost no solver
time.

### 🔴 WHAT MUST NOT BE PUT ON THIS IMAGE

- **No claim of agreement with AGARD AR-138, the tunnel, or any reference.**
- **No `Cp` or shock-location number presented as a result.** The registered verdict path
  is `scripts/grade_m6_agard_cp.py` against the 14 frozen bands; **this lane did not grade
  L3 and quotes no verdict of its own.** The measured shock-strength figures above are
  cited from the committed M6I-R1 Addendum 3 (`9027a1a64`), not produced here.
- **No implication that a three-level family exists.** L2 is `NOT A RESULT` (SIGFPE) and
  L1 has produced nothing; Addendum 3 registers that **fewer than three shock-bearing
  levels ⇒ NO three-level order and NO GCI is computed, quoted or implied.**

---

*Filed by a cfd `lab-lane`, 2026-09-12. No solver launched. Alters no gate, threshold, cap
or label. No agent's message is Sanaa's consent. Submissions parked.*

---

## `M6I_R1_L3_cp_vs_agard.png`

> **ONERA M6 — surface pressure at the six registered AGARD stations, M6I level L3 against
> AGARD AR-138 TABLE B1-14 TEST 2308 (M = 0.8395, α = 3.06°, Re = 11.72e6).** Solve
> `M6I-R1-L3-R3`, `rhoSimpleFoam`, SpalartAllmaras, 4 ranks, completed 2026-09-12T22:17:26Z,
> `rc = 0`, 3,000 iterations, `End` line, outer-iteration residuals ≤ 7.8e-05, planted
> control seen.
>
> 🔴 **THIS FIGURE IS A GATE FAIL AND SHOWS WHY IN ONE GLANCE. NOTHING ON OR NEAR IT MAY BE
> PRESENTED AS A VALIDATED M6 RESULT.** The experiment (open symbols) reaches −Cp ≈ 1.0–1.2
> on the upper surface and then drops through a shock; **the CFD (blue) peaks at −Cp ≈ 0.43
> and has no shock at all.** Measured by the frozen grader: `cfd_cp_rise_at_shock` **0.087**
> against the experiment's **0.424** at η = 0.65, and **0.053** against **0.640** at η = 0.90
> — an order of magnitude short of the registered shock-strength limb S1 (≥ 0.212, ≥ 0.320).
> All 12 Cp rows miss the registered RMS ≤ 0.050 band, by factors of 3.4 to 8.7.
>
> **The cause is resolution, and it was disallowed in advance as a mesh-quality excuse.**
> 15,360 cells give 480 wing faces — **24 points around the section, about 12 per surface.**
> `M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 1 §A1.4 registered, before any Cp existed, that
> an inboard miss could **not** be blamed on the family's 87° non-orthogonality, because
> η = 0.20, 0.44 and 0.65 carry 84, 62 and 116 faces over 70° out of L1's 191,794.
>
> **η = 0.96 additionally carries `NOT A RESULT — PATH-DEPENDENT`** (ADDENDUM 7 §A7.2): the
> ramped and un-ramped runs of this same level differ there by max|ΔCp| **0.0165** against a
> registered limb of 0.01, while the other five stations agree to better than 0.0022.
>
> **Colour carries no identity on its own** — experiment is black open symbols, CFD a blue
> line, and upper/lower are separated by marker shape and line style as well as hue, so the
> figure survives greyscale and colour blindness. The dataviz skill's palette validator was
> run and **is blind in this environment**: a deliberately failing pair one hex step apart
> produced **zero bytes and exit 0**, exactly as a good palette did, because its entry point
> reads `document.body` and never executes under node. **A pass from a reader not shown able
> to see a failure is not evidence** (rule 3), so no validation is claimed and the design is
> safe by construction instead.
>
> Produced by `scripts/plot_m6i_cp.py`. The upper/lower split is **transcribed from the
> frozen grader** `scripts/grade_m6_agard_cp.py:cfd_curve()`, not re-decided here; the
> experiment's split is its own Z/L sign, already resolved in the data file.

---

# ADDENDUM 1 — 2026-09-12 — **THE MESH RENDER ABOVE WAS SILENTLY COLOURED BY PRESSURE, AND THE CAPTION CALLING IT A MESH WAS WRONG. RE-RENDERED, AND THE FIELDS HALF OF HER DIRECTIVE IS NOW ACTUALLY SATISFIED.**

Appended, not inserted: **lines whose number changed above this section: 0.**

## A1.1 WHAT WAS WRONG WITH THE IMAGE I SHIPPED

`scripts/render_openfoam_3d_paraview.py` called ParaView's `Show()` and never disabled its
**automatic colouring**. Measured with `pvbatch` on this very case: **immediately after
`Show()` and before any `ColorBy` call, `d.ColorArrayName` already reads
`['POINTS', 'p']`.** The blue-to-white gradient across the wing in the first version of
`M6I_R1_L3_mesh_surface.png` **was the pressure field**, not lighting — **unlabelled, with
no colour bar, under a caption that called it a mesh render.**

**That caption was wrong and this addendum says so rather than quietly replacing the file.**
The image has been re-rendered with colouring explicitly disabled; the mesh render is now a
genuine neutral-grey surface with black cell edges, and the caption above is true of it.

## A1.2 AND THE FIELDS HALF OF HER DIRECTIVE IS NOW SATISFIED, NOT WORKED AROUND

Sanaa, ~20:30Z: *"all fields should be stored as the fine mesh result fields (whenever we
have it)."* The head of this file recorded that half as unavailable because `--field` was
believed to be a silent no-op. **It never was** — see `A1.3`. A second image is therefore
saved beside the mesh render:

> **`M6I_R1_L3_field_p_surface.png` — ONERA M6 wing, surface pressure, level L3, 480 wing
> faces.** `p` coloured by its **CELLS** association (the array the solver wrote;
> interpolating to points would smooth the data the picture exists to show), range
> **[50 974.4, 147 628.9] Pa**, with a **scalar bar carrying the field name and its
> numbers** so the colours can be decoded. Planted colour control **PASSED — the
> collapsed-map plant moved 94.31 % of body pixels.**
> 🔴 **THE CAVEAT AT THE HEAD OF THIS FILE APPLIES UNCHANGED AND APPLIES HARDER TO A FIELD
> PICTURE: THIS RUN CARRIES NO SHOCK.** A pressure picture of a shockless transonic wing
> shows a smooth expansion where the literature shows a lambda foot. **It is not a
> validated M6 pressure field and must never be captioned as one.**
> **Fields are L3's own**, because L3 remains the only completed level — `L2` is dead at
> `rc = 136` (SIGFPE) and `L1` has produced nothing.

## A1.3 HOW THE DEFECT SURVIVED TWO FIX ATTEMPTS — THE CONTROL WAS NOT A CONTROL

`_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md` concluded `--field` was a silent no-op because
`--field p` and "the plain mesh render" came out identical. **They came out identical
because the plain mesh render was ALREADY `p`.** The comparison had no uncoloured arm, so
it could not have shown a difference whatever the tool did.

**This is the third instance tonight of one mechanism: an instrument reporting on a proxy
instead of the registered quantity.** The face-count guard passed an image with no wing in
it; the hue-std guard passed the exact artifact it was written to catch; and this control
compared a thing against itself. In each case the number was real and the thing it stood
for was not.

**`--field` works and always did**: colouring by `T` instead of `p` moves **7.07 %** of
frame pixels, measured.

## A1.4 THE REPAIR AND ITS CONTROLS — `25caef4c6`

| behaviour | result |
|---|---|
| no `--field` | **solid neutral surface**; ParaView auto-colouring explicitly disabled |
| `--field p` | coloured by CELLS, rescaled, **scalar bar shown** |
| `--field alphat` (range 0, 0) | **REFUSED, exit 2** — a constant field paints one flat colour that reads as a field picture and shows nothing |
| `--field NoSuchField__` | **REFUSED, exit 2**, listing the arrays actually present |
| planted colour control | **collapse the colour map to one value, re-render, read the PNG back off disk.** Varying fields move 96.17 % / 96.58 % of body pixels; the CONSTANT field moves **0.00 %** — a demonstrated failing case. Floor 10 %. |
| 12-limb geometry selftest | **12/12**, unchanged |

**A control that does not discriminate was measured and rejected before shipping:** "does
the field render differ from a solid render" **fails**, because the constant field differs
from solid by **96.24 %** — a constant maps to one *end* of the colormap, nowhere near grey.

## A1.5 WHAT IS STILL OWED, AND IT IS AGAINST US

**The three DrivAer renders are in the same class** — shipped as mesh renders while
silently carrying an auto-picked field — and **have not yet been re-rendered.** Named here
so the defect is not closed while mislabelled images stand.

*Appended by a cfd `lab-lane`, 2026-09-12. No solver launched. Alters no gate, threshold,
cap or label. Submissions parked.*

---

# ADDENDUM 2 — 2026-09-13 — **L1 LANDED. THE FIELDS FIGURE IS NOW THE FINEST LEVEL, THE MESH FIGURE IS STILL THE COARSEST, AND THE LADDER FIGURE SHOWS BOTH HALVES OF THE ANSWER AT ONCE.**

Appended, not inserted: **lines whose number changed above this section: 0.**
Alters no gate, threshold, band, cap or label. No solver launched. Submissions parked.

`L1` completed at **2026-09-13T03:35:40Z**, `rc = 0`, `End` line, last `Time = 8000`
== `endTime 8000`, in `log.rhoSimpleFoam.resume.2`. It is now the **finest completed
level**, so the head of this file's *"this caption is to be updated the moment L2 or L1
lands"* is discharged here.

**SANAA'S TWO CLAUSES, RE-APPLIED TO THE LEVELS THAT NOW EXIST:**

| her clause | what is applied now |
|---|---|
| *"the coarse mesh (or medium mesh if the coarse isnt converged)"* | **L3, 15,360 cells, 480 wing faces — unchanged.** `M6I_R1_L3_mesh_surface.png` stands as the mesh figure. L3 converged, so her rule still selects it, and at 4× the surface resolution per step the L1 grid is not legible as a mesh picture. |
| *"all fields should be stored as the fine mesh result fields (whenever we have it)"* | **L1, 983,040 cells, 7,680 wing faces — NEW.** We now have it. `M6I_R1_L1_field_p_surface.png` replaces L3 as the field figure. The L3 field image is **kept, not deleted**, as the coarse-end member of the ladder. |

---

## `M6I_R1_L1_field_p_surface.png` — **MESH SHOWN: L1 (fine). NUMBERS: L1 (fine).**

> **ONERA M6 wing — surface static pressure `p`, level L1 of the M6I import ladder,
> 983,040 cells, 7,680 wing faces, time 8000.** Solve `M6I-R1-L1-TVD-RESUME2`,
> `rhoSimpleFoam`, Spalart–Allmaras, 4 ranks, completed 2026-09-13T03:35:40Z with
> `rc = 0` and an `End` line. Coloured by the **CELLS** association (the array the solver
> wrote), scalar bar carries the field name and its numbers. Camera convention `--up z`,
> the same one the L3 pair used, so the two images are directly comparable.
> **Face-count guard: expected 7,680 from `constant/polyMesh/boundary`, rendered 7,680 —
> EXACT MATCH.** Planted colour control **PASSED: the collapsed-map plant moved 91.80 %
> of body pixels** (floor 10 %), read back off the saved PNG.
>
> 🔴 **STILL NO SHOCK, AND THE PICTURE MUST NOT BE PRESENTED AS A VALIDATED M6 FIELD.**
> Measured by the frozen grader on this very level: `cfd_cp_rise_at_shock` **0.1098**
> against the experiment's **0.4240** at η = 0.65, and **0.0827** against **0.6400** at
> η = 0.90 — against the registered shock-strength limb S1 (≥ 0.212, ≥ 0.320). Sixty-four
> times the cells of L3 bought the shock rise only **0.0875 → 0.1098 at η = 0.65**. The
> smooth expansion in this image is the wing's real computed state, not a rendering
> artifact, and it is not what AR-138 measured.
>
> 🔴 **THE COLOUR RANGE IS SET BY 1 % OF THE SURFACE AND THAT IS DISCLOSED, NOT TUNED
> AWAY.** The bar reads **[20,523.9 , 202,655.4] Pa**, i.e. `Cp` **[−1.617 , +2.028]** at
> `q∞ = 49,977.1 Pa`. Measured from the `.vtp` the renderer read: both extremes sit in
> tip-edge cells at `y ∈ [1.485, 1.502]` — the **η ≈ 1.00 rounded tip**, which the
> pre-registration §2 already excludes as the region where chord and surface normal are
> least well defined. Only **1.05 %** of wing cells exceed `|Cp| > 1.2`; the 1st–99th
> percentile band is `Cp` **[−1.169 , +0.813]**. The renderer rescales to the true data
> range and has no range flag, so the wing washes toward mid-grey. **No hand-picked range
> was substituted to make the picture prettier** — the number is stated instead.
> (`Cp = +2.028` also exceeds the compressible stagnation ceiling ≈ +1.17 at M∞ = 0.8395
> and is recorded here as a tip-cell overshoot, not defended.)
>
> **Renderer exit code was 1, and that is disclosed.** `pvbatch` raised
> `GLXBadContext / X_GLXMakeCurrent` **after** the `WROTE` line, the face-count guard and
> the planted colour control had all been emitted — a teardown fault in the X context, not
> a render fault. The evidence the image is real is the guard and the plant, both printed
> before the fault, plus the sidecar
> `M6I_R1_L1_field_p_surface.json` carrying `graded_tree_untouched: true`.

---

## `M6I_R1_L1_cp_vs_agard.png` — **MESH SHOWN: none (a graph). NUMBERS: L1 (fine).**

> **ONERA M6 — surface pressure at the six registered AGARD stations, M6I level L1
> (983,040 cells, 8,000 iterations) against AGARD AR-138 TABLE B1-14 TEST 2308
> (M = 0.8395, α = 3.06°, Re = 11.72e6).** Produced by `scripts/plot_m6i_cp.py`; the
> upper/lower split is transcribed from the frozen grader
> `scripts/grade_m6_agard_cp.py:cfd_curve()`, not re-decided.
>
> 🔴 **THIS FIGURE IS A `GATE FAIL` AND SHOWS WHY IN ONE GLANCE.** Graded by
> `scripts/grade_m6_agard_cp.py` (blob `e9d5c04b` at `4c931d97c`, hash-verified against
> the committed blob immediately before the run), output
> `verification/runs/M6I_runs/L1/m6i_grade_L1.json`. Planted control fired:
> `reader_saw_the_plant: true`, RMS moved **0.0984** against a required **0.0617**.
> **11 of 12 Cp rows miss the registered RMS ≤ 0.050 band; both shock stations miss B2.**
> The one row inside the band is **η = 0.65 lower, RMS 0.0494** — the first row anywhere
> in this family to sit inside B1, and it is a lower-surface row.
>
> **What the eye should take from it:** the lower surface (dashed, squares) now lies on
> the experiment across all six stations. The upper surface (solid, circles) reaches
> −`Cp` ≈ **0.98** where the experiment reaches ≈ **1.21**, and then **decays smoothly to
> the trailing edge where the experiment holds a plateau and drops through a shock.**
> The missing physics is on the suction side and it is a shock, not an offset.

---

## `M6I_R1_LADDER_cp_vs_agard.png` — **MESH SHOWN: none (a graph). NUMBERS: L3, L2 AND L1 TOGETHER.**

> **ONERA M6 — the whole M6I grid ladder at the six registered AGARD stations: L3
> (15,360 cells, 3,000 it), L2 (122,880 cells, 5,000 it), L1 (983,040 cells, 8,000 it),
> against AGARD AR-138 TABLE B1-14 TEST 2308.** Cells rise ×8 per step; wing faces ×4 per
> step (480 → 1,920 → 7,680).
>
> **THIS IS THE FIGURE THAT CARRIES THE ARGUMENT, AND IT SAYS TWO OPPOSITE THINGS AT
> ONCE — BOTH MEASURED, NEITHER ASSERTED.**
>
> 1. **The Cp deviation IS converging.** All **12 of 12** station/surface rows fall
>    monotonically L3 → L2 → L1 on `rms_dev`. Span-averaged (weighted by graded
>    orifices): **0.3328 → 0.2045 → 0.1423**. The upper-surface suction peak climbs
>    monotonically at every station — at η = 0.65, −`Cp` **0.435 → 0.732 → 0.965** against
>    the experiment's **1.181**, i.e. 37 % → 62 % → 82 % of the measured peak.
> 2. **The shock is NOT converging.** `x_shock_cfd` at η = 0.65 reads **0.9531 (L3) →
>    0.8851 (L2) → 0.8851 (L1)** — *identical* across the ×8 refinement from L2 to L1 —
>    and at η = 0.90 it reads **0.9233 at all three levels.** The D1 detector is finding
>    the trailing-edge recovery, not a shock, at every level. B2's `|Δx|` therefore does
>    **not improve at all** between L2 and L1 (0.4099 and 0.6436, unchanged).
>
> **Nothing on this figure may be presented as grid convergence of a validated result.**
> The pre-registration `A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md` §0/§8.2 registers
> this comparison as **VALIDATION ON A SINGLE GRID**, and `M6I_R1_SOLVE_PREREGISTRATION.md`
> ADDENDUM 3 registers that **fewer than three shock-bearing levels ⇒ NO three-level
> order and NO GCI is computed, quoted or implied.** None of the three levels is
> shock-bearing under S1, so **no observed order and no GCI appears anywhere in this
> caption**, and the monotone `rms_dev` sequence above is reported as a *sequence*, never
> as a converged extrapolation.
>
> 🔴 **A LEGIBILITY DEFECT IN THIS FIGURE, DISCLOSED RATHER THAN QUIETLY SHIPPED.** The
> L1-only figure separates upper from lower by **marker shape and line style**, so it
> survives greyscale. This three-level figure separates the *levels* by **lightness of
> one hue alone** — `plot_m6i_cp.py` shades additional cases rather than re-encoding them
> — and at η = 0.20 the legend box overlaps the L1 lower-surface entry. **The level
> identity on this figure is therefore weaker than the surface identity.** Read the
> per-level numbers from the caption above or from the grade JSONs, not from the shades.
> No palette-validator pass is claimed: ADDENDUM 1 established that the skill's validator
> is **blind in this environment** (a deliberately failing pair produced zero bytes and
> exit 0), and a pass from a reader not shown able to see a failure is not evidence
> (CLAUDE.md rule 3).

---

## THE MESH FIGURE IS DELIBERATELY NOT L1, AND HERE IS THE MEASUREMENT BEHIND THAT

`M6I_R1_L3_mesh_surface.png` **stays** as the mesh figure of this campaign, per Sanaa's
first clause. L1's wing carries **7,680 faces against L3's 480 — 16× as many** — and at
1920×1080 with black cell edges the L1 surface reads as a dark hatch, not a mesh: the
measured ink fraction of the L1 field render is **0.0773** with edges over 7,680 faces in
the same frame where L3's 480 faces are individually countable. **Coarse mesh for
legibility, finest fields for the numbers**, exactly as she put it.

*Appended by a cfd `lab-lane`, 2026-09-13. No solver launched. Alters no gate, threshold,
band, cap or label. No agent's message is Sanaa's consent. Submissions parked.*
