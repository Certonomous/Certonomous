# T5 AMENDMENT 9 — DRAFT, NOT ADOPTED, NOT PROMOTED

**Status: `PENDING` the heat-transfer supervisor's personal read of the diff
(`SUPERVISION_CHARTER.md` §3 check 1). Nothing in this file is in force.**
The frozen `build_t5.py` (blob `c7b7063d`) is **UNCHANGED on disk**; the proposal
is held beside it as `build_t5.A9_PROPOSED.py` (blob `9d7be1cb`) with its unified
diff at `build_t5.A9.diff` (blob `f8d37ff3`), exactly as AMENDMENT 3 held
`analyse_t5.A3_PROPOSED.py`. **No queue entry was dropped and no solver ran.**

Proposed document version bump: **1.7 → 1.8**. **Lines whose number changed in
`T5_PREREGISTRATION.md`: 0** — this draft is a separate file and amends nothing
until the supervisor promotes it.

Drafted by the T5 grading lane on the heat-transfer supervisor's ruling
`[lab-attributed]`, relayed 2026-08-26 ~22:20Z: *"`build_t5.py` is not in the
§16.9 freeze set and `S_m` has never run, so implementing its fluid-only meshing
branch is legal as a pre-first-compute-for-`S_m` disclosure amendment."*

---

## A9.1 Condition (`CLAUDE.md` rule 2), and how it was checked

Rule 2's second limb closes gates **after first compute**. Compute HAS happened
on this rung — `X_2d`, `T5_CUBE_c`, `H_c` and `T5_CUBE_m` are DONE and `P_m`,
`L_m`, `T5_CUBE_f` are running — so this draft is **pre-first-compute for `S_m`
ONLY**, and it is therefore held to the stricter standard: **it moves no gate,
band, threshold, floor, cap, label, control or verdict for ANY case, `S_m`
included.**

Checked at 2026-08-26T22:30:21Z by `ls`, not asserted:

- **`verification/runs/T-family/T5_runs/S_m` does not exist** — no case directory.
- **No `STATUS.S_m` and no `DONE.S_m`** at the `T5_runs` root.
- **Zero core-minutes have been spent on the `S_m` arm.** It has never been
  built, never been armed, never been enqueued, and its one drafted queue entry
  has only ever been REFUSED (§A9.6).
- `build_t5.py` is **NOT in the §16.9 freeze set**, which says so in terms:
  *"`build_t5.py` is NOT in this set and is NOT written."* Its blob is `c7b7063d`.

Nothing a verdict depends on is read by this draft. The one measurement it takes
(§A9.4) is a **registered input to `S_m`'s boundary condition**, prescribed by §8
`DS` before any compute, not a graded quantity.

## A9.2 The defect this repairs, stated as it actually is

AMENDMENT 8(d) recorded *"`S_m` is NOT enqueued: its launcher refuses without
`M`'s surface T."* **That is only one of two refusals, and it is the one that has
since become clearable.** `build_t5.py` refuses `S_m` twice:

1. **l.575** — `"%s (constant-T arm) needs --s-m-tsurf = area-averaged conjugate
   surface T from T5_CUBE_m (§8 DS); it is not built before T5_CUBE_m has run"`.
   **Now clearable:** `T5_CUBE_m` is DONE under the strict rule and its conjugate
   surface `T` is on disk at `T5_CUBE_m/5000/air/{T}`.
2. **l.624** — `"S_m fluid-only meshing (remove epoxy cells) is not implemented
   until T5_CUBE_m has run"`. **NOT clearable by `M` running.** It is the `else`
   arm of the conjugate `splitMeshRegions` step and there is no fluid-only
   meshing code behind it at all. Its wording implies a precondition; what it
   guards is an unwritten branch. **That gap is what A9 fills, and naming it
   correctly is half the point of this draft.**

## A9.3 What changes — 4 lines removed, 65 added, confined to one branch and one new function

Diff held at `verification/runs/T-family/T5_runs/build_t5.A9.diff` (85 lines,
two hunks) for the supervisor's own read. Summary, so a reader knows what to look
for rather than taking this summary as the check:

**Hunk 1 — the meshing branch (l.618–628).** `splitMeshRegions -cellZonesOnly
-useFaceZones -overwrite` moves OUT of the `if conjugate:` and runs for both
arms, because both arms need the same cut; the branch that follows chooses what
to do with the result — `rename_interface_patches(case)` for the conjugate arm
(byte-unchanged), `strip_solid_region(case)` for `S_m`. The `refuse` at l.624 is
removed. **The cleanup loop below it is untouched** and needs no change: its
entries are existence-guarded.

**Hunk 2 — one new function, `strip_solid_region()`**, inserted after
`rename_interface_patches` and before `build_x2d`. It:

- renames the four air-side interface patches `<face>_air_to_epoxy` → `<face>`,
  the same bare names `analyse_t5.py`'s `YPLUS_WALLS` reads;
- inside those four patch blocks **only**, turns `type mappedWall;` into
  `type wall;` and drops `sampleMode` / `sampleRegion` / `samplePatch` /
  `offsetMode` / `offset`, because they name a neighbour region that is gone;
- deletes `constant/epoxy`, `system/epoxy`, `0.orig/epoxy`, `0/epoxy` and the
  `cellToRegion` addressing left by the split;
- rewrites `constant/regionProperties` to the fluid-only form;
- **re-reads the bytes back from disk and REFUSES** on: a cube patch absent, an
  un-renamed `_air_to_epoxy` name, a surviving `mappedWall`, a surviving
  `sampleMode`/`sampleRegion`/`samplePatch`, or a surviving `epoxy` region.
  Six refusals, all on facts read back rather than on the code's intentions.

**The fluid-side cells are removed by `splitMeshRegions` itself**, which is the
whole reason the conjugate cut is reused: the air region's `polyMesh` already
contains only air cells. `strip_solid_region` does not touch geometry.

**What A9 does NOT change.** No band, floor, gate, threshold, cap, label or
control. Not `analyse_t5.py` (`9c2c1d44`), not `mark_done_t5.py` (`a74ce20d`),
not `run_one_t5.sh` (`313df45c`), not `digitise_t5.py`, not
`T5_PREREGISTRATION.md`. Not `air_fields()` — its non-conjugate branch
(`cube_T = ["type fixedValue;", "value uniform %g;" % t_surf]`) **already
existed** and is used unchanged. Not `main()` — `--s-m-tsurf` already existed.
**0 `ast.Assert` nodes** in the proposed file (L-332), and it parses clean.

## A9.4 The registered input, MEASURED

§8 `DS` registers the cube surface at *"a uniform temperature equal to the
**area-averaged** conjugate surface temperature from the conjugate medium case."*
Measured from `T5_CUBE_m` at `5000/`, on a scratch copy so the DONE case was not
written into, with OpenFOAM's own `surfaceFieldValue` (`areaIntegrate` of `T`
with `writeArea true`, per patch, air side):

| patch | ∫T dA (K·m²) | A (m²) | patch-mean T (K) |
|---|---:|---:|---:|
| `cube_front` | 0.03681321204 | 0.0001125 | 327.228551 |
| `cube_rear` | 0.03720046580 | 0.0001125 | 330.670807 |
| `cube_top` | 0.03737210366 | 0.0001125 | 332.196477 |
| `cube_side_n` | 0.07487779141 | 0.0002250 | 332.790184 |
| **total** | **0.18626357291** | **0.0005625** | — |

**Area-averaged `T_surf` = 0.18626357291 / 0.0005625 = `331.135241 K`.**

Sanity, stated rather than assumed: it lies between the registered inlet
`T_IN = 293.65 K` and the core `T_CORE = 348.15 K`, as a cube surface under a
9:1 conjugate jump must; the half-domain areas are consistent with `H = 0.015 m`
(`cube_side_n` is a full face at `H²`, the other three are half faces at `H²/2`).

**DISCLOSED, and left for the supervisor rather than silently repaired.**
`air_fields()` writes the value with `%g`, so `0.orig/air/T` carries
`value uniform 331.135;` — **331.135, not 331.135241**. The loss is 0.24 mK on a
driving difference of ≈ 37.5 K (6.4e-06 relative) and moves no registered band.
**A9 does not change that format string**, because `%g` is shared by every field
of every case and widening the diff to chase 0.24 mK would put the conjugate
arms' bytes at risk for no physical gain. If the supervisor wants the full
precision, the targeted change is `%g` → `%.9g` on that one line, and it should
be its own amendment with its own byte-identity control.

## A9.5 Driven before proposal — two controls, and the second is the one that matters

Driven on scratch copies outside the run tree; **no solver ran**, and the live
`T5_runs` tree was not written to. Scratch spend ≈ 0.4 core-min, **not charged to
the rung** (the AMENDMENT 8 precedent).

**The build itself.** `build_t5.A9_PROPOSED.py --case S_m --s-m-tsurf 331.135241`
→ **rc 0**, 7 s. Result, verified by reading the built case:

- `constant/` holds `air g polyMesh regionProperties` and **no `epoxy`**;
  `find` for `*epoxy*` over the whole case returns **nothing**.
- **`cells: 212942`** — exactly `T5_CUBE_m`'s air-region count (the conjugate
  case is 212 942 air + 3 272 epoxy). The epoxy cells are gone and no fluid cell
  moved.
- All four cube patches read `type wall;` with `nFaces`/`startFace` unchanged;
  `grep -c 'mappedWall|sampleMode|sampleRegion|samplePatch'` = **0**.
- `constant/regionProperties` → `regions ( fluid (air) );`
- `0.orig/air/T` `cube_front` → `type fixedValue; value uniform 331.135;`

**CONTROL 1 — the conjugate path is byte-for-byte unchanged.** `T5_CUBE_c` was
built TWICE into separate scratch roots, once with the frozen `build_t5.py` and
once with `build_t5.A9_PROPOSED.py`; `diff -r -x 'log.*'` between the two trees
reports **NO DIFFERENCE**. A9 cannot alter a conjugate case, and this is measured
rather than argued from the diff's shape.

**CONTROL 2 — the mesh-quality result is the conjugate air region's own, not
something A9 introduced.** `S_m`'s `checkMesh -allRegions -allTopology
-allGeometry` reports `***Cells with small determinant (< 0.001) found, number of
cells: 15727` and `Failed 1 mesh checks.` **The conjugate `T5_CUBE_m` built with
the same builder reports the SAME 15 727 cells and the same single failed check
on its air region** (with `Mesh OK.` for epoxy). The two are the same mesh. This
is AMENDMENT 5's already-disclosed mesh-quality mismatch — **expectation, not
precondition** — and it is unchanged, neither improved nor worsened, by A9.

*(The `Mesh OK.` in the live `T5_CUBE_m/log.checkMesh` is not a contradiction:
that file was rewritten by the launcher's own `checkMesh` at 20:57Z, which does
not pass `-allGeometry`, so it never ran the determinant check. Named here
because a later reader comparing the two files would otherwise be misled.)*

## A9.6 The queue entry — still HELD, and what the validator says both ways

The drafted entry is at
`verification/runs/T-family/T5_runs/queue_drafts/T5_S_m_BLOCKED.json`
(`cost_core_min_estimate` 489.0, **`cap_core_min_registered` 1467.0**,
`--timeout 88020`, `--ranks 1`, `--no-detach` per AMENDMENT 6(b),
`prereg_commit` `299296a29b30def2c9fec910b66a554b4f4f11cd`). It is **NOT in
`verification/queue/heat-transfer/` and was not put there.**

| probe | `scripts/queue_entry_check.py` | rc |
|---|---|---|
| the held entry, real `cwd` (`T5_runs/S_m`, not built) | `REFUSED … AGE-GUARD: cwd … does not exist as a directory, so it cannot be shown free of a prior answer.` | **2** |
| the same entry re-pointed at the A9-built case | `ACCEPTED … team=heat-transfer case=T5_S_m ranks=1 est=489.0 core-min` | **0** |

**Read together these say exactly one thing: every clause of the entry other than
the existence of a built case already passes, and the built case is precisely
what A9 supplies.** The validator's own note is carried unsoftened — *"acceptance
is a mechanical guard only. Enqueueing is not authorisation; SUPERVISION_CHARTER
§3 check 4 is the supervisor's own and is not performed by this script."*

**Core-minutes added to the heat-transfer queue by this draft: 0.0.**

## A9.7 What is NOT done by this draft

- **Not promoted.** `build_t5.py` on disk is still blob `c7b7063d`.
- **Not enqueued.** No file was written into `verification/queue/heat-transfer/`.
- **No solver ran** on `S_m`, and no case was built inside `T5_runs/`.
- **No gate, band, threshold, floor, cap, label, control, verdict, mesh,
  `writeInterval`, `deltaT` or field set moves**, for `S_m` or any other case.
- **`T5_PREREGISTRATION.md` is not touched**; if the supervisor promotes this,
  the amendment text lands there as AMENDMENT 9 with the version bump and the
  `lines whose number changed above this section: 0` assertion.
- Nothing was sent, filed, uploaded, posted or registered outside this box
  (rule 7), and no permission setting, `CLAUDE.md` or `.claude/` config was
  touched (rule 9).
