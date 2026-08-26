# F17b-KV40-EXT — Kovasznay flow, Re = 40, LADDER EXTENSION 192×128 / 384×256 / 768×512 (`simpleFoam`) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F17b_KV40_EXT_PREREGISTRATION.md`
frozen at **`61b47973bdec19aa061d11030967bd612038ba01`** (v1.1; Amendment 1 is
pre-first-compute — run root ABSENT and 0 core-min at its writing — and moved
G-F17-2's *reference* only, never a band width, cap or label). **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3, as the parent F17): counts toward no challenge
column. Graded 2026-08-26T22:09:33Z–22:12:01Z by a cfd lab-lane at **zero new
compute**; the three levels were launched by the queue runner at 21:22:37Z with no
agent attached and completed 21:51:27Z.

Grader run **exactly as the launcher printed it**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F17b_kovasznay_ext/grade_f17.py --prereg-commit=61b47973bdec19aa061d11030967bd612038ba01`
— **rc 0**. Stdout: `verification/runs/F17b_runs/F17b_GRADED.out`. Record:
`verification/runs/F17b_runs/F17b_GRADED.json` (the grader's default output path).
Gated by `scripts/roache_triple.py::grade_ladder`, one call node (AST census in
the JSON: 0 `assert` nodes across 4 files, planted assert seen; call node at
line 674, grep matcher driven both ways).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F17-1 `E2_velocity_L2` | **6.155850e−06** | [2.299887e−06, 2.069898e−05] | CONVERGING (dim 2, r = 2.000, monotone) — printed beside, **not a result** | 1.8585 — printed beside, **not a result** | 227.5672 % = 1.400869e−05 absolute — printed beside, not quoted as a result | **NOT A RESULT** |
| G-F17-2 `u_at_probe` (0.5, 0) | **0.382383179** | [0.382373500, 0.382394846], reference 0.382384173 (Amendment 1, same-stencil) | CONVERGING (dim 2, r = 2.000, monotone) — printed beside, **not a result** | 3.4708 — printed beside, **not a result** | 0.0002 % = 5.944173e−07 absolute — printed beside, not quoted as a result | **NOT A RESULT** |

The grader's tally, verbatim:

    G-F17-1_E2_velocity_L2                   NOT A RESULT
        levels fine,medium are not iteratively converged or not plateaued; no grid claim can be made from this triple
    G-F17-2_u_at_probe                       NOT A RESULT
        levels medium are not iteratively converged or not plateaued; no grid claim can be made from this triple

Level values (from `<level>/4000/U`, read by the frozen reader):

| level | cells | h | E2 | u(probe)/U0 |
|---|---|---|---|---|
| coarse | 24,576 | 1/128 | 1.423137e−04 | 0.382441158 |
| medium | 98,304 | 1/256 | 3.558768e−05 | 0.382387976 |
| fine | 393,216 | 1/512 | 6.155850e−06 | 0.382383179 |

The coarse row is the same grid as F17's fine level and reproduces F17's fine
values to every printed digit (F17: E2 1.423137e−04, u(probe) 0.382441158 —
`verification/campaign/F17_KV40_RESULTS.md` §1).

**Registered prediction (prereg §5 — both triples CONVERGING with observed
p ≈ 2, fine values inside both bands → PASS) — NOT MET.** Both gates are
**NOT A RESULT by rule 5 limb 1**, which the grader applies before any triple
or band is consulted; the gate can only turn a PASS or GATE FAIL *into* NOT A
RESULT, never the reverse, and no order claim is made from this ladder. For the
record only, and carrying no verdict weight: the fine values sit inside both
registered bands (the grader's `band_verdict` field reads `PASS` on both rows
before limb 1 overrides it), and the raw triples are CONVERGING with observed
orders 1.858 (E2) and 3.471 (probe) — neither ≈ 2 as registered, and neither
is a result.

**Rule 5 limbs, in order, from the grader's own `levels_detail`.**

(1) Iterative convergence and plateau. The residual census is clean at every
level — **0 of 1,200 iterations above tolerance for Ux, Uy and p in the Class C
window 2801–4000** (worst: coarse Ux 1.47e−11 / Uy 8.69e−11 / p 1.13e−08;
medium 1.74e−09 / 8.51e−09 / 3.75e−07; fine 7.81e−10 / 2.02e−09 / 2.20e−08
against 1e−6 / 1e−6 / 1e−5). **The Class C plateau on the graded quantity is
what fails** (40 checkpoints, 12-sample window spanning iterations 2900–4000,
trend tolerance 2e−4 relative drift, variance-ratio band [0.2, 5]):

| level | E2: relative drift over window | E2 state | u(probe): drift / variance ratio | u(probe) state |
|---|---|---|---|---|
| coarse | 1.818e−06 | PLATEAUED | 3.11e−09 / 1.0000 | PLATEAUED |
| medium | **1.459e−02** | **NOT_PLATEAUED_TREND** | 1.97e−06 / **0.0968** | **NOT_STATIONARY_VARIANCE** |
| fine | **1.350e−01** | **NOT_PLATEAUED_TREND** | 1.97e−06 / 1.344 | PLATEAUED |

At fine the E2 window mean is 5.776e−06 against a final 6.156e−06 with a
positive fitted slope of 7.09e−10 per iteration: E2 was still moving by 13.5 %
of itself over the last 1,100 iterations. Mechanism, read from the same
numbers and stated as a finding, not as a softening: the per-iteration
movement of the fine field is of the order of its initial residual (~1e−9),
which over the 1,100-iteration window integrates to ~1e−6 — the same order as
the fine level's discretisation error E2 = 6.2e−06. The residual tolerances
(Ux ≤ 1e−6) and the fixed 4,000-iteration count were inherited byte-for-byte
from F17, where E2_fine = 1.4e−04 and the iterative contribution was 100×
smaller than the discretisation error; at 768×512 the two are comparable and
the registered instrument, correctly, refuses. (2) and (3) are not reached.
The grader's `iterative_convergence` field reads CONVERGED at every level; it
is the plateau limb of Class C, not the residual limb, that carries the refusal.

**Planted-zero control (rule 3), into the real artefact through the real
reader** (`fine/4000/U`): E2 — planted 1.227910e−03, read back
1.227910e−03 (delta 1.6e−17 class), `e2_from_files`; u(probe) — planted
1.234e−03, read back 1.2340000000000129e−03, `u_probe_from_files`. **Both
PASS.** All 11 registered controls passed, including Amendment 1's
`PZ-F17-AMEND1_probe_reference_same_stencil_zero_error_and_plant_read_back`
(reference 0.382384173, stencil error +1.135312e−05, zero-error field read back
0.0, plant read back 1.234e−03) and the 10 inherited from F17 (symbolic
substitution with residuals identically 0 and the λ×1.1 plant non-zero;
constant-ratio refinement both directions; boundary data balancing to 1.1e−16;
model solved and second order, orders 2.0020 / 2.0020; four Class C limbs each
shown able to refuse; single `grade_ladder` call site both ways; solver
dictionaries agree with the registration; reader parses real solver-written
`U` on this box; L-342 field classes driven both ways). The §7 gate
demonstrations were re-executed by the grader: 1× model error inside both
bands, 40× outside both.

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path the pre-registration names plus the gating script, checked
`git hash-object <disk>` against `git rev-parse 61b47973:<path>` **before
grading** — **15 of 15 SAME**; the grader would have been refused on a mismatch.

| path | blob |
|---|---|
| `cases/F17b_kovasznay_ext/grade_f17.py` | `cfebd8a4` |
| `cases/F17b_kovasznay_ext/exact_f17.py` | `56fef386` |
| `cases/F17b_kovasznay_ext/foam_io_f17.py` | `5b28e23b` (byte-identical to F17) |
| `cases/F17b_kovasznay_ext/build_f17.py` | `16732087` (byte-identical to F17) |
| `cases/F17b_kovasznay_ext/run_f17.sh` | `c41c7867` |
| `cases/F17b_kovasznay_ext/case/0/U.template`, `0/p` | `b6f3251b`, `0105f6fe` |
| `case/constant/transportProperties`, `turbulenceProperties` | `81921b4b`, `ba5bb3d1` |
| `case/system/blockMeshDict.template`, `controlDict`, `fvSchemes`, `fvSolution` | `ad0f3269`, `4a152ee1`, `f0eea325`, `96a0fc1b` |
| `verification/campaign/F17b_KV40_EXT_PREREGISTRATION.md` | `0ae54990` (== the blob at HEAD) |
| `scripts/roache_triple.py` | `78e56a3b` |

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines | last Time == endTime | fields at `4000/` | age guard (`0/U` → `4000/U`, `4000/p`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 4000 | 4000 == 4000 | U p phi | 21:24:16.042 → 21:25:23.654 / .670 Z | 67 s / 66.49 s |
| medium | 0 | 1 | 4000 | 4000 == 4000 | U p phi | 21:25:28.501 → 21:31:39.334 / .395 Z | 371 s / 368.04 s |
| fine | 0 | 1 | 4000 | 4000 == 4000 | U p phi | 21:31:53.140 → 21:51:27.100 / .343 Z | 1174 s / 1173.92 s |

`ExecutionTime` lines: 4000 at every level (== endTime). All clauses hold at
every level; the grader's own `completion()` agrees (`n_times` 4000, `latest`
4000.0, rc `0`, `done` true at all three). Serial, 1 rank at every level;
`decomposePar` never invoked (launcher output, decomposition seed `none`).
Mesh admissibility per level from `MESH_LINE.txt` (source `log.checkMesh`):
max non-orthogonality 0°, max skewness 1.4e−14 / 4.3e−14 / 8.5e−14 against
gates 70° / 4.

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8) | **32.1 core-min** (coarse 0.97, medium 5.03, fine 26.1); registered cap **150** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 67 s → 1.1167; medium 371 s → 6.1833; fine 1174 s → 19.5667; **26.8667 core-min gross** |
| launcher's own tally (`cases/F17b_kovasznay_ext/launcher.queue.out`) | 26.866666666666667 core-min — **agrees with the log reading to every digit** (it is the same ClockTime lines summed) |
| actual cleaned | **26.8667** — cleaned == gross (longest level 1,174 wall s; nothing matches the 3600-s stall rule) |
| waste, named separately | **0.000 core-min** — no stall, kill, re-run or cap movement; the ladder completed and was graded once |
| quantisation | ClockTime is integer-second: ± 0.0083 core-min per level |
| share of cap | 17.9 % |
| dollars | 26.8667 / 60 × $0.0513 = **$0.02297 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **0.837** |

**Gap attribution — the F17 measured basis HELD; the residual 16 % is the
+30 %-per-doubling growth assumption, which was pessimistic at the fine level
and optimistic at the two below it.** Measured per-cell-iteration rates
(ClockTime ÷ cells ÷ 4,000): **0.682 / 0.944 / 0.746 µs** (coarse / medium /
fine) against the registered 0.590 / 0.767 / 0.997. The coarse level is F17's
fine grid re-run under a full box (launcher probe: 0.5 free cores of 16, load
19.55 at launch) and came in 16 % slower than F17's 0.590 on the identical
grid; medium 23 % over its projection; fine **25 % under** its projection —
the GAMG cycle growth that the +30 %/doubling term priced did not continue to
768×512. Contention: **present in the box load, absent from the wall-versus-CPU
reading** — ExecutionTime/ClockTime = 0.992 / 0.992 / 1.000, so the serial
rank was never descheduled; the slower coarse and medium rates under load are
consistent with shared-cache/memory-bandwidth pressure rather than lost CPU
time, and are not separable from the measurement into a contention figure.
**Carry forward:** laminar 2-D `simpleFoam`, serial, on this box ≈ 0.68–0.94
µs per cell-iteration under a full box (0.45–0.59 measured on an idle-ish box
in F17); a single measured rate from the same case definition predicts the
extension to within a factor 1.2 — the basis was sound.

Calibration row: landed in `docs/COST_CALIBRATION.md` in the commit following
this record (id derived at commit time from the ledger's maximum existing id).

## 5. WHAT THE EXTENSION SETTLED

F17b was registered to settle whether the F17 instrument reads p ≈ 2 on a
finer triple. **It did not:** on the extension ladder the instrument reads
**NOT A RESULT × 2**, because its own registered Class C plateau criterion
fails on the medium and fine levels at the inherited 4,000 fixed iterations —
the discretisation error at 384×256 and 768×512 is small enough that the
residual-level iterative movement is no longer negligible against it. No p is
claimed. The raw CONVERGING triples (1.858 / 3.471) are printed beside the
verdict as rule 5 requires and are not evidence of anything.

What would be needed for a finer triple to be graded is a registration matter,
not a re-grade: a deeper iterative floor (more iterations or a
`residualControl` tightened to the fine level's error scale) registered
before compute. That choice sits with the cfd supervisor; nothing in this
record proposes it as done.

## 6. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- `cases/F17b_kovasznay_ext/STATUS.F17b_KV40_EXT` reads `launcher_rc=0
  end=2026-08-26T21:51:27Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`
  and was written by the queue runner. The solver rc per level is `RC.txt` = 0
  at all three, cited in §3. `launcher.queue.out` under the case directory is
  the runner's record; not committed by this lane.
- The grader's `cost_claim` carries **no defects**; the cost claim above is
  not refused (`core_min_claim` 26.866666666666667, `partial_sum_core_min`
  the same, cap 150.0).
- No foreign grade artefact was present in the run root before this grade
  (`F17b_GRADED.json` / `.out` are the only non-level entries; both written by
  this invocation at 22:12Z).
- The frozen grader was run with plain `python3`, never `-O` (the launcher's
  instrument line confirms `grade_f17 exits 2 under -O`).
- Box at grading: load ~20 of 16, four foreign solvers live (F18b `icoFoam`,
  F21 `rhoCentralFoam`, T3 and T4b `buoyantBoussinesqSimpleFoam`); the grader
  is zero compute and touched no run directory but its own output files.

## 7. NOT REGISTERED, NOT SENT

No re-grade of any row; no re-registration; no claim about p; no turbulence
claim; no amendment to the frozen pre-registration (post-compute). **Nothing
is sent, filed, uploaded or submitted** (rule 7). Field data stays on disk
under `verification/runs/F17b_runs/` and is not committed.
