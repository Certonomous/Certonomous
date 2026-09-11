# DRIVAER LAYERFIX — PRE-REGISTRATION

**Team:** cfd | **Rung id:** `DRIVAER_LAYERFIX` | **Registered:** 2026-09-11
**Status at freeze:** PRE-COMPUTE. Verified at freeze time: neither
`verification/runs/navier_class/DRIVAER/LAYERFIX_A1_coarse_relativeSizes` nor
`verification/runs/navier_class/DRIVAER/LAYERFIX_A2_medium_relativeSizes`
exists on disk. No compute has been spent against this registration.

This registration is frozen by its commit sha. Gate, threshold, cap and label
below are closed the moment the first mesh build starts (CLAUDE.md rule 2).

---

## 1. THE DEFECT THIS TESTS

`snappyHexMesh` added **zero** boundary layers on the DrivAer geometry while
printing `Finished meshing without any errors`.

**Established by log measurement, 2026-09-11, zero compute** (all line numbers in
`verification/runs/navier_class/DRIVAER/DIAG_v3_coarse_explicitSnap_tol2_layersFixed/log.snappyHexMesh`):

| quantity | DrivAer coarse | SUBOFF_A1/L2 control |
|---|---|---|
| iteration-0 illegal faces | **54,848** (`:3211`) | 454 |
| iteration-0 extrusion | 6,236 / 23,365 = 26.7 % | 444,087 / 444,636 = 99.88 % |
| final extrusion | **0 / 23,365 = 0 %** (`:4944`) | 443,263 / 444,636 = 99.69 % |
| `Snapped mesh` -> `Layer mesh` cells | 128,230 -> **128,230** (net 0) | 6,051,099 -> 9,121,237 |
| `Mesh with layers :` line | **absent** | present |
| achieved layer cells | **0 / 116,825 = 0.000 %** | 3,070,138 / 3,112,452 = 98.640 % |

**Why the banner is emitted anyway:** snappy's final face-quality check runs on
the POST-layer mesh. With nothing added, that mesh IS the clean snapped mesh, so
the check is trivially clean. *The success report is produced by the failure.*

**Root cause, arithmetic:** DrivAer sets `relativeSizes false` with an absolute
`firstLayerThickness 0.00075` m against a **50 mm** surface cell (base block
0.8 m, `level (4 4)`) = **66.7 : 1** near-wall aspect. SUBOFF sets
`relativeSizes true` = **6.2 : 1**. Every other `addLayersControls` parameter is
effectively identical between the two (featureAngle 130, slipFeatureAngle 30,
maxThicknessToMedialRatio 0.3, nGrow 0, nLayerIter 50, nRelaxedIter 20).
The iteration-0 failure breakdown is dominated by the three sliver-sensitive
checks: `determinant < 0.001` **27,192**, `tetQuality < 1e-15` **15,767**,
`faceWeight < 0.05` **10,770**. The faceWeight violation is deterministic:
outer layer 1.831 mm against a 50 mm bulk cell gives
0.916 / (0.916 + 25) = **0.0353 < 0.05**.

**Two prior hypotheses are REFUTED and are not retested here:**
- `mergeTolerance` — 1e-8 gave 52,248 against 52,165, marginally worse.
- **face merging** — `truncateDisplacement` un-extruded **6 faces total** across
  all 32 iterations against **12,273** un-extruded by mesh-quality rejection
  (0.049 %).

---

## 2. SCOPE LIMIT — WHAT THIS REGISTRATION DOES NOT COVER

- **The zero was measured at COARSE ONLY** (128,230 cells, 50 mm surface cell).
  All four `addLayers true` diagnostics on this geometry are coarse. No DrivAer
  mesh has ever been built with layers on at medium or fine.
- **The three GRADED levels (`r1_coarse`, `r1_medium`, `r1_fine`) carry
  `addLayers false` in their own dicts** (`r1_fine/system/snappyHexMeshDict:12`).
  They have no layers because none were requested — **not** because snappy
  failed. Snappy's failure lives in the `addLayers true` diagnostics. Nothing in
  this document may be quoted as showing the graded family failed to mesh.
- **Do not cite "52,165 neg-vol cells / 40.7 %" against the graded family.**
  That figure belongs to an `addLayers true` diagnostic build.
  `MESH_FAMILY_MEASURED.json` records zero negative-volume cells at all three
  graded levels.
- This registration grades the **meshing mechanism only**. A PASS here does not
  certify near-wall resolution, y+, or fitness for any solve.

---

## 3. PREDICTION (made before the build, from the mechanism)

`level (4 4)` is constant across the graded family; the base block is what
refines. Under the CURRENT absolute spec the outer layer is 1.831 mm at every
level, so the faceWeight limb is predicted to fail at coarse ONLY:

| level | base | surface cell | near-wall aspect | faceWeight | vs 0.05 |
|---|---|---|---|---|---|
| coarse | 0.800 m | 50.00 mm | 66.7 : 1 | 0.0353 | **FAIL** |
| medium | 0.400 m | 25.00 mm | 33.3 : 1 | 0.0682 | pass |
| fine | 0.200 m | 12.50 mm | 16.7 : 1 | 0.1278 | pass |

**This row is a PREDICTION, not a result, and may not be quoted as covering
medium or fine.** `minDeterminant` — the dominant failure at 27,192 faces — is
aspect-driven too and is NOT asserted to clear at any level.

**Under `relativeSizes true`** the outer layer becomes 0.5 x local cell, so
faceWeight = 0.25 / (0.25 + 0.5) = **0.333** at EVERY level, independent of base
refinement — a factor 6.7 above the 0.05 limit. That is the mechanism's central
claim and the reason this fix is expected to work at all resolutions.

---

## 4. ARMS

**A1 (primary).** `LAYERFIX_A1_coarse_relativeSizes` — a byte-for-byte copy of
`DIAG_v3_coarse_explicitSnap_tol2_layersFixed` with exactly ONE change, the
thickness specification in `addLayersControls`:

    relativeSizes       true;          (was false)
    finalLayerThickness 0.5;           (replaces firstLayerThickness 0.00075)
    expansionRatio      1.25;          (unchanged)
    minThickness        0.02;          (was 0.0003 absolute; now relative)

`nSurfaceLayers 5` on all 50 patches, unchanged. Every other dict, the STL, the
blockMesh and `meshQualityDict` are unchanged. Serial, as the diagnostic was.

**A2 (contingent — runs ONLY if A1 is PASS).**
`LAYERFIX_A2_medium_relativeSizes` — same single change applied at medium.
Tests whether the fix is resolution-independent as predicted in §3.

---

## 5. GATE, THRESHOLD, LABEL — FROZEN

Graded by `scripts/check_snappy_layers.py` (committed alongside this file).
**The `Finished meshing without any errors` banner is not evidence and is not
read by the gate.** `checkMesh` rc is not read; printed verdict lines only.

**Threshold, pre-registered here BEFORE the build so it cannot be chosen to fit
the answer:**

> **`--min-added-frac 0.70`** and **`--min-mesh-layers 1.0`** — the guard's
> defaults, adopted for this rung now, sight-unseen.

| outcome | label |
|---|---|
| A1 achieved layer fraction **>= 70 %**, `Mesh with layers :` present, achieved per-patch table present with every patch >= 1.0 mesh layers, no negative-volume verdict from `checkMesh` | **PASS** — aspect-ratio mechanism CONFIRMED, fix works |
| A1 achieved fraction **> 0 % but < 70 %** | **GATE FAIL** — mechanism is real but `relativeSizes true` alone is not sufficient |
| A1 achieved fraction **= 0 %** (collapse reproduces) | **GATE FAIL**, and the aspect-ratio mechanism of §1 is **REFUTED**; cause lies elsewhere (candidate: the 50-patch topology and its feature-edge junctions) |
| build does not complete, or the guard cannot read a required field | **NOT A RESULT** |
| cap in §6 exceeded | run STOPS; **NOT A RESULT** |

The guard refuses rather than assumes on any absent measurement, so a missing
input yields **NOT A RESULT**, never a pass.

**Open hypothesis, registered as a hypothesis and NOT assumed:** `addLayers
false` on the graded family may have been set *because* turning layers on
produced nothing — in which case that registration choice is a symptom of this
defect rather than an independent decision. Neither this lane nor the supervisor
knows this. **A1 is its cheap falsifier.** It is recorded here so it cannot
later be presented as something that was known all along.

---

## 6. COST — CAP IS BINDING, AN OVERRUN STOPS THE RUN

Unit: core-minutes (wall s x ranks / 60). Both arms serial (1 rank), as every
DrivAer mesh build on this box has been.

| arm | basis (measured, same box) | estimate | **CAP** |
|---|---|---|---|
| A1 coarse | `DIAG_v3` meshed in 109.5 s serial = 1.83 core-min; + blockMesh, surfaceFeatureExtract, checkMesh | **3 core-min** | **15 core-min** |
| A2 medium | `r1_medium` meshed in 357.45 s serial = 5.96 core-min at `addLayers false`; layers on scales it ~3x | **18 core-min** | **60 core-min** |
| | | **21 core-min** | **75 core-min total** |

75 core-min = 1.25 core-h x $0.0513/core-h = **$0.064** — **derived at the
recorded rate, NOT measured**; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Far below the $25 pre-authorisation.

Estimate-versus-actual lands as a row in `docs/COST_CALIBRATION.md` at
completion (CLAUDE.md rule 12).

---

## 7. DISK PRECONDITION — THE BOX IS UNDER AN ALERT

Free space at freeze: **24 GiB (96 % used)**. MRF medium is still running and
returns ~2.7 GiB/h and 2 cores when it lands.

**Launch preconditions, all four required:**
1. MRF medium has completed and released its space.
2. `df` shows **>= 30 GiB free** immediately before staging. If not, the arm is
   **PENDING**, not run.
3. Never touch pid 316601 (ansys `rhoCentralFoam`) or cfd's MRF `simpleFoam`
   ranks.
4. A1 alone is expected to need < 0.5 GiB (128,230 cells); A2 < 2 GiB
   (748,658 cells). If either exceeds 3x its figure, stop and report.

---

## 8. WHAT A PASS DOES AND DOES NOT LICENCE

A PASS licences: re-registering the DrivAer mesh family with layers enabled, at
a resolution and thickness spec to be registered separately.

A PASS does NOT licence: quoting this rung as near-wall resolution for any
solve; grading any other family with `--min-added-frac 0.70` without registering
that threshold for that family first; or treating the §3 medium/fine rows as
measured.

---

## AMENDMENT 1 — 2026-09-11 — PRE-COMPUTE, EVIDENCE ADDED TO THE §5 HYPOTHESIS

**Legality condition and how it was checked:** this registration is still
pre-compute. Checked immediately before writing this section:
`verification/runs/navier_class/DRIVAER/LAYERFIX_A1_coarse_relativeSizes`
does not exist on disk, and neither does the A2 directory. No gate, threshold,
cap or label below or above is altered by this amendment; it adds evidence only.

**lines whose number changed above this section: 0**

### What was checked, at zero compute

§5 registers a hypothesis: *`addLayers false` on the graded family may have been
set BECAUSE turning layers on produced nothing.* A cheap partial falsifier
exists and was run — build chronology by file mtime:

| dict written | log finished | `addLayers` | case |
|---|---|---|---|
| 21:37:14 | 21:40:11 | **true** | `DIAG_v1_coarse_explicitSnap_tol2_noCarLayers` |
| 21:46:06 | 21:48:04 | **true** | `DIAG_v2_coarse_implicitSnap_tol1_layersON_BROKEN` |
| 21:46:07 | 21:48:03 | **true** | `DIAG_v3_coarse_explicitSnap_tol2_layersFixed` |
| **21:50:21** | 21:51:32 | **false** | `r1_coarse` |
| 21:54:59 | 22:01:09 | **false** | `r1_medium` |
| 21:55:00 | 22:34:29 | **false** | `r1_fine` |
| 23:15:40 | 23:17:09 | **true** | `DIAG_v5_coarse_layersON_mergeTol1e-8` |

All three `addLayers true` diagnostics ran first (21:40 -> 21:48) and **all three
produced 0 % layers**. The graded family's `addLayers false` dicts were written
at **21:50:21**, two minutes eighteen seconds after the last of them finished,
and the whole graded family was then built 21:51 -> 22:34.

### What this does and does not establish

**Does not establish:** causation or intent. An mtime ordering shows sequence,
not why a value was chosen. This is **not** a finding and the hypothesis is
**not** promoted.

**Does establish:** the sequence is the one the hypothesis predicts, and it is
not the one the competing explanation predicts. If `addLayers false` had been an
independent design decision, there is no reason for the layers-off dicts to
appear two minutes after three consecutive layers-on collapses. The hypothesis
is therefore **registered with supporting chronological evidence, still
unproven**, and A1 remains its real falsifier.

### Filing gap found while checking this

Git history could not be used, because **the graded DrivAer case dicts are
untracked** — `git ls-files verification/runs/navier_class/DRIVAER/` returns
**5 files** for the entire directory, and `git check-ignore` returns nothing, so
they are not ignored, merely never committed. File mtime is consequently the
only chronological evidence that exists for these builds, and mtime does not
survive a copy. Recorded here as a defect in its own right; not fixed by this
lane, and not a blocker for A1.

---

## AMENDMENT 2 — 2026-09-11 — PRE-COMPUTE — §7's DISK PRECONDITION, DERIVED

**Legality condition and how it was checked:** still pre-compute. Checked
immediately before writing:
`verification/runs/navier_class/DRIVAER/LAYERFIX_A1_coarse_relativeSizes` does
not exist on disk, and neither does the A2 directory. **No gate, threshold, cap
or label is altered** — §5's gate table and §6's 75 core-min cap stand exactly
as frozen. This amendment touches one launch **precondition** only.

**lines whose number changed above this section: 0**

### Why this is being derived rather than adjusted

§7 requires **>= 30 GiB free**. That number was never derived — I wrote it, and
I did not compute it from anything. The supervisor has since measured that the
box sits at 24 GiB with MRF's ET8000 tree alone holding 17 GB, and that medium
completing does not free space but only stops adding, so nothing on the current
trajectory reaches 30 GiB.

**That fact is not the justification for this amendment and must not be read as
one.** Changing a precondition because it stands in the way is fitting the gate
to the circumstance. What follows is A1's footprint derived from builds already
on disk; the fact that the derived figure happens to be satisfiable is a
*consequence*, not the reason. **Had the derivation come out above 30 GiB, the
correct outcome was `BLOCKED` on disk, and that is what this section would say.**

### Measured inputs (all read off this box, 2026-09-11, zero compute)

**`writeFlags ( )` is EMPTY** in the DrivAer dict — snappy writes no
intermediate meshes, only the final mesh to `constant`. Confirmed by directory
listing: `DIAG_v3` contains `0/`, `constant/`, `system/` and no intermediate time
directories. **Therefore peak disk == final disk for these builds**, and no
intermediate-write multiplier applies. (SUBOFF uses `writeFlags (noRefinement)`,
which also suppresses them.)

| case | measured dir | cells | B/cell |
|---|---|---|---|
| `r1_coarse` (no layers) | 30 MiB | 128,230 | 245 |
| `DIAG_v3` (layers attempted, 0 added) | 46 MiB | 128,230 | 376 |
| `r1_medium` (no layers) | 140 MiB | 748,658 | 196 |
| `SUBOFF_A1/L1` (layers ACTUALLY added) | 699 MiB | 3,268,613 | 224 |

`r1_fine` (6,136 MiB) is **excluded as a basis**: its directory carries solve
output, not mesh alone, and using it would inflate the estimate ~5x.

### Derivation

A1 at 100 % extrusion: 128,230 snapped + (23,365 faces x 5 layers) = **245,055
cells**, a factor 1.911 on the snapped mesh.

- on the `DIAG_v3` basis: 46 MiB x 1.911 = **88 MiB**
- on the `SUBOFF_A1/L1` layers-on basis (224 B/cell): **52 MiB**
- **conservative A1 footprint: 90 MiB**

A2 at the same factor: 748,658 -> 1,430,729 cells.

- on the `r1_medium` basis (196 B/cell): 267 MiB
- on the `DIAG_v3` basis (376 B/cell): 513 MiB
- **conservative A2 footprint: 550 MiB**

**The §7 per-arm figures as frozen — A1 < 0.5 GiB, A2 < 2 GiB — survive this
derivation unchanged and are retained.** They were already conservative by 5x
and 3.7x respectively. Only the free-space gate was undderived.

### The replacement precondition

> **Free space before staging must be at least `max(10 x derived arm footprint,
> 8 GiB)`.** For A1 that is `max(0.88, 8)` = **8 GiB**. For A2,
> `max(5.37, 8)` = **8 GiB**.

The two terms, stated separately because they have different standing:

1. **`10 x derived arm footprint` is derived** — 90 MiB and 550 MiB above, times
   ten. The 10x covers the one genuinely uncertain input: A1's cell count is a
   *prediction* (245,055 assumes 100 % extrusion), so if the fix overshoots or
   the mesh behaves unexpectedly the footprint could exceed the estimate. It is
   not covering intermediate writes, because `writeFlags ( )` shows there are
   none.
2. **The `8 GiB` absolute floor is a JUDGEMENT, not a derivation**, and is
   labelled as such. It is anchored on two quantities: A1+A2 combined are
   0.64 GiB, so they cannot be what tips the box; and the floor leaves roughly
   two hours of headroom at the box's stated ~2.7 GiB/h concurrent write rate for
   peers. Its purpose is protecting **other people's runs** — pid 316601 and the
   MRF `simpleFoam` ranks — from a full disk, which is not a quantity A1's own
   footprint can speak to. **Anyone is free to argue the floor should be higher;
   nobody should present it as measured.**

**For A1 the binding term is the floor, not A1's own footprint** — A1 needs
0.88 GiB by the derived rule and is held to 8 GiB by the shared-box judgement.
Stated plainly so the 9x gap is visible rather than buried.

### Consequence and status

Free space read while writing this section: **23 GiB** (down from 24 GiB earlier
today — it is falling, which is an argument for a real floor rather than none).

**A1 is therefore NOT blocked on disk.** It remains **`PENDING`** on the other
§7 preconditions, which are unchanged: MRF medium must complete first, and pid
316601 and the MRF `simpleFoam` ranks must not be touched. A2 remains contingent
on A1 being PASS.

**Not verified by this lane:** the supervisor's measurement that MRF's ET8000
tree holds 17 GB and that medium completing frees nothing. I did not re-measure
it, and this derivation does not depend on it — the derived requirement is
8 GiB whether or not medium frees anything.

