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
---

## ADDENDUM 1 — 2026-09-11 — §2's MECHANISM DESCRIPTION IS WRONG. PROSE ONLY.

**I quoted a commented-out block.** §2 describes the criterion as *"the angle between
each endpoint's vector to its nearest wall point"* and cites the comment *"Both end
points of edge have very different nearest wall point."* **That comment sits above a
DISABLED block.**

Read at HEAD of the installed source,
`/usr/lib/openfoam/openfoam2606/src/mesh/snappyHexMesh/externalDisplacementMeshMover/medialAxisMeshMover.C`:

- **`:100–112` are entirely commented out**, including `//if ((v0 & v1) < minCos)`.
  That is the nearest-wall-point form, and it does not execute.
- **`:114–120` is the LIVE test**, and its own comment reads *"Detect based on
  extrusion vector differing for both endpoints — the idea is that e.g. a sawtooth wall
  can still be extruded successfully as long as it is done all to the same direction."*

      if ((pointWallDist[e[0]].data() & pointWallDist[e[1]].data()) < minCos)

**`.data()` is the EXTRUSION VECTOR, not the vector to the nearest wall point.** The real
criterion is whether two endpoints of an edge want to extrude in **different directions**.

### What does NOT change — checked clause by clause

| item | changed? |
|---|---|
| the parameter changed (`minMedialAxisAngle 90 → 130`) | **no** |
| the direction of relief | **no** — verified below |
| §7 gate rows, and their order | **no** |
| **R** threshold (≥ 6 confirm, 1–5 partial, 0 refute) | **no** |
| **C** ≥ 3.00, **G** ≥ 50.057 % | **no** |
| **P** limb (≥ 3 → NOT A RESULT) | **no** |
| majority-class baseline R = 0 of 12 | **no** |
| §6 degeneracy limb | **no** |
| noise floor 1.00 | **no** |
| §9 cost point 3.0, cap 15 | **no** |
| §8 exhaustion clause | **no** |
| the 12-candidate group | **no** |

**This addendum alters no gate, threshold, cap, label, R, P or baseline.** It corrects
prose describing a mechanism. Had it touched any row above it would be illegal, because
first compute has occurred — B2 launched before this was written.

### The direction still holds, and here is the arithmetic

`:161` — `minMedialAxisAngleCos = cos(degToRad(minMedialAxisAngle))`.
`cos(90°) = +0.0000`; `cos(130°) = −0.6428`. The live test marks a point when
`(d₀ · d₁) < minCos`. Raising the angle **lowers** `minCos`, making the test **harder**
to satisfy, so **fewer** edges are marked and the reduction is **relieved**. The probe is
pointed the right way. **Both forms compare a dot product against the same `minCos`, so
the direction survives the correction; the physical meaning does not.**

### What the correct mechanism predicts — an OBSERVATION, not a gate

Extrusion-vector disagreement is what a **thin protruding part with opposing faces**
produces: a mirror shell, a brake disc, a wheel-support plate. Two points across such a
part extrude nearly **opposite**, so `d₀ · d₁ ≈ −1`, which is **below −0.6428 as well as
below 0** — **they stay marked as medial-axis at 130° exactly as they were at 90°.**

That is a better physical story for this particular group than the one §2 gave, and it
**predicts R = 0**. It is recorded as an observation and **changes no row of §7**: the
gate was frozen before compute and is not being re-pointed now that a sharper expectation
exists. If R = 0, that outcome was already §7's last row and §8's exhaustion clause
already governs it.

It does sharpen §8 clause 3: the follow-on diagnostic should read **snappy's own
per-point extrusion vectors** on the blocked patches, which is a more specific instrument
than "per-patch extrusion decision" as written.

### The lesson

**A comment describes the code somebody meant to leave there.** When reading a solver for
semantics, confirm the line quoted is the line that **executes** — a dead block keeps its
rationale, and that rationale reads exactly like a live one's. Same family as a banner
that was never evidence and a status artifact that outlived its run: **an artifact
describing a state that is no longer real.**
