# PPTC VP1304 — HUB/ROOT MESH REPAIR RUNG: GRADING RECORD

**Graded 2026-09-13 by a cfd lane. Mesh `F360_coarse_shaft4`.**

**VERDICT: GATE FAIL.** The §3.2 SPD gate fails with a named witness, and the rung's three
repair predictions (P1, P3, P6) fail against their pre-registered thresholds **in the wrong
direction — the mesh is worse than the baseline on every damage count.** The three
load-bearing predictions that this rung would NOT cure the mesh (P2, P5, P7) all HELD.
**There is no prediction miss to record: nothing came out better than registered.**

Governed by `cases/PPTC_VP1304/HUB_ROOT_MESH_RUNG_PREREGISTRATION.md`.

---

## 0. FREEZE VERIFICATION — DONE BEFORE GRADING, NOT AFTER

The frozen file **is** the file that governs, verified by hashing the working tree against the
committed blob, and the whole chain predates the build.

| artefact | commit | committed blob | working tree | time | vs build start 17:24:18Z |
|---|---|---|---|---|---|
| registration, FROZEN | `e2a8294f` | `7b875397a51d97cb9902c64fcfb3a666dd99f852` | — | 17:04:18Z | **−20 min** |
| + Addendum 1 | `f373bc11` | `f2a7a5a52e4aad84b859063c03fbee078686731e` | — | 17:13:04Z | **−11 min** |
| + Addendum 2 | `1c95466b` | `7ad845b0d6c25dfbacbc5d278b0cca516b3e0d6a` | **`7ad845b0…` MATCH** | 17:20:45Z | **−4 min** |
| grader `grade_p1_p7.py` | `4150a347` | `9110876c6f0dc0bed91391ea143873a89284670c` | **`9110876c…` MATCH** | 17:31:17Z | +7 min from launch, **−4 h from the mesh** |

Both addenda are **append-only against their parent** — `git diff --numstat` reports `57 0`
and `82 0`, zero deletions, which is what the "*lines whose number changed above this
section: 0*" assertion claims.

**Honest caveat on the grader's freeze.** `4150a347` landed **7 minutes after snappyHexMesh
was launched**, not before. It is frozen **before the mesh existed** (21:28:44Z, 3 h 57 m
later) and therefore could not be fitted to the answer, but "before any compute" would be
wrong and is not claimed. The thresholds it implements were themselves frozen at `e2a8294f`,
20 minutes before the build.

**`spd_gate.py` was UNTRACKED at grade time** and is committed with this record. Its mtime is
`17:16:34Z` — 8 minutes before the build and 4 h 12 m before the mesh existed — and its
two refusal limbs and its exact arming value are described in Addendum 2 §A2.3, which **was**
committed pre-build at `1c95466b`. That addendum pins its behaviour; the file's own commit
does not predate the mesh, and this is stated rather than glossed.

---

## 1. THE SPD GATE — §3.2, WITH ITS GEOMETRY CONTROL REPORTED BESIDE THE VERDICT

**The widened stop-rule of Addendum 2 §A2.2 is binding: a verdict whose geometry control
refuses is VOID in either direction. The control PASSED, so this verdict stands.**

### 1.1 Arming, on every invocation (CLAUDE.md rule 3)

| control | result |
|---|---|
| NEGATIVE — a valid two-cell mesh | **PASS**, 0 faces `w_f ≤ 0`, 0 cells `A_PP ≤ 0` |
| POSITIVE — one face deliberately inverted | **GATE FAIL**, witness cell **0**, `A_PP = −8.842105263e-01` |

**That witness value is bit-identical to the one Addendum 2 §A2.3 recorded pre-build**
("witness cell 0, `A_PP = −8.842105263e-01` — **unchanged**"). The instrument reproduces a
number registered before this mesh existed.

### 1.2 LIMB 1 — points/faces consistency: **PASSED, it did not refuse**

`nPoints` = **20,688,884** = `max(face vertex index) + 1` = **20,688,884**. **Zero orphan
points.** Against `F360_coarse`, which carries 10,620 orphan points and is refused.

The `finish_and_queue.sh` stale-points defect **was not present here, and this was checked on
disk rather than assumed**: `constant/polyMesh/points` (mtime 21:31:24) is **byte-identical**
(`cmp`, exit 0) to `0/polyMesh/points`, the final position array, and it was staged **5
seconds before `checkMesh` started** at 21:31:29. Every downstream reader — checkMesh, the
gate, the grader — saw the same, correct array.

### 1.3 THE VERDICT AND ITS WITNESS

> ## GATE FAIL

| quantity | value | of total |
|---|---|---|
| internal faces with `w_f ≤ 0` (or `S_f·d_f = 0`) | **1,267** | of 59,461,641 (**0.00213 %**) |
| cells with `A_PP ≤ 0` | **666** | of 19,829,120 (**0.00336 %**) |
| **WITNESS CELL INDEX** | **1,858,792** | |
| **its `A_PP`** | **−3.422338033e+04** | `x = e_1858792` ⟹ `xᵀAx = −3.422338033e+04 ≤ 0` |
| witness cell centre | **(0.133067, −0.002162, 0.005922) m** | x = 133.067 mm, **r = 6.304 mm** |

**Where the witness sits, and it is not where this rung looked.** `cap`'s downstream tip is
at x = 133.415 mm and `axisRod` begins at x = 133.276 mm. The witness cell centre is
**0.35 mm upstream of the cap tip at r = 6.3 mm — the cap-to-axisRod junction.** Not the
shaft this rung refined, and not the blade root the rung was originally ruled in on.

### 1.4 GEOMETRY CONTROL — **PASSED** (Addendum 2 LIMB 2, blocking)

| control quantity | this run | threshold | Addendum 2's VOID run on `F360_coarse` |
|---|---|---|---|
| max relative cell-volume difference vs OpenFOAM `0/cellVolume` | **4.999e-08** | ≤ 1e-6 | 2.144e+09 |
| negative-volume cells, this instrument | **357** | must equal OpenFOAM | 9,809,857 |
| negative-volume cells, OpenFOAM | **357** | | 316 |
| internal faces flagged `w_f ≤ 0` | 1,267 (0.00213 %) | — | 29,417,841 (**49.8 %**) |

The same-mesh assert ran **in the same invocation** at 19,829,120 cells. The instrument's own
geometry agrees with OpenFOAM's to 5.0e-08 and its negative-volume count matches **exactly**.
**The reader signature that produced the VOID verdict — half the mesh failing — is absent.**

---

## 2. P1–P7 FROM THE FROZEN GRADER

Instrument `grade_p1_p7.py` at blob `9110876c…`, **unmodified**, hash re-checked immediately
before the run.

### 2.1 §3.2a SAME-MESH ASSERT — LIVE, IN THE GRADING INVOCATION

```
0/cellVolume       len = 19829120
0/minPyrVolume     len = 19829120
cellLevel          len = 19829120
all equal, and equal to the graded mesh cell count 19829120: ASSERT PASSED
```

**Cross-mesh pairing is unconstructible here, and that was confirmed rather than assumed.**
Every baseline in the grader is a **scalar** quoted from the registration (`BASE = dict(neg_vol=316,
wrong_oriented_set=2089, wrong_oriented_checkmesh=2548, enrich_4_3=31.2, minpyr_nonpos=1028,
pos_vol_inverted=712)`) — there is no baseline **array** in the instrument for a `F360_coarse`
array to be paired against. The rebuilt mesh has 19,829,120 cells against the baseline's
19,700,035, a difference of 129,085 by construction, and the assert is what makes that
difference visible instead of silently plausible.

### 2.2 THE GRADER VALIDATED AGAINST NUMBERS IT NEVER SAW

The frozen grader was run **unmodified on `F360_coarse` itself**. It reproduces the frozen
registration **exactly, on every figure**:

| figure | registration (frozen `e2a8294f`) | frozen grader on `F360_coarse` |
|---|---|---|
| negative-volume cells | 316 | **316** |
| `wrongOrientedFaces` set | 2,089 | **2,089** |
| 4↔3 enrichment | 31.2× | **31.2×** |
| cells `minPyrVolume ≤ 0` | 1,028 | **1,028** |
| positive volume + inverted face | 712 | **712** |
| bad-cell face slots, of which 4↔3 | 206 of 1,558 (13.2 %) | **206 of 1,558 (13.22 %)** |
| baseline 4↔3 share | 0.42 % | **0.4235 %** |
| negative volume with a POSITIVE pyramid | 0 | **0** |

**This is the strongest control available to this rung**: an instrument frozen before the mesh
existed, reproducing to the last digit a set of numbers measured independently and committed
hours earlier. Cost: 0.784 core-min.

### 2.3 THE GRADED ROW

| # | prediction | measured | baseline | verdict |
|---|---|---|---|---|
| **P1** | negative-volume cells **< 200** | **357** | 316 | **GATE FAIL** |
| **P2** | negative-volume cells **> 0** (rung NOT predicted to cure) | **357** | 316 | **PASS** |
| **P3** | `wrongOrientedFaces` set **< 1,800** | **2,577** | 2,089 | **GATE FAIL** |
| **P4** | 4↔3 enrichment among survivors **< 10×** | **27.8×** | 31.2× | **GATE FAIL** |
| **P5** | the §3.2 SPD gate **still FAILS**, with a named witness | **GATE FAIL, witness cell 1,858,792, `A_PP` = −3.422338033e+04** | — | **PASS** |
| **P6** | cells with `minPyrVolume ≤ 0` **< 700** | **1,282** | 1,028 | **GATE FAIL** |
| **P7** | positive volume + inverted face **> 0** | **925** | 712 | **PASS** |

checkMesh's own "incorrectly oriented" count, recorded beside P3's set count as the
registration requires: **3,024** against the baseline's **2,548**.

### 2.4 P4 IS MEASURABLE — THE RATIFIED "NOT MEASURABLE" RULING DOES **NOT** APPLY

The advance ruling was: *if the rebuild removes the 4↔3 transition entirely, P4 is NOT
MEASURABLE, not passed.* **It did not remove it. The category is not empty, so P4 is graded
on its merits, and it is GATE FAIL at 27.8× against a 10× threshold.**

The face count that settles it: **544,200 internal faces are 4↔3 in the rebuilt mesh**, of
59,461,641 (0.4858 %), and **244** of them touch a negative-volume cell.

---

## 3. WHAT THE RUNG ACTUALLY DID — THE PREMISE OF §2 IS REFUTED BY ITS OWN BUILD

### 3.1 The registered change was applied, and only it

Diffed against the baseline build's own dictionary, the built `snappyHexMeshDict` differs by
**exactly the two lines Addendum 1 §A1.1 registered, and nothing else**:

```
86c86   <  { file "shaft.eMesh"; level 3; }   >  { file "shaft.eMesh"; level 4; }
109c109 <          level (3 3);               >          level (4 4);
```

A1.1 asserted this from a *generated* dictionary pre-build; it is confirmed here against the
**built** artefact.

### 3.2 It did not do what §2 said it would do

> §2: *"Raising `shaft` to 4 removes the 4↔3 transition from the interior of those regions,
> which is the transition the population is 31.2× enriched on."*

**It added 4↔3 interface. It did not remove it.**

| quantity | `F360_coarse` | `F360_coarse_shaft4` | change |
|---|---|---|---|
| level-3 cells | 212,280 | 206,040 | **−6,240 (−2.9 %)** |
| level-4 cells | 18,532,547 | 18,669,352 | +136,805 |
| **4↔3 internal faces** | **471,240 (0.4235 %)** | **544,200 (0.4858 %)** | **+72,960 (+15.5 %)** |
| 4↔3 enrichment among bad cells | 31.2× | 27.8× | −10.9 % |

**The mechanism, and it is geometric, not speculative.** The `shaft` patch spans
x ∈ [−0.3568, −0.0494] m (checkMesh's own bounding box). The two level-4 refinement regions
span x ∈ [−0.100, +0.060] (`bladeRegion`) and x ∈ [−0.250, +0.030] (`tipVortex`). **The
shaft therefore runs from x = −0.357 to x = −0.250 entirely OUTSIDE both level-4 regions.**
Raising its surface level to 4 clads that whole upstream segment in new level-4 cells sitting
against a level-3 background — **manufacturing new 4↔3 interface faster than it removed the
interior transition it was aimed at.** Only 2.9 % of level-3 cells disappeared; the 4↔3
population grew by 15.5 %.

The enrichment fell 31.2× → 27.8× only because numerator and denominator moved together. **The
lever was pulled and it pushed.**

### 3.3 Every damage count moved the wrong way

| count | `F360_coarse` | `F360_coarse_shaft4` | change |
|---|---|---|---|
| negative-volume cells | 316 | **357** | **+41 (+13.0 %)** |
| `wrongOrientedFaces` set | 2,089 | **2,577** | **+488 (+23.4 %)** |
| checkMesh "incorrectly oriented" | 2,548 | **3,024** | **+476 (+18.7 %)** |
| cells `minPyrVolume ≤ 0` | 1,028 | **1,282** | **+254 (+24.7 %)** |
| positive volume + inverted face | 712 | **925** | **+213 (+29.9 %)** |
| snappy "Finished meshing with … illegal faces" | 91,876 | **91,916** | **+40 (+0.044 %)** |
| minimum cell volume | −5.7249909e-10 | −5.5391623e-10 | marginally less negative |
| cells | 19,700,035 | 19,829,120 | +129,085 |

**Illegal faces, plainly, as asked: 91,916 against 91,876 — UP by 40, a 0.044 % increase.**
The direction is worse; the magnitude is negligible beside the +13 % to +30 % moves in every
count that is actually resolved cell-by-cell. The snappy headline is the *least* sensitive
instrument of the seven and should not be read as "essentially unchanged" evidence.

### 3.4 §3.3's structural finding reproduces on the new mesh

**Cells with negative volume but a POSITIVE pyramid: 0.** The 357 negative-volume cells are
again a **strict subset** of the 1,282 inverted-pyramid cells. The min-cell-volume gate the
lab quotes sees **357 of 1,282 — 27.9 %** of what exists here, against 30.7 % on the baseline.
**The under-coverage disclosed in §3.3 is unchanged and slightly worse.** Recorded as a
disclosure about the existing gate; retiring or altering a gate is Sanaa's alone.

---

## 4. ZERO PRISM LAYERS — EXPECTED, NOT THIS RUNG'S FAILURE, AND READ PER L-590

`Extruding 0 out of 780220 faces (0%). Removed extrusion at 363015 faces.`, then a second pass
at 0 removing 0, then **`Added 0 out of 4681320 cells (0%).`**

**ACHIEVED LAYER COVERAGE = 0 on all four wall patches.** Read per **L-590** and
`docs/standards/MESH_STANDARD.md` §16.6 rule **L5**.

**Exactly ONE per-patch layer table exists in the whole log, at line 3064**, and it sits
**before** `Outer iteration : 0` at line 3073 — i.e. before any extrusion is attempted. **It
is the REQUEST** (`blades 382204 6 1.79e-06 1.07e-05`, and note that 1.79e-06 m near-wall is
the collapsed request §2 already names). **After the extrusion there is no table at all**:
line 3301 `Extruding 0 out of 780220 faces (0%)`, line 3302 `Added 0 out of 4681320 cells
(0%)`, line 3303 straight to `Layer mesh : cells:19829120 …`. `snappyLayerDriver.C:5102-5110`
breaks before `printLayerData()` at `:5211`. **An absent table is a positive finding of ZERO,
never "unknown", and the request table is NOT substituted for it.**

**The zero does not rest on an absence.** Two *positive* statements of zero corroborate it
independently — `Extruding 0 out of 780220 faces (0%)` and `Added 0 out of 4681320 cells
(0%)` — so this reading would survive even if the absent-table rule did not exist. Stated
because a zero read only from something missing is exactly the zero CLAUDE.md rule 3 distrusts,
and **no log in this build family has ever achieved a non-zero layer count**, so this reader
could not be shown a non-zero achievement table to control against.

**This is not this rung's failure and is not charged against it.** The measured cause is
`relativeSizes true` scaling every thickness by `getLevel0EdgeLength()`, which returns the
**global minimum** level-0 edge — here the 2 mm axis rod's azimuthal chord — poisoning by
95.53×. That is **PRISM-A2's rung** (frozen `748d2691`, amendments `ef98fc88`, `b3deca9b`),
**which has not been built.** The two must not be conflated: this rung changed a refinement
level and touched no line of the layer dictionary.

---

## 5. AN INPUT-PATH DEPARTURE, DISCLOSED — THE FROZEN GRADER WAS NOT EDITED

**The frozen grader refused rather than degraded, and it was right to.** Pointed at the case
directly it raised `FileNotFoundError` on
`constant/polyMesh/sets/zeroVolumeCells` and exited 1 — **after** printing a passing same-mesh
assert. It produced no number.

**Cause — a staging difference, not a mesh defect.** Because `0/polyMesh/points` exists in this
build (the stale-points repair, §1.2), OpenFOAM resolved the mesh instance to time 0, so
`checkMesh` wrote its sets to **`0/polyMesh/sets/`**. In `F360_coarse` they are in
`constant/polyMesh/sets/`, which is the path the grader was frozen against.

**What was done, and what was deliberately not done.** The grader is frozen and **was not
edited — its blob is `9110876c…` before and after.** Instead a **symlink view** was built at
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse_shaft4/grade_view/`, presenting **this
same mesh's own artefacts**, every entry a symlink to the real file, nothing copied and
nothing altered. It lives under the run directory it belongs to, not in a scratchpad (L-186).

**The readers were controlled against checkMesh's own printed numbers before the grader used
them**, which is the §3.3 discipline: `zeroVolumeCells` declares **357** against checkMesh's
`<<Writing 357 zero volume cells to set zeroVolumeCells`; `wrongOrientedFaces` declares
**2,577** against `<<Writing 2577 faces with incorrect orientation to set wrongOrientedFaces`.
Both exact. The grader's own guard (`zeroVolumeCells max index >= NC` ⟹ REFUSE) and the §3.2a
assert both ran live inside the graded invocation and both passed at 19,829,120.

---

## 6. AN UNRELATED BUILD DEFECT FOUND WHILE GRADING — REPORTED, NOT WORKED AROUND

**`BUILD_STATUS` reads `BUILD_RC=1 stage=topoSet`.** The build is marked failed. The cause is
**not** the mesh:

```
--> FOAM FATAL ERROR: cannot find file ".../F360_coarse_shaft4/system/topoSetDict"
```

`topoSetDict` was never written into the case. **Consequence: no cellZones exist** — checkMesh
confirms "No cellZones found" and "Number of regions: 1 (OK)" — **so the MRF rotating zone is
absent from this mesh.** It does not affect a single number in this record (the gate and the
grader read `points/faces/owner/neighbour/cellLevel` and the checkMesh fields, none of which
depend on a cellZone), but **any design-point solve on this mesh would run with no MRF zone.**

Per Sanaa's 2026-09-10 directive this is surfaced as a finding, not patched around.
**No design-point family was launched. The propeller's 48 ranks were not touched.**

---

## 7. COST — RULE 12 CALIBRATION, DOLLARS DERIVED NOT MEASURED

Core-minutes measured from logs (wall s × ranks ÷ 60). All work serial, 1 rank.

| item | measured | registered | source |
|---|---|---|---|
| snappyHexMesh rebuild | **242.959** | 230 | `Finished meshing in = 14577.53 s` |
| `checkMesh -allGeometry -allTopology` | **8.950** | 15 | log header 21:31:29 → mtime 21:40:26 (537 s) |
| §3.2 SPD gate (arming + graded mesh + control) | **6.342** | 20 | `/usr/bin/time -v`, 380.54 s wall, peak RSS **46.9 GB** |
| `surfaceFeatureExtract` | **0.828** | — | `ExecutionTime = 49.68 s` |
| P1–P7 grader, graded run | **0.548** | — | `/usr/bin/time -v`, 32.88 s |
| P1–P7 grader, `F360_coarse` baseline control | **0.784** | — | `/usr/bin/time -v`, 47.07 s |
| **EXECUTED TOTAL** | **260.412 core-min** | **265** (like-for-like) | **ratio 0.983×** |

**NOT EXECUTED, and named so the ratio is not flattered:** `decomposePar` (registered 10) and
the §3.4 PCG/DIC probe (registered 33) were not run — the probe is a solver disclosure and no
solve was authorised. **43 core-min of the 308 registered is unspent**, so the like-for-like
denominator is 265, not 308. Against the full 308 the executed figure is 0.845×; that number
is **not** the calibration ratio and is given only for completeness.

**WASTE, named separately and never absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER` §6):

| waste | core-min | cause |
|---|---|---|
| `topoSet` | **1.217** | missing `system/topoSetDict` (§6) |
| P1–P7 grader, first attempt | **0.243** | input-path refusal (§5) — a refusal, not a wrong number |
| pre-build VOID gate run on `F360_coarse` | **5.017** | Addendum 2 §A2.4, already disclosed pre-build |
| **TOTAL WASTE** | **6.476** | |

**Gross 266.888 core-min. Registered cap 924 core-min — 28.9 % of cap, not approached.**

**Dollars DERIVED, NOT MEASURED**: executed 4.3402 core-h × $0.0513/core-h = **$0.2227**;
gross 4.4481 core-h = **$0.2282**. `cost_basis`: the rate is **reported by the owner, not
measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
Core-minutes are measured from logs.

**Gap attribution.** Misprediction ≈ 1.0× overall and the estimate was good, but the item-level
agreement is coincidental cancellation and is reported as such: the **rebuild ran 1.056× its
230 core-min estimate** (the +8 % allowance for added shaft cells was very close — the mesh
grew 0.66 % in cells but the snap phase, 10,200 s of 14,578, dominated); the **gate ran 0.317×
its 20 core-min estimate** and the **checkMesh 0.597× its 15**. **No contention term is
claimed**: load average was ~52 throughout, but every figure here is serial `ExecutionTime` or
a serial wall clock on a single rank, and no like-for-like idle-box measurement of these same
stages exists to separate contention from work. Inventing one would be an estimate dressed as
a measurement. **The §5 memory-footprint omission disclosed in Addendum 2 §A2.4 is now
measured: the gate peaks at 46.9 GB on 19.8 M cells**, above the 33.4 GB measured on the
19.7 M-cell baseline; §5 declared no memory footprint at all and should.

---

## 8. WHAT THIS RECORD DOES NOT CLAIM

It produces no KT, no KQ and no y+. It does not grade the open-water curve. It says nothing
about the 70× layer collapse beyond confirming achieved coverage is zero and pointing at
PRISM-A2. It does not identify the cause of the 39.6 % of bad cells that sit on no refinement
transition at all — that population is untouched and its cause remains unidentified. The
witness cell at the cap/axisRod junction is **one** located counterexample, not a survey of
where the 666 non-positive diagonals live.

**No submission, filing or send of any kind was made or prepared.**
