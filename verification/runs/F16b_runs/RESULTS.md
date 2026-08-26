# F16b-SL2 — Stokes' second problem, ±x CYCLIC (`icoFoam`) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F16b_SL2_PREREGISTRATION.md`
frozen at **`cadb4887b505af082c63e977fd4fdf73e9878b46`**, inheriting F16's gates,
bands and ladder verbatim (`F16_SL2_PREREGISTRATION.md` at `2aea29d9`). This
is the successor to F16, whose ±x `empty` patches left Ux unsolved (identically
zero fields, closed NOT A RESULT on physics, row C-123). Graded 2026-08-26 by a
cfd lab-lane at **zero new compute**.

Grader run **exactly as the launcher printed it**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F16b_stokes_second_problem/grade_f16b.py --prereg-commit=cadb4887b505af082c63e977fd4fdf73e9878b46`
— **rc 0**. Stdout: `verification/runs/F16b_runs/F16b_GRADED.out`. Record:
`verification/runs/F16b_runs/F16b_GRADED.json` (the path prereg §10 names).
Gated by `scripts/roache_triple.py::grade_ladder`, one call node (0 `assert`
nodes across 2 files).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band (inherited verbatim) | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F16-1 `E2_velocity_profile_L2` | **1.319909e−04** | [4.101177e−05, 3.691059e−04] | **CONVERGING** (dim 1, r = 2.000, monotone) | **1.8252** | 137.1876 % = 1.810751e−04 absolute | **PASS** |
| G-F16-2 `u_at_delta` (ωt = 0 mod 2π) | **−0.309394169** | [−0.310278390, −0.308841361], exact −0.309559876 | **CONVERGING** (dim 1, r = 2.000, monotone) | **1.9930** | 0.0673 % = 2.082305e−04 absolute | **PASS** |

Level values (from `<level>/postProcessing/profile/40/profile_U.xy`, the
4-column `axis y` layout the grader pins, read by the frozen reader):

| level | cells | Δy = Δt | E2 | u(δ)/U0 |
|---|---|---|---|---|
| coarse | 56 | 2.5e−03 | 1.806234e−03 | −0.306921316 |
| medium | 112 | 1.25e−03 | 5.004684e−04 | −0.308897662 |
| fine | 224 | 6.25e−04 | 1.319909e−04 | −0.309394169 |

**Registered prediction (prereg §5) — MET:** observed order p ≈ 2 (1.83 on the
L2 profile error, 1.99 at the point value); the design order is recovered on
the smooth transcendental solution. E2_fine measured / analytic prediction =
1.319909e−04 / 1.230353e−04 = **1.07**. The F15/F16 pairing claim (p ≈ 1 vs
p ≈ 2) waits on F15's grade. The 137 % relative GCI on G-F16-1 is the relative
form on a quantity extrapolating to −1.29e−05 (near zero); the absolute GCI
1.81e−04 carries the meaning. Both printed as the grader printed them.

**Rule 5 limbs, in order.** (1) Iterative convergence: census of every step's
final p residual against 1e−09 — **0 above tolerance at every level**
(32,000 / 64,000 / 128,000 readings; worst 9.99953e−10 / 9.99983e−10 /
9.99987e−10). Class C on the phase-locked series, 40 samples, 12-period
window: PLATEAUED at every level — relative drift over the window ≤ 7.32e−08
(fine, E2) and ≤ 1.55e−10 (fine, u(δ)). (2) Triple CONVERGING on both rows.
(3) Inside band → PASS.

**Planted-zero control (rule 3), into the real artefact through the real
4-column reader** (`fine/postProcessing/profile/40/profile_U.xy`): E2 — planted
1.085209e−03, read back 1.085209e−03 (identical to the printed digits),
`e2_from_xy`; u(δ) — planted 1.234e−03, read back 1.2340000000000129e−03,
`u_at_delta_from_xy`. **Both PASS.** All 9 registered controls passed
(symbolic substitution into the full NS with residuals identically 0 and the
1.37k exponent plant non-zero; truncation floor dominated by discretisation;
constant-ratio refinement; four Class C limbs each shown able to refuse; single
`grade_ladder` call site both ways; solver tolerance agrees with `fvSolution`;
the R2 real-log completion reader driven both ways; the real 4-column
`read_xy_u` driven both ways).

**F16's Finding B is closed on the artefacts:** `Solving for Ux` appears at
every step — 16,000 / 32,000 / 64,000 lines (F16: 0 / 0 / 0).

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path the pre-registration names and every path the freeze commit
carries, checked `git hash-object <disk>` against `git rev-parse cadb4887:<path>`
before grading — **11 of 11 SAME**:

| path | blob |
|---|---|
| `cases/F16b_stokes_second_problem/grade_f16b.py` | `a7d14ed9` (as prereg §0 states) |
| `run_f16b.sh` | `89bd60d9` (as stated) |
| `exact_stokes.py` | `78bd3342` (as stated; byte-identical to F16's) |
| `case/0/U.template`, `case/0/p` | `6a5c0b88`, `57a10277` (as stated) |
| `case/system/blockMeshDict.template`, `controlDict.template`, `fvSchemes`, `fvSolution` | `4bcf8ed5` (as stated), `0960654b`, `f29359b6`, `0dcad02d` |
| `case/constant/transportProperties` | `522d6fc6` |
| `verification/campaign/F16b_SL2_PREREGISTRATION.md` | `518ac4f7` |

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines == endTime/Δt | last Time == endTime | fields at `40/` | age guard (`0/U` → `40/U`, `40/p`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 16000 == 16000 | 40 == 40 | U p | 16:42:04.968 → 16:42:11.071 Z | 7 s / 6.07 s |
| medium | 0 | 1 | 32000 == 32000 | 40 == 40 | U p | 16:42:11.411 → 16:42:26.582 Z | 15 s / 15.12 s |
| fine | 0 | 1 | 64000 == 64000 | 40 == 40 | U p | 16:42:26.940 → 16:43:19.156 / .157 Z | 53 s / 50.87 s |

All clauses hold at every level; the grader's `completion()` agrees
(`done: True`, `n_times` 16000/32000/64000, `latest` 40.0). Serial, 1 rank,
`decomposePar` never invoked (launcher output, decomposition seed `none`).

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8) | **~0.5 core-min** = F16's measured 0.4167 × ~1.2; registered cap **5** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 7 s → 0.1167; medium 15 s → 0.2500; fine 53 s → 0.8833; **1.2500 core-min gross** |
| actual cleaned | **1.2500** — cleaned == gross (longest level 53 wall s; nothing matches the 3600-s stall rule) |
| waste, named separately | **0.000 core-min** (the §9 smoke arm, < 0.017 core-min, was named in the prereg and is charged nowhere else) |
| quantisation | ClockTime is integer-second: ± 0.0083 core-min per level |
| share of cap | 25.0 % |
| dollars | 1.25 / 60 × $0.0513 = **$0.00107 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **2.50** |

**Gap attribution — misprediction of the basis, not contention and not
waste.** The basis was F16's measured 3 / 7 / 15 s — but F16 was the
degenerate run: identically-zero fields, so **every one of its 128,000 pressure
solves at fine took 0 iterations** (`No Iterations 0` × 128,000) and no Ux
equation was solved. F16b's fine level does the work F16 never did: 128,000 p
solves at **19–21 iterations each** (76,490 at 21; 51,431 at 20; 79 at 19) plus
64,000 Ux solves. The ×1.2 uplift priced "one more component", not the linear-
solver work a non-trivial field costs. Contention: **negligible** —
ExecutionTime 50.87 s against ClockTime 53 s at fine (4 %), 6.07 vs 7 s at
coarse, launcher probe 2.21–2.41 free cores of 16. **Carry forward:** a cost
basis measured on a run later found NOT A RESULT on physics is not a basis; for
this family, serial `icoFoam` on this box ≈ 3.7 µs per cell-step at 224 cells
(53 s / (224 × 64,000)).

Calibration row: landed in `docs/COST_CALIBRATION.md` in the same commit as
this record (id derived at commit time from the ledger's maximum existing id).

## 5. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- The grader printed **`BOOKKEEPING DEFECT: STATUS.F16b absent (infrastructure
  field; grade proceeds)`**: it looks for `STATUS.F16b` under the run root,
  while the queue runner wrote `cases/F16b_stokes_second_problem/STATUS.F16b_SL2`
  reading `launcher_rc=0 end=2026-08-26T16:43:19Z
  note=exit-status-of-the-launch-argv-NOT-the-solver-rc` — the launch argv's
  exit status, **not the solver rc**. The solver rc per level is `RC.txt` = 0
  (§3). Because of the defect the tally printed no cost line; the cost in §4
  is this lane's reading of the three logs' `ClockTime` lines, and it agrees
  with the JSON's `infrastructure_census` (7 / 15 / 53 s, 1.25 core-min, cap
  5.0) and with the launcher's running tally.
- **Textual defect in the frozen pre-registration, disclosed, not edited:**
  §8 reads "Derived dollars: /bin/bash.0004 predicted, /bin/bash.0043 at the
  cap" and "(/bin/bash.0513/core-h …)" — an unquoted `$0` expanded to the
  writing shell's name. The intended figures reconstruct from the stated
  core-minutes: 0.5 × $0.0513 / 60 = $0.0004 and 5 × $0.0513 / 60 = $0.0043 at
  the rate $0.0513/core-h. No number in core-minutes, no band, cap or label is
  affected. Whether a dated addendum is wanted is the supervisor's call.
- The frozen grader was run with plain `python3`, never `-O` (the launcher's
  instrument line confirms `grade_f16b exits 2 under -O`).

## 6. NOT REGISTERED, NOT SENT

No change to any F16 band or label; no re-grade of F16 (its row stands NOT A
RESULT on physics). **Nothing is sent, filed, uploaded or submitted** (rule
7). Field data stays on disk under `verification/runs/F16b_runs/` and is not
committed.
