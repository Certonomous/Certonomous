# DRIVAER R2b — ABSOLUTE-FIRST-LAYER PROBE (coarse only)

**Status: FROZEN ON COMMIT. No compute has run. Awaiting cfd-supervisor check 4.**
Rung id `R2b-C1`. One level, one build, no solver. 2026-09-12, cfd.

## 0. THE FALSIFIER, WRITTEN FIRST AND BEFORE ANY NUMBER BELOW

**This probe exists to be able to kill option (b). If it cannot reach that verdict it is
worthless, so the killing condition is registered ahead of the passing one.**

**(b) IS DEAD — verdict `GATE FAIL`, and DrivAer Cd is then `BLOCKED` on snappyHexMesh
layer addition — if EITHER holds:**

- **F1 — coverage collapse.** Extruded/candidate wall-face coverage **< 50.0 %**.
  The control (`r2_coarse`, same mesh, same geometry, relative sizing) measures
  **16,887 / 23,365 = 72.275 %** [`r2_coarse/R2_MEASURED.json`]. F1 fires at a loss of
  more than roughly a third of that.
- **F2 — the wall model still will not sit in its band.** Layered-group area-weighted
  median y⁺ **outside [30, 300]**.

**If F1 or F2 fires, the lab stops spending cells on DrivAer Cd.** The current spec's
fine rebuild (~4,205 core-min) is then not authorised, because a y⁺-held family is the
only route to an admissible Roache triple on a wall-bounded QoI and this probe would
have shown that route shut. **That is a publishable outcome and it must remain
reachable.**

## 1. Why — the finding this tests

`addLayersControls` is `relativeSizes true; finalLayerThickness 0.5; expansionRatio
1.25`, so the first layer is `0.5·h/1.25⁴ = 0.2048·h` and the first cell centre is
`0.1024·h`. With `yplus_per_metre = 90,623.25 m⁻¹`, **y⁺ ∝ h_surf exactly, by
construction of the layer spec.** Back-calculated surface cells: 51.9 mm coarse,
25.0 mm medium; ratio 2.076, which is the measured y⁺ ratio 481.565/232.027 = 2.0755.
**The family therefore moves the wall model every time it refines**, and a wall-function
family has no `f_exact` for Roache to extrapolate to — as h→0 the first cell enters the
viscous sublayer where the log law is wrong. Confirmed independently by the
cfd-supervisor on his own arithmetic (481.623 / 231.996 against measured 481.565 /
232.027).

## 2. THE ONE CHANGE — three lines, against a control that is otherwise byte-identical

Probe root: `verification/runs/navier_class/DRIVAER/LAYERFIX_C1_coarse_absoluteFirstLayer/`.
Staged from `r2_coarse`'s mesh-build `system/` and the canonical STL by symlink. Its
`system/snappyHexMeshDict` differs from `r2_coarse`'s
(sha256 `d13bbac350e032546546c0f228e45978b296ca2ae3428cc4bf581c17cca32ec3`) in exactly
these three lines and nothing else, proven by `diff` into `THE_ONE_CHANGE.diff`:

```
-    relativeSizes       true;        +    relativeSizes       false;
-    finalLayerThickness 0.5;         +    firstLayerThickness 2.10e-3;
-    minThickness        0.02;        +    minThickness        5.25e-4;
```

`expansionRatio 1.25` and `nSurfaceLayers 5` on all 47 vehicle patches are UNCHANGED.

**`minThickness` is changed because it MUST be, and this is the trap that would have
made the probe a false negative.** With `relativeSizes false` every thickness in the
block becomes **absolute metres**. The inherited `minThickness 0.02` would mean **20 mm
— nine times the 2.10 mm first layer** — and snappy would reject every layer it built,
returning 0 % coverage that looked like a physics result and was an arithmetic one. It
is set to 0.25 × firstLayerThickness.

## 3. Predictions, with bands, registered before the build

| quantity | predicted | band | basis |
|---|---|---|---|
| layered-group median y⁺ | **95.2** | **[60, 150]** | y = t₁/2 = 1.05e-3 m; y⁺ = 90,623.25 × y. Band allows snappy not achieving the requested t₁ exactly and the area-weighted median's spread |
| extruded/candidate coverage | **≥ 65 %** | PASS ≥ 65 %, **F1 < 50 %** | control 72.275 %; a thinner first layer is easier to extrude, not harder, so a material loss would be a finding |
| total layer stack | 17.2 mm | — | t₁(1.25⁵−1)/0.25 = 8.2070 × 2.10 mm; 33 % of the 51.9 mm coarse surface cell |
| unlayered-group median y⁺ | **unchanged, ~1,941** | not gated | those 20 patches get no layers at any spec; **this probe does not and cannot fix them** |

**Gate C1 `PASS` requires BOTH:** coverage ≥ 65 % **and** layered median y⁺ in [60, 150].
Coverage in [50 %, 65 %) or y⁺ in [30,300] but outside [60,150] → **`GATE REACHED`**,
partial, and the fine-build decision returns to the supervisor.

**A prediction this registration deliberately does NOT make:** that the y⁺-held family
is buildable at the medium and fine levels. One coarse level cannot show that.

## 4. Cost — and NO CAP KILLS ANYTHING

**Predicted 4.4 core-min** (serial; control `r2_coarse` build measured **4.03 core-min**
[`CORE_MINUTES.txt`], LAYERFIX_B2 measured 4.4 on the same geometry). **Prediction cap
15 core-min**, allowing the 3.25× contention measured on this box tonight. **The cap is
a PREDICTION SCORED AT COMPLETION under rule 12, NEVER A KILL** — Sanaa has ruled no cap
three times. **Predicted peak memory 0.6 GiB** (control snappy max RSS 481,960 kB =
0.460 GiB). **A MemAvailable refusal IS armed** — it is a physics guard, not a budget
guard — via `run_build.sh`'s caller; the probe is refused, not killed, if predicted peak
exceeds available − 4 GiB. **At 0.6 GiB it bids against nothing**: it does not contend
with SUBOFF L2 or M6H1 for the memory pool.
Derived: 4.4 core-min = 0.0733 core-h → **$0.0038, DERIVED NOT MEASURED** at
$0.0513/core-h, reported-by-owner (`COMPUTE_BUDGET_CHARTER` §5).

## 5. The grading path, FIXED BY LITERAL HASH VALUES

Not by a recipe that re-reads the file and agrees with itself at every commit.

| instrument | sha256 at freeze |
|---|---|
| `cases/navier_class/DRIVAER/mesh/run_build.sh` | `7577f707d17e0718aacefadb95fb304f94e934578e2926ae2ca623ed72aecebd` |
| `cases/navier_class/DRIVAER/mesh/stage_r2_measure.py` | `c86a8ea4317f0dc21a00c9c739f8de7932bebf86345751632deddffd1640bb0e` |
| control dict `r2_coarse/system/snappyHexMeshDict` | `d13bbac350e032546546c0f228e45978b296ca2ae3428cc4bf581c17cca32ec3` |

Coverage is read from `stage_r2_measure.py`'s `layers.extruded_faces` /
`layers.extrude_candidate_faces`; y⁺ from `yplus.layered_group.yplus_area_weighted_median`.
**Before any verdict is believed, each hash is re-computed and compared against the
literal above; a mismatch is a REFUSAL, not a note.**

## 6. Completion

rc captured inside the wrapper (`setsid timeout cmd` exits 0 for every outcome);
`BUILD_RC` must end `ALL_STEPS_OK` with every step `rc=0`; `log.checkMeshFull` present.
**No solver runs, so rule 4's solver clauses and the age guard do not apply and are not
claimed.** Mesh non-conformance against `docs/standards/MESH_STANDARD.md` travels with
any number as a CLAIM CAP, as it does for every other DrivAer level.
