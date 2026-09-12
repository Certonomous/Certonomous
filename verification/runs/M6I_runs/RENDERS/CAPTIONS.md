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
