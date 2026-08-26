# held/ — entries the runner MUST NOT see

`scripts/queue_runner.py` enumerates only top-level `*.json` in the team directory
(`list_entries`, `d.glob("*.json")`), so this subdirectory is outside its drop path.

**Supervisor ruling 2026-08-26 `[lab-attributed]`:** no dafoam entry goes to the drop path
until its launcher carries G-ROOT.5 (refuse if a running container carries the item
prefix+arm, or a live driver pid holds the run root) AND the entry names a precondition
artifact that must exist on disk. Three entries were launched on drop by the daemon
before that ruling (runner.log 16:10:17Z, 16:11:22Z, 16:17:27Z; each aborted rc=1 on its
absent `step_plan*.json`, zero stages) and are held here with the runner's own
`_launch` record intact: `D12R_phase3.json`, `D12R_phase4.json`, `W2R_phase2.json`.

Held is not cancelled. An entry leaves this directory only by a supervisor's dispatch,
after the precondition artifact exists.

**Move rule (supervisor, 2026-08-26):** every entry here names a `precondition_artifact`; it moves to the drop path the moment the runner evaluates preconditions (cfd's repair of `scripts/queue_runner.py`), not before.

**SUPERSEDED (lane Q2, 2026-08-26 ~17:15Z, `[lab-attributed]`, permission `bc0e687e`):** the runner still evaluates no precondition, so the route taken was a launch argv that evaluates its own — `cases/dafoam/_common/dafoam_wait_then_launch.sh` (W2R `ADDENDUM 2`, commit `331d1a2d`). `W2R_phase2.json` here is SUPERSEDED by the drop-path entry `W2R_phase2_wait.json` (launched by the runner 17:15:37Z, now in `launched/`), with `W2R_phase3_wait.json` and `W2R_phase4_wait.json` beside it and the comparator plan steps `W2R_plan*_wait.json` (`ADDENDUM 3`). The three files here stay as the historical record of the 16:10–16:17Z premature fires (their `_launch` blocks are the runner's own). **`D12R_phase3.json` and `D12R_phase4.json` were NOT re-filed:** `cases/dafoam/curriculum_D12R` (`f9c8b9c8`) is the item the supervisor's own ruling re-registered as D12R2 (`e6580910`; `docs/COST_CALIBRATION.md` C-107 — phase 1 `NOT A RESULT`, 63.95 core-min booked as waste, its frozen comparator `d12x_grade.py` refuses that run at stage 1 of 32), so its `step_plan*.json` can never be written by the registered grading path and the entries could only ever BLOCK at their bound. The live D12 line's later phases are W2R's, and those are what was filed. Reported to the supervisor for a ruling; held is not cancelled.

**SUPERSEDED (lane Q-A, 2026-08-26 ~20:59Z, `[lab-attributed]`, permission `bc0e687e`):** `D6_chain.json` here (prereg `a1283284`, 1,694.7 core-min, 20g per arm, floor 24.0, withdrawn 17:45:47Z on D5's G-ROOT.3 refusal) is SUPERSEDED by the drop-path entry **`D6_chain_wait.json`** — the same `d6_chain_driver.sh O_mp ACC_mp F_mp REF_off` argv behind `cases/dafoam/_common/dafoam_wait_then_launch.sh`, precondition `<D5 run root>/CHAIN_DONE` (D5 Addendum 3), bound 86,400 s, prefix `d6_` — registered by D6 ADDENDUM 2, because 20g cannot co-run with D5 (12g) + D4-SHIPPED (12g) under the 30.6 GiB aggregate rule and a bare entry would BLOCK at its 4 h bound before D5 ends. This file stays as the record; held is not cancelled.
