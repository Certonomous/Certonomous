# PRE-REGISTRATION — VMFL011-R2: Laminar Flow in a Triangular Cavity

**Re-registration of VMFL011** (VM2026R1 p.41) under `ANSYS_VERIFICATION_CHARTER` §6: a
**NEW register row that cites row #26 and never overwrites it**. Row #26 stands as
`NOT A RESULT` (the frozen comparator refused on its own planted-zero control) whatever
this row returns.

Frozen by sha **before any R2 solver starts** (CLAUDE.md rule 2). Drafted by
`ansys-lane-opus`, **2026-08-26**. This file is a frozen file under rule 6.

**NOT YET RUN.** `verification/runs/ansys_verification/VMFL011-R2/` **does not exist** at
**2026-08-26T21:01:02Z** — `test -e` on that path returns false and the directory is absent
from `ls verification/runs/ansys_verification/`, whose sibling entries are all other cases
(`VMFL011` among them, the attempt-1 root, which is **not touched by this registration**).
No R2 solver has started, no level directory exists, no `RUN_RC.L1`, no `LAUNCH_RECORD.txt`.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL011-R2 -- Laminar flow in a triangular cavity, manual p.41
                     (title-page verified). Solver = simpleFoam (OpenFOAM v2606), steady
                     incompressible laminar SIMPLEC, Re = U_wall*base/nu = 2*2/0.01 = 400,
                     2-D. NOT YET RUN; verification/runs/ansys_verification/VMFL011-R2/
                     absent at 2026-08-26T21:01:02Z.
2. REFERENCE       : the normalised x-velocity profile u_x/U_wall along the vertical line
                     bisecting the base of the cavity (manual Figure .11.2). Source:
                     R. Jyotsna & S.P. Vanka, "Multigrid Calculation of Steady, Viscous
                     Flow in a Triangular Cavity", J. Comp. Phys. 122, 107-117 (1995) --
                     the manual's own cited Reference. The manual p.42 prints this ONLY as
                     a FIGURE with NO discrete target table, so the curve is carried as the
                     digitised CSV reference/vmfl011_benchmark_xnorm.csv, blob
                     9f11191b8c823eb32edd3f2b74bd29da855aab55 -- BYTE-IDENTICAL to attempt
                     1 and re-checked by the comparator at grade time (see CONTROLS 1).
                     Characteristic functional: u_min/U_wall = -0.318062 at y = -0.987 m.
3. REFERENCE KIND  : NUM, code-to-code, and doubly indirect (digitised from a figure).
                     Buys NEITHER V NOR P.
4. TIER CEILING    : GATE REACHED. BYTE-IDENTICAL to attempt 1 line 9. The comparator
                     hard-codes it as the in-band verdict; it cannot print PASS.
5. QUANTITIES      : gate = rms_vs_benchmark at the finest level (L3) -- the RMS, over the
                     46 benchmark abscissae, of (u_lab/U_wall - u_bench/U_wall), the lab
                     profile linearly interpolated from the 401 fixed bisector samples onto
                     those abscissae. Triple channel = u_min_norm, the most negative
                     normalised x-velocity on the bisector. BOTH BYTE-IDENTICAL to attempt 1.
6. BANDS (THE GATE): rms_vs_benchmark <= 0.030 at L3. BYTE-IDENTICAL to attempt 1 line 5,
                     carried character for character and NOT re-justified from any number:
                     the reference is a plot digitisation whose reading error is ~1-3 % of
                     full scale, and the Jyotsna-Vanka curve carries its own multigrid
                     discretisation. NEVER tightened or loosened from a run.
7. LADDER          : simpleFoam, laminar, SIMPLEC (consistent yes), nu = 0.01 m2/s
                     (rho = 1, mu = 0.01, manual p.41). Triangular cavity: base 2 m
                     (x -1 -> 1), movingWall at y = 0 with U = (2,0,0), apex at (0,-4,0),
                     sideWalls noSlip, front/back empty, apex a genuinely COLLAPSED-hex
                     block. endTime = 20000 SIMPLE iterations, no residualControl, so
                     "last time == endTime" is literally testable. EVERY CASE INPUT AND THE
                     REFERENCE ARE THE ATTEMPT-1 FILES REUSED BYTE FOR BYTE -- nine blob
                     shas below, CHECKED AT LAUNCH. Birth-certified per level from checkMesh.
8. DECOMPOSITION   : grid triple r = 2, base cells NB and height cells NH refined together:
   SEED              L1 (20, 40) = 800 cells; L2 (40, 80) = 3 200; L3 (80, 160) = 12 800.
                     NB EVEN at every level so the bisector x = 0 is a cell-face plane
                     identically placed under refinement. SERIAL, RANKS = 1, no domain
                     decomposition and no RNG anywhere in the case.
9. PRINCIPAL RISK  : THE PREDICTED OUTCOME OF THIS RUN IS `GATE FAIL`, and this
                     registration says so IN ADVANCE rather than discovering it -- see
                     PRIOR KNOWLEDGE below. The risk this registration carries is the
                     opposite of the usual one: that a reader mistakes a re-registration
                     for an attempt to convert a bad answer into a good one. It is not.
                     The band, the reference, the gate quantity, the ceiling, the mesh
                     family, the cap and endTime are carried BYTE-IDENTICAL precisely so
                     that nothing on the gate path could be re-tuned to the numbers attempt
                     1 already published. What this R2 buys is a GRADED VERDICT where
                     attempt 1 could produce NO NUMBER AT ALL.
10. EXPECTED ORDER : formal p_f = 2 for the schemes in use; attempt 1 measured p = 1.60 on
                     u_min. p_obs is NOT the headline (the gate is the RMS value). NO GCI is
                     quoted unless the triple is monotone CONVERGING and p >= P_MIN = 0.05.
11. WEDGE/GEOM BIAS: N/A (planar 2-D Cartesian, not an axisymmetric wedge; N-AV9 does not
                     apply). The collapsed-hex apex is a mesh property, disclosed, not a bias
                     term.
12. COST + CAP     : cap **50 core-min**, RUNNING TOTAL across the three levels, RANKS = 1 --
                     BYTE-IDENTICAL to attempt 1 line 7. An overrun STOPS the run and does
                     NOT get a new budget (rule 12); the launcher enforces it as
                     timeout_s = remaining_core_min * 60 / RANKS and refuses at zero.
                     ESTIMATE **8.3 core-min total**, and the basis is a MEASUREMENT of these
                     byte-identical inputs, not a guess: attempt 1 ran L1/L2/L3 to endTime
                     20000 for 0.25 + 0.9667 + 7.0 = **8.2167 core-min measured**, from each
                     level's own RUN_RC.txt and COST.txt under
                     verification/runs/ansys_verification/VMFL011/. 8.3 is that figure
                     rounded up; nothing in this R2 changes a mesh, a scheme or an iteration
                     count. Rate $0.0513/core-h (c7a.4xlarge) is REPORTED-BY-OWNER, NOT
                     MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER
                     sec.5); dollars are DERIVED ($0.0071 at 8.3 core-min). Under the
                     2026-08-21 blanket (<$25) and still costed per item. Estimate-vs-actual
                     calibrated at closure into docs/COST_CALIBRATION.md.
13. CONTROLS       : comparator cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py, blob
                     45aa4613253d1d594b69b7f774e18cd7a312a20e. L-340 PLANT-SIZING CONTROL
                     (the control that DRIVES this repair, run on the REAL attempt-1 bytes)
                     + planted-zero per channel (rule 3) + frozen-constant and
                     reference-blob control + strict completion (rule 4) with L-342 field
                     classes + Roache gating (rule 5) + observed-order floor P_MIN = 0.05
                     with its own two-way control + L-332 ast.Assert census + LAUNCHER
                     FREEZE CHECK (rule 2, non-droppable). NO `assert` carries any of them:
                     ast.Assert count = 0, measured by the file itself with the counter shown
                     able to count a planted one. `--selftest` 33/33 PASS, exit 0, output
                     BYTE-IDENTICAL under `python3` and `python3 -O`.
```

---

## WHAT IS BYTE-IDENTICAL — cited by blob sha, and CHECKED AT LAUNCH, not asserted in prose

`run_vmfl011_r2.sh` hashes every one of these against its **attempt-1 HEAD blob** before a
core-minute is spent and **ABORTs (exit 2)** on any mismatch. "The case and the reference did
not change" is therefore a check, not a claim. The comparator independently re-hashes the
reference CSV at grade time (`frozen_constants_control()`), computing git's blob sha itself so
the check survives in a tree with no repository.

| what | attempt-1 path | blob sha |
|---|---|---|
| mesh family (all 3 levels) | `VMFL011/case/system/blockMeshDict.template` | `eb2778961e49a91cdd78fd5f50187b5bca1b91b2` |
| controlDict (endTime 20000, the 401-point bisector, solverInfo) | `VMFL011/case/system/controlDict.template` | `7a6325cee0763f1e7e65b3a02b24203d793788a2` |
| schemes | `VMFL011/case/system/fvSchemes` | `5f997a3b9051bc7c4c284c065cebc946f66507ae` |
| solvers / SIMPLEC / no residualControl | `VMFL011/case/system/fvSolution` | `a857323458d76e615ec28e48717eb427b6e4f7c6` |
| initial/boundary U | `VMFL011/case/0/U` | `619d6ae48402f4faa7298c7de0b2e5f034972adf` |
| initial/boundary p | `VMFL011/case/0/p` | `e8c95d011203afd1a853862c3597f19841705cd8` |
| transportProperties (nu) | `VMFL011/case/constant/transportProperties` | `7b8c1fffc1dabfb83aac38419009c9d0a46e1583` |
| turbulenceProperties | `VMFL011/case/constant/turbulenceProperties` | `59cdc5d570fab13a72ce1454d3b5691a60e464c8` |
| **the reference itself** | `VMFL011/reference/vmfl011_benchmark_xnorm.csv` | `9f11191b8c823eb32edd3f2b74bd29da855aab55` |

And, carried unchanged **inside the comparator** from attempt-1 blob
`e369496bf2e28ccb7145756e1c2442eb11e8e3f7`: the gate quantity (`rms_vs_benchmark` at the
finest level), the band `BAND_RMS = 0.030`, the tier ceiling `GATE REACHED`, `U_WALL = 2.0`,
`ENDTIME = 20000`, `RESID_FLOOR = 1.0e-7`, `PLANT = 1.234e-3`, `LEVELS`, `FIELDS`, the triple
channel `u_min_norm`, the `roache()` classifier at `Fs = 1.25`, `r = 2`, and the verdict path.
**`frozen_constants_control()` re-checks all eleven and REFUSES (exit 2) on drift**, so
"byte-identical" is enforced at grade time and not only at freeze time.

---

## WHAT CHANGED — the plant sizing on ONE channel, and nothing else on the gate path

### The defect, exactly as row #26's refusal named it

`grade_vmfl011.py --run-root …VMFL011` → **exit 2**:

> REFUSING (exit 2): planted-zero control FAILED for rms_vs_benchmark. planted 0.001234
> into …/L1/postProcessing/bisector/20000/bisect_U.xy, reader moved by only 3.67709e-07.

**The reader was never blind.** It moved by 3.68e-07 — exactly the correct RMS sensitivity to
a one-row perturbation. **L-340**: a `delta > 0.1·plant` threshold fits a **point** reader; an
**averaging** reader over N points dilutes a single-point plant, and the control refuses a
working reader. `u_min_norm` — a point reader — passed the identical control.

### The repair, and why it is a theorem rather than a tuning

Let `e_i = u_i/U_WALL − b_i` over the 46 benchmark abscissae, `base = sqrt(mean(e²))`,
`⟨e⟩ = mean(e)`. A uniform raw plant `P` applied to **every** data row shifts every `e_i` by
exactly `d = P/U_WALL` — exactly, because linear interpolation of a uniformly shifted sampled
function is uniformly shifted and the comparator's end-clamping preserves that. Hence

```
new² = base² + 2·d·⟨e⟩ + d² ,      and      |⟨e⟩| ≤ base   (Cauchy–Schwarz).
```

With `d = K·base`, the worst case `⟨e⟩ = −base` gives `new = (K−1)·base`, so

```
(K − 2)·base  ≤  delta  ≤  K·base ,        threshold = 0.1·P = 0.1·K·U_WALL·base .
```

The control is **guaranteed** to pass for any working reader iff `K·(1 − 0.1·U_WALL) > 2`,
i.e. `K > 2.5` at `U_WALL = 2`. **`RMS_PLANT_K = 4.0` is registered**, worst-case margin
`(K−2)/(0.1·K·U_WALL) = 2.5×`. **No measured value entered that choice** — it is the smallest
round `K` clearing the derived bound with a factor-2 margin. `RMS_PLANT_FLOOR = 1.0e-6` covers
a run that matched the benchmark exactly; the same bounds hold there.

**THE THRESHOLD RULE `delta > 0.1·|plant|` IS CARRIED CHARACTER FOR CHARACTER.** L-340 is
answered by sizing the plant at the call site, **never** by loosening the test — a control
repaired by weakening its own threshold would be no control at all.

### The change, line by line

| | attempt 1 (blob `e369496b…`) | R2 (blob `45aa4613…`) |
|---|---|---|
| `rms_vs_benchmark` plant shape | `_perturb` — **one** data row | `_perturb_all` — **every** data row |
| `rms_vs_benchmark` plant magnitude | fixed `PLANT = 1.234e-3` | `rms_plant_for(base) = K·U_WALL·max(base, floor)`, `K = 4` |
| `u_min_norm` (a POINT reader) | `_perturb`, `−|PLANT|·100`, `0.1·plant` | **UNCHANGED, byte-identical** |
| threshold rule | `delta > 0.1·|plant|` | **UNCHANGED, byte-identical** |
| attempt-1 pair | the grading path | **preserved verbatim** as `_perturb` + `PLANT`, used OFF the grading path so the control can show it refusing the same bytes |
| observed-order floor | none | `P_MIN = 0.05` → `DEGENERATE` → `NOT A RESULT`, no GCI |
| completion field classes | one class; a missing `RUN_RC` voided the level | **L-342**: physics-critical clauses gate; an **absent** infrastructure record prints `NOT MEASURED`, is disclosed in the grading JSON, and the grade **proceeds** |
| `RUN_RC` location | `<level>/RUN_RC.txt` | `<run root>/RUN_RC.<level>`, written by the VMFL064-R2-shaped launcher |
| absent gate artifact | `RuntimeError` (a traceback) | `sys.exit(2)` with a named refusal |

**Two of these changes are not the reader repair and are disclosed as such, with their
direction stated:**

1. **`P_MIN = 0.05`** (`docs/ansys_verification/FINDING_p_floor.md` §4) is **one-directional**:
   rule 5 fixes that a triple gate can only turn a result **INTO** `NOT A RESULT`, never the
   reverse, and `DEGENERATE` is a non-`CONVERGING` state like any other. It **cannot** convert
   attempt 1's outcome into a better one. On attempt 1's own measured `p = 1.60` it does not
   bite.
2. **L-342 field classes** widen in the other direction — an absent `RUN_RC` no longer voids a
   level — and that is **Sanaa's own rule**, verbatim: *"a bookkeeping failure invalidates the
   bookkeeping, never the physics artifacts — and graders must separate physics-critical fields
   from infrastructure fields so a dead poller can never void a run again."* **Every
   physics-critical conjunct of rule 4 is unchanged and still gates**, and a `RUN_RC` that is
   **present** and reports `rc != 0` still **REFUSES**: absence is a disclosure, a bad value is
   not a licence. Both directions are driven in `--selftest`.

**Why this is a re-registration and not an amendment.** Attempt 1's first compute has happened;
rule 2 closes its gates permanently and its comparator is never edited. This is a **new case
directory, a new run root, a new comparator blob and a new register row**, exactly as
`ANSYS_VERIFICATION_CHARTER` §6 requires.

**One inherited prose discrepancy, corrected here and changing no number.** Attempt 1's
`PREREGISTRATION.md` §2 and §5 say the benchmark carries **55** rows. The CSV carries **46**
(blob `9f11191b…`, unchanged since before attempt 1's freeze), and the comparator has always
taken `N` from the file itself, never from that prose. So no gate, band or number ever depended
on the "55". This registration states **46**, and `frozen_constants_control()` **REFUSES** if
the reference does not present exactly 46 abscissae.

---

## PRIOR KNOWLEDGE — DISCLOSED IN FULL, BEFORE THE FREEZE

**This registration is NOT blind, and pretending otherwise would be the dishonest move.**
Attempt 1's `RESULTS.md` (blob `23f33ad327c653569b2966c8968d02e1a86dd45b`) already publishes,
beside its `NOT A RESULT`, what the ungraded channels read on the attempt-1 fields:

| level | `rms_vs_benchmark` (band 0.030) | `u_min_norm` (bench −0.318062) |
|---|---|---|
| L1 (800 c) | 0.0403 | −0.264494 |
| L2 (3 200 c) | 0.0348 | −0.319438 |
| L3 (12 800 c) | **0.0341** | −0.337560 |

Four consequences, stated so a reader can price them:

1. **THE PREDICTED VERDICT OF THIS R2 IS `GATE FAIL`.** 0.0341 > 0.030 at the finest level.
   A correctly predicted failure is still a failure, and this registration is made **knowing**
   that and saying so on line 9. **A re-registration whose predicted outcome is a failure
   cannot be an attempt to fit an answer** — it is the purchase of a graded verdict where the
   instrument previously produced none.
2. **The band could not have been chosen to fit, because the band was not chosen.**
   `BAND_RMS = 0.030` is byte-identical to the attempt-1 freeze, made before any VMFL011 number
   existed. So are the reference, the ceiling, the mesh family, the cap, `endTime` and the gate
   quantity. **There is no new gate-path constant in this file.** The only new constants
   (`RMS_PLANT_K`, `RMS_PLANT_FLOOR`) live inside the rule-3 control and can reach no verdict.
3. **The u_min triple is expected `CONVERGING`** (attempt 1: steps −0.05494, −0.01812, ratio
   0.330, `p = 1.60`, Richardson −0.3465), so the verdict is expected to be decided at the
   band rather than at the triple. **The converged lab minimum sits 8.9 % from the digitised
   benchmark −0.318, larger than the 1–3 % digitisation noise the band assumed.** That gap is
   **physics and/or digitisation, not an instrument defect**, it is **not** what row #26's
   refusal named, and **this R2 changes nothing about it** — deliberately. Whether it is the
   digitisation, the collapsed-hex apex, or an under-resolved corner vortex (`p = 1.60` below
   the formal 2.0) is **OPEN** and is not resolved by this registration.
4. **It is still a re-run, not a re-read.** The R2 grades **fresh L1/L2/L3 solves in a new run
   root**; the attempt-1 fields are cited here and are read by the comparator **only** inside
   `rms_sizing_control()`, off the grading path, as the bytes the repair is driven against. A
   fresh solve on a contended box may differ, and the falsification clause below is live.

## FALSIFICATION — named before the run

- **`GATE FAIL` is the PREDICTED outcome** and is recorded honestly if it lands, never softened.
- **`GATE REACHED` is a real possible outcome.** A fresh solve could land the L3 RMS below
  0.030 (attempt 1's 0.0341 is 14 % above the band; nothing in this R2 moves it, but the run
  is fresh). It would be a `GATE REACHED`, never a `PASS` — the ceiling forbids more.
- **`NOT A RESULT` is a real possible outcome.** The `u_min_norm` triple must be monotone
  `CONVERGING`; `EXACT`, `STAGNANT`, `OSCILLATORY`, `DIVERGENT` or `DEGENERATE` (`p < P_MIN`)
  forces `NOT A RESULT` whatever the RMS. So does any level failing iterative convergence
  against the frozen `1e-7` floor, or any physics-critical completion clause.
- **A REFUSAL is a real possible outcome, and this R2 does not make one less likely by
  weakening anything.** A blind reader on either channel, a drifted frozen constant, a
  reference blob that is not `9f11191b…`, an `assert` in the comparator, a `RUN_RC` present
  and reporting `rc != 0`, or an absent gate artifact each REFUSE (exit 2). **The R2 control
  is STRICTER than attempt 1's on every path except the one L-340 named.**
- **The repair can be shown wrong in a way this registration would catch:** if the parent's
  single-row pair ever *stopped* refusing those bytes, probe (1) refuses, because then nothing
  drives this re-registration.

## CONTROLS — all non-droppable, all driven, NONE on an `assert`

`python3 -O` deletes every `assert` (L-332), so a refusal written as one is a refusal *offer*
the runner accepts or declines by an interpreter flag. **`ast.Assert` count in
`grade_vmfl011_r2.py` = 0**, measured by the file itself with `ast.walk` — and **the counter is
shown able to count a planted assert**, so its zero is a reading and not a blind spot.
`grep -cE '^\s*assert '` is also **0**. Every refusal is `sys.exit(2)`.

1. **FROZEN-CONSTANT AND REFERENCE-BLOB CONTROL.** Eleven registered constants plus the
   reference CSV's git blob sha, recomputed in-process (no git subprocess), plus its row count.
   **REFUSES on any drift.** This makes "carried byte-identical" a grade-time check.
2. **THE L-340 PLANT-SIZING CONTROL — the control that DRIVES this repair.** It runs in
   `--selftest` **and in `main()` before any level is read**, on the **REAL bytes** of the
   refusal: `verification/runs/ansys_verification/VMFL011/L1/postProcessing/bisector/20000/`
   `bisect_U.xy`, 401 points, embedded verbatim in the comparator and re-checked against its
   registered RMS. Four probes, each refusing (exit 2) on its own failing path:
   - **(1) drives the fix.** The **attempt-1 pair** (one-row plant, fixed `PLANT`) must
     **still REFUSE** on those bytes, and must reproduce the delta quoted in row #26's refusal
     to 1e-11. If it did not refuse, nothing would justify this file existing.
   - **(2) the SIZING is load-bearing, not the shape.** An **all-row plant at the parent's
     magnitude** must **also still REFUSE**. This is the measured statement that L-340's first
     suggested remedy — "plant into all points" — is **not sufficient on its own here**.
   - **(3) the registered pair passes**, and its move must fall inside the **derived** bounds
     `[(K−2)·base, K·base]`. A reader that responded differently from the theorem is refused.
   - **(4) adversarial.** A profile constructed so that a **fixed** all-row plant moves the RMS
     by **exactly zero** (`⟨e⟩ = −d/2`) must defeat the fixed plant and must **not** defeat the
     sized one.
3. **Planted-zero per channel (rule 3).** `rms_vs_benchmark` with the sized all-row plant;
   `u_min_norm` with the attempt-1 point plant, byte-identical. The only way out of
   `planted_zero()` is to have seen the plant. A blind reader is driven in `--selftest` and
   REFUSES (exit 2).
4. **Strict completion (rule 4) with L-342 FIELD CLASSES.**
   - **PHYSICS-CRITICAL (these gate):** an `\nEnd` line in `log.simpleFoam` **by exact name**
     (a `log*` glob matches `log.blockMesh` first — driven behaviourally); last time ==
     `endTime` (20000); `U` and `p` present at `endTime`; `ExecutionTime` count == `endTime`;
     **age guard** — every field at `endTime` strictly newer than the case's own `0/`.
   - **INFRASTRUCTURE:** `RUN_RC.<level>`, `COST.txt`. **Absent or unparseable → `rc` reported
     `NOT MEASURED`, disclosed in the printed output and in the grading JSON, and the grade
     PROCEEDS. Present and `rc != 0` → REFUSE.** Both directions driven.
5. **Roache triple gating (rule 5), `Fs = 1.25`, `r = 2`** on `u_min_norm`: any
   non-`CONVERGING` state → `NOT A RESULT` whatever the value; no GCI unless monotone.
6. **Observed-order floor `P_MIN = 0.05`, driven both ways**: a genuinely computed `p = 0.01`
   → `DEGENERATE`, no GCI; `p = 0.5` → `CONVERGING` **with** a GCI, so the floor cannot swallow
   a real result.
7. **LAUNCHER FREEZE CHECK (rule 2, non-droppable).** `run_vmfl011_r2.sh` hashes **this file**
   and **the comparator** against their `HEAD` blobs, gating explicitly with
   `|| { echo ABORT…; exit 2; }`, records the resolved shas in `LAUNCH_RECORD.txt`, and
   additionally hashes all **nine** case inputs and the reference against their attempt-1
   blobs. It runs `--selftest` under **both** `python3` and `python3 -O` and ABORTs unless the
   two outputs are **byte-identical** and green, and unless each of five named control lines is
   present.

**MEASURED at this freeze (numbers, not recollections):**

- `--selftest` → **33 checks, 33 PASS, 0 FAIL, exit 0**; `cmp` reports the `python3` and
  `python3 -O` outputs **byte-identical**, and identical run to run.
- `ast.Assert` = **0**; `grep -cE '^\s*assert '` = **0**.
- **The repair, on the real attempt-1 L1 bytes** (`base = 0.0402642150`):
  parent pair delta **3.677091e-07** < threshold **1.234000e-04** → **REFUSES** (reproducing
  row #26's recorded `3.67709e-07`); all-row plant at the parent magnitude delta
  **1.063654e-04** < **1.234000e-04** → **STILL REFUSES**; the sized plant **0.322114** →
  delta **1.185698e-01** > threshold **3.221137e-02** → **PASSES**, inside the derived bounds
  **[8.052843e-02, 1.610569e-01]**.
- **Four mutants, each under BOTH interpreters, every one rc = 2 with no green line:**
  sizing reverted to the parent constant → refuses at probe (3); threshold multiplier zeroed →
  refuses at probe (1) (the parent pair stops refusing, so nothing drives the change); the RMS
  reader blinded → refuses at the embedded-bytes identity check; a planted `assert` → refuses
  at the L-332 census **even under `-O`**, because the census parses the source, not the
  compiled code.
- Launcher: `bash -n` clean; **no `set -u` statement** (one mention, in the comment explaining
  its absence); **no `[0-9]*` glob** (two mentions, both in comments citing L-339); the argv
  usage guard drives — `bash run_vmfl011_r2.sh` with no argument exits **rc 1** with
  `usage: run_vmfl011_r2.sh <run_root> [levels...]`, and with a run root it reaches and fires
  the freeze check. **Every queue entry for this launcher MUST pass `<run_root>` as argv[1]**
  (VMFL064R2-ENTRY-DEF-1, whose entry omitted it and whose launcher refused at zero compute).

**REGISTERED IN ADVANCE, so it is not a departure:** after this freeze a **launcher smoke** is
run — `VMFL_SMOKE=1`, **L1 only**, `endTime` shortened to **20**, in a **scratchpad** root that
the launcher itself refuses to leave. It exercises the launcher end to end, **grades nothing**,
writes nothing under `verification/runs/`, and **no gate, band, cap, ceiling or label depends
on it**. Its cost is seconds and is reported with the run's calibration.

## GRADING PATH (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py`, blob
`45aa4613253d1d594b69b7f774e18cd7a312a20e`, reading
`verification/runs/ansys_verification/VMFL011-R2/{L1,L2,L3}` and
`verification/runs/ansys_verification/VMFL011-R2/RUN_RC.{L1,L2,L3}`.
Launcher: `cases/ansys_verification/VMFL011-R2/run_vmfl011_r2.sh`, blob
`b1d6a74a718e8e0dc8c5a76c0a07cf48006d2ab5`, modelled line for line on
`cases/ansys_verification/VMFL064-R2/run_vmfl064_r2.sh`.
Grading output: `verification/runs/ansys_verification/VMFL011-R2/GRADING_VMFL011_R2.json`.

## PROVENANCE

- **Attempt 1, cited and not overwritten:**
  `cases/ansys_verification/VMFL011/PREREGISTRATION.md` (blob
  `4bd8c4285e379e93e1ad4e6c2b9967604d042523`), `RESULTS.md` (blob
  `23f33ad327c653569b2966c8968d02e1a86dd45b`), comparator blob
  `e369496bf2e28ccb7145756e1c2442eb11e8e3f7`, launcher blob
  `17f8bd4b452dccbc3291700e6f9633eb4e6bf636` — register row #26, `NOT A RESULT`, and the
  refusal quoted verbatim in that `RESULTS.md`. Measured cost 8.2167 core-min.
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p.41–43, title-page verified against the PDF beside it (rule 15). Density 1 kg/m3, viscosity
  0.01 kg/m-s, cavity height 4 m, base width 2 m, moving (base) wall 2 m/s, other walls
  stationary — read from that page and reproduced above.
- **Standing rules and lessons applied:** CLAUDE.md rules 1–6, 10, 12, 13;
  `docs/ansys_verification/FINDING_p_floor.md` §4 (`P_MIN`); **L-332** (no guard on an
  `assert`); **L-336** (detachment by SID, not ppid); **L-339** (no `[0-9]*` glob);
  **L-340** (the plant sized to the reader — the defect this file repairs);
  **L-342** (physics-critical vs infrastructure field classes).
- **Compute authority:** Sanaa's permission boarded at commit `bc0e687e`. RANKS = 1, cap 50
  core-min, unchanged from attempt 1.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL, a NOT A RESULT or a refusal is recorded honestly and never softened.*
