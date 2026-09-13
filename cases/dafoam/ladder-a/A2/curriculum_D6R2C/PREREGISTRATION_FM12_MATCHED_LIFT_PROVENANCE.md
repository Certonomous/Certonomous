# Curriculum D6R2C — PRE-REGISTRATION for arm `FM12`: THE COMPARISON AT MATCHED LIFT, WITH THE EXTRUSION PROVED INSTEAD OF ASSUMED

**STATUS: FROZEN AT THE COMMIT THAT CARRIES THIS FILE. Gates, thresholds, caps and labels are closed
from that sha; changes land only as dated addenda (CLAUDE.md rule 2).**

**`FM11` IS `BLOCKED` AND STAYS `BLOCKED`. ITS FROZEN FILES ARE NOT EDITED (rule 6).** `FM12` is a NEW
registration that inherits `FM11`'s design — which was right — and repairs the four things that stopped
it, each named below with the measurement that establishes it.

**SUBMISSIONS PARKED (rule 7).** Nothing in this arm is sent, filed, uploaded or registered anywhere.

---

## 1. WHY THIS ARM EXISTS

`FM11` was frozen at `6190e070c6f53fe07f058dfcfa610ba7fb246596`, launched, and graded **`BLOCKED`** after
**22 s wall / 1.467 core-min**, at its first staging step, on all four ranks. The refusal, from its own
arm log:

```
d6r2c_fm9_stage.Refusal: REFUSE_FRESH_IS_BASE the generated mesh's points.gz md5 equals the
BASE mesh's (0fb1935a9b8781b73ac4ccb136e3ec68).
```

### 1a. THE BLOCK IS A REGISTRATION DEFECT, NOT PHYSICS, AND IT IS L-593 EXACTLY

`REFUSE_FRESH_IS_BASE` lives in the **inherited** `d6r2c_fm9_stage.py:95-100` and fires when the
generated mesh's `points.gz` md5 equals the base mesh's. It was written for `FM9`/`FM10`, where *"fresh"*
always meant **the optimum's** mesh, so identity with base could only mean the staging had silently
reused the base.

**`FM11` introduced the state `Zb`, for which that identity is the CORRECT AND EXPECTED OUTCOME.** A mesh
generated at zero shape from the base surface *should* be the base mesh. The inherited guard cannot tell
the two situations apart.

`FM11`'s own producer had this right — `d6r2c_fm11_states.py:measure_against_base` gates `Zo` on
difference and **reports** `Zb` — and then called `stg.stage_mesh(arm_dir)` at line 438, which carries
the fused guard. **A pin proves what a file IS, not what it NEEDS (L-593).**

### 1b. AND THE ARM LEFT A REAL RESULT ON DISK ON ITS WAY TO BEING BLOCKED

MEASURED, on `FM11`'s own artifacts, by `d6r2c_fm12_stage.py --live-controls`:

| quantity | value |
|---|---|
| `Zb` generated `points.gz` md5 | `0fb1935a9b8781b73ac4ccb136e3ec68` |
| registered base `points.gz` md5 | `0fb1935a9b8781b73ac4ccb136e3ec68` |
| max point difference | **0.0 m exactly** |
| points identical | **40209 / 40209** |
| elapsed since the base mesh was built | **47.719 days** (2026-07-28T00:18:12Z → 2026-09-13T17:33:34Z) |
| gzip header MTIME field, both files | **0** |

The gzip MTIME field being zero on **both** files is what makes the md5 half of this admissible: md5
identity here is a true statement about the **points**, not an artefact of two files having been written
at the same second. This is registered as gate **`R1`** in §3 — with its own verdict, and it never flips
this arm's label.

### 1c. THE FOUR REPAIRS, AND NOTHING ELSE

1. **`M0b` / `M0o`** — two extrusion-evidence gates replacing one, §3.
2. **the age datum is threaded into the producer** — `M0b`'s load-bearing limb is rule 4's age guard.
3. **the grader's external-anchor reader is repaired**, §1d.
4. **`R1` is registered as a gate**, §3.

Everything else — three states `Zb`/`Zo`/`Do` plus the `Ez` diagnostic, every solve at **zero shape and
zero twist** on a mesh generated for that shape, trimmed to the registered `CL` targets, `G1` the fresh
ratio against `R_def`, `G2` the trim, `G-WALL`, `M1`, `D1`, `D2`, `Q1`, `H4` — **is `FM11`'s design,
unchanged.**

### 1d. THE GRADER COULD NOT LOAD ITS OWN EXTERNAL ANCHOR, AND ITS PRE-FREEZE CHECK COULD NOT SEE THAT

`d6r2c_fm11_grade.py:199`, in `_J()`, tried the keys `("obj", "J", "fun", "weighted_CD")`.

MEASURED on the real record
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl`,
md5 `2c0b8143caad198cd2e21d8047986aa3`:

| `n` | `funcs` keys | `obj.J` |
|---|---|---|
| 2 | `cl04/cl05/cl06.aero_post.functionals.CL`, `geometry_cl05.thickcon`, `geometry_cl05.volcon`, **`obj.J`** | `[0.030641631438997615]` |
| 88 | (the same keys) | `[0.023063259528677764]` |

**The real key is `obj.J` — with a dot — its value is a ONE-ELEMENT LIST, and the `F` records carry no
per-condition `CD` at all.** So `FM11`'s emitted grading command, run on the real record, could only
return `REFUSE_NO_J_IN_RECORD`.

**The anchor itself was never in doubt.** `0.023063259528677764 / 0.030641631438997615 = 0.752677270941`
— `R_def` to twelve places, the registered 24.732273 % gain. **Only the reader was wrong.**

**And `FM11`'s pre-freeze clause (b) could not see it, because it ran the emitted command with
`--evals SYNTHETIC --fm10-record SYNTHETIC`.** It drove the command line and **not the data the command
line reads.** That is **L-595 surviving its own lesson**, and §7 tightens the clause because of it.

---

## 2. THE STATES — `FM11`'s TABLE, UNCHANGED

Two sub-arms, each with its own mesh. `Zo`, `Ez` and `Do` share one mesh and therefore one process.

| sub-arm | state | mesh extruded around | `shape` | `twist` | incidence | trimmed | `G-WALL` |
|---|---|---|---|---|---|---|---|
| `Zb` | `Zb` | `surfaceMesh_base.cgns` | **0** | **0** | re-trimmed from `x0` | yes | **GATED** |
| `Zo` | `Zo` | the FFD-updated surface | **0** | **0** | re-trimmed from `x0` | yes | **GATED** |
| `Zo` | `Ez` | (the same mesh) | **0** | **0** | `a*_opt`, as flown | no | **GATED** |
| `Zo` | `Do` | (the same mesh) | `s*` | `t*` | `a*_opt` | no | **REPORTED** |

`shape = 0` and `twist = 0` on the zero states because **the mesh already carries the deformation** —
this is the PRODUCER fix for the defect at `d6r2c_freshmesh.py:423-425`, where `--phase solve` re-applies
`s*` to a volume mesh already extruded around the deformed surface. `Do` reproduces that double
application **on the same mesh**, so the excess can be attributed by measurement rather than by argument.

**The phase order**, emitted by `d6r2c_fm12_run_arm.sh --emit-cmd`:

```
Zb:  freshmesh --phase mesh          ->  fm12_states --sub-arm Zb --datum-file ...
Zo:  freshmesh --phase deform  ->  --phase mesh  ->  fm12_states --sub-arm Zo --datum-file ...
```

`d6r2c_freshmesh.py --phase solve` — the producer whose double application made `FM10` `NOT A RESULT` —
**is not called by this arm**, and the launcher's selftest asserts that on the emitted block.

---

## 3. THE GATES, THEIR THRESHOLDS AND THEIR LABELS

### `G1` — THE RATIO AT MATCHED LIFT (the arm's question)

`R_fresh = J_opt_fresh / J_base_fresh`, both recomputed by the grader from the per-condition `CD` and the
frozen weights, never from a producer's own `J`.

- `R_def = Jf / J0 = 0.752677270941`, **read from the real record's `obj.J` at `n = 2` and `n = 88`**.
- `FM_BAND_ABS = 0.01 × J0`; `RATIO_BAND` = that band propagated through the ratio in quadrature.
- **`PASS`** if `R_fresh ∈ [R_def − RATIO_BAND, R_def + RATIO_BAND]`, else **`GATE FAIL`**.
- `RATIO_BAND` is a **DECLARED decision band, not a measured discretisation uncertainty and NOT a GCI.**

### `G2` — THE TRIM REACHED THE REGISTERED CONDITIONS

`|CL_p − target_p| ≤ TRIM_TOL` for every condition of `Zb` and `Zo`, with
`TRIM_TOL = CL_FINDING_TRIGGER / 5.0 = 1.0e-3`. **HARD.** A trim that did not close is a MISSING
MEASUREMENT, never a solve at whatever lift it reached.

### `M0o` — THE `Zo` EXTRUSION, EVIDENCED BY DIFFERENCE FROM BASE. **HARD.**

`max_point_difference(generated, base) > 0.0`, **strictly, with no tolerance of any kind.**

**THIS IS `FM11`'s CONDITION, UNWEAKENED BY ONE BIT.** Zero difference means the deformation never
reached the mesher and `J_opt_fresh` would be the base geometry's drag under another name: `REFUSE`
(`REFUSE_M0O_MESH_IS_BASE`). The base mesh is identified by md5 before it is read
(`REFUSE_M0O_NOT_THE_BASE_MESH`).

**Its failing control is LIVE**, on real disk: `FM11`'s `Zo/constant/polyMesh` is still the seeded base
mesh, because the arm blocked before `Zo`'s mesh phase ran — and `M0o` refuses it. Its **positive** is
also driven: the registered base mesh with one point moved **one nanometre** passes.

### `M0b` — THE `Zb` EXTRUSION, EVIDENCED BY PROVENANCE. **HARD.**

Difference-from-base is not available to `Zb` and a tolerance invented for it would be precisely the
relaxation this arm exists to avoid. `M0`'s real purpose — *this arm's extrusion RAN and the mesh was not
silently inherited* — is proved instead by:

| limb | evidence | refusal |
|---|---|---|
| `M0b.1` | every build artifact `phase_mesh` writes exists and is **newer than the arm's own age datum** | `REFUSE_M0B_NO_BUILD_ARTIFACT` / `REFUSE_M0B_STALE_ARTIFACT` |
| `M0b.2` | `mesh_generation.log` carries the banner of **every** mesh step, **in order** | `REFUSE_M0B_NO_MESH_STEP` |
| `M0b.3` | the build order holds **in time**: `surfaceMesh.cgns ≤ volumeMesh.xyz ≤ constant/polyMesh/points` | `REFUSE_M0B_BUILD_ORDER` |
| `M0b.4` | `mesh_rc.txt` reads `0`, and `surfaceMesh.cgns` **is** the registered base surface by md5 | `REFUSE_M0B_MESH_RC` / `REFUSE_M0B_NOT_BASE_SURFACE` |
| `M0b.5` | the polyMesh **the solver actually READ**, rebuilt from its own `pointProcAddressing`, equals the mesh this arm generated, exactly | recorded per state; graded |

**`M0b.1` is the load-bearing limb and it is rule 4's age guard applied to the mesh.** The launcher seeds
the condition cases with `cp -a`, which **preserves mtimes**, so a mesh that was inherited rather than
generated carries its original date. MEASURED on `FM11`: datum `2026-09-13T17:33:21Z`; the generated
`Zb/constant/polyMesh/points.gz` at `17:33:34` (13 s **after**); the seeded
`Zb/mp04/constant/polyMesh/points.gz` at `2026-07-28T00:18:12` — **47.719 days before.** An inherited
mesh is 47.7 days too old to pass.

**`M0b`'s failing controls are LIVE**, on real disk, and the **age limb is driven in isolation**: a tree
complete in every other respect whose polyMesh is the seeded one refuses `REFUSE_M0B_STALE_ARTIFACT`.

**HONEST STATEMENT ABOUT `M0b.5`.** It is **the same measurement as `M1` restricted to `Zb`**. It is cited
under `M0b`'s name so that `M0b`'s claim about what the solver held is evidenced rather than assumed. It
is **not** a second independent reading and two green limbs here are one reading, not two.

**`M0b` AND `M0o` ARE NOT INTERCHANGEABLE.** They are two callables with two disjoint refusal families,
and the grader **REFUSES** (`REFUSE_WRONG_M0_GATE`) if `Zb` was gated by `M0o` or `Zo` by `M0b` — which is
what stops a future edit from writing one relaxed gate and pointing both sub-arms at it.

### `R1` — MESHER DETERMINISM ACROSS TIME. **ITS OWN VERDICT. IT NEVER FLIPS THIS ARM'S LABEL.**

**Threshold: `max_point_difference == 0.0 m` EXACTLY, and every point identical.** A tolerance here would
make the word *deterministic* unfalsifiable.

- **`PASS`** ⇒ `genWingMesh.py` plus the family sequence, re-run on the same base surface at the same
  parameters, reproduces the base volume mesh **bit for bit** after the measured interval.
- **`GATE FAIL`** ⇒ the value, the identical-point count and the interval are printed beside it.
- The **md5 half of the claim is admissible only when the gzip header MTIME field reads 0 on both files**;
  when it does not, that half is **WITHDRAWN** and the verdict rests on the point measurement alone.
- **It does not flip this arm's label.** This arm's question is the drag ratio; no mesher-determinism
  threshold was pre-registered as its gate. `R1` is graded, printed on its own line, and carried into
  `findings`, and **the headline may not be quoted without it.**
- **An ABSENT `R1` measurement is a refusal** (`REFUSE_MISSING_R1`), never a pass. A registered gate with
  no measurement is `PENDING`.

**Why it matters:** rules 8 and 9 of this family — periodic re-meshing and fresh-mesh checkpoints —
**rest** on the mesher being reproducible. Until `FM11` blocked, that was assumed.

**What `R1` does NOT claim:** it is a statement about **this** mesher on **this** surface at **these**
parameters over **this** interval. It is not a claim that `genWingMesh.py` is deterministic in general,
and it says nothing about a different surface, a different machine or a different image.

### `M1` — THE MESH THE SOLVER LOADED. **HARD.**

Rebuilt from each condition's own `pointProcAddressing` and compared for **EXACT** equality against the
mesh this arm generated, re-measured by the grader from the run directory. A tolerance would let a mesh
that is *nearly* the generated one pass as the generated one, and the question admits no *nearly*.
`FM5`/`FM7`/`FM8` had *mesh exists / from the pinned script / differs from base* all three true while the
solver read something else.

### `W1` / `G-WALL` — THE DV SET MOVED NO WALL POINT. **HARD.**

`max wall displacement ≤ WALL_MOVE_TOL = 4 × 1031 × eps × 1 m = 9.157e-13 m`, **derived in the producer's
own invocation** and the derived value used. `GATED` on `Zb`, `Zo`, `Ez`; **`REPORTED` on `Do`**, where a
large displacement is the contrast that shows the guard is not blind. Re-measured by the grader from
disk, so a producer that mis-measured its own guard cannot carry the arm.

### `D1` — THE DOUBLE-DEFORMATION DIAGNOSTIC. Reported with a branch.

`mean|E_zero| / mean|E_star| < 0.50` ⇒ the excess follows the shape DVs, not the mesh; the double
application is **CONFIRMED** and `FM10`'s `J_fresh` is withdrawn as a measurement of anything. `0.50` is a
**DECLARED** split of a measured interval and is not dressed up as derived; the raw ratio is printed
whatever it is. `E_star` is `FM10`'s **measured** excess: `+0.149286 / +0.151566 / +0.152398`.

### `D2` — `Do` REPRODUCES `FM10`. **HARD — THE PLANTED CONTROL IN THE LARGE.**

`|J_Do − J_FM10| ≤ FM_BAND_ABS` **and** `max|CL_Do − CL_FM10| ≤ TRIM_TOL`, against `FM10`'s measured
`J = 0.036964341843903646`. If the same inputs on the same mesh do not return the same numbers, nothing
else in this arm is evidence. Failure here is `NOT A RESULT` for the **whole arm**.

### `Q1` — MESH QUALITY OF THE MESH THAT RAN. **REPORTED, NEVER GATED, NEVER SILENT.**

`checkMesh` on the **as-run** case — the generated topology with the reconstructed as-run points —
against DAFoam's **own** declared `maxNonOrth`, parsed from the md5-asserted runScript. MEASURED
elsewhere and the reason this clause exists: the optimisation mesh as-run **71.24** and `FM10` as-run
**79.21** both breach the declared **70.0**, and neither was ever checked. A breach does not flip this
arm's label; it is written into the verdict line and into `findings`, and the headline may not be quoted
without it.

### `H4` — COMPLETION AND HYGIENE. **HARD.**

`rc = 0`; both footers present; `uid = 1000`; no root-owned file newer than the datum; both records newer
than the datum; and **convergence read from the ARM LOG**, whose writer is the solver itself.
**`primal_residual.json` is DELETED from these instruments** — it had four readers, zero writers, zero
files on disk, and its default `conv[p] = True` stood for every condition of every arm. The log limb
**REFUSES** an absent log (`REFUSE_NO_ARM_LOG`) and a log with no primal block
(`REFUSE_NO_PRIMAL_BLOCKS`): an absent source is **NOT** zero failures (rule 3).

### THE LABEL

| condition | label |
|---|---|
| any of `G2`, `D2`, `M0b`, `M0o`, `M1`, `W1`, `H4` fails, **or** the cap is crossed | **`NOT A RESULT`** |
| all hard gates pass and `G1` is inside its window | **`PASS`** |
| all hard gates pass and `G1` is outside its window | **`GATE FAIL`** |

`R1` and `Q1` carry their own verdicts and **never** change this label. **Sanaa's directive #17 is in
force: nothing is stopped by the cap.** A crossing is REPORTED, the row is graded `NOT A RESULT`, and the
cap is never raised.

### THE PLANTED CONTROL (rule 3)

`PLANT = 1.234e-03` is planted into **the per-condition `CD` the grader reads back from disk**, into `M1`,
`W1`, `D1`, `D2`, **`M0b`** and **`R1`**, and the grader **REFUSES** (`REFUSE_PLANT_UNSEEN`) unless every
plant moves the graded fingerprint. The fingerprint is the graded **quantities**, not only the booleans,
so a plant that moves a value without crossing a threshold is still SEEN. The control is itself driven to
its failing side: a deliberately blind grader must be refused.

---

## 4. THE COST, DERIVED FROM ITS OWN ANCHORS

Every term names the run it came from. **Not one of them is a figure this arm produced.**

| term | value | anchor |
|---|---|---|
| per objective evaluation | **5.447 core-min** | DEC7 `d6r2c_dec5.jsonl` STATE `O`, 81.7 s × 4 ranks ÷ 60 |
| per gradient evaluation | **11.863 core-min** | `O_mp` `d6r2c_evals.jsonl`, median of **26** `G` records, 177.944 s × 4 ÷ 60 |
| **gradient evaluations in this arm** | **0** | **registered so the zero is BY DESIGN and VISIBLE, not by omission. `FM12` runs no adjoint.** |
| `Zb` trim | 574.5 s | DEC7 STATE `B` |
| `Zo` trim | 2400.3 s | DEC7 STATE `S` |
| mesh + deform + stage | 88.2 s × 2 | `FM10` arm wall 160 s − its solve 71.847 s |
| model load per process | 14.1 s × 2 | DEC7 FOOTER 5918.862 − Σ states |
| `Ez` + `Do` | 81.7 s × 2 | one objective evaluation each |

`PREDICTED_WALL_S = 3342.8 s` at 4 ranks ⇒ **`PREDICTION = 222.853 core-min`**, cap at ×3.00 =
**`668.559 core-min`**.

**Dollars are DERIVED at $0.0513/core-h and are NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5): prediction **$0.1905**, cap **$0.5716**.

These figures are **identical to `FM11`'s by construction**, because `FM12` runs the same states on the
same anchors and adds no compute: the repairs are gates and readers, not solves. They are nevertheless
**re-derived from the anchor files in the pre-freeze invocation**, not copied.

### `FM11`'s ESTIMATE-VERSUS-ACTUAL CALIBRATION (CLAUDE.md rule 12)

| | core-min | $ (DERIVED) |
|---|---|---|
| `FM11` predicted | 222.853 | 0.1905 |
| `FM11` cap | 668.559 | 0.5716 |
| **`FM11` actual** | **1.467** | **0.0013** |
| ratio actual/predicted | **0.006583** | |

**ATTRIBUTION: the `BLOCKED` refusal, NOT misprediction.** The arm refused at its first staging step after
22 s wall and never reached a single solve, so the prediction was never exercised in either direction.
Nothing about the 222.853 figure is confirmed or falsified by 1.467, and it is carried into `FM12`
unchanged for that reason. The 221.386 core-min not spent is **not waste** — it is compute the arm
correctly declined to start — and it is named here rather than absorbed.

---

## 5. WHAT THIS ARM DOES NOT CLAIM

- **No GCI is computed and none may be quoted.** `RATIO_BAND` is a DECLARED decision band; a Roache triple
  would need three grid levels this arm does not run (CLAUDE.md rule 5).
- **The cross-mesh ratio `J_fresh / Jf`** mixes a fresh-mesh numerator with a deformed-mesh denominator
  and must not be quoted.
- **`FM10`'s `NOT A RESULT` stands** and is not re-graded into anything.
- **`FM11`'s `BLOCKED` stands** and is not re-graded into anything.
- **`R1`** is scoped as stated in §3.
- **`M0b.5` is `M1` restricted to `Zb`**, not a second confirmation.
- A defect note against `d6r2c_fm9_stage.py`'s fused guard would be a **DRAFT** carrying **`NOT FILED`**;
  **submissions are parked (rule 7)** and nothing is sent.

---

## 6. THE INSTRUMENTS, FROZEN IN THIS COMMIT

Every file below exists at the stated md5 **before** the freeze sha, and `d6r2c_fm12_prefreeze.sh` hashes
**this table's own rows** — it carries no list of its own, so a row added here is a row it hashes, and a
row it cannot parse is a FAILURE, not a skip (L-579).

| file | role | md5 |
|---|---|---|
| `d6r2c_fm12_stage.py` | THE ONE REGISTERED CHANGE: `M0b` (provenance) and `M0o` (difference), and the staging | d0d969a925da7e7b04ff35f8f8bb2d75 |
| `d6r2c_fm12_states.py` | the producer: zero shape, zero twist, trimmed; `G-WALL`; the as-run export | 612fb2e6d60320e1f225a2e7555eb1d1 |
| `d6r2c_fm12_grade.py` | the grader: `G1 G2 M0b M0o R1 M1 W1 Q1 D1 D2 H4`, the repaired anchor reader, the planted control | 8f344aabff28fbba394821ca0f88f496 |
| `d6r2c_fm12_run_arm.sh` | the launcher: `G-ROOT G-BOX G-FREEZE G-DEPS G-CPUSET G-COLD G-IMG G-LIVE`, and the ONE source of both emitted commands | 97e7d57702d8ada8ccd1354ccc077798 |
| `d6r2c_fm12_prefreeze.sh` | the three charter clauses, driven, with clause (b) against the REAL anchors | 6cb411dfb70cc28249f1573d5d30af51 |
| `d6r2c_fm9_stage.py` | INHERITED, UNCHANGED, FROZEN: the OpenFOAM readers and the processor-addressing reconstruction | ea6d180fda38a3980bbb275b86d192c1 |
| `d6r2c_freshmesh.py` | INHERITED, UNCHANGED: `--phase deform` and `--phase mesh` | 1d15ce361673ca600d565280441b67e0 |
| `d6r2c_decomp.py` | INHERITED, UNCHANGED | 42ec0dd582584812a69129a474b2783e |
| `d6r2c_dec5_decomp.py` | INHERITED, UNCHANGED: the trim, the governor, the frozen-model loader | fb19791784ebb73747c2f6c466a0d174 |
| `d6r2c_opt_runScript.py` | INHERITED, UNCHANGED: the frozen model and its declared `maxNonOrth` | 2f2ae43a627146cf8e0f065b035ada4b |

**The inherited files are reused BYTE FOR BYTE and none is edited (rule 6).** `d6r2c_fm9_stage.py` in
particular keeps its `REFUSE_FRESH_IS_BASE` exactly where it is: `FM12` does not weaken it, it stops
routing `Zb` through it.

---

## 7. THE PRE-FREEZE CHECK, AND THE CLAUSE THIS ARM TIGHTENS

`d6r2c_fm12_prefreeze.sh` answers `DAFOAM_CHARTER.md` §22.4's three clauses:

**(a)** every instrument named in §6 exists at its stated md5, read out of §6's own rows, plus the
assertion that the launcher's `$PINNED_PY` list and §6's table are **one** list.

**(b) — TIGHTENED, AND THIS IS THE BINDING CHANGE.**

> **The pre-freeze check drives the EXACT CLI the launcher emits, AGAINST THE REAL ANCHOR FILES. A
> synthetic run is allowed only as an ADDITIONAL case, never as the only one, and is reported
> separately.**

`FM11`'s clause (b) asked the launcher for the command and then ran it with
`--evals SYNTHETIC --fm10-record SYNTHETIC`: **it drove the command line and not the data the command
line reads**, which is L-595 surviving its own lesson — and it hid the live `_J` defect of §1d.

For `FM12`, **(b1)** runs the emitted command **verbatim, with not one flag altered**, so it reads the
real `d6r2c_evals.jsonl` and the real `FM10` record through the launcher's own defaults, and asserts that
the printed `R_def` is `0.752677271`. Its **negative** is driven on the same real file: `FM11`'s key chain
finds nothing there and the record carries no per-condition `CD`, so its command could only have refused
— the green is the repair working, not the check being blind. **(b2)** runs the synthetic-anchor form as
an additional case, reported separately. **(b3)** lifts the producer's argument vector out of the emitted
container block, drives it through the producer's own argparse, asserts it carries `--datum-file`, and
requires the producer to **REFUSE** when the datum is absent.

**(c)** every channel a gate reads has a writer that ran: zero live read sites for
`primal_residual.json` in the `FM12` instruments, with the sweep itself driven to its failing side
against the inherited file that does carry the channel; `H4`'s log limb read against a real arm log and
refused against an absent one.

**And beyond the charter:** `M0b` and `M0o` driven to both sides **against the real artifacts on disk**;
`R1` driven at zero and at a planted non-zero; `G-WALL` driven to its failing side with a planted cloud;
every verification constant re-derived **from the real anchors** in the same invocation and the derived
value asserted to be the one the instrument serves; the cost figures re-derived from DEC7 and `O_mp`; and
all four instrument selftests.

**HONEST GAP, NAMED BEFORE IT IS DISCOVERED.** No instrument of this arm has executed against the solver.
It cannot before the compute this registration authorises. `--selftest` drives the pure logic and every
refusal path; `--live-controls` drives `M0b` and `M0o` against real disk; `--parse-only` drives the exact
frozen argument vector through argparse and the input validation. What remains unexercised until the run
is the solver-coupled path: `prob.setup()` decomposing the staged mesh, the trim closing, and `M0b.5`'s
read-back against real processor directories.

---

## 8. THE LAUNCH

```
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_fm12_run_arm.sh FM12 \
  dafoam-idwarp-rot@sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
```

**The image reference carries its repository**, because a bare `sha256:...` digest does not resolve for
`docker run` — `FM11` recorded that as a defect in its own §8 (its ADDENDUM 1) and it is not repeated
here.

- run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance`
- **`G-ROOT.2` forbids writing `FM11`'s root**, whose artifacts are this item's live controls and are
  READ, never written — alongside the parent, `FM9`/`FM10`, `AFTER`, `DEC4`, `FM6`, the A2 surface root
  and the tutorial directory.
- 4 ranks; the cpuset is **chosen at launch** by `free_cpuset` from the union of the docker occupancy and
  a 1 %-busy sample over 2 s, and `G-CPUSET` refuses to start on any intersection. **Nothing running is
  ever stopped.**
- registered arm ids: **`FM12`, `FM12R2`, `FM12R3`** — re-run ids carrying the identical registered cap.
  `FM13` is `FM11`'s re-run id and this launcher **refuses** it, so an arm registered by another document
  cannot be launched by this one.
- **NOTHING IS STOPPED BY THE CAP** (Sanaa's directive #17, 2026-09-12). A crossing is REPORTED, the row
  is graded `NOT A RESULT`, and the cap is never raised.

**SUBMISSIONS PARKED (rule 7).**

---

## ADDENDUM 1 — 2026-09-13 — **THE OUTCOME: `BLOCKED` AT `Zo`'s DEFORM PHASE, CAUSE CLASS `PRODUCER`; `Zb` IS COMPLETE, CLEAN, AND ITS NUMBERS STAND**

**This addendum alters NO gate, threshold, cap or label of the registration above** (CLAUDE.md rule 6).
It records what the run did. Lines whose number changed above this section: **0**. The label below is
`dafoam-supervisor`'s, assigned from a personal crash triage (`SUPERVISION_CHARTER.md` §3, non-delegable);
this lane implemented it and verified its load-bearing measurements independently, and reports that every
one of them reproduced.

**SUBMISSIONS PARKED (rule 7).** Nothing here is sent, filed, uploaded or registered anywhere. The defect
below is **OUR defect in OUR script**, a FIX and not a filing; it is not an upstream DAFoam defect and the
four upstream defect classes remain **`NOT FILED`**.

### A1.1 THE VERDICT

> **`BLOCKED`** — at the `Zo` sub-arm's `--phase deform`. **Cause class `PRODUCER`**
> (`DAFOAM_CHARTER.md` §22.3, the fifth class).

`rc = 1`, wall **269 s**, **17.933 core-min** (`ledger.txt`, `D6R2C_FM12_ROW`). Rank **1** exited 1
(`Process name: [[52239,1],1]`, arm log line 6235). The immediately preceding three lines of the same log
(6227–6229) are:

```
cgio_create_node:ADF  5: String is not an ASCII-HEX string.
```

`Zo` produced **no** state record, **no** solve and **no** graded quantity. **Nothing about the optimum
was measured by this arm, in either direction.**

### A1.2 THE DEFECT, MEASURED IN THE FILE AND IN THE ARTIFACT

`d6r2c_freshmesh.py` — the **inherited frozen** producer, md5 `1d15ce361673ca600d565280441b67e0`, and the
byte-identical copy staged into `FM12/Zo/` — computes

```
213:    rank0 = MPI.COMM_WORLD.rank == 0
```

and first **uses** it at

```
301:    if rank0:
```

**88 lines after**

```
268:    grid.writeToCGNS(surface_out)
```

That write is therefore executed by **all four MPI ranks onto one path**. `cgnsutilities`/ADF is not a
parallel writer and has no file lock: four ranks open, truncate and write the same CGNS file
concurrently. The measured consequence is the three `cgio_create_node` lines, rank 1's exit 1, and an
output of

| file | bytes |
|---|---|
| `FM12/Zo/surfaceMesh_final.cgns` | **8,192** |
| `FM10/surfaceMesh_final.cgns` | 114,688 |
| `FM8/surfaceMesh_final.cgns` | 114,688 |
| `FM7/surfaceMesh_final.cgns` | 114,688 |
| `FM5/surfaceMesh_final.cgns` | 114,688 |

— **truncated to a 7 % stub.** `FM10` ran the **byte-identical** `mpirun -np 4 … --phase deform` command
and its log carries **zero** `cgio` lines: **it won the race.**

**The corrupt artifact is PRESERVED, deliberately, at**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/FM12/Zo/surfaceMesh_final.cgns`.
**It is the evidence and the known-bad control for the fix. It is not to be deleted.**

### A1.3 THE IMPLICATION, STATED WITHOUT SOFTENING

**EVERY FRESH-MESH ARM THIS FAMILY HAS EVER RUN WAS ROLLING THIS DICE.** A silent win looks exactly like
a correct run. Swept for the signature across every fresh-mesh arm log on disk — `FM3`, `FM4`, `FM5`,
`FM6`, `FM7`, `FM8`, `FM9`, `FM10`, and the `DEC`/`DEC2`/`DEC3` logs — the `cgio` count is **0 in every
one of them**. That is **not** reassurance that the write was correct in those arms; it is the
observation that **the failure mode is silent when it does not crash**, and that no arm before `FM12`
carried any instrument capable of telling a won race from a correct write. No prior arm's label is
changed by this addendum and none is re-graded (`FM10` stays `NOT A RESULT`, `FM11` stays `BLOCKED`,
`O_mp` stays `GATE FAIL`); what is recorded is that **their fresh-surface provenance was never
evidenced**, and the instrument that would have evidenced it is registered in `FM13`.

**This is the SECOND independent `PRODUCER` defect in this one file.** The first was the double design
variable application at `d6r2c_freshmesh.py:423-425`, which made `FM10` `NOT A RESULT` and which
`DAFOAM_CHARTER.md` §22.3 was written from. **The fifth cause class is now earned twice over, in the same
623-line file.**

### A1.4 `Zb` IS COMPLETE AND CLEAN, AND ITS NUMBERS STAND AS MEASURED

`Zb` ran to `rc = 0` and wrote its `STATE` and `FOOTER` records
(`FM12/Zb/d6r2c_fm12.jsonl`). It is untouched by the `Zo` refusal: the two sub-arms are separate
processes on separate meshes, and `Zb` never calls `--phase deform`.

| quantity | measured | registered comparator | margin |
|---|---|---|---|
| `J_base_fresh` | **0.030642507915** | optimiser's own `J0` **0.030641631439** | diff **8.765e-07** = **0.0029 %** |
| that difference against `FM_BAND_ABS` (`= 0.01 × J0` = 3.064163e-04) | | | **349.6× inside the band** |
| max \|`CL` − target\| | **5.643e-07** (`cl06`) | `TRIM_TOL` = **1.0e-3** | 1772× inside; closed in **2** trim evaluations |
| `M0b.5` read-back | **pass** | the mesh the solver read | **0.0 m exactly** on all three conditions, 4 processors each |
| as-run `checkMesh` max non-orthogonality | **66.965** | DAFoam's declared **70.0** | **INSIDE** — unlike the optimisation mesh at **71.24** and `FM10` at **79.21**, which both breach it |
| `R1` mesher determinism | **0.0 m exactly**, **40209 / 40209** points identical, md5 identical, gzip header `MTIME` = **0 on both files** | | across **47.743 days** |
| `G-WALL` | **pass**, all three conditions | max displacement 1.000e-13 m | tol 9.157e-13 m, DERIVED in the producer's own invocation |

`Zb` wall **163.413 s**, **10.894 core-min**, **0** continuation steps, **2** primal evaluations.

### A1.5 WHAT `Zb` MEANS, AND WHAT IT DOES NOT

> **`Zb` shows the BASELINE reproduces on a freshly generated mesh to 0.0029 %. It says NOTHING about
> whether the optimum reproduces. The 24.7 % remains untested in both directions, and no reading of `Zb`
> supports it.**

`Zb` is a control on the *pipeline*, not on the *answer*. It establishes that mesh generation, staging,
decomposition, the trim and the objective assembly can be driven end to end on a mesh built today and
land on the optimiser's own starting objective. The arm's actual question — whether `J_opt` computed on a
mesh extruded around the deformed surface reproduces the 24.732273 % gain — is carried entirely by `Zo`,
and `Zo` did not run.

### A1.6 THE COST — ESTIMATE VERSUS ACTUAL (CLAUDE.md rule 12)

| | core-min | $ (DERIVED, **not measured**) |
|---|---|---|
| `FM12` predicted | 222.853 | 0.1905 |
| `FM12` cap (×3.00) | 668.559 | 0.5716 |
| **`FM12` actual** | **17.933** | **0.0153** |
| ratio actual / predicted | **0.080470** | |

**The cap was not crossed.** Dollars are DERIVED at the owner-stated $0.0513/core-h and are **NOT
MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**ATTRIBUTION: the `Zo` refusal, not misprediction.** `Zo` carried **2400.3 s** of the predicted
**3342.8 s** — 72 % of the whole prediction — and it never reached a solve, so its terms are neither
confirmed nor falsified and are carried forward **labelled untested**. The 204.920 core-min not spent is
**not waste**: it is compute the arm correctly declined to start once its input was corrupt.

**Named SEPARATELY, and NOT folded into the ratio above, because it is genuine calibration information:**
`Zb`'s registered term was **676.8 s** (574.5 s DEC7 `STATE B` trim + 88.2 s mesh/deform/stage + 14.1 s
model load) and it ran in **163.413 s** — **4.14× faster**. The cause is measured, not guessed: the trim
closed in **2** evaluations where DEC7 `STATE B` needed **6**, because `Zb` starts from `x0` on a mesh
generated at zero shape. `FM13` re-anchors `ZB_TRIM_WALL_S` on this measurement.

### A1.7 WHAT THIS ADDENDUM DOES NOT DO

- It does not change `FM12`'s gates, thresholds, caps or label; the registration above is closed.
- It does not grade `Zb` as a `PASS` of any `FM12` gate. `G1` is a `Zo` gate and `Zo` did not run;
  the `Zb` figures are reported as **measured**, under the arm's `BLOCKED` label.
- It does not re-grade `FM10`, `FM11` or `O_mp`.
- It authorises no send. **SUBMISSIONS PARKED.**
