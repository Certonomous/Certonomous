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
