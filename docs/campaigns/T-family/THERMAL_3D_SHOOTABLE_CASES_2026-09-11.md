# Heat-transfer: the GENUINELY 3D thermal cases this lab can shoot — with mesh-convergence plan and cost, 2026-09-11

**Team: heat-transfer. Drafted by a `lab-lane` at ZERO solver core-minutes.**
**For Sanaa's desk, relayed by the heat-transfer supervisor.**

> **NOT SENT. NOT FILED.** `CLAUDE.md` rule 7 — nothing in this file has been
> sent, uploaded, posted or registered outside this box, and nothing here
> authorises a launch. A freeze is the supervisor's act; a send is Sanaa's alone.

**This is a LIST, not a verdict.** It assigns no verdict from rule 1's
vocabulary to any case. Every number below is read from an artifact named
beside it, on disk at the time of writing.

**What Sanaa asked for.** 2026-09-10 19:35Z, a bullet list of shootable 3D
cases; 19:45Z, every hard case run and completed **with its mesh convergence**,
ASAP; *"since rn the priority for me are these 3D cases"*; *"No team works on
demos rn. Teams work on RUNS."* This list is the thermal half of that answer and
it has been outstanding since.

---

## 0. THE BAR THIS LIST APPLIES, AND WHAT IT THROWS OUT

**3D means `checkMesh` reports THREE geometric (non-empty/wedge) directions on
the BUILT mesh, with zero `empty` and zero `wedge` patches.** Not an intent, not
a `blockMeshDict`, not a description — the built artifact.

**Excluded by that bar, named so no reader credits them:**

| case | why it is not on this list | artifact |
|---|---|---|
| **T4e** (impinging jet, live now) | **2 geometric directions.** 2.5° axisymmetric wedge, one cell thick in z | `verification/runs/T-family/T4e_runs/T4e_IJ_f/log.checkMesh:92` — *"Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)"* |
| **T4f** (URANS successor of T4e) | inherits T4e's mesh **byte-identical**; same 2.5° wedge | `docs/campaigns/T-family/T4f_PREREGISTRATION.md:87`, `:295` |
| **T23 / T23G / T23G2(R,Rn,Rn2) / T24** | 5.0° axisymmetric wedge, one cell thick | `docs/campaigns/T-family/T23_PREREGISTRATION.md:132` |
| **T5 `X_2d`** | 2 geometric directions; it is the registered 2D control | `verification/runs/T-family/T5_runs/X_2d/log.checkMesh:87` |
| **K2b pilot slice** | 2D rack-row slice at 12.5 mm | `docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md` |

> **AND THE CAP-STOP EXEMPTION DOES NOT REACH T4e.** Sanaa's CASE_PROTOCOL
> closing clause suspends the budget stop *"for all these 3D cases that still
> need to run."* T4e is a 2-direction wedge, so it is outside that scope and
> its registered cap still binds it as a cap. It is running and is not touched
> by this document.

**NO NEW FAMILIES.** CASE_PROTOCOL §7 names heat-transfer's front as T4e.
Every entry below is a rung of the T-family or of the F14/K DC-cooling spine, or
realises a module Sanaa has already approved. **She approved `K2a`, the rack-row
module, in her own words at ~20:20Z on 2026-09-10; an approval travels with the
case, not with a document's filename.** No agent message is her consent.

**THE MESH-RATIO RULE THIS LIST ENFORCES ON ITSELF.** CASE_PROTOCOL §1: *"three
similar levels from one script at ratio 1.5 to 2."* In 3D the cell count steps
by `r³`. **The ratio is achieved by moving the DIVISIONS until the BUILT counts
land — never by widening a window.** K2d and T26 both registered a ratio their
built mesh could contradict; every entry below states whether its ratio is
**BUILT** or **PROJECTED**, because that distinction is the whole difference.

---

## 1. THE LIST — ranked cheapest-defensible-first

---

### ① K2f — the rack row, full 3D. **LAUNCH THIS ONE.**

- **Family:** F14 DC-cooling spine. Realises `K2a_RACK_ROW_MODULE_SPEC.md`
  unchanged — **the module Sanaa approved 2026-09-10 ~20:20Z**. Not a new family.
- **What makes it 3D:** a four-rack row in a room with a cold aisle, a hot aisle,
  supply tiles and end walls — spanwise recirculation over the rack tops is the
  physic, and a slice cannot hold it. **BUILT AND VERIFIED, not asserted:** all
  three K2d levels report *"Mesh has 3 geometric (non-empty/wedge) directions
  (1 1 1)"* —
  `verification/runs/F14-cooling-ladder/K2d_runs/K2d_L1/log.checkMesh`,
  `.../K2d_L2/log.checkMesh`,
  `.../RETIRED_2026-09-11/K2d_L3/log.checkMesh`.
- **Mesh-convergence plan — the only ladder on this list whose ratio is BUILT:**

  | level | target cells | **BUILT by K2d** | step | r = step^(1/3) |
  |---|---:|---:|---:|---:|
  | L1 | 59,259 | **58,368** | — | — |
  | L2 | 200,000 | **196,992** | **3.37500** | **1.50000** |
  | L3 | 675,000 | **664,848** | **3.37500** | **1.50000** |

  `58,368 × 3.375 = 196,992` exactly; `196,992 × 3.375 = 664,848` exactly.
  **The divisions were moved until the built counts landed — this ladder is the
  worked example of the rule, not a projection of it.** r = 1.5000 sits at the
  lower edge of CASE_PROTOCOL's [1.5, 2] band; that is inside the band and is
  stated rather than glossed. Gate `G-MESHSIM` reads the built counts from each
  level's own `constant/polyMesh` and refuses outside [3.2063, 3.5438]
  (`K2f_PREREGISTRATION.md` §1).
- **Cost — arithmetic open, on a rate MEASURED ON THIS RUNG'S OWN GEOMETRY:**
  K2d's three levels measured `core-s/iteration` = 0.3111 / 2.0959 / 17.9441,
  i.e. **cost per iteration scaling as N^1.568 then N^1.765, not N^1.0**
  (`K2f_PREREGISTRATION.md` §10.1). At `endTime` 3,000:
  - L1: `0.3111 × 3000 ÷ 60` = **15.6 core-min**
  - L2: `2.0959 × 3000 ÷ 60` = **104.8 core-min**
  - L3: `17.9441 × 3000 ÷ 60` = **897.2 core-min**
  - `C-DECOMP` control re-run at L2 = **104.8 core-min**
  - **contention-free total = 1,122.4 core-min**; at K2d's measured contention
    factors (1.003 / 1.320 / 1.775) = **1,884.7 core-min**
  - **CARRIED BRACKET: 1,120 – 1,890 core-min = 18.7 – 31.4 core-h**
  - **$0.96 – $1.61 DERIVED, NOT MEASURED** at $0.0513/core-h
    (`18.707 × 0.0513 = 0.960`; `31.412 × 0.0513 = 1.611`). The box cannot read
    its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); `cost_basis` =
    reported-by-owner.
  - **Named limits:** the 8-rank L3 row rests on an *assumed* 4→8 parallel
    efficiency — no K2d level ever ran above 4 ranks. The contended column is a
    property of that night's load, not of this rung.
- **Exists:** `K2a` module spec; `build_k2f.py`, `launch_k2f.sh`,
  `mark_done_k2f.py` (all in
  `verification/runs/F14-cooling-ladder/K2f_runs/`); the frozen
  `K2f_PREREGISTRATION.md` draft with its ladder, gates and cost; three built
  meshes from K2d proving the divisions land.
- **MUST BE WRITTEN:** **`analyse_k2f.py` — the comparator does not exist.**
  `find . -name "analyse_k2f*"` returns nothing; `K2f_PREREGISTRATION.md:759`
  carries it as *pending*. **This is the exact file whose absence retired K2d** —
  `analyse_k2d.py:613-619` was a stub with no grading path. Then the four
  pre-freeze obligations driven by execution (`A-INPUT`, `A-DRIVE`, clause-7,
  the launcher assertion), the supervisor's personal diff read, and the freeze
  commit.
- **HONEST EXPECTATION, stated before the spend:** K2f's own §4 registers
  `S-ONSET` / **`NOT A RESULT`** as the *expected* outcome — K2d measured the
  steady solver converging six decades on L1 and limit-cycling at L2 and L3.
  **This run is very likely to return a non-convergence finding, not a PASS.**
  That finding is worth having and is honestly a hard 3D result; it is not a
  green gate on camera.

---

### ② T26 — motor-in-duct conjugate heat transfer, full 360°

- **Family:** T-family. The genuinely-3D successor of the T23/T24 motor spine
  that Act A films as a 5° wedge. Not a new family.
- **What makes it 3D:** a full 360° duct bore with **three support struts at 0°,
  +120° and −120°**, conjugate at both ends — the struts *are* the conduction
  path from motor to duct wall, three strut wakes convect onto the hub tail, and
  `T_max` is located in 3-space rather than on a ray. A 5° wedge holds none of
  it. **Gate `D-3D` (registered §13.6) certifies this from the BUILT mesh** —
  `checkMesh` must report 3 geometric directions and the `boundary` file zero
  `empty` and zero `wedge` patches, recorded verbatim per level into
  `gate_t26.json`. Dimensionality is never inferred from a dict.
- **Mesh-convergence plan — ratio 1.500, but PROJECTED, and that is this entry's
  one real weakness:**

  | level | base Δ₀ | **projected** cells | step | r |
  |---|---:|---:|---:|---:|
  | L1 | 8.000 mm | 262,373 | — | — |
  | L2 | 5.333 mm | 885,508 | 3.375 | **1.500** |
  | L3 | 3.556 mm | 2,988,590 | 3.375 | **1.500** |

  (Amendment 1 §13.3, which shifted the ladder down exactly one rung; 262,373 is
  derived as `885,508 / 3.375 = 262,372.7`.) Δ₁ is held fixed across levels
  deliberately, so the y⁺ regime does not change between levels.
  > **THE GAP, MEASURED: T26 registers NO BUILT-CELL-COUNT-RATIO GATE.** Its
  > registered gate set is `GEO-1…8, D-3D, G-MINCELL, G-CONV-h/p/U/t, G-CONT,
  > G-BAL, G-ITER` — there is no `G-MESHSIM` equivalent. The 3.375 steps live
  > only in *projected* counts, and these are `snappyHexMesh` counts: with the
  > surface-refinement levels and the 18/12/5 layer counts held fixed, the built
  > count will **not** follow `Δ₀^-3`. **This must be closed before freeze by
  > adding K2f's `G-MESHSIM` on the built counts and moving the base divisions
  > until they land — not by widening the window.** It is precisely the error
  > that cost K2d its ladder.
- **Cost — arithmetic open. `core-min = N_cells × N_iter × 4.9328e-06 ÷ 60 ÷ 0.75`:**
  - L1: `262,373 × 4,000 × 4.9328e-06 ÷ 0.75 ÷ 60` = **115.04** solve + 26.24
    mesh = **141.28 core-min**
  - L2: `885,508 × 8,000 × 4.9328e-06 ÷ 0.75 ÷ 60` = **776.54** + 88.55 =
    **865.09 core-min**
  - L3: `2,988,590 × 12,000 × 4.9328e-06 ÷ 0.75 ÷ 60` = **3,931.23** + 298.86 =
    **4,230.09 core-min**
  - geometry gate: **0.05 core-min, MEASURED** (already run and passed)
  - **REGISTERED POINT = 5,236.51 core-min = 87.28 core-h = $4.477 DERIVED**
  - **AND THE POINT IS NOT CARRIED ALONE.** The rate 4.9328e-06
    core-s/cell-iteration is measured (`COST_CALIBRATION.md` row `C-209`, T5b,
    `chtMultiRegionSimpleFoam`, 1 rank) over **52,684 → 882,024 cells**, where the
    per-iteration exponent was **1.18 then 0.97** — near-linear *on this solver*.
    **T26's L3 sits 3.39× beyond the top measured anchor**, and the
    counter-example is on the next entry's own geometry: K2d's
    `buoyantBoussinesqSimpleFoam`/GAMG ladder scaled at **N^1.57–N^1.77**.
    Re-deriving the two refinement steps at those exponents (multiplier
    `3.375^(e−1)`: 2.0747 at e = 1.60, 2.5514 at e = 1.77):

    | | e = 1.00 (registered) | e = 1.60 | e = 1.77 |
    |---|---:|---:|---:|
    | L2 solve | 776.5 | 1,611.1 | 1,981.1 |
    | L3 solve | 3,931.2 | 8,156.4 | 10,030.3 |
    | **rung total** (+115.0 L1, +413.7 mesh, +0.05 gate) | **5,236.5** | **10,296.3** | **12,540.2** |

  - **CARRIED BRACKET: 5,237 – 12,540 core-min = 87.3 – 209.0 core-h.**
    **$4.48 – $10.72 DERIVED, NOT MEASURED** at $0.0513/core-h
    (`87.275 × 0.0513 = 4.477`; `209.00 × 0.0513 = 10.722`).
  - **Named limits:** parallel efficiency **η = 0.75 at 4/8/16 ranks is a CLASS
    DEFAULT, never measured** — this territory holds no
    `chtMultiRegionSimpleFoam` anchor above 1 rank, and 16 ranks on a 16-vCPU
    box is the optimistic end. The meshing rate 6.0e-03 core-s/cell is also a
    class default. **CASE_PROTOCOL §5 staging closes both: run L1, measure the
    actual rate and the actual η, re-derive L2 and L3 on the measured exponent
    before committing L3.** A point estimate on linear scaling is how K2d lost
    535.600 core-minutes.
- **Exists:** the geometry gate **already run and passed** (`GEOMETRY GATE: PASS`,
  exit 0, §2.1) under a live planted control that caught a real reader defect
  (§2.2). **Independently re-checked for this list, 2026-09-11:** the source
  surface `cases/demo-surfaces/motor_in_duct.stl` is on disk (314,484 B,
  sha256 `131aab8e…`) and `geometry_gate_t26.py --selftest` returns **SELFTEST
  PASS** with every mutant arm firing (deleted facet, flipped facet, zero-area
  facet, inward normals, crossing pair, coplanar overlap) and both disjoint
  controls correctly silent — the gate is demonstrably not a constant-pass.
  **One honest gap: the gate's own OUTPUT is not on disk as an artifact** — the
  measured values live transcribed in `T26_PREREGISTRATION.md` §2.1. A
  transcription is not the instrument's output; the gate should be re-run into a
  named artifact at freeze. And every instrument is written —
  `geometry_gate_t26.py` (333 lines), `build_t26.py` (246), `analyse_t26.py`
  (1,551), `mark_done_t26.py` (530), `orchestrate_t26.py` (366),
  `launch_t26.sh` (553), all in `docs/campaigns/T-family/`.
- **MUST BE DONE:** add the built-ratio gate (above); pin `analyse_t26.py`'s
  sha256 into §8.3; the supervisor's **personal** reading of the comparator as a
  diff (non-delegable, `SUPERVISION_CHARTER.md` §3.1); the §0.3 id derivation and
  §0.4 absence condition re-taken in the committing invocation; rulings on §0.5
  and §7.3.3; then the freeze commit. **No comparator to write from scratch.**
- **What it can and cannot earn:** T26 registers **grid convergence and
  conservation on a 3D geometry — VERIFICATION, NOT VALIDATION.** Reference tier
  is **NONE**: no reference of any tier exists for this configuration (§5.4). It
  can return a CONVERGING triple and a PASS on a grid-convergence gate; it can
  never be cited as validating a motor temperature.

---

### ③ T5d / T5e — the heated-cube array, conjugate 3D. **The only entry with an experimental reference — and it is BLOCKED.**

- **Family:** T-family, the T5 line. Not a new family.
- **What makes it 3D:** a wall-mounted heated cube (epoxy solid + air) in a
  channel, two conjugate regions, three-dimensional horseshoe vortex and wake.
  **BUILT AND VERIFIED:** all three T5b levels report *"Mesh has 3 geometric
  (non-empty/wedge) directions (1 1 1)"* for **both** regions —
  `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/log.checkMesh:97` and
  `:169`.
- **Mesh-convergence plan — BUILT, in band, and NOT self-consistent:**

  | level | air cells | step | r | epoxy cells | step | r |
  |---|---:|---:|---:|---:|---:|---:|
  | c | 52,684 | — | — | 869 | — | — |
  | m | 212,942 | 4.0419 | **1.5926** | 3,272 | 3.7653 | **1.5559** |
  | f | 882,024 | 4.1421 | **1.6058** | 14,507 | 4.4337 | **1.6432** |

  Every r is inside [1.5, 2]. **But no two of them are equal.** The fluid ladder
  drifts 0.83 % between steps and **the solid region refines at a different ratio
  from the fluid** (1.556 → 1.643 against 1.593 → 1.606). A Roache triple assumes
  three geometrically similar meshes; a conjugate triple whose two regions refine
  at different ratios is not that. **The fix is to move the divisions until one
  r is built in both regions at both steps** — it is exactly the K2d/T26 lesson,
  applied to a ladder that already exists.
- **Cost — MEASURED, and it is the cheapest solve on this list.** `C-209`,
  1 rank, 5,000 iterations: wall 1,007 + 5,252 + 20,851 s = 27,110 core-s
  = **451.8 core-min** for the three levels. **$0.386 DERIVED**
  (`451.83 ÷ 60 = 7.531 core-h; × 0.0513 = 0.386`). A ratio-corrected re-ladder
  moves the cell counts and therefore this figure; carry it as the **anchor**,
  not as the estimate, and re-derive after the divisions are fixed.
- **Exists:** frozen builders (`build_t5b.py`, `build_t5d.py`), comparators
  (`analyse_t5b.py`, `analyse_t5c.py`, `analyse_t5e.py`), three built meshes,
  and — uniquely on this list — **an experimental reference**: Meinders 1998 TU
  Delft thesis, OPEN, title-page verified, sha256 `36c89a54…`, stated uncertainty
  5 % mid-face / 10 % edges in local `h`.
- **STATE: `BLOCKED`, and the blocker is named.** `build_t5d.py --case T5_CUBE_c`
  returned rc = 0 and the builder's own
  `checkMesh -allRegions -allTopology -allGeometry` then reported, on the **air**
  region: *"Cells with small determinant (< 0.001) found, number of cells: 7658
  … Failed 1 mesh checks."* The registered stop in `T5d_PREREGISTRATION.md` §6
  fired and the build stopped — no `0/`, no time dir, no `STATUS`, no solver.
  Artifact: `verification/runs/T-family/T5d_runs/T5_CUBE_c/log.checkMesh`. The
  triage found the defect **inherited from T5**, not introduced by T5d.
- **MUST BE DONE:** repair the 7,658 small-determinant cells (mesh engineering,
  cost unmeasured — this is the real spend and it is not a solve); fix the
  two-region ratio mismatch above; then re-ladder. **T5c's most recent grade was
  0 of 6 PASS** — 1 `GATE FAIL`, 5 `NOT A RESULT` on `OSCILLATORY` / `DIVERGENT`
  triples (`verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt`) — so the
  physics is not expected to fall into band on a re-run alone.

---

## 2. WHAT I WOULD LAUNCH TODAY, IF GIVEN ONE LANE

**`K2f`.** Four grounds, in order of weight:

1. **Its mesh-convergence ladder is the only one on this list that has actually
   been BUILT at the registered ratio** — 58,368 → 196,992 → 664,848, exactly
   ×3.37500 twice, r = 1.50000. Sanaa asked for cases completed *with their mesh
   convergence*; this is the one where the divisions are already known to land,
   and landing them is the single thing K2d and T26 both got wrong.
2. **Its cost model is measured on its own geometry**, at N^1.57–N^1.77, not a
   linear guess and not an exponent transferred from another solver. Bracket
   1,120–1,890 core-min, **$0.96–$1.61 derived** — the cheapest defensible 3D
   thermal run this team owns.
3. **Sanaa approved the module** (K2a, her own words, 2026-09-10 ~20:20Z), and
   K2f realises it unchanged.
4. **One instrument stands between it and a launch** — `analyse_k2f.py` — and
   K2d's forensics say exactly what it must do, because K2d died of that file's
   absence.

**The honest counterweight, so the choice is made with it in view:** K2f's own
registration expects `S-ONSET` / **`NOT A RESULT`** — the steady solver
limit-cycling as the mesh refines. **If what is wanted is a 3D case that can
PASS a gate, that is ② T26**, at 2.8×–6.7× the compute and with a built-ratio
gate to add before freeze. K2f buys a defensible hard 3D *finding*; T26 buys a
3D case that can return a green grid-convergence verdict.

---

## 3. WHAT THIS LIST DOES NOT CLAIM

- **No entry here is a capability.** None has reported. Naming a plan as a
  capability is the error campaign T exists to avoid.
- **No verdict is assigned**, and no gate, threshold, cap or label is set. Every
  entry still needs its own frozen pre-registration before a solver starts
  (`CLAUDE.md` rule 2).
- **Two of the three entries carry reference tier NONE** — K2f and T26 are
  verification, not validation. Only T5 has an experimental primary, and T5 is
  `BLOCKED`.
- **No cost figure here is measured except where it says MEASURED**: T26's
  0.05 core-min geometry gate, T5's 451.8 core-min ladder, and K2d's rate basis.
  Every dollar figure is **DERIVED** at the owner-stated $0.0513/core-h and is
  never a measurement — the box cannot read its own billing.
- **Nothing here has been sent** (`CLAUDE.md` rule 7).

*Drafted by a heat-transfer `lab-lane`, 2026-09-11. Zero solver core-minutes.
No running solver was touched; T4e was read only through its committed
`log.checkMesh`.*
