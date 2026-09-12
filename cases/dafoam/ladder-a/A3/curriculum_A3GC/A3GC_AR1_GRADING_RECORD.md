# A3GC-AR1 — GRADING RECORD. **NOT A RESULT.**

Graded 2026-09-12 by a `lab-lane` of the dafoam team against
`A3GC_ANCHOR_RERUN_PREREGISTRATION.md`, **frozen at `3d416043b` before the run root
existed**. SUBMISSIONS PARKED (CLAUDE.md rule 7).

Run root: `/home/ubuntu/certonomous-runs/A3GC-AR1`
Solver log: `/home/ubuntu/certonomous-runs/A3GC-AR1/primal.log`

---

## 1. VERDICT

**`NOT A RESULT`**, composed by the frozen comparator's own `compose_verdicts()`.

| registered limb | token | measured |
|---|---|---|
| §5 gate 1 — strict completion (rule 4) | **NOT A RESULT** | clause 5 FAIL; see §3, and read §3.1 before believing it |
| §5 gate 2 — every per-equation initRes ≤ 1e-06 | **NOT A RESULT** | `nuTilda` = **1.008860e-06**, i.e. **1.0089×** the registered floor |
| §5 gate 3 — CD inside 0.0229956 ± 2 % | **PASS** | **0.02300300328**, **+0.0322 %** off anchor |
| §5 gate 3 — CL inside 0.3131159 ± 2 % | **PASS** | **0.3131159742**, **+0.0000 %** off anchor |

**The band PASS does not lift the verdict and was never able to.** CLAUDE.md rule 5's
direction clause is one-way: a gate can turn a PASS *into* `NOT A RESULT` and never the
reverse, and §5 of the registration says in its own words that failing gate 1 or 2 makes
the row `NOT A RESULT`. Both numbers are recorded here because suppressing a passing
band would be as dishonest as quoting it as the verdict.

**The registered band was not widened and is not proposed for widening.**

---

## 2. FROZEN-PATH PROVENANCE — CHECKED, NOT ASSUMED

| artifact | md5 on disk | md5 of the committed blob | agree |
|---|---|---|---|
| `a3gc_grade.py` | `73dbe368934956700da87e5a1f44ea0c` | `3d416043b:` → same; `HEAD:` → same | **yes** |
| `A3GC_ANCHOR_RERUN_PREREGISTRATION.md` | `c1c6669ed68e1ae4bf76ab6f53dc884f` | `3d416043b:` → same | **yes** |

The registered md5 in §6 of the pre-registration is the md5 that ran. The proposed
`a3gc_grade_R2_GFIELD.diff` was **NOT applied** and is not part of AR1 (§6).

**Planted-zero control (CLAUDE.md rule 3), frozen CLI `plant` sub-command, all five seen:**

| reader | true | planted | read back | ok |
|---|---|---|---|---|
| cell count | 399,360 | 1,234,567 | 1,234,567 | yes |
| patch faces | 6,240 | 4,321 | 4,321 | yes |
| log `CD` | p2p 1.632e-07 | 1.234e-03 | p2p 1.234041e-03 | yes |
| log `CL` | p2p 2.590e-08 | 1.234e-03 | p2p 1.234010e-03 | yes |
| `initRes` (N-D44, `finalRes` decoy 9.99) | — | 1.234e-12 | 1.234e-12 | yes |

`ALL PLANTED CONTROLS SEEN`. Every zero and every pass below comes from a reader shown
able to see a non-zero **of this family's own on-disk format**.

`guard_no_asserts()` passed (L-332): the comparator carries zero `assert` statements.

---

## 3. §5 GATE 1 — STRICT COMPLETION, CLAUSE BY CLAUSE

Run through the frozen `gate_g_complete()` unchanged.

| clause | result | measured |
|---|---|---|
| 1 `rc == 0` | OK | `rc = 0` from `primal.log.rc` |
| 2 `End` line present | OK | found |
| 3 last time == `endTime` | OK | last printed `Time = 6000`, controlDict `endTime 6000` |
| 5 `ExecutionTime` count | **FAIL** | **61 `ExecutionTime` lines vs 62 `Time = ` lines** |
| 4 fields present at `endTime` | OK | all 6 fields from `0` present: `T U alphat nuTilda nut p` |
| 6 **AGE GUARD** | OK | **all 36 endTime fields NEWER than `processor0/0/T.gz`** |

Cadence cross-check, printed by the comparator as REPORTED-NOT-GATED:
`1 + floor(6000/100) = 61` predicted, **62** measured.

### 3.1 CLAUSE 5's FAILURE IS A READER ARTIFACT OF A SHARED LOG FILE, AND I AM REPORTING IT AS A COMPARATOR DEFECT, NOT AS AN AR1 DEFECT

`primal.log` holds **two programs' output concatenated**. `decomposePar` ran first and
wrote into the same file; its output contains **its own `Time = 0` at line 116 and its
own `End` at line 123**, before the solver's banner at line 127. The solver's first step
is `Time = 1` at line 585 and its own `End` is at line 37561.

So the arithmetic is:

* 62 `Time = ` lines = **61 solver samples + 1 from `decomposePar`**
* 2 `End` lines = `decomposePar`'s + the solver's

The solver's own cadence is **61 == 61**, exactly the frozen cross-check's prediction.
`read_log()` reads the whole file and counts `^Time = ` and `^End` across both programs,
so on this family's launch pattern — one log for the decomposition and the solve —
**clause 5 fails a healthy run**.

**The frozen file has NOT been edited and I am not proposing that it be edited here**
(CLAUDE.md rule 6; the change is the supervisor's call, and any departure is a dated
amendment at the foot of the file with its own version bump). Two things must travel
with this defect:

1. **It is directionally safe.** Clause 5 can only turn a `PASS` into `NOT A RESULT`.
   The comparator stayed conservative; it did not manufacture a favourable verdict.
2. **It is not load-bearing for this verdict.** §5 gate 2 fails independently, on
   physics, in §4 below. Clause 5 could be repaired tomorrow and AR1 would still be
   `NOT A RESULT`.

### 3.2 G-COLD WAS NOT RUN AT LAUNCH AND THERE IS NO AT-LAUNCH ARTIFACT

§5 gate 4 registers G-COLD. `_a3gc_wrapper.sh` and `runScript_a3gc.py` contain **no call
to `a3gc_grade.py cold`** — checked by reading both. G-COLD is a *pre-launch* guard;
run post-hoc on a finished case it necessarily refuses, and it did (12 violations, one
per surviving time directory per rank). **That refusal says nothing about AR1** and is
recorded here only so nobody later reads it as a finding.

What *can* still be established, and was: the age guard (clause 6) shows **every one of
the 36 fields at `endTime` is newer than the case's own `0/T`**, so no pre-existing field
survived into the graded set. That is the substance G-COLD protects; the gap is that it
was established after the fact rather than refused before the spend.

---

## 4. §5 GATE 2 — ITERATIVE CONVERGENCE. THE LIMB THAT ACTUALLY DECIDES THIS ROW

Read through the frozen `gate_g_res()`, from the `<eq> initRes:` lines, **never from
`finalRes`** (N-D44).

G-TOL first, from the solver's own `DAOption` dump — not carried across from anywhere:
`primalMinResTol = 1e-08`, `primalMinResTolDiff = 100`, so the accept floor is the
**product** (N-D43) = **1e-06**, matching the registered value.

| equation | initRes at `endTime` | ≤ 1e-06 |
|---|---|---|
| `U0` | 1.080499e-07 | OK |
| `U1` | 6.981760e-08 | OK |
| `U2` | 8.981687e-08 | OK |
| `he` | 2.711194e-07 | OK |
| `p` | **3.714456e-07** | OK |
| `nuTilda` | **1.008860e-06** | **FAIL** |

**Five of six equations cleared. `nuTilda` missed by 0.89 %.** That is the whole of the
physics failure and it should be stated at its true size rather than dressed up in either
direction: this is not a diverged solve, and it is not a pass.

The registered §4 prediction for `p` was ≈ 3.74e-07 and the measured value is
**3.714456e-07** — the prediction landed, and it is REPORTED, NOT GATED.

---

## 5. §5 GATE 4 — G-MESH. EVERY FAILED CHECK NAMED, AS REGISTERED

`checkMesh -allGeometry -allTopology`, `meshgen/logCheckMesh.txt`: **`Failed 2 mesh
checks.`** The registration requires every failed check be named and registers no
threshold on them, so they are named and not graded:

1. **`***Error in face tets`** — 220 faces with low quality or negative volume
   decomposition tets (written to set `lowQualityTetFaces`).
2. **`***Cells with small determinant (< 0.001)`** — **64,028 cells** (set
   `underdeterminedCells`); minimum cell determinant 7.06e-08, average 0.234.

Both are the signature of a high-aspect-ratio boundary-layer mesh — 64 wall-normal
layers at `s0 = 1.0e-4` on a 12-chord march — and the anchor's mesh is built the same
way. Reported quantities that did pass: non-orthogonality max **61.16**, average 13.65;
max skewness **1.441 OK**; face flatness min 0.991; face volume ratio min 0.306.

**Decomposition, disclosed with every number above (registered requirement):** np = 4,
`scotch`, max 100,738 cells on a rank (0.90 % above the 99,840 average), 14,661
processor faces.

---

## 6. GEOMETRY CONFIRMED INDEPENDENTLY, BY A TOOL THAT NEVER READ THE REGISTRATION

ParaView read the reconstructed `constant/polyMesh` and reported, without being told what
to expect:

| quantity | ParaView | registered §2 | agree |
|---|---|---|---|
| wing patch faces | **6,240** | 6,240 | exact |
| volume cells | **399,360** | 399,360 | exact |

and, from a slice of the wing patch at η = 0.65, the **aerofoil contour**:
local chord **0.57292**, thickness **0.05600**, **t/c = 0.0977**. The ONERA M6 uses the
ONERA D section at t/c = 0.10 — agreement to **2.3 %** — and linear taper from the
0.8059 root to the 0.4526 tip predicts 0.5763 at this station against 0.57292 measured,
**0.6 %**. The geometry that ran is the M6.

---

## 7. COST — RULE 12, ESTIMATE VERSUS ACTUAL

Registered §7: **81.4 core-min**, on the *measured* basis of the anchor's
`ExecutionTime = 1221.21 s × np 4` (`logs_A3/run_model_run3.log`).
**CAP: 250 core-min, RECORDED AND REPORTED — NOT A STOP** (§7, struck cap-stop clause;
Sanaa's NO-CAP rulings).

| basis | figure | ratio to predicted |
|---|---|---|
| predicted | 81.400 core-min | 1.000× |
| actual, **same basis** (`ExecutionTime 3590.84 s × 4`) | **239.389 core-min** | **2.941×** |
| actual, **gross** (`ClockTime 7467 s × 4`) | **497.800 core-min** | **6.115×** |

**Cap crossing, reported not absorbed:** 250 core-min is **not** crossed on the
registered basis (239.389) and **is** crossed on the gross basis (497.800, 1.99×). The
run was not stopped and was never going to be.

**Attribution — and the misprediction is not laundered into contention, nor contention
into misprediction.** AR1 is a *bit-for-bit repeat of the anchor*: same 399,360-cell
mesh, same `np = 4`, same `endTime 6000`, `fvSolution`/`fvSchemes` byte-identical (§3).
The physical work predicted was therefore **correct** and the **misprediction component
is ≈ 1.0×**. The gap is contention, measured two independent ways:

* `ClockTime / ExecutionTime` = **7467 / 3590.84 = 2.079×** on AR1, against **1233 /
  1221.21 = 1.010×** on the anchor — the anchor's box was idle, AR1's carried a load of
  ≈ 39 on 16 cores beside two live solvers, exactly as §7 disclosed in advance.
* AR1's `ExecutionTime` is itself **2.941×** the anchor's *for identical work*. That is
  not extra work; it is MPI spin-wait inflating CPU time under oversubscription.

**THE CALIBRATION LESSON, and it generalises past this row:** `ExecutionTime × ranks` is
**not a contention-free cost basis on a loaded box**. The registration used it in good
faith and it under-reports true occupancy by the contention factor — here 2.08×. A
future pre-registration on this box should either price in `ClockTime` or state that its
`ExecutionTime` basis holds only at low load.

**Dollars: $0.426 at $0.0513/core-h on the gross basis — DERIVED, NOT MEASURED.** The box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 8. WHAT I COULD NOT VERIFY

* **The frozen comparator has no `grade` path that fits AR1.** `cmd_grade` requires
  `--l3 --l2 --l1` and gates on the triple's registered cell counts (99,840 / 798,720 /
  6,389,760); AR1 is 399,360 and §1 of its own registration says it "is **not** a grid
  triple". §6 accordingly says only the per-level limbs are read. Those limbs
  (`gate_g_complete`, `gate_g_tol`, `gate_g_res`) have **no CLI sub-command**, so they
  were driven by importing the frozen module and calling them unchanged —
  `cases/dafoam/ladder-a/A3/curriculum_A3GC/a3gc_ar1_drive_frozen_limbs.py`, which
  re-checks the md5 before importing and applies **no threshold of its own**.
* **The ±2 % band is applied from the registration, not from the comparator.**
  `a3gc_grade.py` **defines** `ANCHOR_CD`/`ANCHOR_CL` at lines 254–255 but **never reads
  them** — its band gates are the triple's GCI bands. The ±2 % is registered in §4 of
  the AR1 pre-registration, frozen at `3d416043b`, and is applied verbatim. Nothing was
  invented and nothing was widened, but the arithmetic is the driver's, not the frozen
  file's, and a reader is entitled to know which.
* **G-PLAT was not run** and is not claimed. It needs a level-to-level difference; AR1
  is one level and §5 does not register it for this row.
* **No gradient, no observed order, no GCI** — §1 of the registration claims none, and
  none is claimed here.

---

## 9. WHAT AR1 DID DELIVER, DESPITE THE VERDICT

The case exists, is complete to `endTime`, and **its fields are on disk at 2000, 4000 and
6000** on all four ranks — which was the stated purpose in §1: the validated anchor's raw
fields were overwritten on 2026-07-28 and a case that cannot be restarted is no use for an
adjoint. That purpose is served whatever the residual limb says. The row is
`NOT A RESULT`; the **restartable M6 primal is real**.
