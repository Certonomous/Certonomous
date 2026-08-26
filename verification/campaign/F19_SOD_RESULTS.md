# F19-SOD — Sod shock tube (`rhoCentralFoam`, 1-D, Toro Test 1) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F19_SOD_PREREGISTRATION.md` frozen at
**`3053d9ec9695666e2491bed0d2398b101de2895f`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3, labelled at registration): counts toward no challenge
column. Graded 2026-08-26 by a cfd lab-lane at **zero new compute**, on a peer
session's addition to the lane's brief (same rules as F17 / F16b / F18).

Grader run **exactly as the launcher printed it**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F19_SOD/grade_f19.py --prereg-commit=3053d9ec9695666e2491bed0d2398b101de2895f`
— **rc 0**. Stdout: `verification/runs/F19_SOD_runs/F19_GRADED.out`. Record:
`verification/runs/F19_SOD_runs/F19_GRADED.json` (the grader's default path; the run
root is `F19_SOD_runs`, as prereg §9 names it). Gated by
`scripts/roache_triple.py::grade_ladder`, one call node (0 `assert` nodes across 4
files, planted assert seen).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p (grader) | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F19-1 `L1_density_error_at_T` | **4.400280e−04** | [1.466760e−04, 1.320084e−03] | **CONVERGING** (dim 1, r = 2.000, monotone) | **1.0177** | 88.5117 % = 3.894762e−04 absolute | **PASS** |
| G-F19-2 `shock_position_at_T` | **0.850539520** | [0.850106024, 0.850756269], exact 0.850431146 | **DEGENERATE**, \|p\| = 0.0319 < P_MIN = 0.05 (c525c247) | −0.0319 | none — no GCI beside a non-CONVERGING triple | **NOT A RESULT** |

The grader's own line for G-F19-2, verbatim: *"finest triple ('coarse', 'medium',
'fine') is DEGENERATE at dim = 1, observed order -0.0319; the value, every triple and
every order are printed beside it, and NO GCI is quoted because |p| < P_MIN = 0.05:
e21 ~ e32 and the fitted order is rounding residual"*.

Level values (from `<level>/0.2/rho`, read by the frozen reader), beside the
registered model (prereg §4, all three levels integrated, none extrapolated):

| level | cells | h | Δt | E1(T) measured | E1 model | x_s measured | x_s model | x_s − exact measured | x_s error model |
|---|---|---|---|---|---|---|---|---|---|
| coarse | 400 | 2.5e−3 | 2.0e−4 | 1.405768e−03 | 1.405768e−03 | 0.850756236 | 0.850756 | +3.2509e−04 | +3.251e−04 |
| medium | 800 | 1.25e−3 | 1.0e−4 | 7.593106e−04 | 7.593106e−04 | 0.850649076 | 0.850649 | +2.1793e−04 | +2.179e−04 |
| fine | 1,600 | 6.25e−4 | 5.0e−5 | 4.400280e−04 | 4.400280e−04 | 0.850539520 | 0.850540 | +1.0837e−04 | +1.084e−04 |

**Registered prediction (prereg §5):**
- **G-F19-1 — MET.** "CONVERGING with p ≈ 0.8, fine value inside the band → PASS":
  CONVERGING, PASS; observed p = 1.018 sits inside the honestly-registered range
  [0.6, 1.2] (the model said 0.79–0.89; the measured order is at the upper end).
- **G-F19-2 — NOT MET on the triple state.** The prereg predicted CONVERGING → PASS and
  named a *non-monotone* x_s triple as a registered possible outcome. What happened is
  neither: the triple is **monotone** and inside the band (fine error +1.08e−04 = 0.17
  cells; band verdict PASS) but its increments are **equal** — e32 = 1.0716e−04,
  e21 = 1.0956e−04 — so the shock-position error decreases *arithmetically* in h
  (3.25 → 2.18 → 1.08 ×1e−04, a fixed ≈ 1.1e−04 per halving) rather than
  geometrically, and the instrument's P_MIN floor reads that as DEGENERATE. Rule 5
  turns the band PASS into NOT A RESULT; the gate never goes the other way. The
  model's three x_s values carry the *same* equal increments (its own error sequence
  +3.251 / +2.179 / +1.084 ×1e−04), so this outcome was predictable from the
  registered model had its x_s triple been passed through `roache_triple.py` at
  registration — it was not, and that is a finding about the registration, not about
  the solver. Recorded here; no band, gate or label changes.
- **The model reproduces the solver to the printed digits on every level** (E1 to 7
  significant figures; x_s error to 4). The numpy re-implementation of the
  Kurganov/vanLeer/Euler discretisation is, on this evidence, the same algorithm as the
  installed `rhoCentralFoam`. What the E1 band therefore tests is that the solver does
  what its source says; the independent truth enters through E1 itself, which is the
  distance to the exact Riemann solution — 4.40e−04 at fine, against a density jump of
  0.875. Said so it is not mistaken for an independent prediction that happened to hit.

**Rule 5 limb (1) — how the grader handled the ABSENT iterative residual.** The
prereg §6 says plainly that an explicit inviscid `rhoCentralFoam` performs no linear
solve and has no residual; limb (1) is registered as a **stability census over every
time step's solver-reported `max Courant Number`** against the ceiling 0.25, with the
line count required to equal the step count and any `nan` / `FOAM FATAL` refusing. The
grader did exactly that and wrote the basis into every row: readings **1,000 / 2,000 /
4,000 == expected**, **0 above the ceiling**, **0 non-finite**, worst **0.0900** at every
level (the registered 0.0877 developed value plus the model's 0.0900 agree), `fatal:
False`; state `CONVERGED` **from that basis only**. Plateau: **ABSENT by construction**
(value at a fixed instant of a transient; `plateau_states = None`, recorded ABSENT in
every row — reported as absent, not as a pass).

**Planted-zero control (rule 3), into the real artefact through the real reader**
(`fine/0.2/rho`): E1 — planted 1.021773e−03, read back 1.021773e−03, `e1_from_files`;
x_s — planted 1.012714e−05, read back 1.012714e−05, `xs_from_files`. **Both PASS.** All
9 registered controls passed (own Newton iteration reproduces Toro Table 4.3 Test 1;
p_R and γ plants move p\*; mass/momentum/energy, RH mass flux and fan isentropy
identities; constant-ratio refinement in h and Δt; model forced, monotone,
mass-conserving, order in range; single `grade_ladder` call site both ways; solver
dictionaries agree with the registration; reader parses real solver-written `rho` on
this box; L-342 field classes driven both ways).

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path prereg §12 lists (14 under `cases/F19_SOD/` plus the prereg), checked
`git hash-object <disk>` against `git rev-parse 3053d9ec:<path>` before grading —
**15 of 15 SAME**: `grade_f19.py` `144d1ab0`, `exact_f19.py` `1fbec0a0`,
`foam_io_f19.py` `c33e3603`, `build_f19.py` `56bf9938`, `run_f19.sh` `56480095`,
`case/0/{p,T,U}.template` `161ec4f0`/`2e975e1b`/`2668db74`,
`case/constant/{thermophysicalProperties,turbulenceProperties}` `ef13a257`/`ba5bb3d1`,
`case/system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution}`
`aec66e8f`/`e953f529`/`aa4ec859`/`e33f492e`, `F19_SOD_PREREGISTRATION.md` `41f035ef`.

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` | `Time =` lines == endTime/Δt | last Time | fields at `0.2/` | age guard (`0/U` → `0.2/rho,U,p,T`) | Courant lines | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 1000 == 1000 | 0.2 | rho U p T | 17:34:11.681 → 17:34:12.314 Z | 1000 | 1 s / 0.39 s |
| medium | 0 | 1 | 2000 == 2000 | 0.2 | rho U p T | 17:34:14.116 → 17:34:15.196–.197 Z | 2000 | 1 s / 1.00 s |
| fine | 0 | 1 | 4000 == 4000 | 0.2 | rho U p T | 17:34:16.822 → 17:34:20.236–.238 Z | 4000 | 4 s / 3.15 s |

All clauses hold at every level; the grader's `completion()` agrees (`done: True`, rc 0,
`n_times` 1000/2000/4000, `latest` 0.2). Serial, 1 rank, `decomposePar` never invoked
(launcher output, seed `none`). Mesh gates from `log.checkMesh` at every level:
non-orthogonality 0°, skewness ≤ 6.7e−13.

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8) | **≈ 0.2 core-min** (0.012 / 0.033 / 0.107 solver + mesh/sampling) from 0.75 µs per cell-step + 0.4 ms per step, both borrowed from 2-D records; registered cap **5** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 1 s → 0.0167; medium 1 s → 0.0167; fine 4 s → 0.0667; **0.1000 core-min gross** (ExecutionTime 0.39 + 1.00 + 3.15 = 4.54 s) |
| actual cleaned | **0.1000** — cleaned == gross (longest level 4 wall s) |
| waste, named separately | **0.000 core-min** |
| quantisation | ClockTime is integer-second: ± 0.0083 per level = **± 0.025 on a 0.100 figure (25 %)** — the dominant uncertainty of this row |
| share of cap | 2.0 % |
| dollars | 0.1 / 60 × $0.0513 = **$0.0000855 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **0.50** (± 0.13 from quantisation alone) |

**Gap attribution — a 2-D basis applied to a 1-D one-cell-wide mesh, inside
quantisation noise; not contention, not waste.** All-in measured rate 4.54 s / 8.4 M
cell-steps = **0.54 µs per cell-step by ExecutionTime** (0.71 by ClockTime), against the
basis's 0.75 µs + 0.4 ms/step (≈ 9 s projected). A 1-D mesh has two internal faces
per cell where the 2-D basis cases have four, so the per-cell flux work is roughly
halved; the 0.4 ms/step overhead term (2.8 s over 7,000 steps) was also the larger
part of the estimate and is not separable from the solve at this size. Contention:
the launcher probe read **0.5 free cores of 16** (a saturated box) and ClockTime
exceeds ExecutionTime by 1.5 s over three levels — but at integer-second resolution
that is not a measurement. **Carry forward:** for sub-second levels the calibration
ratio is quantisation-bound; price 1-D `rhoCentralFoam` at ≈ 0.5 µs per cell-step.

Calibration row: landed in `docs/COST_CALIBRATION.md` in the same commit as this
record (id derived at commit time from the ledger's maximum existing id).

## 5. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- `cases/F19_SOD/STATUS.F19_SOD` reads `launcher_rc=0 end=2026-08-26T17:34:20Z
  note=exit-status-of-the-launch-argv-NOT-the-solver-rc`; the solver rc per level is
  `RC.txt` = 0 (§3). Runner outputs under the case directory are the runner's records;
  not committed by this lane.
- The grader's `cost_claim` carries **no defects**; the cost claim is not refused.
- Run with plain `python3`, never `-O` (the launcher's instrument line confirms
  `grade_f19 exits 2 under -O`).

## 6. NOT REGISTERED, NOT SENT

No claim about the contact position (not gated); no re-grade; no change to any band or
label. **Nothing is sent, filed, uploaded or submitted** (rule 7). Field data stays on
disk under `verification/runs/F19_SOD_runs/` and is not committed.
