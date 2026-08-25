# F1 (ONERA M6) — v2 BUTTERFLY TIP-FILL MESH TRIAL — RESULTS

**Date:** 2026-08-25, 19:05:38Z → 19:07:12Z (UTC)
**Team:** cfd · **Lane record**, written back into the run directory as the reporting channel.
**Instrument:** `verification/runs/F1_MESH_TRIALS_2026-08-25/run_trials.sh`
**Generator:** `cases/F1_onera_m6/make_blockmesh_f1.py` (v2 butterfly, emitted as a `blockMeshDict`)
**Both committed at `c90f9411`, BEFORE the trial was fired** (they were a killed lane's
uncommitted work; they were committed verbatim, not one byte edited).

## What this is, and what it is not

This is **not a registered rung and it grades nothing.** `docs/standards/MESH_STANDARD.md`
§8.1 requires build-and-`checkMesh` **before** any ladder is frozen, and this is that build.
It therefore carries no pre-registration and no gate. CLAUDE.md rule 12 still binds and the
measured core-minutes are recorded below.

`verification/campaign/F13_ONERA_M6_PREREGISTRATION.md` and
`verification/runs/F13_ONERA_M6_runs/analyse_f13.py` were **not touched**. The F1 R0
`GATE FAIL` at `verification/runs/F13_ONERA_M6_runs/R0_TERMINAL.md` is **settled and is not
reopened here.**

---

## HEADLINE

**The butterfly is STRUCTURALLY VALID — and it does NOT clear ≤ 70°.**

1. **`blockMesh` ACCEPTED the v2 butterfly at all three levels, rc = 0, `End` at each.**
   This is the thing v1 could not do: v1's lens tip fill was **refused** by blockMesh v2606
   with **rc 134** (repeated-vertex prism, 48 zero-area faces), and that refusal was routed
   around by hand-writing `polyMesh`. v2 needs no bypass. The generator's own docstring
   argument — that a topology should be redesigned, not the refusing tool circumvented
   (`MESH_STANDARD.md` §8.2) — is vindicated on the structural question.

2. **Max non-orthogonality is 81.9396° / 83.8768° / 83.6438° against a ≤ 70° gate.
   It DOES NOT CLEAR, at any level.** A rung frozen on this topology would fail §5
   admission exactly as R0 did. **This is a finding, not a failure**, and the generator was
   **not** edited to chase the gate.

3. **But the failure mode has changed, and that is the useful part.** v1's peak climbed
   monotonically toward 90° under refinement (84.64 → 86.02 → 86.78) because a collapsed
   line is a geometric singularity. v2's peak is **bounded and non-monotone** (81.94 → 83.88
   → 83.64). The butterfly removed the singularity; it did not remove the residual.

4. **The residual is at the TIP TRAILING EDGE, not in the fill's interior** — see §"Where
   the worst faces are". 98.4 % of severe faces at m = 4 lie in the tip fill at
   **x/c 0.903 → 0.998**, where the M6 section's half-thickness closes from 0.005851 to
   **exactly 0.000000** at the sharp TE.

5. **The one `checkMesh` failure is INHERITED, not caused by the tip fill.** The single
   failed check at every level is **high aspect ratio**, and its values are near-identical
   to v1's (5934.1 / 6469 / 6748.52 vs v1's 5934.1 / 6469.0 / 6748.5). R0_TERMINAL
   established this is arithmetic from §5's frozen 20·c_root wake, present in the control.
   **The topology redesign left it exactly where it was**, which independently corroborates
   R0_TERMINAL's attribution.

---

## MEASURED — v2 butterfly (every number read from `log.checkMesh` on disk)

| quantity | m = 1 | m = 2 | m = 4 |
|---|---|---|---|
| **cells built** | **111 872** | **894 976** | **7 159 808** |
| target (generator docstring) | 111 872 | 894 976 | 7 159 808 |
| equals target? | **YES** | **YES** | **YES** |
| refinement ratio r | — | 8.000000 (=2³) | 8.000000 (=2³) |
| **max non-orthogonality** (gate ≤ 70°) | **81.9396°** | **83.8768°** | **83.6438°** |
| **clears ≤ 70°?** | **NO** | **NO** | **NO** |
| — faces > 70° (severe) | **598** | **4 286** | **31 358** |
| — mean non-orthogonality | 15.9139° | 15.8799° | 15.8693° |
| max skewness (gate ≤ 4) | 1.4431 | 1.44325 | 1.44331 |
| **`checkMesh` prints `Mesh OK`?** | **NO** | **NO** | **NO** |
| — `Failed n mesh checks` | **1** | **1** | **1** |
| — WHICH check failed | **high aspect ratio** | **high aspect ratio** | **high aspect ratio** |
| max aspect ratio (*not gated*) | 5934.1 / 5 368 cells | 6469 / 42 950 cells | 6748.52 / 334 824 cells |
| domain bounding box | (−16.118 −16.118 0) → (16.118 16.118 1.55579) | same | same |
| blocks / vertices / polyLine edges | 24 / 60 / 28 | 24 / 60 / 28 | 24 / 60 / 28 |

`Mesh OK` count in all three `log.checkMesh`: **0 occurrences.** `Non-orthogonality check OK.`
*does* appear — OpenFOAM's default non-orthogonality **failure** threshold is 80° on the
*mean*-based test and severe faces are reported as a warning (`*`), not a failure (`***`).
**The lab's ≤ 70° gate is stricter than `checkMesh`'s own default, and it is the lab's gate
that binds.** This is why `Failed 1` names only the aspect ratio while the mesh is still
inadmissible on §5.

### Return codes — each read from its `RC_*.txt` file on disk

| level | generator `RC_dict.txt` | `blockMesh` `RC_blockMesh.txt` | `checkMesh` `RC_checkMesh.txt` | `End` in `log.blockMesh` | leg wall |
|---|---|---|---|---|---|
| m = 1 | **0** | **0** | **0** | yes | 1 s |
| m = 2 | **0** | **0** | **0** | yes | 10 s |
| m = 4 | **0** | **0** | **0** | yes | 75 s |

Runner `RC_TRIAL.txt` = **0**. **No `blockMesh` refusal occurred**, so MESH_STANDARD §8.2 /
`SUPERVISION_CHARTER.md` §3 check-2 crash triage is **not triggered** by this trial.

---

## THE HONEST COMPARISON — v1 lens vs v2 butterfly

v1 figures are quoted from `verification/runs/F13_ONERA_M6_runs/R0_TERMINAL.md` lines 20–26.

| quantity | level | **v1 lens** (hand-written polyMesh) | **v2 butterfly** (blockMesh) | change |
|---|---|---|---|---|
| accepted by `blockMesh`? | all | **NO — rc 134, refused** | **YES — rc 0** | **fixed** |
| cells built | L1 / L2 / L3 | 108 216 / 865 728 / 6 925 824 | 111 872 / 894 976 / 7 159 808 | +3.4 % (fill has more blocks) |
| **max non-orthogonality** | L1 | 84.6437° | **81.9396°** | −2.70° |
| | L2 | 86.0173° | **83.8768°** | −2.14° |
| | L3 | 86.7767° | **83.6438°** | −3.13° |
| trend under refinement | — | **monotone ↑ toward 90°** | **bounded, non-monotone** | **singularity removed** |
| **clears ≤ 70°?** | all | **NO** | **NO** | **unchanged** |
| faces > 70° | L1 / L2 / L3 | 36 / 216 / 1 440 | **598 / 4 286 / 31 358** | **≈ 16–22× MORE** |
| severe faces per cell | L1 / L2 / L3 | 3.3e−4 / 2.5e−4 / 2.1e−4 | 5.3e−3 / 4.8e−3 / 4.4e−3 | ~20× larger, both ≈ level-invariant |
| max skewness (≤ 4) | L1 / L2 / L3 | 1.44254 / 1.44298 / 1.44318 | 1.4431 / 1.44325 / 1.44331 | unchanged, both pass |
| max aspect ratio | L1 / L2 / L3 | 5934.1 / 6469.0 / 6748.5 | 5934.1 / 6469 / 6748.52 | **identical** |
| `Mesh OK` | all | NO | NO | unchanged |
| `Failed n mesh checks` | all | 1 (high aspect ratio) | 1 (high aspect ratio) | unchanged |

**Read this table honestly in both directions.** The butterfly is a genuine improvement on
the structural question and on the peak — it is a mesh blockMesh will build, and its worst
angle no longer marches toward 90°. It is a genuine **regression on extent**: it trades a
narrow 90°-bound singularity for a **~20× larger region sitting in the low 80s**, because the
severe faces are now spread along an aft strip rather than concentrated on two lines.
Neither topology is admissible. **The butterfly does not clear ≤ 70°.**

---

## WHERE THE WORST FACES ARE

Measured by `locate_bad_faces.py` in this directory, which reads
`constant/polyMesh/{points,faces}` and the `nonOrthoFaces` faceSet `checkMesh` wrote, and
computes each flagged face's centroid. `z_tip = 1.1967629` (measured).

**The reader carries a planted control (CLAUDE.md rule 3).** `--selftest` displaces one
flagged face's points by a known offset (1.234e−03, −5.678e−03, 9.012e−03) and asserts the
reported centroid moves by exactly that offset, and asserts an empty faceSet reports
`NO FLAGGED FACES`. Both assertions **passed** before any count below was believed.

| flagged faces | m = 1 | m = 2 | m = 4 |
|---|---|---|---|
| total | 598 | 4 286 | 31 358 |
| outboard of z_tip | 540 (90.3 %) | 4 008 (93.5 %) | 31 056 (99.0 %) |
| — **in the TIP FILL proper** (\|y\| ≤ 0.2) | **516 (86.3 %)** | **3 912 (91.3 %)** | **30 864 (98.4 %)** |
| — out in the wrap / farfield | 24 | 96 | 192 |
| inboard of z_tip | 58 (9.7 %) | 278 (6.5 %) | 302 (1.0 %) |

Tip-fill faces at m = 4 occupy **x ∈ [1.1001, 1.1433], \|y\| ≤ 0.00454, z ∈ [1.20424, 1.54831]**.
At the tip section (`xle = 0.690952`, `chord = 0.453096`, `xte = 1.144048`) that is
**x/c 0.9030 → 0.9983** — i.e. the butterfly's **aft strip only**, from the U2 = 0.90 block
break to the trailing edge. The M6 section's half-thickness over that strip runs
**0.005851 → 0.001497 → 0.000000** at x/c 0.90 → 0.98 → 1.00.

**Diagnosis.** The butterfly removed the two collapsed lines, and there is no repeated vertex
anywhere — blockMesh's acceptance is the proof. What it did **not** remove is that the tip
fill's aft blocks must still fill a wedge that **closes to exactly zero thickness at the
sharp trailing edge**. The core boundary (`cup90` → `mte` → `clo90`) converges on the TE
point, so the aft cells are wedge-shaped and read ~84° non-orthogonal. **The residual is the
sharp TE, not the O-grid.** The 24 / 96 / 192 wrap faces sit at a single station x = 1.1434
running radially to \|y\| ≈ 15.5 — the TE→farfield block interface, a different and much
smaller effect.

**Nothing here was acted on.** The generator was not edited to chase the gate, per the brief.

---

## COST — CLAUDE.md rule 12

- **Measured wall:** **86 s** (`TRIAL_WALL_S.txt`, from `date +%s` either side of the runner).
  Legs: m=1 1 s, m=2 10 s, m=4 75 s (`TRIAL_STDOUT.txt`).
- **Ranks:** **1** (serial; the brief allocated 1 core on a shared box). Not decomposed.
- **Measured cost = 86 × 1 ÷ 60 = 1.4333 core-minutes** = 0.02389 core-hours.
- **Derived** at the recorded c7a.4xlarge rate $0.0513/core-h: **≈ $0.00123**.
  **Derived, not measured** — the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Waste:** none. No stalled leg (longest 75 s, far under the 3600 s stall threshold), no
  re-run, no aborted level.
- **Estimate-vs-actual:** **no pre-registered estimate exists to compare against**, because a
  MESH_STANDARD §8.1 build trial carries no pre-registration (see §"What this is"). No
  `docs/COST_CALIBRATION.md` row is therefore owed for a predicted/actual ratio. The actual,
  **1.4333 core-min**, is recorded here should the supervisor wish to open one. This lane did
  not append to that ledger: `scripts/append_record.py` hands out colliding ids and no
  prediction exists to calibrate.

## CONTENTION NOTE

The box is shared — heat-transfer had 3 solvers and dafoam 2 containers live throughout.

| | start 19:05:38Z | end 19:07:12Z |
|---|---|---|
| load average (1/5/15 min) | **8.17 / 8.77 / 9.21** | **10.33 / 9.33 / 9.36** |
| MemAvailable | **18.09 GiB** | **17.91 GiB** |

Cores: 16. This trial took **1 rank**. Files: `CONTENTION_START.txt`, `CONTENTION_END.txt`.

**Memory guard (`memory_guard.sh`, log `MEMORY_GUARD.log`).** m = 4 is 7.16 M cells and an
OOM would have taken down three other teams' runs, so a watchdog polled every 10 s and would
have stopped **only** `blockMesh`/`checkMesh` processes whose `/proc/PID/cwd` resolved inside
this run directory — it could not touch another team's process. Two triggers: skip m = 4 if
MemAvailable < 6 GiB at leg start, and a hard floor at < 3 GiB. **Neither fired.**
MemAvailable at the m = 4 leg start was **17.35 GiB**; the minimum observed across the whole
trial was **12.02 GiB**. `GUARD_TRIPPED.txt` and `M4_SKIPPED.txt` do not exist. **All three
levels ran; none was skipped.**

---

## WHAT THIS LANE COULD NOT VERIFY

- **Whether any tip topology can clear ≤ 70° with §5's frozen domain.** This trial measured
  one alternative. It did not search the space, and it is not evidence that no admissible
  topology exists.
- **Why the peak fell from m = 2 (83.8768°) to m = 4 (83.6438°).** Non-monotone by 0.23°.
  Consistent with a bounded wedge angle sampled at different discrete stations, but this lane
  did not prove that; it is an observation, not an explanation.
- **The exact worst face.** `checkMesh` reports the max angle and the set of faces > 70°; it
  does not tag which face carries the max. The location analysis above is over the whole
  severe set, so "the worst faces are at the tip TE" is an inference from where the set
  concentrates (98.4 % at m = 4), not a direct read of the argmax.
- **R0's v1 figures were not re-derived.** They are quoted from `R0_TERMINAL.md` lines 20–26
  as the brief directed; that verdict is settled and was not re-audited.
- The post-hoc `locate_bad_faces.py` analysis was not separately instrumented for cost; it
  ran in tens of seconds on 1 core and is not included in the 1.4333 core-min above.

## STATUS

**An admissible F1 ladder is NOT yet reachable on this topology, and no fresh
pre-registration is warranted on this evidence.** Max non-orthogonality 81.9396° / 83.8768° /
83.6438° against ≤ 70°. Whether to pursue a third tip topology — the residual is now
localised to the sharp trailing edge at x/c 0.903–0.998 — is the supervisor's call, not this
lane's. No pre-registration was drafted.

## ARTIFACTS (all under `verification/runs/F1_MESH_TRIALS_2026-08-25/`)

`run_trials.sh` · `memory_guard.sh` · `locate_bad_faces.py` · `TRIAL_STDOUT.txt` ·
`RC_TRIAL.txt` · `TRIAL_WALL_S.txt` · `TRIAL_T0.txt` · `CONTENTION_START.txt` ·
`CONTENTION_END.txt` · `MEMORY_GUARD.log` · `v2_m{1,2,4}/log.{makeDict,blockMesh,checkMesh}` ·
`v2_m{1,2,4}/RC_{dict,blockMesh,checkMesh}.txt` · `v2_m{1,2,4}/system/blockMeshDict`

The built `constant/polyMesh` trees (m = 4 is 7.16 M cells) are **left on disk, not
committed** — every number above cites a log, and the meshes can be rebuilt by
`run_trials.sh` in 86 core-seconds.
