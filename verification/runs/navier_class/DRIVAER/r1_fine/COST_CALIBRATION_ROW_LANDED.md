# DRIVAER R1 STAGE A — rule-12 cost row: LANDED

**STATUS: LANDED in `docs/COST_CALIBRATION.md` on 2026-09-11 as id
`C-20260911T162610.013753Z-ff39f947`** (uncommitted in the working tree at the time of
writing; the grading lane commits it).

**DO NOT feed this file to `scripts/append_record.py --rows`.** The row is already in the
register; re-running would double-append it. The copy below is provenance, not an input.

## Why this file is no longer "PENDING"

It was drafted at 15:37Z as a parked row because `scripts/append_record.py` refused
(exit 8, D549 clause 1a) on a malformed pre-existing id at `docs/COST_CALIBRATION.md:522`
(`C-20260910T230023.521144Z-mrfr1a1` — a seven-character suffix with a non-hex character
where 8 hex are required). **That blocker was repaired by the verification team at commit
`bc5588bc7` while this grading was in progress**, so the registered land command succeeded
instead of refusing. Nothing in this row and nothing in the register was edited to achieve
that. The 15:37Z draft it supersedes — which asserts, now falsely, that no Stage A verdict
was produced and cites the superseded A1.6 grader pin — is preserved verbatim beside this
file as `COST_CALIBRATION_ROW_PENDING.SUPERSEDED_1537Z.md`.

## DEFECT FOUND WHILE LANDING — `append_record.py --rows` appends the file VERBATIM

`append_record.py` writes `head_text + rows_text`, where `rows_text` is **the entire
`--rows` file**, not the row lines parsed out of it. The 15:37Z parked-row pattern put a
44-line explanatory HTML comment in the very file its own documented land command names as
`--rows`, so executing that command **injected the whole comment block into the shared
register** — including the sentence "NOT YET LANDED in docs/COST_CALIBRATION.md", landed.
It was removed the same minute by a targeted edit that deleted only the comment block and
touched **zero rows**, leaving the register as HEAD plus exactly one row line (verified:
`git diff HEAD` = 1 insertion, 0 deletions).

**This is a latent trap for every team that parks a row this way, and the same shape is on
disk in other cases.** `scripts/append_record.py` is owned by the **verification** team;
this lane did not edit it and proposes no repair here. **NOT FILED — nothing sent (rule 7).**
The safe pattern in the meantime: the `--rows` file contains **row lines only**, and any
explanation lives in a separate sibling file.

---

## The row as landed

| C-20260911T162610.013753Z-ff39f947 | 2026-09-11 | cfd | **DRIVAER R1 STAGE A, fine level** (`r1_fine`, 5,025,587 cells, `simpleFoam` kOmegaSST no layers, 8 MPI ranks, `endTime` 3000; prereg FROZEN `903dc88d1` with Addendum 1 `5e12ce4ba`, Addendum A1 `90f2fcbdd`, Addendum A2 `b06e0526b`) — **PROCESS COMPLETE: the rung is graded. RUNG VERDICT `NOT A RESULT`** by CLAUDE.md rule 5 limb (1), the single level being neither iteratively converged nor plateaued; **Gate A1 `GATE FAIL`** (iterative `NOT_CONVERGED`, worst final Initial residual 1.476127633e-02 on Uy against `RES_TOL` 1e-4, 148× over; Cd `NOT_PLATEAUED` excursion 6.31302e-02 against 5.0e-03; Cl `NOT_PLATEAUED` excursion 11.270582); **Gates A2 and A3 band verdicts `PASS` computed first and unconditionally (Cd 0.29795528411 in [0.15,0.60]; Cl 0.0078616272713 in [−0.50,+0.50]), then converted to `NOT A RESULT` by the same limb** — one-way, never the reverse. **NOT credential-eligible**: mesh max_skewness 10.315144 against `docs/standards/MESH_STANDARD.md` threshold 4.0, 2.579× over on 16 faces — STATED LIMITATION, never HOLDS. The p-field planted-zero control that refused this mesh on 2026-09-10 at exactly 3.000000× its own expectation now **PASSES with both arms fired** (m=1 cell 1563756 reader_delta 1.980299975912203e-05; m=3 cell 1702645 reader_delta 5.940899927736609e-05; both reader/expected = 1.000000000036). Rule-4 completion HOLDS on every limb and is NOT the reason for the GATE FAIL (rc=0 from both `rc` and `RC.txt`, one `End`, last `Time` 3000 == `endTime`, `p U k omega nut phi` present at 3000, 3000 `ExecutionTime` lines == round(3000/1), age guard clear — `3000/p` newer than `0/U` by 36,638 s). Comparator on disk sha256 `6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`, matching **Addendum A2.7's** pin (A1.6's `1b51dc1d…` and §8's `0eddb558…` are both superseded) and byte-identical to the HEAD blob. Grading record: `verification/campaign/DRIVAER_R1_STAGE_A_RESULTS.md`. | **8,376 core-min** for the fine level (prereg §11 table; point estimate 8,426 including a 50 core-min exercise smoke that was never run). Registered cap **12,000 core-min**, whose STOP action was suspended by Addendum 1 (`5e12ce4ba`) under Sanaa's 2026-09-10 3-D directive — the cap NUMBER did not move. Predicted dollars 8,426/60 × $0.0513 = **$7.20 DERIVED, NOT MEASURED**. | **4,866.13 core-min MEASURED** from `log.simpleFoam` (`core_min = wall_s × ranks / 60` = 36,496 s ClockTime × 8 / 60), re-derived independently by the grading lane. CPU-held component **3,957.72 core-min** (ExecutionTime 29,682.9 s × 8 / 60). = 81.102 core-h → **$4.16 DERIVED, NOT MEASURED** at $0.0513/core-h, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5 — this box cannot read its own billing). **Grading instrument: 0.339 core-min** (20.35 wall s, serial, 1 rank) for the registered `--stage-a` invocation, plus a sub-second `--selftest`. 0 GPU-h. | **= gross (4,866.13).** No stall row matched M5 on the coefficient trace (a row was written every iteration). **WASTE on the graded run: 0.000 core-min** — no relaunch, no restart, one uninterrupted march to `endTime`. Named separately and NOT waste of this run: **58.547 core-min of pre-compute diagnostics** (six mesh builds 57.026 + the `mergeTolerance` 1e-8 layer test 1.521, both from prereg §11 / §12.1). Named separately and also NOT waste: the **first grading attempt that exited 2** on the false control refusal — its cost is the instrument's ~0.3 core-min, not the solve's, and the solve was never repeated. | **0.581** (4,866.13 / 8,376). | **MISPREDICTION, in the CONSERVATIVE direction, and contention is named separately rather than folded in.** The estimate assumed 30,000 cell-iterations per core-second; the run delivered **63,491** CPU-held and **51,638** wall-inclusive (5,025,587 cells × 3,000 iterations = 1.50768e10 cell-iterations). **CONTENTION cost 908.41 core-min, 18.67 % of gross** (gross 4,866.13 minus CPU-held 3,957.72) and made the run MORE expensive, not less — without it the ratio would have been 0.472, so contention is not what produced the under-spend. **The run finished at 40.6 % of the 12,000 cap.** Recorded against Addendum 1 §A1.3: its iteration-889 projection of 10,703 core-min (11,420 on the prior lane's arithmetic) was taken from the single worst 89-iteration window of the run — wall 35.72 s/iter over iterations 801–889, against 8.56 over 601–700 and 8.18 over 2501–3000 — and overstated the outturn by **2.2×**. The renice of the competing ranks recorded in that addendum is a plausible cause of the recovery, so the addendum may have dissolved its own premise; an unrun counterfactual is not a measurement and neither reading is asserted over the other. **CALIBRATION LESSON for the successor run:** the 30,000 cell-iterations/core-s assumption is low by ~2.1× for `simpleFoam` kOmegaSST at ~5M cells on 8 ranks of c7a.4xlarge; 60,000 CPU-held / 50,000 wall-inclusive is the measured basis to carry forward, and the successor needs a LONGER run — the rung is `NOT A RESULT` because the signal is drifting, not oscillating. | `verification/runs/navier_class/DRIVAER/r1_fine/log.simpleFoam`, `.../RUN_META.txt`, `.../rc`, `.../RC.txt`, `.../STAGE_A_REPORT.json`; prereg `verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md` at `b06e0526b`; grading record `verification/campaign/DRIVAER_R1_STAGE_A_RESULTS.md`; comparator `cases/navier_class/DRIVAER/grade_drivaer.py` sha256 `6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`. |
