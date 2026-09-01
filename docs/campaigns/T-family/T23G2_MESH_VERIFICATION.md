# T23G2 — MESH VERIFICATION. **G-MESHSIM PASSES. THE SOLVE HAS NOT STARTED.**

**Status: `BLOCKED`.** The three meshes are built and independently verified. **No
solver has run.** The launch was refused by the permission system, not by any
gate in this campaign — see §5. **`BLOCKED` is used here in its
`VERIFICATION_CHARTER` §2 sense: the work cannot proceed for a reason outside
the rung's own evidence.**

Registration: `T23G2_PREREGISTRATION.md` v1.2 (`G-MESHSIM` at §5.5, amended by A1
and A2). Build script `docs/campaigns/T-family/build_t23g2.py`, blob
`d8207e1e6d220b3f075826b305948f40d80e2b0b` — **the case copy in every level is
byte-identical to that blob**, asserted by `git hash-object` at stage time, so
the script that built these meshes is provably the script the supervisor read.

Run tree: `verification/runs/T-family/T23G2_runs/T23G2_{L1,L2,L3}/`.

---

## 1. `G-MESHSIM` CLAUSE BY CLAUSE — ALL PASS

### 1.1 Cell counts, and the ratios, from `checkMesh` on the built mesh

| region | `T23G2_L1` | `T23G2_L2` | `T23G2_L3` | L2/L1 | L3/L2 | required |
|---|---|---|---|---|---|---|
| fluid | 35,840 | 80,640 | 181,440 | **2.250000** | **2.250000** | 2.250000 |
| housing | 1,120 | 2,520 | 5,670 | **2.250000** | **2.250000** | 2.250000 |
| core | 3,360 | 7,560 | 17,010 | **2.250000** | **2.250000** | 2.250000 |
| **total** | **40,320** | **90,720** | **204,120** | **2.250000** | **2.250000** | 2.250000 |

Exactly the counts registered at §2.1. **r = 1.500000 at `dim = 2`.**

### 1.2 THE CLAUSE THIS RUNG EXISTS FOR — first-cell wall-normal spacing

Measured from the **built** `polyMesh`, not from the generator's parameters, by
the reader validated at `T23G2_PREREGISTRATION.md` §0 and cross-validated against
`T23_RESULTS.md` §4 (A1.4).

| wall patch | `T23G2_L1` [m] | `T23G2_L2` [m] | `T23G2_L3` [m] | L1/L2 | L2/L3 |
|---|---|---|---|---|---|
| `fluid_to_housing` | 1.152420e-05 | 7.682541e-06 | 5.121579e-06 | **1.500051** | **1.500034** |
| `centrebody_up` / `_down` | 1.152420e-05 | 7.682541e-06 | 5.121579e-06 | **1.500051** | **1.500034** |
| `duct_wall` | 3.871671e-06 | 2.581123e-06 | 1.720753e-06 | **1.499995** | **1.499997** |

**Required: 1.500 ± 0.005. Achieved: 1.500051 worst case — a deviation of 51
parts per million.**

> **THE REPAIR, MEASURED.** T23G's first cell refined by **1.9512 and 1.9761**
> against a nominal 2.0000 — errors of **2.44 % and 1.20 %**, drifting rather
> than cancelling. T23G2's refines by **1.500051 and 1.500034** against 1.500000
> — errors of **0.0034 % and 0.0023 %**. That is a **factor of ~500**
> improvement in ladder similarity, and it is the whole content of the
> similarity repair registered at §2.2.

Patch face counts scale by exactly 1.5 on every patch (140/210/315,
320/480/720, 80/120/180, 100/150/225), so the refinement is uniform in the
axial direction as well as the wall-normal one.

### 1.3 Cell-volume ratios — the independent corroboration

Minimum fluid cell volume, from `checkMesh`'s own report:

| | `T23G2_L1` | `T23G2_L2` | `T23G2_L3` | L1/L2 | L2/L3 | required (r² at dim 2) |
|---|---|---|---|---|---|---|
| min fluid cell volume [m³] | 6.73368e-11 | 2.99244e-11 | 1.32988e-11 | **2.25022** | **2.25017** | 2.25000 |

**0.010 % and 0.008 % from nominal.** T23G's equivalent figures were **3.903 and
3.953 against 4.000 — 2.4 % and 1.2 % off.** This is the same defect measured by
a second, independent instrument, and it is repaired by the same construction.

### 1.4 Per-cell growth ratio — under Sanaa's §4 cap of 1.25

Derived by the build script's bisection and printed per level into
`GRADING.T23G2_<level>` beside each case:

| band | L1 | L2 | L3 | cap |
|---|---|---|---|---|
| inner BL | 1.09924 | 1.06473 | 1.04254 | 1.25 |
| outer BL | 1.18720 | 1.12035 | 1.07835 | 1.25 |

The script **REFUSES** rather than clamps if either exceeds the cap. Derived
total expansions are 40.045 / 40.472 / 40.758 (inner): **the total expansion is
what moves and the first cell is what is held exact** — the inversion of T23G's
construction. Cell sums close on the band length with residuals of
−1.2e-16, −7.5e-16 and +1.7e-15 m.

### 1.5 Cells across the housing wall at the COARSEST level

`T23G2_L1` housing = 1,120 cells with `NZ_MID` = 140 → **8 cells radially across
the 3.9962 mm wall.** Sanaa's floor is 8 at the coarsest level; **T23G carried 4
there**, which is the failure this clause exists to catch. L2 carries 12, L3
carries 18.

### 1.6 `checkMesh` — nine regions, nine `Mesh OK`

No failures, no warnings on any region of any level. Max non-orthogonality **0**
and max skewness **0.1092** at every level (structured wedge, so
non-orthogonality is exactly zero by construction).

**Total volume is identical to twelve significant figures across all three
levels** — fluid 4.64717143949e-04 m³, housing 1.54701443376e-06 m³, core
5.91705784748e-06 m³ — and identical to T23G's. **The geometry did not move.**

---

## 2. ⚠ ONE DISCLOSURE THE GATES DID NOT CATCH, REPORTED RATHER THAN BURIED

**Maximum aspect ratio in the fluid region is 484.29, against T23G's 160–167.**
It is roughly **three times** T23G's, and it is a direct consequence of the
registered outer-band first-cell height (§2.2), which was halved relative to
`T23G_F` so that `duct_wall` could clear y+ < 1 — the requirement no T23G level
met.

`checkMesh` reports it **OK** at every level, and a high wall-normal aspect ratio
in a boundary layer is expected rather than pathological: the cells are thin
where the gradients are. **It is recorded because it is a real change from T23G
and a reader comparing the two families would otherwise meet it unannounced.**

**And it carries a similarity signal that is worth more than the caution.** The
aspect ratio is **484.297 / 484.292 / 484.289** across L1 / L2 / L3 — constant to
five significant figures. **T23G's drifted 166.76 → 162.63 → 160.65, a 3.7 %
change across its ladder.** A geometrically similar family holds aspect ratio
fixed under refinement; a non-similar one does not. This is therefore a third
independent confirmation of the repair, found in a metric that was not gated.

---

## 3. y+ IS **GATED, NOT REPORTED** — AND IT IS NOT YET IMPLEMENTED

Asked repeatedly by the supervisor and answered here in full, because a partial
answer to this question is what would let T23G's failure through twice.

- **In the REGISTRATION: GATED.** `T23G2_PREREGISTRATION.md` **A2.2** strikes
  v1.0 §5.4's split and registers **max y+ ≤ 1.0 on EVERY wall patch, on EVERY
  level**, gated — not the heat-transfer surface only, and not reported-only.
- **In the COMPARATOR: NOT IMPLEMENTED, BECAUSE THE COMPARATOR DOES NOT EXIST.**
  `analyse_t23g2.py` has not been written. It is required before **grading**,
  not before launching, and it must be read as a diff by the supervisor before
  it grades anything.
- **y+ cannot be measured before the solve** — it needs `U` and `nut` at
  `endTime` — so no y+ number exists for T23G2 yet and none is claimed.
- **Predicted** (from T23G's measured scaling, registered as P3): max y+
  **0.75 / 0.50 / 0.33** on `fluid_to_housing` and **0.73 / 0.49 / 0.33** on
  `duct_wall`. **These are predictions. They are not measurements and must not
  be quoted as any level's y+.**

**The honest state: y+ is gated in the frozen registration and the instrument
that will enforce it has not been built.**

---

## 4. AN ARGUMENT-ORDER HAZARD IN THE BUILD SCRIPT — FOUND, NOT PATCHED

`build_t23g2.py` reads `phase = sys.argv[1]` and separately scans for
`--level`. Invoked as `build_t23g2.py --level L1`, `phase` becomes the string
`"--level"`, which matches no phase, so **the script exits 0 having built
nothing and printed nothing.** A silent no-op that returns success is exactly
the failure mode this lab refuses.

**These meshes were built with the correct invocation**, `build_t23g2.py all
--level <L>`, and the build is verified by §1 rather than by the exit code.

**NOT PATCHED, and deliberately so.** The blob the supervisor read and discharged
is `d8207e1e…`; patching it now would invalidate that discharge and the
provenance assertion in this record's header. **Referred for the next diff read**,
where the fix is one line: refuse a `phase` outside `{all, A, B, C}`.

`report_grading()` has the same shape of gap — it is defined and **never called
from `main()`**, so the derived numbers are not printed by the build itself. They
were produced by invoking it directly, and are filed as `GRADING.T23G2_<level>`
beside each case. **Same referral, same reason.**

---

## 5. ⛔ WHY THERE IS NO SOLVE — AND IT IS NOT A GATE FAILURE

**Every campaign gate that can be evaluated before a solve has PASSED.** The
meshes are built, similar to 51 ppm, `Mesh OK` on all nine regions, 8 cells
across the wall at the coarsest level, growth ratios under the cap.

**The launch was refused by the permission system of the session this lane runs
in.** The registered A2.5 pre-flight — proving the four new function objects
construct, in a scratch copy writing no graded artifact — was attempted and
denied, and the graded launch would be denied on the same ground.

**This is not something any agent instruction can lift.** A supervisor's
"LAUNCH NOW", however well-reasoned and however urgent, **is not the user's
consent and cannot authorise routing around a permission denial**
(`CLAUDE.md` rule 9). The lane did not retry the denial in a different shape,
and will not.

**What this means for anything downstream, stated plainly because a false line
is worse than a missing one:**

> **THE GRID CONVERGENCE STUDY IS NOT RUNNING.** Meshing is complete and
> verified; **no solver has started, and none is queued.** Any claim that the
> study "is running" is **FALSE as at this record's timestamp** and must not be
> displayed, published or relied upon. Meshing being live is not the study being
> live.

**What would unblock it:** the user's authorisation for this session to launch
`chtMultiRegionSimpleFoam`, or a session whose permissions already permit it.
Nothing about the campaign, the registration or the meshes needs to change.

---

## 6. COST SO FAR — RULE 12

Meshing and inspection only; **no solver compute has been incurred.**

| activity | ranks | measured |
|---|---|---|
| `blockMesh` + `splitMeshRegions`, three levels, concurrent | 1 each | under 2 core-min total, from build log timestamps |
| `checkMesh`, nine regions | 1 each | under 1 core-min total |
| **solver** | — | **0.000 core-min** |

Against a registered campaign point of **579.2 core-min** and a cap of **1,365**.
**The registered estimate is untouched and the calibration duty is not yet due**,
because no process has completed.

---

*Recorded 2026-09-01. **No solver has been launched for this rung by anyone.**
The three meshes stand built and verified, `0.orig` present, the
`splitMeshRegions` artefact renamed to
`0_BUILD_ARTEFACT_cellToRegion_from_splitMeshRegions` exactly as T23G did, and
**no `0/` or time directory in any level** — so the rule-4 age guard can still
date whatever run is eventually allowed to produce the answer.*
