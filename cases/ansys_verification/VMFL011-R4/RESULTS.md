# VMFL011-R4 — Laminar Flow in a Triangular Cavity — RESULTS

**Case.** VM2026R1 §.11 (p. 41/42): laminar flow in a triangular cavity driven by
the moving base wall. OpenFOAM v2606 `simpleFoam`, steady laminar SIMPLEC on a
collapsed-hex triangular block (apex vertices genuinely merged). ρ = 1 kg/m³,
μ = 0.01 kg/m·s, base 2 m, height 4 m, moving base-wall U = 2 m/s → Re = 400. All
levels run to `endTime` 20000 SIMPLE iterations.

**Verdict: `GATE FAIL`** (register row #65). The pre-registration
PREDICTED `GATE FAIL` before compute — the rms resolves and stays above 0.030.
This is a finding, not a credential; the tier is `NOT HELD`.

**Ceiling `GATE REACHED` (never `PASS`).** The reference is code-to-code and
doubly indirect: R. Jyotsna & S.P. Vanka, *J. Comp. Phys.* **122**:107–117
(1995), carried by the manual p. 41 Reference and digitised by Ansys from the
p. 42 FIGURE (`VMFL011_xvel.xy`, "Benchmark x-norm", 46 rows; reference blob
`9f11191b…`). The manual prints no discrete target table. A code-to-code
digitised referent buys neither V nor P, so the comparator is hard-capped at
`GATE REACHED` and cannot print `PASS` whatever the number.

## The four-level family and the graded triple

Four levels L1/L2/L3/L4 on an r = 2 family; **the graded triple is the finest
three, L2/L3/L4, fixed a-priori with no fallback**. Strict completion (CLAUDE.md
rule 4) HOLDS at every level: `rc = 0`, one `End` line, last `Time` == `endTime`
20000, fields `U p phi` present at `endTime`, `ExecutionTime` count == 20000, and
the age guard met (each `20000/U` newer than its `0/U`). L1 iterative residuals
fell to ~1e-13/1e-14.

| level | rc | End | last Time | endTime | fields | age guard | rms_vs_benchmark | u_min_norm | complete |
|---|---|---|---|---|---|---|---|---|---|
| L1 | 0 | 1 | 20000 | 20000 | U p phi | yes | 0.040264214986 | −0.264494 | YES |
| L2 | 0 | 1 | 20000 | 20000 | U p phi | yes | 0.034775135234 | −0.319438 | YES |
| L3 | 0 | 1 | 20000 | 20000 | U p phi | yes | 0.034087720284 | −0.337560 | YES |
| L4 | 0 | 1 | 20000 | 20000 | U p phi | yes | 0.034089222270 | −0.342312 | YES |

## The gate and the numbers

- **Gate:** `rms_vs_benchmark ≤ 0.030` at the finest CONVERGING level (L4), the
  rms over the 46 benchmark abscissae of the normalised x-velocity error on the
  base-bisector.
- **Finest value:** `rms_vs_benchmark = 0.03408922226979811` at **L4**, against
  band **≤ 0.030** — **exceeds by +13.6 %** → `GATE FAIL`.
- **The rms plateaus, it does not resolve under 0.030:** L2/L3/L4 =
  0.0347751352338498 / 0.034087720284… / 0.03408922226979811 (L3→L4 flat, +2e-6).
  Exactly the pre-registered prediction.
- **Roache triple (on `u_min_norm`, the self-converging functional):** values
  L2/L3/L4 = −0.319438 / −0.337560 / −0.342312 (monotone), state **`CONVERGING`**,
  r = 2.0, **observed order p = 1.9313**, **GCI_fine = 0.006166 (0.6166 %)** at
  Fs = 1.25, Richardson `f_ex` = −0.344001. Because the triple is `CONVERGING`,
  rule 5 does NOT convert the row to `NOT A RESULT`; the `GATE FAIL` stands.
  (Diagnostic-only L1/L2/L3 triple also `CONVERGING`, p = 1.600 — moves no gate
  quantity.)

## Controls (CLAUDE.md rule 3) — all FIRED

- **On-path planted-zero controls PASS at every level**, both channels: the
  `rms_vs_benchmark` averaging reader and the `u_min_norm` point reader each move
  by their sized plant (rms plant sized `K·U_wall·base` per L-340; u_min point
  plant −0.1234 → reader Δ 0.0617 > threshold 0.01234).
- **Off-path controls correctly REFUSE (exit 2):** parent-pair Δ 3.68e-07 <
  1.234e-04; all-row unsized Δ 1.06e-04 < 1.234e-04; adversarial fixed plant Δ
  1.39e-17 < 0.04; and the L-347 apex-placement probe (a row-0 plant landing on
  u ≡ 0 at the merged apex moves `min()` by exactly 0 → refuses; the registered
  argmin plant moves it by 0.0617 → passes).
- Frozen constants (18 checked) and the reference blob `9f11191b…` matched the
  registration; assert-census 0 guards; observed-order floor catches p = 0.01,
  passes p = 0.5.

## Freeze / verification chain (CLAUDE.md rule 2, §3 check 4)

- **Freeze commit `f98d34c4e69ac47ca556496f45fc1579474ab8c1`.**
- **Comparator** `cases/ansys_verification/VMFL011-R4/grade_vmfl011_r4.py`, blob
  **`cbf376c03d285c4b149a17e955878971fc25badf`** — `git hash-object` on disk ==
  blob at the freeze `f98d34c4` == blob at HEAD; the comparator's own
  `--verify-frozen f98d34c4` printed "FROZEN: the comparator on disk IS the
  committed blob" (rc 0). `RUN_RC.L1..L4` independently record this comparator
  blob and the prereg blob before any core-minute was spent.
- **Pre-registration** `cases/ansys_verification/VMFL011-R4/PREREGISTRATION.md`,
  blob **`04c51c13a149223665e7818636b41aa83f3da6e5`**. Driver
  `run_vmfl011_r4.sh` blob `4e96cd0f`.
- **Independent reproduction:** the grade was re-run answer-blind to a scratch
  output and reproduced the canonical
  `verification/runs/ansys_verification/VMFL011-R4/GRADING_VMFL011_R4.json`
  bit-for-bit (verdict, tier, ceiling, deviation, triple p/GCI, all three
  graded-triple rms values).

## Cost (CLAUDE.md rule 12)

Measured core-minutes (ranks = 1, `wall_s × 1 ÷ 60`) from `RUN_RC.L1..L4` /
`COST.txt`:

| level | core-min | cap | use |
|---|---|---|---|
| L1 | 0.25 | 3 | 8 % |
| L2 | 0.9667 | 8 | 12 % |
| L3 | 6.8333 | 25 | 27 % |
| L4 | 128.1667 | 130 | 98.6 % |
| **total** | **136.2167** | backstop 170 | 80 % |

- **$ derived, not measured:** 136.2167 core-min = 2.27028 core-h × $0.0513/core-h
  = **$0.1165 DERIVED** (owner-stated rate, c7a.4xlarge; the box cannot read its
  own billing, `COMPUTE_BUDGET_CHARTER.md` §5).
- **`ESTIMATE_OVERRUN.txt` present** (elapsed 4876 s > 1.10 × estimate 4380 s =
  73 core-min): reported, **NOT enforced, NOT killed** — no registered cap on the
  runner as-built (D539 advisory, OFF); no per-level or backstop cap fired.
- **Actual/estimate = 136.22 / 73 = 1.87×**, attributed to **contention, not
  misprediction:** `CONTENTION.txt` at launch recorded load avg **32.60 on 16
  cores (~2.0× oversubscription)**, with 3 `simpleFoam` + 2 `rhoCentralFoam` +
  3 `python3` live; the dominant serial L4 leg's wall was inflated ~2×, matching
  the 1.87× ratio.
- **Stall-rule disclosure:** L4 ran 7690 wall s (> the §2 3600-s figure), but it
  reached `endTime` cleanly and passed strict completion, so it is productive
  compute reported **gross == cleaned**, not cleaned out (T4d/VMFL064-R2
  precedent). **Waste 0.000 core-min**, named separately (§6), folded into no
  ratio.

## Provenance and supersession

- **Grading artifact:**
  `verification/runs/ansys_verification/VMFL011-R4/GRADING_VMFL011_R4.json` (with
  `L1/L2/L3/L4`, `RUN_RC.L1..L4`, `COST.txt`, `LAUNCH_RECORD.txt`,
  `CONTENTION.txt`, `ESTIMATE_OVERRUN.txt`, `STATUS.queue.VMFL011-R4`).
- **Supersedes register row #36 (VMFL011-R3, `GATE FAIL` at the identical
  finest-level rms 0.034088)** under `ANSYS_VERIFICATION_CHARTER` §6 — a NEW row
  that cites #36 and does NOT overwrite it; #36's tree, prereg and comparator are
  preserved. Also cites the earlier VMFL011 attempts (rows #26, #31), both
  `NOT A RESULT` on planted-control refusals.
- **Calibration:** `docs/COST_CALIBRATION.md` row `C-20260908T203521.154517Z-d49de713`.
