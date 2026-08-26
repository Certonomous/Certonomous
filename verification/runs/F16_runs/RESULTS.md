CERTONOMOUS MORNING REPORT
Date:       2026-08-26
Assembled:  2026-08-26T16:16:49Z
Sections:   6 of 6
Missing:    none

# F16-SL2 — Stokes' second problem, three-level serial ladder — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F16_SL2_PREREGISTRATION.md`
frozen at commit `2aea29d97c74f54183c1d99a28d86568ee254815` (Amendment 2).
Grader run: `python3 cases/F16_stokes_second_problem/grade_f16.py --prereg-commit=2aea29d97c74f54183c1d99a28d86568ee254815`,
rc 0, stdout in `GRADE_F16.out`, machine record `F16_GRADED.json` (both beside this file).

## 1. SPEND

- Unit: core-minutes = ClockTime(s) × ranks ÷ 60 (prereg §8; ClockTime, not ExecutionTime), ranks = 1 at every level (serial, decomposePar never invoked).
- ClockTime from each level's own `log.icoFoam`: coarse **3 s**, medium **7 s**, fine **15 s**. Sum 25 s → **0.416667 core-min MEASURED** (gross = cleaned; no row within three orders of the 3600-s stall rule). Integer-second read-out quantisation: ±0.05 core-min over three levels (±0.008333 each).
- The launcher's own running tally (`launcher.out`) reads 0.4166666666666667 core-min of 20 — identical to the log-derived figure.
- Registered: central estimates 0.56 / 1.12 / 1.87 core-min at 0.3 / 0.6 / 1.0 ms/step (prereg §8 table), **REGISTERED CAP 20 core-min**. Realised rate: 25,000 ms / 112,000 steps = **0.223 ms/step**, below the lowest tabled assumption. Ratio actual/central(1.0 ms/step) = **0.223**; actual/cap = **0.021**. Cap never approached.
- Dollars: 0.416667 core-min ÷ 60 × $0.0513/core-h = **$0.000356 DERIVED, NOT MEASURED** (c7a.4xlarge rate reported-by-owner; the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5).
- Waste, named separately: **0.000 core-min** on compute. Attempt 1 (`STATUS.F16.attempt1`: rc=1 end=2026-08-26T15:56:10Z; `launcher.attempt1.out`) died at zero compute on `openfoam2606/etc/bashrc: WM_PROJECT_DIR: unbound variable` (the L-339-class `set -u` defect) before any solver started — zero core-minutes, retained on disk, not deleted.
- Left running: nothing. STATUS.F16 reads `rc=0 end=2026-08-26T16:13:02Z`; no F16 process remains.
- Field data (54 MB, `du -sh` of this directory) stays on disk and is NOT committed; the graded artifacts, logs, RC and STATUS files are.

Source: `coarse/log.icoFoam`, `medium/log.icoFoam`, `fine/log.icoFoam` (ClockTime lines); `launcher.out`; `STATUS.F16`; `STATUS.F16.attempt1`; `launcher.attempt1.out`; prereg §8 at `2aea29d9`.

## 2. LADDER POSITIONS

Sense of rung: a three-level Roache refinement ladder (Δy and Δt both halved per level, ratio 2.0/2.0 confirmed by the comparator's `constant_ratio_refinement` control).

Rule 4 strict completion, applied by this lane to each level before grading (all three hold):

| level | rc (RC.txt) | End line | last Time | `Time =` lines vs endTime/dt | endTime dir | fields at 40/ | age guard (mtime 0/U → 40/*) |
|---|---|---|---|---|---|---|---|
| coarse | 0 | yes | 40 | 16000 = 16000 | 40/ | U p phi U_0 phi_0 uniform | 1787760756 → 1787760759, newer |
| medium | 0 | yes | 40 | 32000 = 32000 | 40/ | U p phi U_0 phi_0 uniform | 1787760759 → 1787760766, newer |
| fine   | 0 | yes | 40 | 64000 = 64000 | 40/ | U p phi U_0 phi_0 uniform | 1787760766 → 1787760781, newer |

Ladder verdict position: **PENDING** on both gate rows, as printed by the frozen comparator (§3). No level is cap-stopped. No observed order p, no GCI and no triple state was produced, so none is quoted (REPORTING §5 rule 5).

Source: `coarse/RC.txt`, `medium/RC.txt`, `fine/RC.txt`; the three `log.icoFoam`; `*/40/` directory listings; `F16_GRADED.json` `controls[3]`.

## 3. GATES

The frozen comparator's tally, verbatim from `GRADE_F16.out`:

    F16 -- STOKES' SECOND PROBLEM -- TALLY
    ==============================================================================
    G-F16-1_E2_velocity_profile_L2           PENDING
        level 'coarse' is not complete: no `Time =` lines in the log
    G-F16-2_u_at_delta                       PENDING
        level 'coarse' is not complete: no `Time =` lines in the log
    ==============================================================================
    gated by: scripts/roache_triple.py::grade_ladder

| gate | reference | band (prereg §5) | coarse | medium | fine | triple | p | GCI | deviation | verdict | guard that held it | artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G-F16-1 E2 velocity-profile L2 | symbolic exact solution (`exact_stokes.py`) | [4.101177e-05, 3.691059e-04] | not computed | not computed | not computed | none | none | none | none | **PENDING** | comparator `completion()`: "no `Time =` lines in the log" | `F16_GRADED.json` rows[0] |
| G-F16-2 u at y = δ | symbolic exact solution | [-0.31027839, -0.30884136] | not computed | not computed | not computed | none | none | none | none | **PENDING** | same | `F16_GRADED.json` rows[1] |

**Finding: the frozen comparator refused on an instrument defect, not on the run.** `grade_f16.py:352` compiles `TIME_RE = ^Time = ...$` and line 369 applies it with `finditer` to the whole log text **without `re.MULTILINE`**, so `^` can only match at byte 0 and the pattern never matches a real OpenFOAM log. This lane checked the same regex line-by-line on `coarse/log.icoFoam` and it matches **16,000** lines (the exact endTime/dt identity the function then wants); the logs are plain ASCII with LF endings. The `--selftest` (rc 0, and rc 2 under -O, both re-confirmed today) never exercises `completion()` on a real log, which is why the instrument passed green at freeze and at both launches. Under rule 2 the comparator is not edited and the verdict is what it printed: **PENDING** on both gates. The completed field data on disk is intact and unaffected; a repair, if the supervisor takes it, is a §2d.1 / re-registration question for the supervisor, not this lane.

Planted-zero and other controls (all passed, from `F16_GRADED.json`): symbolic substitution into full NS residuals all 0; **PZ-F16-EXPONENT planted 1.37× exponent — residual non-zero, reader sees it (passed)**; truncation floor ratio 782.9 (passed); constant-ratio refinement 2.0/2.0 (passed); PZ-F16-CLASSC four plateau limbs each shown able to refuse (passed); grade_ladder call-site AST census + grep both ways (passed); solver tolerance 1e-09 on disk = registered (passed). Gate-demonstration constructions (synthetic, prereg §7): 1× amplitude inside both bands, 40× amplitude outside both, as intended.

Registered prediction (prereg §1/§8: the smooth transcendental solution must recover design order, **p ≈ 2**): **NOT TESTED** — no observed order was produced. Neither met nor missed.

Freeze verification (rule 2), disk blob == `git rev-parse 2aea29d9:<path>`: `grade_f16.py` `679823ff`, `exact_stokes.py` `78bd3342`, `run_f16.sh` `8071f9f8`, prereg `514d91ea` — all four identical.

Source: `GRADE_F16.out`; `F16_GRADED.json`; `cases/F16_stokes_second_problem/grade_f16.py` lines 352–372 at `2aea29d9`; `coarse/log.icoFoam`.

## 4. FD TABLES

nothing

Source: not applicable — no adjoint or finite-difference rung in this campaign.

## 5. REFILLED QUEUE

nothing

Source: no queue refill performed by this lane; ranking is the supervisor's.

## 6. WAITING LIST

- F16-SL2 gate rows G-F16-1 and G-F16-2: **PENDING** on the comparator's `completion()` regex defect (§3). Waits on the supervisor's ruling — §2d.1 repair route or re-registration — and, if repaired, a re-grade against the retained field data at zero further compute.
- Cost-calibration row landed as `docs/COST_CALIBRATION.md` C-118.

Source: this file §3; `docs/COST_CALIBRATION.md`.
