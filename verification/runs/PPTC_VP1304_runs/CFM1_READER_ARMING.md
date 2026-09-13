# PPTC VP1304 — RUNG CFM-1 — READER ARMING RECORD

**VERDICT: `BLOCKED`.** Under the registered stop rule
(`verification/campaign/PPTC_CFM1_PREREGISTRATION.md` §8) and refusal limb **R4** (§9),
**neither a `PASS` nor a `GATE FAIL` from a cfMesh mesh is admitted, and nothing is said about
cfMesh at all.** `cartesianMesh` was **not launched**, and the registered run directory
`/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh` **still does not exist.**

| control | registered requirement | outcome |
|---|---|---|
| **B** — synthetic, both directions, at `--nlayers 6` **and** `--nlayers 2` | layered `== 100.000%`, layerless `== 0.000%` | **PASSES, all four readings** (§2) |
| **A** — known-NO-layers real mesh, at `--nlayers 6` **and** `--nlayers 2` | `C_full == 0.000%` **AND** `C_2 == 0.000%` | **FAILS** in the false-positive direction: `C_2 = 0.248%` at both depths (§1, §3) |
| **C** — the planted zero, rule 3 | `max abs delta-t1 == PLANT` to `1e-9` | **NOT EXERCISED** — the reader refused before the plant was written, on a defect in its own CLI (§3b) |
| **D** — SPD geometry control | volume difference `<= 1e-6`, identical negative counts | **arming fired both ways first-hand; the registered comparison did NOT run in this lane's hands** (§4) |

**Two findings, not one.** The rung is `BLOCKED` by **A**. Separately, **C could not be run at
all**, which means the instrument has **never been shown seeing a known non-zero on a real
mesh** — and CLAUDE.md rule 3 says exactly what that costs: a zero from a reader not shown able
to see a non-zero is not evidence. **That second finding is the one that must be repaired
first** (§7 route 0).

**What this record is.** §4 of the pre-registration registers the reader's arming as a
**blocking precondition** and discloses that the instrument was **unexercised** at the v1.0
freeze. §8 registers four controls and a stop rule **written in both directions**. This file
records **what the controls actually printed**. It is a run record, not a pre-registration, and
it grades nothing about cfMesh.

**Instrument, unchanged:** `cases/PPTC_VP1304/mesh/read_cfmesh_layers.py`, sha256
`c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8` — **identical to the value
frozen at §14 item 4. Not one line of the reader was edited**, before or after the failure.

**Registration state:** v1.1, amendments A1 and A2 committed at `0e162fb058d1cd9b0aa18dada2e0952fc9301c41`.
The arming was run at `--nlayers 6` (as §8 registers control B) **and** at `--nlayers 2` (the
depth G1 now reads under amendment A2.5), because A2.10 added the second run to the stop rule.

---

## 1. WHAT FAILED, AND IN WHICH DIRECTION

**Control A — the known-NO-layers real mesh — FAILS in the FALSE-POSITIVE direction.**

The registered requirement (§8 row A) is **`blades C_full == 0.000%` AND `C_2 == 0.000%`** on
`/home/ubuntu/certonomous-runs/PPTC_VP1304/F360_coarse`, whose own log reads
`Extruding 0 out of 724711 faces (0%)` (`…/F360_coarse/log.snappyHexMesh:3314`).

At `--nlayers 6`, on 382,233 sampled `blades` boundary faces of a 19,700,035-cell mesh:

| field | read | requirement | |
|---|---|---|---|
| `C_full(depth>=6)` | **0.000%** | `== 0.000%` | meets it |
| `C_2(depth>=2)` | **0.248%** | `== 0.000%` | **FAILS** |
| `median t1` | `4.780831e-04` m (`0.7649` local cells) | — | reported, not gated |

The reader **refused rather than degraded**, exactly as §4 and CLAUDE.md rule 4 require, and
exited **rc = 2** with its own words:

> `GEOMETRY CONTROL FAILED: the reader reports layers on a mesh whose own log says 0 faces were
> extruded. NOTHING IT SAYS IS EVIDENCE. REFUSE.`

**0.248% of 382,233 faces is roughly 948 blade faces** on which a mesh that extruded nothing
reads as layered to depth ≥ 2 — a near-wall cell thinner than `0.5 s_P` with a second cell
`1.10–1.35×` taller than it. That is a plausible property of a mesh carrying **316
negative-volume cells and 91,876 illegal faces** after snapping, and it is **not** evidence of a
coding error in the reader; but the registered requirement is `0.000%`, **not a tolerance**, and
the stop rule admits no reading of it as "close enough".

**THIS IS WHY THE BIDIRECTIONAL STOP RULE EXISTS.** §8's preamble records that this act was
already bitten by a stop rule written in one direction only. The direction that fired here is
the one a one-sided rule would have missed: `C_full` at the registered depth read a clean
`0.000%`, and **a rule that only asked "did the known-bad mesh pass?" would have waved this
through.**

## 2. CONTROL B — THE SYNTHETIC POSITIVE AND NEGATIVE — **PASSES, IN BOTH DIRECTIONS, AT BOTH DEPTHS**

`--selftest` builds a column of graded sub-cells inside one local cell and a plain layerless
column of the same cell, and requires the reader to read **100.000%** on the first and
**0.000%** on the second. Amendment A2.10 added the second depth to the stop rule.

**B at `--nlayers 6`** — as §8 registers it, `s_P = 6.2500e-04` m, 5-cell and 9-cell synthetic meshes:

| direction | `C_full(depth>=6)` | `C_2(depth>=2)` | `median t1` | requirement | |
|---|---|---|---|---|---|
| POSITIVE — synthetic LAYERED column | **100.000%** | 100.000% | `6.294109e-05` m (`0.1007` local cells) | `== 100.000%` | meets it |
| NEGATIVE — synthetic LAYERLESS column | **0.000%** | **0.000%** | `6.250000e-04` m (`1.0000` local cells) | both `== 0.000%` | meets it |

> `ARMED: layered column reads 100.000% at depth 6; layerless column reads 0.000% at depth >= 2.
> Both directions fired.`

**B at `--nlayers 2`** — the depth G1 now reads under amendment A2.5:

| direction | `C_full(depth>=2)` | `C_2(depth>=2)` | `median t1` | requirement | |
|---|---|---|---|---|---|
| POSITIVE — synthetic LAYERED column | **100.000%** | 100.000% | `2.840909e-04` m (`0.4545` local cells) | `== 100.000%` | meets it |
| NEGATIVE — synthetic LAYERLESS column | **0.000%** | **0.000%** | `6.250000e-04` m (`1.0000` local cells) | both `== 0.000%` | meets it |

> `ARMED: layered column reads 100.000% at depth 2; layerless column reads 0.000% at depth >= 2.
> Both directions fired.`

**TWO THINGS THIS CONTROL INDEPENDENTLY CONFIRMS, BOTH OF THEM PREDICTIONS MADE BEFORE IT RAN:**

1. **The 2-layer arithmetic of amendment A2.3 is exactly right.** The reader, given a column
   built to the 2-layer specification, measured `median t1 = 2.840909e-04 m` and
   `0.4545 local cells` — the `s_P/2.2 = 2.840909e-4 m` and `t_1/s_P = 0.454545` that A2.3
   registered as the prediction, **to every digit printed**. The `1.10×` headroom against
   `FIRST_FRAC = 0.5` that A2.3 registered as a **weakening** is visible in that `0.4545`.
2. **The `6.29461e-5` transcription slip that A2.3 disclosed in the struck §5 table is
   confirmed as a slip.** The instrument, given the 6-layer column, printed
   `median t1 = 6.294109e-05 m` — A2.3's corrected `6.294110e-5`, not the frozen table's
   `6.29461e-5`.

## 3. CONTROL A AT `--nlayers 2` — **FAILS IDENTICALLY, AND THE IDENTITY IS ITSELF INFORMATION**

Amendment A2.5 registered a cheap arming check on the invocation: at `--nlayers 2`,
`C_full(depth>=2)` and `C_2(depth>=2)` are the same quantity and **must print the same number**,
or `--nlayers 2` did not reach the reader. On `F360_coarse`, 382,233 sampled `blades` faces:

| field | read | requirement | |
|---|---|---|---|
| `C_full(depth>=2)` | **0.248%** | `== 0.000%` | **FAILS** |
| `C_2(depth>=2)` | **0.248%** | `== 0.000%` | **FAILS** |
| `median t1` | `4.780831e-04` m (`0.7649` local cells) | — | reported, not gated |

**The two fields printed the same 0.248%**, so the invocation check passes: `--nlayers 2`
reached the reader and the reading is not void for that reason. Wall `6:15.62`, peak RSS
`46.6 GB`, exit **rc = 2**, same refusal text as §1.

**THE SIZE OF THE CONTAMINATION, STATED BECAUSE IT WILL BE THE FIRST QUESTION — AND IT DOES NOT
CHANGE THE VERDICT.** `0.248%` sits **101× below** G1's `25.0%` `GATE FAIL`/R1 boundary and
**363× below** its `90.0%` `GATE REACHED` bar, so on these numbers the false-positive floor
could not by itself carry G1 across a band. **That is an argument about magnitude and the
registered requirement is not a magnitude: §8 row A says `== 0.000%`, the stop rule says a
failure in EITHER direction stops the rung, and §8's own preamble records that this act was
already bitten once by a stop rule that was not strict enough.** The rung is `BLOCKED`.

## 3b. CONTROL C — THE PLANTED ZERO — **COULD NOT BE EXERCISED. THE REASON IS A DEFECT IN THE READER'S CLI, AND IT IS THE SECOND FINDING OF THIS ARMING.**

Control C was run as §8 registers it, at the depth G1 now reads:

> `read_cfmesh_layers.py --nlayers 2 --case …/F360_coarse --points
> …/F360_coarse/0/polyMesh/points --plant-dir …/CFM1_READER_ARMING/plantC`

It reached the control's own banner —

> `=== PLANTED-ZERO CONTROL: PLANT = 1.234000e-03 m at 5000 blades faces ===`

— and then **refused**, exit **1**, wall `4:03.10`, peak RSS `23.0 GB`:

> `REFUSE: points/faces inconsistent:
> …/F360_coarse/constant/polyMesh/points has 20518324 entries but the face list references
> 20507704. This is the stale-points defect. The reader does NOT measure an inconsistent mesh.`

**No plant was written. `…/CFM1_READER_ARMING/plantC` does not exist.**

### THE TRIAGE — a crash is a finding until triage says otherwise (`SUPERVISION_CHARTER` §3)

**The guard is right and the plumbing is wrong.** `--points` exists in this reader **precisely**
for this defect — its own help text reads *"override `constant/polyMesh/points` (stale-points
defect)"* (`read_cfmesh_layers.py:432`) — and the docstring at `:32` records that the whole
points/faces consistency check *"was paid for by the stale-points defect on `F360_coarse`"*.
**Two of the three call sites honour the override and the third does not:**

| call site | line | honours `--points`? |
|---|---|---|
| control **A**, the known-no-layers mesh — `Mesh(a.control_none, points_path=a.control_none_points)` | `:454` | **yes** |
| the final measurement pass — `Mesh(a.case, points_path=a.points)` | `:474` | **yes** |
| control **C**, inside `plant_check` — `base = Mesh(case)` | `:364`, signature at `:360` | **NO — `plant_check` has no parameter to receive it** |

So on any case whose final point positions live in `0/polyMesh/points` — which is every snapped
snappy mesh in this act — **the registered planted-zero control cannot be run through the
registered CLI at all**, while the two controls beside it can. The refusal is the mesh
consistency guard firing correctly; what it exposes is that **`--points` was threaded to two of
three readers and missed the one that matters most to CLAUDE.md rule 3.**

**THIS LANE CHANGED NOTHING.** `read_cfmesh_layers.py` re-hashes to
`c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8`, the §14 item 4 value, after
this refusal as well as before it. The repair is a **measurement-script diff**, and under
`SUPERVISION_CHARTER` §3 check 1 the supervisor reads such a diff **personally, as a diff** —
it is undelegable and this lane has written none. For the supervisor's convenience the shape of
it is: give `plant_check` a `points_path` parameter and pass it at `:364`; `:395`'s
`Mesh(plant_dir)` is already correct, because the plant directory's own `points` file **is** the
planted one.

### WHAT THIS COSTS THE DIAGNOSIS

**C's absence does not change the verdict** — the stop rule is conjunctive and **A has already
failed**, so the rung is `BLOCKED` either way. **It does cost the diagnosis**, and that matters
for §7:

- **Had C passed**, the reader would have been shown seeing a known non-zero of exactly
  `1.234e-03` m on a real mesh, and the `0.248%` of §1 and §3 would most likely be a **real
  geometric property of a snapped mesh carrying 316 negative-volume cells** — making
  `F360_coarse` a poor negative control rather than the reader a poor instrument.
- **Had C failed**, the reader could not see a planted non-zero, and under rule 3 **its zeros
  would not be evidence either** — making the clean `0.000%` that `C_full(depth>=6)` returned in
  §1 worthless too.

**Neither branch is closed.** The planted-zero control on this rung is **`PENDING`** in the
registered sense — not yet run — and **§7 should not be ruled on until it has been.** A control
that cannot be run is not a control that passed.

## 4. CONTROL D — THE SPD GEOMETRY CONTROL

**D's own arming fired first-hand, in both directions.** `spd_gate.py`
(`verification/runs/PPTC_VP1304_runs/spd_gate.py`, blob `c68c4ddb`, verified at `HEAD` for that
path) ran its planted controls before touching any real mesh:

| direction | mesh | faces with `w_f <= 0` | cells with `A_PP <= 0` | verdict |
|---|---|---|---|---|
| NEGATIVE | a valid two-cell mesh, must PASS | 0 | 0 | **PASS** |
| POSITIVE | one face DELIBERATELY INVERTED, must FAIL | 1 | 2 | **GATE FAIL**, witness cell **0**, `A_PP = -8.842105263e-01`, witness centre `(0.500000, 0.500000, 0.434524)` m |

> `ARMED: valid mesh PASS, inverted mesh FAIL with witness cell 0 A_PP = -8.842105e-01`

**The registered D comparison did NOT run in this lane's hands, and that is stated rather than
borrowed.** `spd_gate.py` then **refused** `F360_coarse`, exit **1**, on its own stale-points
guard:

> `REFUSE: points/faces inconsistent in …/F360_coarse/constant/polyMesh: points file has
> 20518324 entries but the face list references 20507704. 10620 orphan points. This is the
> stale-points defect: the final positions are in 0/polyMesh/points. The gate does NOT grade an
> inconsistent mesh.`

That is the instrument refusing rather than degrading — **correct behaviour, not a control
failure** — and it means `spd_gate.py` has no `--points` override and needs a consistently
staged case. **This lane did not build one**: staging a second 4 GB copy of a 19.7 M-cell mesh
to arm a control whose registered subject is the *produced* cfMesh mesh is not compute this
lane was authorised for, and the rung is already `BLOCKED` on control A.

**A prior lane's artifact carries D's registered numbers and is CITED AS SUCH, not claimed:**
`/home/ubuntu/certonomous-runs/PPTC_VP1304/spd_gate_baseline2_status` (mtime 2026-09-13 17:21)
records, on consistently staged `F360_coarse` geometry, `19700035` cells:

| registered requirement (§8 row D) | value in that artifact | |
|---|---|---|
| max relative cell-volume difference `<= 1e-6` | **4.998e-08** | meets it |
| identical negative-volume counts | **mine 316 / OpenFOAM 316** | meets it |

**Provenance limit, stated:** that artifact was produced by a prior lane, not by this one. Its
file mtime (17:21) follows `spd_gate.py`'s (17:16), which is consistent with the registered
blob having produced it, **but this lane did not witness the run and does not assert the
identity of the binary that wrote it.** Under the stop rule that makes D **not independently
discharged by this lane**; it does not change the verdict, which is already `BLOCKED` on A.

## 5. WHAT WAS WRITTEN, AND WHAT WAS NOT TOUCHED

- **The registered run directory `/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_cartesianMesh`
  was NOT created and does not exist** — checked before and after the arming. §14 item 1 still
  holds.
- All arming output went to **`/home/ubuntu/certonomous-runs/PPTC_VP1304/CFM1_READER_ARMING/`**,
  registered for the purpose at amendment A2.10.
- **`…/F360_coarse/` and `…/PRISM_A2_absthick/` were not written to** (§13). **Nothing at all
  was written by control C** — it refused before its first write, and
  `…/CFM1_READER_ARMING/plantC` does not exist. Disclosed for the successor who repairs §3b:
  when C does run, its implementation **hard-links** `faces`, `owner`, `neighbour` and
  `boundary` from the source case into the plant directory (`read_cfmesh_layers.py`,
  `plant_check`, the `os.link` loop). A hard link creates a directory entry in the *plant*
  directory and changes no byte and no mtime in `F360_coarse`; it does bump those inodes' link
  count. **Named here rather than left to be discovered.**
- **PRISM-A2 was live throughout** — `…/PRISM_A2_absthick/log.snappyHexMesh` was being written
  within ten minutes of the start of this arming. Nothing in this arming touched it. The
  preamble's rule that **CFM-1 must not start before PRISM-A2 reports** is unaffected: no
  mesher ran.
- **The reader was not edited.** `read_cfmesh_layers.py` re-hashes to
  `c64d25a138167df3491b9cee57e185d7dc5f46524b2f0b640c6a1c2968680fd8`, the §14 item 4 value,
  **after** the failure as well as before it.
- `__pycache__` under `cases/PPTC_VP1304/mesh/` was cleared before the first control and
  `PYTHONDONTWRITEBYTECODE=1` was set for every run, because a stale bytecode inverts exactly
  this class of control.

## 6. WHAT THIS DOES NOT SAY

- **It says nothing about cfMesh.** Refusal limb **R4** is explicit: any control failure means
  `BLOCKED` and **no statement about cfMesh is made at all**. This record makes none.
- **It is not a `GATE FAIL`.** No gate in §6 has a value. G1, G2, G3, P-CFM, G4 and G5 are all
  **`PENDING`** — the display state, not a softened failure.
- **It is not a finding against the reader's code.** The reader did exactly what §4 and rule 4
  require: it refused, in the direction the registered requirement names, and exited non-zero.
  **The instrument worked. The control did not pass.** Those are different sentences.
- **Nothing here is sent, filed, uploaded, registered, posted or commented outside this box.**

## 7. WHAT THE SUPERVISOR MUST RULE ON — OPTIONS, NOT A CHOSEN REPAIR

**This lane changed no line of the reader and proposes no threshold change.** Five routes exist
and they are not equally honest; they are listed with that said.

0. **RUN CONTROL C FIRST. Nothing else should be ruled on before it.** C is the rule-3 planted
   zero and it **has not been exercised at all** (§3b) — not because it failed, but because
   `plant_check` does not receive the `--points` override that the two controls beside it do.
   Until the reader has been shown seeing a known non-zero **on a real mesh**, routes 1-4 are
   being argued about an instrument whose sensitivity is untested, and **CLAUDE.md rule 3 says
   plainly that its zeros are not evidence in that state.** The repair is a measurement-script
   diff at `read_cfmesh_layers.py:360` and `:364`, which is **the supervisor's to read as a
   diff** and which this lane has not written.
1. **Diagnose before repairing.** Locate the ~948 offending `blades` faces and test whether they
   sit inside the snapped mesh's damaged region (the 316 negative-volume cells / 91,876 illegal
   faces). If they do, the finding is that **`F360_coarse` is a poor negative control** — it is a
   *distorted snapped* mesh, not a clean layerless cartesian one — and the reader is sound.
   **This is the route that produces knowledge rather than a passing control.**
2. **Register a better known-NO-layers control.** The natural one is a cfMesh mesh built with the
   `boundaryLayers` block absent — a clean octree mesh with provably zero layers. It costs a
   mesher run, so it is rung compute and the supervisor's call.
3. **A validity guard in the reader**, so a column walked through an illegal face is reported as
   undefined rather than as a depth. **This is a measurement-script edit and under
   `SUPERVISION_CHARTER` §3 check 1 the supervisor reads the diff personally as a diff.** This
   lane has written no such diff.
4. **Loosen control A's `0.000%` to a tolerance. THIS LANE RECOMMENDS AGAINST IT.** Even
   pre-compute, where §2b makes it legal, relaxing a control *because it failed* is the exact
   shape the freeze exists to prevent, and §8's own preamble records that this act was bitten
   once already by a stop rule that was not strict enough.

**Until these are ruled on and satisfied, CFM-1 is `BLOCKED` and `cartesianMesh` does not run.**

**One further thing the supervisor should know, and it is not about this rung.** `git status`
reports the shared index carrying a **staged deletion** of
`cases/PPTC_VP1304/mesh/cfmesh/meshDict.bunnyOctree.PUBLISHED` and `MM` on both files this lane
committed, while all three verify **byte-identical against `HEAD`**. That is the known stale
shared-index read under concurrency, not a real state. **This lane inspected it and did not
revert it** — the index is the chief's call (CLAUDE.md rule 10) — but a peer who runs a bare
`git commit` would delete that file from `main`.

## 8. COST — MEASURED, AND COMPARED WITH THE PRE-REGISTERED ESTIMATE (CLAUDE.md rule 12)

**Unit: core-minutes** = wall s × ranks ÷ 60. Every control ran **single-threaded, 1 rank**, on
the 96-core box alongside a live PRISM-A2. Wall and peak RSS are read from `/usr/bin/time -v`
output staged beside this record; nothing is typed from memory. `…` is
`/home/ubuntu/certonomous-runs/PPTC_VP1304` throughout.

| control | wall (s) | ranks | **core-min** | peak RSS | artifact |
|---|---|---|---|---|---|
| **B @ `--nlayers 6` + A @ `--nlayers 6`** | 466.34 | 1 | **7.772** | 46.6 GB | `…/CFM1_READER_ARMING/log.controlB6_and_A6.{out,time}` |
| **B @ `--nlayers 2` + A @ `--nlayers 2`** | 375.62 | 1 | **6.260** | 46.6 GB | `…/CFM1_READER_ARMING/log.controlB2_and_A2.{out,time}` |
| **D** — selftest fired both ways, then refused on stale points | 281.40 | 1 | **4.690** | 23.5 GB | `…/CFM1_READER_ARMING/log.controlD.{out,time}` |
| **C** — refused before the plant was written | 243.10 | 1 | **4.052** | 23.0 GB | `…/CFM1_READER_ARMING/log.controlC.{out,time}` |
| **TOTAL** | **1366.46** | 1 | **22.774** | 46.6 GB max | |

**Against the pre-registration's §11 rows**, which are the frozen estimates:

| §11 row | predicted (core-min) | actual (core-min) | ratio | comparable? |
|---|---|---|---|---|
| "reader arming, controls **B** and **A**" | 45 | **14.032** — and that is **two** full B+A runs, at both depths, where §11 costed one | **0.312** | yes |
| "planted-zero control **C**" | 60 | **4.052** | **0.068** | **NO** — C refused before the plant was written; the row prices work that did not happen |
| "`spd_gate.py` + control **D** (G4)" | 20 | **4.690** | **0.235** | **NO** — the row bundles G4, and G4 never ran |
| **arming block, total** | **125** | **22.774** | **0.182** | mixed, per the rows above |

**Attribution, split honestly rather than rolled into one ratio:**

- **Misprediction, conservative direction, on the one row that IS comparable — and the basis
  explains the whole gap.** §11's A row was reasoned from *"A walks 724,711 boundary faces of a
  19.7 M-cell mesh"*. The reader in fact walks the **382,233 `blades`** faces of that mesh;
  **724,711 is the four-patch total from the snappy log, not the blades count.** The estimate
  was therefore built on a face count **1.90× larger than the work actually done**, and even at
  **twice** the registered number of runs the row came in at `0.312`. **This is a misprediction,
  not a saving: the run did less work than the estimate described.**
- **Two rows are NOT comparable and are not presented as if they were.** C's `0.068` and D's
  `0.235` price runs that **ended in refusals before reaching the work the row budgeted**. A
  ratio computed against work that did not happen would flatter the lab's forecasting, which is
  exactly what this ledger exists to prevent. **They are reported, and marked as not
  comparable.**
- **No contention component is claimed.** PRISM-A2 was live and box load averaged ~56 of 96
  cores, but these are single-threaded jobs on an unsaturated box and **no per-run contention
  was measured, so none is attributed** rather than guessed at.
- **Waste, named separately and never absorbed into the ratio (`COMPUTE_BUDGET_CHARTER` §6):
  0.000 core-min.** Every run produced either a registered control reading or a registered
  refusal, and **both refusals are findings** (§3b, §4), not discarded work. No row is near the
  charter's 3600 s stall threshold, so **gross and cleaned are the same figures.**
- **Dollars, DERIVED NOT MEASURED** — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER` §5), so this is reported-by-owner arithmetic at the recorded
  c7a.4xlarge rate **$0.0513/core-h**: 22.774 core-min = 0.3796 core-h = **$0.0195 derived**.
- **The cap is untouched.** §11's `1200 core-min` cap is the rung's, it is **recorded, not a
  stop** (Sanaa's NO-CAP ruling of 2026-09-12, directive #17), and the arming has spent
  **1.90%** of it.

**A row is appended to `docs/COST_CALIBRATION.md` for this process** per rule 12, with a
machine-minted id.
