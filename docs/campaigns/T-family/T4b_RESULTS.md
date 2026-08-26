# T4b results — PENDING: `verification/runs/T-family/T4b_runs/T4b_IJ_f` (LIVE)

**Verdict on the rung: `PENDING`.** The frozen comparator refuses a partial triple, verbatim (rc 2, `T4b_runs/log.analyse_t4b.refused.20260826T205552Z.txt`):

```
REFUSE: no DONE.T4b_IJ_f -- the whole rung is graded or none of it is (mark_done_t4b.py decides; this comparator does not overrule it)
```

Nothing was forced. No graded number exists for this rung yet and none is quoted here.

Pre-registration `docs/campaigns/T-family/T4b_PREREGISTRATION.md` (AMENDMENT 1 at `51618879`, pre-first-compute, launcher guard re-frozen `8bd93c23`). Run tree `verification/runs/T-family/T4b_runs/`. Written by a lab lane on the heat-transfer supervisor's order `[lab-attributed]`, 2026-08-26T21:00:22Z.

## 1. Frozen instruments, hashed before use

| instrument | §11 blob | `git hash-object` on disk | match |
|---|---|---|---|
| `T4b_runs/mark_done_t4b.py` | `d5411c3f` | `d5411c3ffad8084d64729d44f908171d5abfd688` | SAME |
| `T4b_runs/analyse_t4b.py` | `69abe6e5` | `69abe6e5d11a3cea29c49faf4c51b8bb8a10c7fd` | SAME |

The comparator printed its own sha256 `06674874d025c11b…` (§11's row) and the frozen import `analyse_t4.py` `9842dbc8…` before refusing.

## 2. Completion so far — two of three

`mark_done_t4b.py T4b_IJ_c`, `T4b_IJ_m`: each `DONE`, rc 0, markers `strict rule met (physics-critical clauses 1-6)`. Disclosed: the lane's first invocation used the short names `IJ_c`/`IJ_m` and was refused — `REFUSE: 'IJ_c' is not one of the registered T4b cases: T4b_IJ_c T4b_IJ_m T4b_IJ_f` — the registered names were then used. `T4b_IJ_f` was NOT marked and NOT touched.

| level | cells | wall s (STATUS) | timeout s | core-min | POINT (§9) | ratio |
|---|---:|---:|---:|---:|---:|---:|
| T4b_IJ_c | 6 048 | 846 | 1 500 | 14.100 | 11.84 | 1.19 |
| T4b_IJ_m | 24 192 | 5 178 | 9 000 | 86.300 | 74.65 | 1.16 |
| T4b_IJ_f | 96 768 | LIVE | 51 600 | — | 429.41 | — |

Source: `T4b_runs/STATUS.T4b_IJ_{c,m}`, `DONE.T4b_IJ_{c,m}`.

## 3. `T4b_IJ_f` — live, not touched

Solver pid 336286 (`buoyantBoussinesqSimpleFoam -case …/T4b_IJ_f`, serial), read from `T4b_IJ_f/log.solve` at 2026-08-26T21:00:22Z:

```
Time=9371 ClockTime=11140s rate=0.8412 it/s remaining=36411s (10.11 h) ETA=2026-08-27T07:07Z projected_total_wall=47551s of timeout 51600 (0.922) projected_core_min=792.5 vs POINT 429.41 (1.846)
```

The projected total wall sits inside the registered 51 600 s timeout; if the rate holds, the run ends before the cap and the rung's cost lands near its POINT. No ETA is a measurement; the rate is the log's mean to now.

## 4. What remains

When `STATUS.T4b_IJ_f` appears with the in-wrapper rc: `mark_done_t4b.py T4b_IJ_f`, then `analyse_t4b.py` (its `--selftest` first), then this file is rewritten with the graded rows, and the rule-12 calibration row lands in `docs/COST_CALIBRATION.md`. No cost row is written for a rung that has not completed.
