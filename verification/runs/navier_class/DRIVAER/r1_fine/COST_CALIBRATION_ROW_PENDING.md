<!-- INPUT FILE for scripts/append_record.py --path docs/COST_CALIBRATION.md --allocate-id.
     NOT a report. This is the rule-12 estimate-versus-actual row for this case, drafted
     2026-09-11 and NOT YET LANDED in docs/COST_CALIBRATION.md.

     WHY IT IS NOT LANDED -- BLOCKED, and not by anything in this row.
     scripts/append_record.py REFUSES (exit 8, D549 clause 1a) on the whole record because one
     PRE-EXISTING committed row carries an id that imitates the tool-allocated form without being
     one: HEAD:docs/COST_CALIBRATION.md line 522, id C-20260910T230023.521144Z-mrfr1a1 (the MRF_R1
     row). A tool-allocated id is <PREFIX>-<YYYYMMDDThhmmss.ffffffZ>-<8 hex>; the suffix mrfr1a1 is
     seven characters and contains a non-hex character, so the id pattern parses no id from a line
     that matches the id-bearing candidate shape. That is a refusal condition, not an absence.
     The SHAPE AUDIT names exactly one such line, so this is the only blocker.

     THE FIX IS NOT AN EDIT TO THIS RECORD and was not attempted here. The module states the two
     permitted repairs itself, both REGISTER EDITS INSIDE scripts/append_record.py: widen that
     records entry in RECORDS if the line carries a real id in a form the pattern cannot see, or
     add its form to KNOWN_EXCLUDED if it deliberately is not an id. That register guards four
     lab-wide records and its declared owner is the verification supervisor, so the choice is not
     this lanes and not one team alone. Measure which repair applies on the real bytes first.

     UNTIL THEN the rule-12 comparison for this case is BLOCKED, and it is recorded here rather
     than in a scratch path (CLAUDE.md rule 13: the scratchpad is never a handoff channel).
     Land with:
       python3 scripts/append_record.py --path docs/COST_CALIBRATION.md --rows <this file> --allocate-id
-->

| {{ALLOCATE_ID}} | 2026-09-11 | cfd | **DRIVAER R1 STAGE A, fine level** (`r1_fine`, 5,025,587 cells, `simpleFoam` kOmegaSST no layers, 8 MPI ranks, `endTime` 3000, prereg FROZEN `903dc88d` with Addendum 1 `5e12ce4b` and Addendum A1 `90f2fcbdd`) — **NO STAGE-A VERDICT WAS PRODUCED: the comparator REFUSED (exit 2) on its own p-field planted-zero control**, so the cost is recorded and the gate is not. Rule-4 completion holds on every limb (rc=0 from both `rc` and `RC.txt`, one `End`, last `Time` 3000 == `endTime`, `p U k omega nut phi` present at 3000, 3000 `ExecutionTime` lines == round(3000/1), age guard clear on BOTH anchors — reconstructed `3000/` fields and solver-written `processor*/3000/` fields all newer than `0/U` by >= 36,496 s). Grader on disk sha256 `1b51dc1d4438f66a`, matching Addendum A1.6's repaired pin and byte-identical to the HEAD blob. | **8,376 core-min** for the fine level (prereg §11 table; point estimate 8,426 including a 50 core-min exercise smoke that was never run). Registered cap **12,000 core-min**, whose STOP action was suspended by Addendum 1 (`5e12ce4b`) under Sanaa's 2026-09-10 3-D directive — the cap NUMBER did not move. Predicted dollars 8,426/60 x $0.0513 = **$7.20 DERIVED, NOT MEASURED**. | **4,866.13 core-min MEASURED** from `log.simpleFoam` (`core_min = wall_s x ranks / 60` = 36,496 s ClockTime x 8 / 60). CPU-held component **3,957.72 core-min** (ExecutionTime 29,682.9 s x 8 / 60). = 81.102 core-h -> **$4.16 DERIVED, NOT MEASURED** at $0.0513/core-h, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5 — this box cannot read its own billing). 0 GPU-h. | **= gross (4,866.13).** No stall row matched M5 on the coefficient trace (a row was written every iteration). **WASTE on the graded run: 0.000 core-min** — no relaunch, no restart, one uninterrupted march to `endTime`. Named separately and NOT waste of this run: **58.547 core-min of pre-compute diagnostics** (six mesh builds 57.026 + the `mergeTolerance` 1e-8 layer test 1.521, both from prereg §11 / §12.1). | **0.581** (4,866.13 / 8,376). | **MISPREDICTION, in the CONSERVATIVE direction, and contention is named separately rather than folded in.** The estimate assumed 30,000 cell-iterations per core-second; the run delivered **63,491** CPU-held and **51,638** wall-inclusive (5,025,587 cells x 3,000 iterations = 1.50768e10 cell-iterations). **CONTENTION cost 908.41 core-min, 18.67 % of gross** (gross 4,866.13 minus CPU-held 3,957.72) and made the run MORE expensive, not less — without it the ratio would have been 0.472, so contention is not what produced the under-spend. **The run finished at 40.6 % of the 12,000 cap.** Recorded against Addendum 1 §A1.3: its iteration-889 projection of 10,703 core-min (11,420 on this lane's arithmetic) was taken from the single worst 89-iteration window of the run — wall 35.72 s/iter over iterations 801-889, against 8.56 over 601-700 and 8.18 over 2501-3000 — and overstated the outturn by **2.2x**. The renice of the competing ranks recorded in that addendum is a plausible cause of the recovery, so the addendum may have dissolved its own premise; an unrun counterfactual is not a measurement and neither reading is asserted over the other. | `verification/runs/navier_class/DRIVAER/r1_fine/log.simpleFoam`, `.../RUN_META.txt`, `.../rc`, `.../RC.txt`; prereg `verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md` at `90f2fcbdd`; grader `cases/navier_class/DRIVAER/grade_drivaer.py` blob `13c1530914407bd4b3250bbd79bca5ba6c4e5d18`. |
