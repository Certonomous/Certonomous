# VMFL011-R2 — Laminar Flow in a Triangular Cavity: `NOT A RESULT` (comparator refused)

## VERDICT: `NOT A RESULT` — the frozen comparator REFUSED (exit 2)

The frozen comparator refused on its planted-zero control (CLAUDE.md rule 3) and produced
no graded number: **no RMS value, no `u_min_norm` value, no triple class, no observed
order, no GCI.** The refusal IS the result and the frozen instrument is not edited
(rule 2). Graded by `ansys-lane-opus`, **2026-08-26**, for the supervisor's audit.
Manual p.41; reference the Jyotsna & Vanka 1995 numerical benchmark (code-to-code,
digitised from Figure .11.2); tier ceiling `GATE REACHED`, hard-coded and never reached.

**Re-registration of VMFL011 (register row #26).** Row #26 stands as `NOT A RESULT`,
unchanged and never overwritten; this is a NEW row (`ANSYS_VERIFICATION_CHARTER` §6).

**The supervisor's prior prediction was `GATE FAIL`. It is not what the instrument
returned, and it is not softened into one: the run never reached its band.**

### The refusal, exactly — verbatim from `GRADING.txt`

`python3 cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py --run-root <run root>
--out <run root>/GRADING_VMFL011_R2.json` → **exit 2**:

> REFUSING (exit 2): planted-zero control FAILED for u_min_norm.
>   planted -0.1234 into /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL011-R2/L1/postProcessing/bisector/20000/bisect_U.xy, reader moved by only 0.
>   A reader not shown able to see a non-zero cannot certify a zero (CLAUDE.md rule 3).

No `GRADING_VMFL011_R2.json` exists: the comparator exited before it wrote one. The
captured stdout/stderr and rc are at
`verification/runs/ansys_verification/VMFL011-R2/GRADING.txt`.

### THE FREEZE HELD — checked, not asserted

| file | on disk | at `9f9d6925` (freeze) | at HEAD |
|---|---|---|---|
| `cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py` | `45aa4613253d1d594b69b7f774e18cd7a312a20e` | same | same |
| `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md` | `a8c9b6f30e4383e23594b4203eea3bd28ded0a2a` | same | same |

`git hash-object` on the working-tree files equals `git rev-parse <commit>:<path>` at
**both** commits. The file that ran **is** the file that was frozen. `RUN_RC.L1/.L2/.L3`
and `LAUNCH_RECORD.txt` independently record the same two blobs, written by the launcher
before any core-minute was spent.

### THE PER-CHANNEL PLANT CHECK — one channel repaired, the other one newly exposed

| channel | reader | plant | move | threshold | result |
|---|---|---|---|---|---|
| `rms_vs_benchmark` | RMS over 46 abscissae (averaging) | all-row, **sized** `K·U_wall·base`, `K = 4` | — | `0.1·plant` | **the L-340 repair works** |
| `u_min_norm` | `min(u)` over 401 samples (point) | one row, fixed `−0.1234` | **exactly 0** | `1.234e-02` | **REFUSED (exit 2)** |

The L-340 sizing control, run on the **real attempt-1 L1 bytes** before any level was
read, fired green exactly as registered and is printed in `GRADING.txt`:
parent pair delta **3.677091e-07** < **1.234000e-04** → REFUSES (reproducing row #26's
recorded `3.67709e-07`); all-row plant at the parent magnitude delta **1.063654e-04** <
**1.234000e-04** → still REFUSES; the sized plant **0.322114** → delta **1.185698e-01** >
threshold **3.221137e-02** → PASSES, inside the derived bounds
**[8.052843e-02, 1.610569e-01]**. **The repair this R2 was registered to make did work.**

### Diagnosis — a SECOND, DISTINCT L-340 failure mode: plant LOCATION, not plant MAGNITUDE (a FINDING)

`_perturb` plants into the **first data row** of `bisect_U.xy`. On the real bisector that
row is the sample at **y = −4 m — the collapsed-hex apex**, where the no-slip solution is
`u ≡ 0` exactly. Adding `−0.1234` there gives `−0.1234`, which is **above** the profile
minimum **`min(u) = −0.528988913215` m/s** (401 samples, L1), so `min()` returns the same
number and the reader moves by **exactly 0**, not by a diluted amount.

**This is not the parent's defect.** Row #26's defect was *magnitude* — an averaging
reader diluting a single-point plant by ~1/√N. This one is *location*: a correctly
sized point plant landed on a row **outside the point reader's support**. Sizing the
plant to the reader does not help when the plant is not on the row the reader reads.

**Why the freeze did not catch it, stated precisely.** The pre-registration recorded
that *"`u_min_norm` — a point reader — passed the identical control"*. That is true of
the **selftest** profiles and was never true of the **real bisector bytes**, because both
comparators build their channels in the same dict order — `rms_vs_benchmark` first,
`u_min_norm` second (attempt-1 blob `e369496b…` lines 262–265; R2 blob `45aa4613…`
`controls()`) — and attempt 1 exited 2 inside the **first** entry. **The `u_min_norm`
plant had therefore never once run on a real VMFL011 bisector file.** Repairing the RMS
channel is precisely what carried execution past it for the first time. A control behind
another control's refusal is an untested control, and this R2 is the measurement that
says so.

**The repair is NOT made here.** Gates close at first compute (rule 2); a plant placed at
the reader's own argmin — or a per-channel plant *location* as well as magnitude — is a
**NEW registration and a NEW row**, never an edit. Candidate lesson flagged to the
supervisor (number to be assigned from the HEAD tail at its own commit, rule 11).

### STRICT COMPLETION (rule 4) — HOLDS AT ALL THREE LEVELS

Applied from `RUN_RC.<level>` plus the solver logs, independently of the comparator.

| level | cells | `rc` | `End` lines | last `Time` | `endTime` | fields at `endTime` | `ExecutionTime` count | age guard (`0/U` older) | wall s | core-min |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 800 | 0 | 1 | 20000 | 20000 | `U p phi` | 20000 | yes | 17 | 0.2833 |
| L2 | 3 200 | 0 | 1 | 20000 | 20000 | `U p phi` | 20000 | yes | 63 | 1.0500 |
| L3 | 12 800 | 0 | 1 | 20000 | 20000 | `U p phi` | 20000 | yes | 465 | 7.7500 |

`End` matched in `log.simpleFoam` **by exact name** (a `log*` glob matches `log.blockMesh`
first). Age guard measured from mtimes: L1 `0/U` 1787778687 < `20000/U` 1787778704;
L2 1787778704 < 1787778767; L3 1787778768 < 1787779233. `STATUS.VMFL011-R2` reads
`launcher_rc=0 end=2026-08-26T21:20:33Z`; `COST.txt` `overall_rc = 0`, `smoke_mode = no`.
**Nothing about this run is incomplete — the instrument refused, not the solver.**

### The physics beside the verdict — NOT MEASURED BY THIS ROW

**This row publishes no lab value.** The comparator refused inside L1's controls, before
any channel value, triple or GCI was computed, so there is no `rms_vs_benchmark`, no
`u_min_norm`, no triple class, no `p_obs` and no GCI to print. Attempt 1's ungraded
readings (row #26: L3 rms 0.0341 against a 0.030 band, `u_min` triple CONVERGING at
p = 1.60 sitting 8.9 % from the digitised benchmark) are **that row's numbers, not this
row's**, and are not restated here as if this run had produced them. The one thing this
run does establish about its own fields is that its L1 bisector reproduces attempt 1's:
`min(u)/U_wall = −0.264494`, matching row #26's L1 `u_min_norm` to six decimals.

### Artifacts on disk (and at HEAD with this commit)

`verification/runs/ansys_verification/VMFL011-R2/` — `GRADING.txt` (the refusal,
verbatim, with `rc = 2`), `RUN_RC.L1`, `RUN_RC.L2`, `RUN_RC.L3`, `STATUS.VMFL011-R2`,
`COST.txt`, `CONTENTION.txt`, `LAUNCH_RECORD.txt`, `launcher.queue.out`, and per level
`L{1,2,3}/log.blockMesh`, `log.checkMesh`,
`postProcessing/bisector/20000/bisect_U.xy`, `postProcessing/resid/0/solverInfo.dat`.

**Disclosed, not hidden:** each level's `log.simpleFoam` is **16.7–16.8 MB** (20 000
SIMPLE iterations at full print) and is **over the 5 MB per-file staging refusal**, so
the three solver logs stay **on disk only** and are not landed at HEAD. The `End` line,
the last `Time` and the `ExecutionTime` count read out of them are quoted above and are
each independently recorded in `RUN_RC.<level>` and `LAUNCH_RECORD.txt`, which are at
HEAD. Bulk fields (`0/`, `20000/`), `constant/polyMesh` and `processor*` stay on disk by
the same ruling.

### Provenance

- **Prereg sha:** `a8c9b6f30e4383e23594b4203eea3bd28ded0a2a`, frozen at commit
  **`9f9d69258dc7bb4ed981490cd90a85d7362ebed4`**, before any R2 solver started.
- **Comparator blob:** `45aa4613253d1d594b69b7f774e18cd7a312a20e` — equal on disk, at the
  freeze commit and at HEAD.
- **Launcher blob:** `b1d6a74a718e8e0dc8c5a76c0a07cf48006d2ab5`
  (`LAUNCH_RECORD.txt`); launched 2026-08-26T21:11:27Z, finished 21:20:33Z, RANKS = 1.
- **Contention at launch** (`CONTENTION.txt`, 21:11:27Z): load average 14.79 on 16 cores,
  with one `rhoCentralFoam`, one `icoFoam` and three `python3` live. Reported, not
  absorbed (`COMPUTE_BUDGET_CHARTER` §6).
- **Supersedes nothing:** register row #26 (VMFL011) is unchanged.

## COST (rule 12 calibration)

- **Measured actual: 9.0833 core-min** = (17 + 63 + 465) wall s × RANKS 1 ÷ 60, from
  `RUN_RC.L1/.L2/.L3` (`core_min` 0.2833 + 1.0500 + 7.7500) and `COST.txt`
  (`total_core_min = 9.0833`). Gross = cleaned: the longest level is 465 wall s, far
  below the 3600 s stall trigger.
- **Pre-registered estimate: 8.3 core-min** (`PREREGISTRATION.md` line 12 at
  `9f9d6925`), itself a *measurement* of attempt 1's byte-identical inputs (8.2167
  core-min). **Ratio actual/predicted = 1.094.**
- **Cap 50 core-min** (running total, byte-identical to attempt 1): **18.2 % used**,
  never approached, no overrun, nothing stopped.
- **Gap attribution:** contention, not misprediction. The box carried load average 14.79
  on 16 cores at launch against attempt 1's uncontended run; a 9.4 % wall inflation on an
  otherwise identical serial workload is that and nothing else. **Waste 0.000 core-min** —
  every level ran to `endTime` with `rc = 0`; a comparator refusal costs no solver time
  and is not a re-run.
- **$ derived: 9.0833 core-min ÷ 60 × $0.0513/core-h = $0.0078** — **DERIVED, NOT
  MEASURED**; the rate is REPORTED-BY-OWNER (c7a.4xlarge, Sanaa 2026-08-21/22) and the
  box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Ledger follow-up:** register row **#31** and calibration row **C-142** land with this
record. The register's credential-count headline is **not** struck: the verdict is
`NOT A RESULT`, so the `PASS` count does not move.
