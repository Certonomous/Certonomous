# DRIVAER LAYERFIX B2 — `minMedialAxisAngle`, THE LAST LIVE LIMB — PRE-REGISTRATION

**Team:** cfd | **Rung id:** `DRIVAER_LAYERFIX_B2` | **Registered:** 2026-09-11
**Status at freeze:** PRE-COMPUTE. Verified at freeze time:
`verification/runs/navier_class/DRIVAER/LAYERFIX_B2_coarse_medialAxisAngle`
does not exist. No compute has been spent against this registration.

Not an extension of `DRIVAER_LAYERFIX` or of `B1`; both closed at their first compute.
**Not arm A2**, which is a medium-resolution repeat contingent on A1 being `PASS`.

## 1. WHAT IS SETTLED — NOT RE-DERIVED

- **H1 REFUTED** (B1, `9a8242e57`): `maxThicknessToMedialRatio` 0.3 → 0.6 moved **zero**
  of the blocked patches past one layer.
- **H3 REFUTED** (ray measurement, `a5b661048` line of work): every blocked patch has a
  **median clear gap of 42.65–309.30 mm**. `Mirrors2` sits in 309 mm with ~90 % of its
  faces striking nothing, and takes 0.00 layers. Clearance is not the blocker.
- **Patch shape NOT SUPPORTIVE** (`bb50e70e6`): `perimeter²/area` gives M = 12/17, the
  **degenerate** classifier. No signal.
- **Baseline, measured twice:** A1 **R = 0**, B1 **R = 0**. Global achieved layer cells
  A1 **50.057 %**, B1 **50.475 %**.

## 2. THE HYPOTHESIS AND ITS DIRECTION — READ FROM THE SOURCE, NOT ASSUMED

> **H2b: `minMedialAxisAngle 90` marks too many points as medial-axis, and the
> resulting thickness reduction is what holds the 12 candidates at zero.**

`medialAxisMeshMover.C:367` passes `minMedialAxisAngleCos` into `isMaxEdge`, whose own
comment reads *"Both end points of edge have very different nearest wall point. Mark
both points as medial axis points."* The test is on the angle between each endpoint's
vector to its nearest wall point. **Raising the angle makes the test stricter, marks
FEWER points as medial axis, and so relieves the reduction.** That is the relieving
direction and it is verified in the source, not inferred from a tutorial.

**A1's own log shows the limb never stops:** medial-axis thickness reduction fires on
11,391 → 7,862 → … → 6,577 nodes, once per iteration, **59,321 node-events**, plateauing
rather than decaying.

## 3. THE ONE CHANGE

Copy of `LAYERFIX_A1_coarse_relativeSizes`'s inputs — **A1, not B1**, because B1's change
is refuted and carrying it would confound two variables — with exactly one edit:

    minMedialAxisAngle  130;      (was 90)

`maxThicknessToMedialRatio` returns to **0.3**, A1's value. Everything else byte-identical,
verified by `cmp` before launch. Serial, 1 rank.

**Noted, NOT changed, so it cannot become a silent fourth variable:** `nMedialAxisIter` is
absent from the dict and defaults to `nTotalPoints` (`medialAxisMeshMover.C:182`), i.e.
an unlimited walk. It is a live candidate for a later rung and is **not** touched here.

## 4. THE GROUP — 12 REAL CANDIDATES

`BrakeDiscfront`, `BrakeDiscrear`, `CTRL_SURFACE_Outlet`, `ExhaustSystem1`, `Mirrors2`,
`Rimsfront`, `Rimsrear`, `WheelSupportfront1`, `WheelSupportfront2`, `WheelSupportrear`,
`Tiresfront`, `Tiresrear`.

**`TirePlinthfront` and `TirePlinthrear` are EXCLUDED**: they carry **zero mesh faces**
and were never layer candidates. This corrects the 14-member group I registered in B1 §4.

CONTROL (must not regress): `floorNoSlip` 4.62, `NotchbackRoof` 4.45,
`NotchbackWindowrear` 4.34, `NotchbackB_Pillar` 4.31, `BodyHood` 4.14 (A1 values).

## 5. NOISE FLOOR — UNCHANGED, BECAUSE IT FIRED AGAINST ITS AUTHOR

> **A candidate counts as REACHED only at achieved mesh layers ≥ 1.00.**

Unchanged from B1 §5, where it stopped `CTRL_SURFACE_Outlet` 0.66 and `Mirrors2` 0.55
being read as success. It stays at 1.00 precisely because it has already cost this lane
a result it wanted.

## 6. BASELINE AND DEGENERACY — BOTH WRITTEN DOWN BEFORE THE RUN

**MAJORITY-CLASS BASELINE: R = 0 of 12.** Measured twice, at A1 and at B1. **Any R that
does not exceed 0 is not an improvement over doing nothing, and R = 0 is therefore the
number this rung must beat to say anything at all.** Registering it here means the score
cannot later be read without its base rate.

**DEGENERACY LIMB.** If the outcome is uniform across the group — **all 12 reaching, or
all 12 not reaching** — the per-patch resolution of this measurement is zero and R alone
cannot distinguish "the limb was relieved" from "something global moved everything".
In that case the verdict is decided **only** with the control group and the global
fraction beside it, and **an all-12-reaching outcome with any control regression is
`NOT A RESULT`**, not a confirmation.

## 7. THE GATE — FROZEN, EVALUATED IN ORDER, EVERY OUTCOME IN EXACTLY ONE ROW

**R** = candidates of the 12 reaching ≥ 1.00. **G** = global achieved layer-cell fraction.
**C** = minimum control-group achieved layers. **P** = candidates whose mesh-face count
changes from non-zero to zero, or zero to non-zero, against A1.

| condition | label |
|---|---|
| build rc ≠ 0, cap exceeded, **index test shows a splice**, or a required field unreadable | **NOT A RESULT** |
| **P ≥ 3** — the patch set itself changed; R is not comparable to A1 | **NOT A RESULT** |
| **C < 3.00** — control regressed | **REGRESSION**; H2b **not** confirmed whatever R is |
| **G < 50.057 %** — global worse than A1 | **REGRESSION**, same treatment |
| **R = 12** (all) **and** any control regression | **NOT A RESULT** (§6 degeneracy limb) |
| **R ≥ 6**, C ≥ 3.00, G ≥ 50.057 % | **H2b CONFIRMED** |
| **1 ≤ R ≤ 5**, C ≥ 3.00, G ≥ 50.057 % | **H2b PARTIAL** |
| **R = 0** | **H2b REFUTED** — and §8 applies |

`1 ≤ P ≤ 2` does not change the label; the affected patches are **excluded from R and
the exclusion is reported with the number**, so R is always stated as *n* of *12 − P*.

## 8. WHAT A REFUTATION LEAVES — WRITTEN BEFORE THE ANSWER IS KNOWN

**If R = 0, all three hypotheses registered in `B1` §6 are dead** and the cause of the
DrivAer zero-layer group lies **outside that enumeration**. Then, and this is fixed now:

1. The rung reports **H2b REFUTED** and the §6 enumeration **EXHAUSTED**. Exhausted is a
   result, not a failure to find one.
2. **No fourth hypothesis is promoted by drift.** Specifically, **patch size does NOT
   become hypothesis four**: it is a real but non-determining correlation (median 77
   mesh faces for failures against 491 for successes) with `NotchbackB_Pillar` — 54
   faces, 4.31 layers — as the standing counterexample. Promoting it after three
   refutations would be choosing the survivor, not testing it.
3. The next step is **not another parameter sweep**. It is a diagnostic that reads
   snappy's own per-patch extrusion decision directly — instrumenting why a named patch
   is dropped — which is a different kind of work and needs its own registration.
4. It becomes a candidate for an **upstream defect note**, which would be a draft
   carrying **`NOT FILED`** in its opening lines. **SUBMISSIONS ARE PARKED**; nothing is
   sent, by anyone, ever, without Sanaa.

## 9. COST (rule 12) — AND A CONTENTION BAND, BECAUSE ONE IS MEASURED

Anchored on the two **succeeding** builds, never on the collapsed `DIAG_v3`.

| | |
|---|---|
| A1 | **2.52 core-min** measured, ratio 0.84 against its estimate |
| B1 | **3.52 core-min** measured, ratio 1.17 against its estimate |
| **point estimate** | **3.0 core-min** |
| **CAP** | **15 core-min**, 900 s `timeout` inside the wrapper; rc 124 writes `CAP_BREACH.txt` |

**The band is stated as a band and the reason is measured:** A1 and B1 are the *same
build at the same size* forty minutes apart and their ratios **bracket 1.0 from both
sides**, differing ~40 % on wall time alone under peer load. **A per-build estimate on
this box cannot be tighter than roughly 0.8–1.2 without a contention term, and none of
the DrivAer rows has one.** So a ratio inside 0.8–1.2 is **not** a prediction success and
will not be reported as one.

3.0 core-min = **$0.0026 DERIVED, NEVER MEASURED** at $0.0513/core-h (owner-stated;
`COMPUTE_BUDGET_CHARTER.md` §5). Disk is not a constraint (507 GiB free).

## 10. THE INDEX TEST IS MANDATORY, BEFORE ANY `checkMesh` NUMBER

points supplied **==** max face vertex index **+ 1**, **zero** unused trailing points,
**no** `0/polyMesh`. A failure makes the rung **NOT A RESULT** — it does not make the
mesh bad, it makes the *reading* void. DrivAer is proved to splice when layers collapse
(`MESH_SPLICE_PROOF.md`), and a physically impossible value is evidence about the
instrument, outranking every plausible value beside it.

## 11. NOT CLAIMED

Nothing here licences A2, re-opens A1's or B1's gates, or says anything about near-wall
resolution, y+, or fitness for a solve. `minMedialAxisAngle 130` is a **probe, not a
proposed production value**.
