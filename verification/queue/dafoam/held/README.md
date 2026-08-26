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
