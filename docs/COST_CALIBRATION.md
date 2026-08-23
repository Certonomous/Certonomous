# Cost calibration ledger

**Purpose.** Sanaa's directive, verbatim (2026-08-23): *"for all teams involved
once a process is completed, the estimated costs must be compared with the
actual incurred costs so we can improve the lab's estimates"*. This file is
where that comparison lands — one row per completed process (a rung graded, a
case closed, a curriculum item finished), from every team. The point is
calibration: the ratio column is the lab's estimate-quality record, and the
gap-attribution column is what turns a miss into a better next estimate.
Codified as the calibration bullet of `CLAUDE.md` rule 12; charter anchor in
the 2026-08-23 amendment at the foot of
`docs/charters/COMPUTE_BUDGET_CHARTER.md`.

**Append rules — the same discipline as the docket.**

1. **Append-only.** New rows land at the foot of the table. An existing row is
   never edited; a correction is a new row naming the row it corrects.
2. **Numbers come from committed records, never from memory.** Every row cites
   the results file or commit its figures were read from, and a figure not in
   the record is left out, stated as absent — not approximated.
3. **Units.** Actuals in the lab's measured unit: core-minutes or core-hours
   from logs (say which), GPU-hours for GPU runs. Dollars are **derived, not
   measured**, at the recorded rate ($0.0513/core-h, c7a.4xlarge,
   reported-by-owner — the box cannot read its own billing,
   `COMPUTE_BUDGET_CHARTER.md` §5), and every dollar figure is labelled
   derived.
4. **Gross and cleaned carry the charter §2 meanings** (cleaned = gross minus
   rows the 3600-s stall rule matches). Where a source record uses its own
   cleaned definition, the row says so beside the figure. **Waste stays
   separately named** (charter §6) and is never laundered into either column
   or into the ratio's explanation.
5. **Concurrent appends — this file is written by multiple teams.** Re-derive
   the table's current tail **at commit time, in the same shell invocation as
   the commit**, and land the row via the **private-index protocol of
   `CLAUDE.md` rule 10** (capture HEAD once; `read-tree`; `update-index` this
   path only; `diff-tree` assert; CAS on `refs/heads/main`; post-commit
   verify). Peers commit constantly; a row built against a stale read of this
   file is re-derived, not forced.

| date | team | process/rung | predicted (core-min or GPU-h) | actual gross | actual cleaned | ratio (cleaned/predicted) | gap attribution | record ref (commit/results file) |
|---|---|---|---|---|---|---|---|---|
| 2026-08-23 | heat-transfer | T10a-R (three repair arms graded) | 2.40 core-h / $0.123 registered (stop threshold 10x = 24.0 core-h / $1.23) | 6.66 core-h (23,969 core-s) = $0.342 derived | not stated in record — figure taken gross, under contention | 2.77x gross/predicted (no cleaned figure in record); within the registered 10x stop threshold | contention (12 T-family solvers live at launch) plus the view-factor generator's under-predicted memory/wall at n = 18,496 (21.0 GB peak vs 5.5 GB solver-basis estimate, a missed prediction reported as such) | `docs/campaigns/T-family/T10aR_RESULTS.md` §7 |
| 2026-08-22 | closure | R5C omega-source repair (27 cases + 2 W2 legacy, GATE FAIL; re-graded 2026-08-23) | 0.210 core-h = $0.0108 (cap 1.0 core-h) | ≤ 0.168 core-h (0.140 measured + ≤ 0.028 bounded postProcess) = ≤ $0.0086 derived | = gross (no ledger row near the 3600-s stall rule; total wall 603.7 s) | ≤ 0.80x — under the estimate | misprediction, conservative direction: 27-run arm under (0.1256 vs 0.184), W2-legacy arm over (0.0140 vs 0.00603), postProcess not separately instrumented so bounded not measured; **waste named: 0.0009 core-h** (D-1, four discarded duct builds) | `cases/RANS_LES_closure_models/R5C_omega_repair/RESULTS.md` §9, prereg frozen at `f364cf2d` |
| 2026-08-23 | dafoam | W4 M1+M2 (hump `-9` conditioning; O2 not launched at budget floor) | 40.0 core-min registered (ceiling 60.0) | ≤ 40.12 core-min = $0.03430 derived | ≤ 20.12 core-min = $0.01720 derived (record's own CLEANED: excludes the named waste row, not a stall-rule cleaning) | 0.50x cleaned/predicted; gross/predicted 1.003x, **reported in the record as a coincidence** — 20.00 core-min of waste almost exactly replaced the unbought O2, two errors cancelling | **waste named: 20.00 core-min** (M2 attempt 1 staging fault, §5a, zero measurement) plus misprediction: both of the lane's own cost predictions MISS (C-P1, C-P2 — M1 ≤ 10.25 vs > 25.0 predicted; total stopped at the O2 launch floor, not the ceiling) | `cases/dafoam/ladder-b/W4_M1M2_RESULTS.md` §5, landed at `64479072` |
| 2026-08-23 | cfd | DPW8_V2 L4 divergence diagnosis (Arm A relaxation, Arm B momentum-upwind; both arms graded, no gate issued) | 61 core-min projected (29.8 core-min per arm solver at the measured 2.979 core-s/iter basis, plus ~1 core-min preflight) = $0.052 derived; CAP 150 core-min total, 75 per arm — prereg §8, frozen `99f939ee` | 21.11 core-min solver **measured** (Arm A 124.26 s, Arm B 1142.22 s, both single-rank, each from its own `solver.time`; record's subtotal 21.1) plus ≈ 0.4 core-min checkMesh/preflight — **estimated, not separately instrumented**, the record states it as an approximation — total ≈ **21.5 core-min** = $0.018 derived | = gross (record §6: no row exceeded 3600 wall s, max wall 1142.22 s, so there is no stall to separate out) | **0.35x** cleaned/predicted (21.5 / 61); **0.14x of cap** (21.5 / 150) | Two named causes, **zero waste**. (a) Arm A terminated at iteration **182 of 600** by the measured phenomenon itself (SIGFPE divergence) — 2.07 vs 29.8 core-min predicted; **not waste**: the crash *is* the measurement and its partial log is the evidence the diagnosis rests on. (b) Per-iteration **misprediction in the conservative direction** on Arm B — **1.904 core-s/iter** actual (derived, 1142.22 s / 600 iter) against the **2.979 core-s/iter** basis, i.e. 0.64x. That basis was measured 2026-07-29 on a box at **load ~19.5** (`verification/campaign/DPW8_V2_joukowski.md` §3a) and applied today at **load 5.03** (prereg §8), so contention was baked into the basis and then charged again to a quiet box. **Calibration lesson: record the load average beside any per-iteration cost basis, and state the load the basis is being re-applied at.** | `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` §6, landed at `b8fe7eea`; pre-registration frozen at `99f939ee` |
| 2026-08-23 | cfd | F7a R0 literature diagnostic (comparator front-definition recovery — executed, no solver) | **0 core-min**, the item's own registered price (spec §7.1 quoting prereg §5 row R0, "priced at **0** core-min"); $0 derived | **0 solver core-min** — no solver, no mesh generation, no new field (spec §7: "**Cost: 0 core-min.**"); literature retrieval plus a reader over already-written, git-tracked fields | = gross, 0 core-min (no run row exists, so the 3600-s stall rule has nothing to match) | **exact (0/0) — as predicted, zero-compute** | None — no gap to attribute, and no waste | `verification/campaign/F7a_REGATE_SPEC.md` §7, landed at `3b9bcf31` |
| 2026-08-23 | closure | FS5/D476 clip-repair instrument amendment (A1/A2/A4 PASS, A3 GATE FAIL referred to verification; instrument not relied on until that audit returns) | 2–6 core-min registered estimate, cap 30 core-min (0.5 core-h) | ~10–12 core-min = ≤ $0.0103 derived (73.44 s build wall + 105.81 audit CPU-s measured by `/usr/bin/time`; the gate-grading/triage remainder estimated from the one measured ~3x CPU-to-wall ratio, stated not-measured in the record) | 3.0 core-min = $0.0026 derived (record's own cleaned definition: registered scope only — one regeneration + one audit; no stall-rule rows, zero solver) | 0.75x cleaned/predicted (against the 4 core-min midpoint; inside the 2–6 band). Gross/predicted 2.5–3x | misprediction of scope: the estimate priced regeneration + audit but not the gate grading, the A1 refusal proof and the A3 triage that the registration itself required; **zero waste, zero contention** | `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`, prereg frozen `bf4956bc`, implemented `7e973ba8` |
