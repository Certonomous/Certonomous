# A5P2 — A5 U-BEND PLATEAU LADDER, SUCCESSOR TO `A5P`. **ONE GATE MOVES AND NOTHING ELSE.**

**PERMISSION: FROZEN AT THIS COMMIT. PRE-COMPUTE — no A5P2 arm has run; run root `/home/ubuntu/certonomous-runs/A5P2-ubend-plateau` DOES NOT EXIST (checked by the supervisor at freeze).**

## 1. WHY THIS EXISTS — a fail with a fix, which is the only thing this lab writes documents for tonight

`A5P` (frozen `da2e5065aee212cc8161666d826d165b012a9cb1`) ran arms `P0` and `P1` to completion —
`solver_rc=0`, `Time = 5000` reached, launch witness seen. **Its physics is measured and clean.**
Its frozen grader nonetheless returned `NOT A RESULT` on both, for one reason only:

> **`F3` reads fields at `endTime = 5000`, and DAFoam writes no field directory at `5000`.**

Measured on both arms: `processor0/` holds `0 0.0001 1000 2000 3000 4000` — writes land at every
`writeInterval` of 1000 **except the last**, although `controlDict` is `endTime 5000 / writeControl
timeStep / writeInterval 1000 / purgeWrite 0` and `Time = 5000` is reached and its `ExecutionTime`
printed. **The final iteration completes without a write.** The `4000` directory is complete
(`T U p nut nuTilda alphat phi rho meshPhi betaFINuTilda …`), so writing works; only the last one
is missing.

**This is a DAFoam/OpenFOAM-layer behaviour and it is SURFACED, not worked around** (Sanaa,
2026-09-10). **The gate was mine and it was unreachable on this solver — that is my defect, not
the run's**, and `A5P`'s arms keep their `NOT A RESULT` rather than being rescued by a rewritten
gate.

## 2. THE ONE CHANGE

| | `A5P` | **`A5P2`** |
|---|---|---|
| `F3` field-check time | `endTime` = **5000** | **the LAST WRITTEN time directory**, discovered from disk, asserted non-empty, and **asserted ≥ 4000** so a truncated run cannot satisfy it cheaply |

**EVERYTHING ELSE IS INHERITED BY REFERENCE FROM `A5P` AT `da2e5065aee212cc8161666d826d165b012a9cb1` AND IS NOT RESTATED HERE:** the five arms P0–P4 and their one-change-each definitions, every predicted outcome, `G1` (`p` initRes ≤ 2.057e-05), `G2` (last-decile monotone non-increasing and spread ≥ 1.0e-03, ≥ 5 samples asserted), `BREAK = G1 AND G2`, the falsifier (spread < 1.0e-06 ⇒ NEW PLATEAU, `GATE FAIL`), `F1`, `F2` (`Residual Norm2` ≤ 1.0e+04), `F4`, the `N-D44` initRes-only rule, the `N-D43` product floor (`1e-8 × 1e7 = 0.1`, `runScript.py:59-60`), the planted-zero controls, the cost model and the cap. **A reader must read `A5P` beside this file.**

**Why ≥ 4000 and not "whatever exists":** an unqualified "last written time" would be satisfied by a
run that died at 1000. The floor makes the check refuse a short run instead of grading it.

## 3. WHAT IS RE-USED AND WHAT IS RE-RUN

The residual limbs (`G1`, `G2`, falsifier, `F1`, `F2`, `F4`) read the **log**, and `A5P`'s logs
already carry them — `P0` `p initRes(5000) = 2.056815e-04`, `P1` `5.931624e-05`, both with
`Bounding = 0` and worst `Residual Norm2` 59.32 / 58.89. **Those numbers are not re-bought.** The
five arms are re-run only so that every limb of one verdict comes from one execution under one
frozen grader, which is worth ~22.7 core-min.

**Cost: 4.533 core-min/arm measured on `A5P` `P0` × 5 arms = 22.7 core-min estimate, cap 68 (3×),
`$0.0194` / `$0.0581` DERIVED, not measured.** The Case Protocol 3D exemption is **not** invoked.

## 4. PREDICTION REGISTERED BEFORE THESE ARMS RUN

From `A5P`'s completed arms: **`P0` reproduces `2.0568e-04`; `P1` (SIMPLEC) lands near `5.93e-05`,
i.e. the plateau MOVES ~3.5× and does NOT break `G1`; and `primalMaxRes` stays on `nuTilda` at
~3.6e-04 in both, essentially unmoved.** **If `P1` instead breaks `G1`, or if `primalMaxRes`
leaves `nuTilda`, this prediction is FALSIFIED and that is the finding.**

## 5. INSTRUMENTS

`a5p2_grade.py` and `a5p2_run_arm.sh`, derived from `A5P`'s with the single `F3` change. md5s and
the image pin are recorded at the freeze commit by the supervisor. The launcher keeps `A5P`'s
first-artifact witness (`^ExecutionTime = `, with `^Time = ` the forbidden decoy), refusal codes
88/89/90, `docker kill` read back, preserved stderr, and the strict-increase mtime pre-capture.

## 6. FREEZE STAMP — 2026-09-11, dafoam-supervisor

**FROZEN AT THIS COMMIT.** `a5p2_run_arm.sh` md5 `042c93257169e5e15ccd3bd61f380a29` (post-substitution, `bash -n` clean, 0 unfilled slots); `a5p2_grade.py` md5 `a02f7d0e0c4392b01e18bbaa5071d293`; image `dafoam/opt-packages:latest` @ `sha256:9d45679d…`; `runScript.py` md5 `06fb0ed4228d9927992a12a2fb68055c`; cpuset 12-15. Grader `--selftest` **35 passed / 0 failed, true exit 0**, run by the supervisor.

**A SECOND REPAIR, FOUND BY RUNNING THE FIXED GRADER AGAINST A5P's REAL P2 ARM AND WORTH MORE THAN THE FIRST.** With `F3` retargeted, the grader still **REFUSED (exit 2)** — on its own planted control:

> `control A residual plant FAILED — the UNPLANTED log already satisfies G1, so the flip proves nothing; control is vacuous on this input`

**The refusal was CORRECT.** `A5P`'s control planted a *passing* value and demanded `G1` flip `False → True`; that is vacuous whenever the arm **already passes**, and `P2` — the one arm that broke the plateau, to `1.449e-08` — is exactly that arm. **So the frozen control could grade every failure and no success.** Rule 3's requirement is that a reader be shown able to return **the other answer**, whichever answer it starts from — not one fixed direction. `A5P2`'s control A is now **direction-aware**: it plants a *failing* value (`9.876543e-03`) when the arm already passes, and the passing value otherwise. Verified on `P2`: *"arm already PASSES G1 unplanted, so the control ran in the OTHER direction… G1 flipped True → False."*

**PRE-COMPUTE RESULT THAT MOTIVATES THE RE-RUN, recorded here before A5P2's own arms run.** Grading `A5P`'s existing `P2` artefacts with this grader yields **`GATE FAIL — indeterminate drift`**: `G1` **True** (`p initRes 1.4485774681e-08`), `G2` **False** (spread `1.686e-06` against the required `≥1.0e-03`), and the falsifier **False** (`1.686e-06` is above the `1.0e-06` new-plateau line). Field health clean — `Bounding 0`, worst `Residual Norm2` `59.32`, `nuTilda` min `1.55e-05` from **4 files at the last written time**, so `F3` now reads.

**AND THE PHYSICS POINT, which is the finding: `TP1−TP2 = 52.34509736` against `P0`'s `52.34517755` — a delta of `1.53e-06`. The pressure residual fell 14,199× and THE OBJECTIVE DID NOT MOVE.** So the `2.06e-04` "plateau" was **not** holding the answer away from convergence; it was an artefact of missing non-orthogonal correction in the pressure equation, and the flow solution was already converged to within 1.5e-06 of the objective. **Registered as a prediction for A5P2's own arms: `P2` will again clear `G1` by ~3 orders while `TP1−TP2` stays within `1e-05` of `P0`'s. If the objective MOVES materially, this reading is falsified and the plateau mattered after all.**
