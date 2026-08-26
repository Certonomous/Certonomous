# F17-KV40 — Kovasznay flow, Re = 40 (steady exact Navier–Stokes, `simpleFoam`) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F17_KV40_PREREGISTRATION.md`
frozen at **`4ad083fbd76d9e75bdf33963e5bfba787291e51d`** (v1.1; Amendment 1 is
pre-first-compute and moved no gate, band, cap or label). **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3, labelled at registration): counts toward no
challenge column. Graded 2026-08-26 by a cfd lab-lane at **zero new compute**.

Grader run **exactly as the launcher printed it**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F17_kovasznay/grade_f17.py --prereg-commit=4ad083fbd76d9e75bdf33963e5bfba787291e51d`
— **rc 0**. Stdout: `verification/runs/F17_runs/F17_GRADED.out`. Record:
`verification/runs/F17_runs/F17_GRADED.json` (the grader's default output path).
Gated by `scripts/roache_triple.py::grade_ladder`, one call node (AST census in
the JSON: 0 `assert` nodes across 4 files, planted assert seen).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F17-1 `E2_velocity_L2` | **1.423137e−04** | [3.689829e−05, 3.320846e−04] | **CONVERGING** (dim 2, r = 2.000, monotone) | **2.0990** | 117.4438 % = 1.671387e−04 absolute | **PASS** |
| G-F17-2 `u_at_probe` (0.5, 0) | **0.382441158** | [0.382201575, 0.382544064], exact 0.382372820 | **CONVERGING** (dim 2, r = 2.000, monotone) | **2.0699** | 0.0236 % = 9.008537e−05 absolute | **PASS** |

Level values (from `<level>/4000/U`, read by the frozen reader):

| level | cells | h | E2 | u(probe)/U0 |
|---|---|---|---|---|
| coarse | 1,536 | 1/32 | 2.462527e−03 | 0.383639464 |
| medium | 6,144 | 1/64 | 5.814174e−04 | 0.382671668 |
| fine | 24,576 | 1/128 | 1.423137e−04 | 0.382441158 |

**Registered prediction (prereg §5) — MET:** both triples CONVERGING with
p ≈ 2 (model 2.01/2.00; observed 2.099 and 2.070), fine values inside both
bands. Against the discretisation model: E2_fine measured / predicted =
1.423137e−04 / 1.106949e−04 = **1.29** (inside the factor-3 window); u(probe)
error measured **+6.834e−05** against the model's **−5.708e−05** — magnitude
ratio 1.20, **sign opposite to the model's** (the band is symmetric, so the
verdict is unaffected; recorded as a miss of the model's sign, not of the gate).
The 117 % relative GCI on G-F17-1 is the relative form on a quantity whose
Richardson extrapolant is 8.60e−06 (near zero); the absolute GCI 1.67e−04 is the
figure that carries meaning here. Both printed as the grader printed them.

**Rule 5 limbs, in order.** (1) Iterative convergence: census of the solver's
own initial residuals over every iteration of the 1,200-iteration Class C
window — **0 of 1,200 above tolerance for Ux, Uy and p at every level**
(worst, fine: Ux 1.47e−11, Uy 8.69e−11, p 1.13e−08 against 1e−6 / 1e−6 / 1e−5).
Class C on the graded quantity, 40 checkpoints, 12-sample window: PLATEAUED at
every level — relative drift over the window ≤ 1.82e−06 (fine, E2) and
≤ 3.11e−09 (fine, u probe); two-half variance ratio 0.99999–1.00000 on every
row. (2) Triple state CONVERGING on both rows. (3) Inside band → PASS.

**Planted-zero control (rule 3), into the real artefact through the real
reader** (`fine/4000/U`): E2 — planted 1.102963e−03, read back
1.102963e−03 (delta 1.1e−14 class), `e2_from_files`; u(probe) — planted
1.234e−03, read back 1.2340000000000684e−03, `u_probe_from_files`. **Both
PASS.** All 10 registered controls passed (symbolic substitution into steady
NS with residuals identically 0 and the λ×1.1 plant non-zero; constant-ratio
refinement both directions; face-averaged boundary data balancing to round-off;
model solved and second order; four Class C limbs each shown able to refuse;
single `grade_ladder` call site both ways; solver dictionaries agree with the
registration; reader parses real solver-written `U` on this box; L-342 field
classes driven both ways).

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path the pre-registration names, checked `git hash-object <disk>` against
`git rev-parse 4ad083fb:<path>` before grading — **14 of 14 SAME**:

| path | blob |
|---|---|
| `cases/F17_kovasznay/grade_f17.py` | `a863a673` |
| `cases/F17_kovasznay/exact_f17.py` | `bc304af5` |
| `cases/F17_kovasznay/foam_io_f17.py` | `5b28e23b` |
| `cases/F17_kovasznay/build_f17.py` | `16732087` |
| `cases/F17_kovasznay/run_f17.sh` | `af2c8b68` |
| `cases/F17_kovasznay/case/0/U.template`, `0/p` | `b6f3251b`, `0105f6fe` |
| `case/constant/transportProperties`, `turbulenceProperties` | `81921b4b`, `ba5bb3d1` |
| `case/system/blockMeshDict.template`, `controlDict`, `fvSchemes`, `fvSolution` | `ad0f3269`, `4a152ee1`, `f0eea325`, `96a0fc1b` |
| `verification/campaign/F17_KV40_PREREGISTRATION.md` | `b0b608d6` |

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines | last Time == endTime | fields at `4000/` | age guard (`0/U` → `4000/U`, `4000/p`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 4000 | 4000 == 4000 | U p | 16:42:13.400 → 16:42:16.586 / .587 Z | 3 s / 3.13 s |
| medium | 0 | 1 | 4000 | 4000 == 4000 | U p | 16:42:18.040 → 16:42:29.683 / .687 Z | 11 s / 11.53 s |
| fine | 0 | 1 | 4000 | 4000 == 4000 | U p | 16:42:31.686 → 16:43:29.731 / .747 Z | 58 s / 57.41 s |

All clauses hold at every level; the grader's own `completion()` agrees
(`n_times` 4000, `latest` 4000.0, rc 0 in the JSON). Serial, 1 rank at every
level; `decomposePar` never invoked (launcher output, decomposition seed `none`).

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8) | **7.6 core-min** (coarse 0.36, medium 1.46, fine 5.82); registered cap **40** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 3 s → 0.0500; medium 11 s → 0.1833; fine 58 s → 0.9667; **1.2000 core-min gross** |
| actual cleaned | **1.2000** — cleaned == gross (longest level 58 wall s; nothing matches the 3600-s stall rule) |
| waste, named separately | **0.000 core-min** — no stall, kill, re-run or cap movement |
| quantisation | ClockTime is integer-second: ± 0.0083 core-min per level |
| share of cap | 3.0 % |
| dollars | 1.2 / 60 × $0.0513 = **$0.00103 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **0.158** |

**Gap attribution — misprediction of the rate basis, not contention and not
waste.** The registered rate, 3.55 µs per cell-iteration, was read from one
record of a *different* case (`FPE_DIAG_runs/BL1`: a turbulent RANS `simpleFoam`
run with turbulence transport equations, first-order upwind turbulence
advection and `residualControl`). This laminar case measured **0.488 / 0.448 /
0.590 µs per cell-iteration** (coarse / medium / fine) — **6.0–7.9× cheaper**
per cell-iteration than the basis. Contention: **none** — ExecutionTime 57.41 s
against ClockTime 58 s at fine (1 %), with the launcher's own probe reading
1.95–2.38 free cores of 16 at each launch. **Carry forward:** laminar 2-D
`simpleFoam`, serial, on this box ≈ 0.5–0.6 µs per cell-iteration; the
turbulent-RANS basis should not be reused for laminar cases.

Calibration row: landed in `docs/COST_CALIBRATION.md` in the same commit as
this record (id derived at commit time from the ledger's maximum existing id).

## 5. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- `cases/F17_kovasznay/STATUS.F17_KV40` reads `rc=0 end=2026-08-26T16:43:29Z`
  and was written by the queue runner: it carries the **launch argv's exit
  status, not the solver rc**. The solver rc per level is `RC.txt` = 0 at all
  three, cited in §3. Runner outputs `launcher.queue.out` and
  `queue_entry_F17_KV40.json` under the case directory are the runner's
  records; not committed by this lane.
- The grader's `cost_claim` carries **no defects**; the cost claim above is
  not refused.
- **A foreign grade artefact** — `verification/runs/F17_runs/GRADE_F17.json`
  and `GRADE_F17.out`, mtime 16:46:09Z, 2 min 40 s after the run ended;
  author not recorded in this lane's brief. Compared leaf-by-leaf to this
  lane's `F17_GRADED.json`: **0 numeric or verdict differences**; 20 leaves
  differ only in path spelling (repo-relative vs absolute). Left uncommitted
  for the supervisor's read; this record cites only the grade this lane ran.
- The frozen grader was run with plain `python3`, never `-O` (the launcher's
  instrument line confirms `grade_f17 exits 2 under -O`).

## 6. NOT REGISTERED, NOT SENT

No re-grade of any row; no turbulence claim; p not graded. **Nothing is sent,
filed, uploaded or submitted** (rule 7). Field data stays on disk under
`verification/runs/F17_runs/` and is not committed.
