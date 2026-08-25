# F12 attempt 2 — admission gate A — `PASS` at all three levels

**Phase 1, mesh only. No solver was launched in producing this record.** The
builder contains no call to `rhoSimpleFoam` and the three case directories carry
no `0/` fields and no `thermophysicalProperties`, so a solver cannot be started
from them by accident.

Graded against `verification/campaign/F12_PREREGISTRATION.md`, HEAD blob
`080303c57aee52849bb625579565a84ca5469717`, **unchanged**: *"max
non-orthogonality <= 70 degrees and max skewness <= 4, boundary faces included"*,
with aspect ratio *"advisory there and recorded with its alignment
justification, not gated."* Nothing in this record alters a gate, a threshold, a
cap or a label.

## 1. The verdict

| level | cells | max non-orthogonality | margin | faces > 70° | max skewness | margin | gate A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| coarse | 23,040 | **51.1237°** | **18.876°** | **0** | 0.957230 | 3.0428 | **`PASS`** |
| medium | 92,160 | **51.5250°** | **18.475°** | **0** | 0.956899 | 3.0431 | **`PASS`** |
| fine | 368,640 | **51.9261°** | **18.074°** | **0** | 0.956588 | 3.0434 | **`PASS`** |

`blockMesh` rc = 0 and `checkMesh` rc = 0 at every level; cell counts equal the
frozen three exactly. Logs: `{coarse,medium,fine}/log.checkMesh`. **An ABSENT log
reads ABSENT and never clean** — the reader was shown refusing on a log that does
not exist (§4).

**Beside attempt 1, from the same reader:**

| | coarse | medium | fine | faces > 70° | trend |
| --- | --- | --- | --- | --- | --- |
| attempt 1 | 70.646° | 70.861° | 72.542° | 892 / 3,598 / 14,399 (×4.03, ×4.00) | over the gate and **rising** |
| attempt 2 | 51.124° | 51.525° | 51.926° | **0 / 0 / 0** | 18° under, rising **0.40°/level** |

Attempt 1's over-threshold count was a fixed **fraction** of the mesh, which is
why refinement could not cure it. Attempt 2 has no such faces at any level.

**Honest and stated in advance:** attempt 2's maximum still rises slightly with
refinement, +0.40° per level. On that trend the gate would not be reached for
tens of further refinements, but the trend is not zero and this record says so.

## 2. Why it passes — the mechanism, not the number

Attempt 1's four-block O-grid mapped the surface onto the far-field circle by
proportional arc length, so the radial grid line at x/c ≈ 0.07 on the lower
surface pointed ~70.6° away from that station's surface normal. **That angle IS
the near-wall non-orthogonality**, and it is a property of the correspondence,
not of the spacing.

Attempt 2 sets every block corner's far-field point from that station's own
surface-normal direction. Because inside a block the inner and outer edges carry
the same grading and the same cell count, the correspondence is proportional arc
length **whatever the grading is** — so orthogonality depends only on corner
placement and corner angles, and **cell counts and gradings cannot move the
gate.** The recipe is therefore not tunable into a pass, which is the point.

Two further mechanisms were identified and are recorded in
`ATTEMPT2_MESH_REGISTRATION.md` §2–§4: the O-ring/wake interface (wedge-versus-
rectangle centroid mismatch), and a wake-block mechanism found only by
measurement, resolved by making the wake outlet **uniform at every level**.

## 3. The instrument was validated against a known non-zero, twice

- The near-wall predictor returns **70.608°** for attempt 1's coarse mesh against
  the **70.646°** its `checkMesh` measured — 0.038° apart.
- An exact non-orthogonality calculator written from the `polyMesh` reproduces
  `checkMesh` to the fourth decimal: **51.1237 against 51.1237**, and
  **64.0958 against 64.0958** on an intermediate candidate.

## 4. Planted controls — the reader was shown able to see a breach

| control | planted | read back | verdict | admissible? |
| --- | --- | --- | --- | --- |
| a known-bad `checkMesh` log | 88.8° | **88.8°** | **`GATE FAIL`** | yes |
| a log that does not exist | — | status `ABSENT` | **`ABSENT`** | yes |
| **attempt 1's correspondence rebuilt** | — | **70.6463°, 892 faces > 70** | **`GATE FAIL`** | yes |

The builder **aborts** and refuses to report any `PASS` if any control fails.

The third control is the strongest: rebuilding attempt 1's own correspondence
through this pipeline reproduces **70.6463° and 892 faces**, which is attempt 1's
measurement to the fourth decimal and to the face. **The only thing that changed
between `GATE FAIL` and `PASS` is the mesh instrument** — not the reader, not the
gate, not the threshold.

Artifacts: `PLANT_checkMesh_log`, `control_attempt1_correspondence/log.checkMesh`.

## 5. Geometric similarity — the ladder is a ladder

| invariant | coarse | medium | fine | spread |
| --- | --- | --- | --- | --- |
| wall-normal first cell (chord) | 2.0e-6 | 1.0e-6 | 5.0e-7 | exact halving |
| wall-normal total expansion | 4,401,087 | 4,598,885 | 4,702,009 | **6.837 %** |
| surface first cell (chord) | 6.670e-4 | 3.350e-4 | 1.678e-4 | ratios **1.9911, 1.9960** |
| wake streamwise total expansion | 728.85 | 749.68 | 760.34 | 4.32 % |
| wake outlet total expansion | 1.0 | 1.0 | 1.0 | **identical in kind** |

The wall-normal invariant's spread is **6.837 %**, matching the repaired ladder's
6.84 % — the same anchoring, carried over unchanged. Every surface spacing halves
because the per-block gradings are held fixed while the per-block counts double.

`scripts/recipe_audit.py` was **not** run against this ladder and its answer would
not have been authoritative if it had been: `similarity_failures()` treats any
change of a block's grading as a similarity failure, which is right for uniform-
background snappy ladders and wrong for a correctly-built graded family, which
**must** change its grading string as it refines. It would report a spurious fork.

## 6. y+ — below 1 at every level, under every convention tabulated

Convention as fixed by the frozen amendment §6: **2.330e5 per chord, on the FULL
first-cell height.**

| level | first cell | y+ full height | y+ cell centre | y+ × LE factor 1.709 |
| --- | --- | --- | --- | --- |
| coarse | 2.0e-6 | **0.4660** | 0.2330 | **0.7964** |
| medium | 1.0e-6 | **0.2330** | 0.1165 | **0.3982** |
| fine | 5.0e-7 | **0.1165** | 0.0582 | **0.1991** |

**No level crosses 1 under any of the three.** No rung is bridged; there is no
wall-function rung sitting in a triple with two wall-resolved ones. The LE factor
is ESTIMATED from a flat-plate correlation with an assumed edge velocity; it is
not measured and it is not a gate.

## 7. Deterministic decomposition

Method **`hierarchical`**, `n (2 2 1)`, 4 subdomains, **seed-free**: the partition
is a pure function of the cell centres, so identical input gives identical
partitions by construction. Run **twice** at every level and asserted identical.

| level | partition cell counts, run 1 | run 2 | identical |
| --- | --- | --- | --- |
| coarse | 5,760 / 5,760 / 5,760 / 5,760 | same | **yes** |
| medium | 23,040 / 23,040 / 23,040 / 23,040 | same | **yes** |
| fine | 92,160 / 92,160 / 92,160 / 92,160 | same | **yes** |

`scotch` is not used: this team measured it return 12777/12906/12965 and then
12974/12870/12865 on a byte-identical mesh, and that alone decided a convergence
verdict. Logs: `*/log.decomposePar.{1,2}`.

## 8. Geometric error floor

The surface polygon is **identical across all three levels** — 2,544 unique
(x, y) points from 32 polyLines per dictionary, byte-for-byte the same set at
coarse, medium and fine. Its reader carries its own planted control: a
deliberately re-sampled polygon written to disk and read back by the same
extractor returns **1,280** unique points, so the reader is shown able to see the
difference. The builder aborts if it cannot.

The polygon is **finer than attempt 1's** (2,544 points against 960), so the
geometric error floor is not the same number as attempt 1's. That is a change and
it is disclosed rather than assumed harmless.

## 9. Reported, not repaired

1. **Aspect ratio.** Max 2,842 (medium) and 1,761 (fine); the coarse level prints
   no aspect-ratio warning at all. All three are **better than attempt 1's
   10,606**. Aspect ratio is advisory under the frozen gate A, the anisotropy is
   wall-normal and on orthogonal cells, and it is recorded, not gated. `checkMesh`
   therefore prints "Failed 1 mesh checks" at medium and fine on that advisory
   check alone; both gated quantities pass with 18° and 3.04 of margin.
2. **Patch asymmetry, inherited.** The upper wake block's far boundary is
   `outflow` while the lower wake block's is `inflow`. Reproduced from attempt 1
   face for face rather than silently corrected: it is a boundary-condition
   question and belongs to gate B, which this phase does not touch.
3. **`_wake_ratio` length mismatch, inherited.** It sizes the wake's streamwise
   grading for a length of 50 while the block edge is 99 long, so the first wake
   cell is 1.98× the trailing-edge spacing its own docstring says it should match.
   Fixing it was **measured** and made the maximum *worse* (65.6 / 67.1 / 68.2),
   so it is left as attempt 1 had it and recorded here.
4. **Neither analytic predictor bounds the measured maximum.** They were used as
   design filters on two identified mechanisms and are validated against known
   non-zeros; a third mechanism is bounded only empirically. Gate A above is
   decided by a real `checkMesh` log and by nothing else.

## 10. Cost — calibration at completion

| | value |
| --- | --- |
| registered before the build | ≤ 5 core-min at ranks = 1 |
| **actual** | **0.4015 core-min** (24.092 s wall, ranks = 1) |
| ratio actual / registered | **0.080** |
| waste, named separately | **0.00 core-min** — no rebuild, no stall, no re-run |
| dollars | **$0.000343, DERIVED at $0.0513/core-h and reported-by-owner, NEVER measured** |
| loadavg at launch | 5.33 / 4.79 / 2.87 |

`blockMesh` + `checkMesh` against the measured fit `t = 0.930 s × (N/23,040)^0.72`:

| level | predicted | actual | ratio |
| --- | --- | --- | --- |
| coarse | 0.930 s | 0.930 s | 1.000 |
| medium | 2.523 s | 2.132 s | 0.845 |
| fine | 6.846 s | 7.191 s | 1.050 |

The N^0.72 fit holds to −15 % / +5 % across a 16× cell-count range. The frozen §4
linear model would have predicted 0.93 / 3.72 / 14.88 s — over-predicting the fine
level by **2.07×**. The fit is the better instrument and this row is a third
independent confirmation of it.

**Exploratory compute NOT in the row above, named separately rather than
absorbed:** the design search and the three mechanism diagnoses ran in the
scratchpad and cost approximately **1.6 core-min** at ranks = 1 (roughly 20
`blockMesh`/`checkMesh` pairs plus two runs of an exact non-orthogonality
calculator). It bought the mechanism, the two validated predictors and the
five-point anchor sweep, all of which are recorded. It is disclosed, not hidden
inside the 0.4015.

## 11. What this record does NOT establish

- **Gate B is untouched.** No solver ran. Convergence, the strict completion rule
  and Gates 1–4 are all `PENDING`.
- **A mesh that passes gate A can still fail gate B.** Attempt 1's rung 1 diverged
  to negative temperature at iteration 180; nothing here shows attempt 2's will
  not, and nothing here should be read as saying so.
- **The launch needs the new instrument threaded into the grading path.**
  `sdk/workflows/rae2822_case9.py`'s `build_case` still builds attempt 1's
  inadmissible mesh. Running attempt 2's ladder through the solver requires that
  module to call this builder's dictionary — which is a change to a **grading
  path** after first compute, and therefore a standing-rule-2 question for the
  supervisor and for verification, not a lane's call.
