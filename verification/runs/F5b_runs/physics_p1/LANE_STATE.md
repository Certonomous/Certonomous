# F5b Physics `physics_p1` — LANE STATE (resume record)

**STATUS: COMPLETE AND GRADED AND CLOSED OUT. Nothing further is owed on this run.**

**VERDICT: `NOT A RESULT`** — see `RESULTS.md` beside this file for the full record.
Calibration row **C-65** landed in `docs/COST_CALIBRATION.md`.

## Do NOT

- **Do not relaunch.** One run only; it has fired. The wrapper refuses if `physics_p1`
  exists (D-1).
- **Do not edit the frozen reader** `analyse_f5b_physics.py`
  (`6c6d34d02e6de925457dbfdbf75a0e004168f345`) or the frozen pre-registration body
  (`c44b9130…8177b9df`, first 85,802 bytes). **F5b HAS FIRED**; rule 6 governs and rule 2
  closed the grading path at the pre-registration commit.
- **Do not re-grade against a patched literal** to convert this verdict. The `NOT A RESULT`
  was returned by the frozen reader run unmodified and it stands (L-44, charter §8).
- **Do not re-use 39.426 core-min as an uncontended cost basis.** §8 item A-4's clean-basis
  deliverable is **NOT DELIVERED** — roughly a third of the run burned at loadavg ≥ 6
  because this lane launched F11 and F3 alongside it.

## The one-line cause, for whoever picks this up

The reader's frozen literal is `END_TIME_STR = "21.9440"` (line 120) and it looks for
`case/21.9440/`. **OpenFOAM wrote `case/21.944/`** — its float formatting strips the trailing
zero. Clause 4 (fields present) and clause 6 (age guard) both fail on that one string. All
five required fields **are** present under the real name and are newer than everything in
`case/0/`; that is recorded in `RESULTS.md` as an **observation, not a re-grade**.

**No selftest caught it** because `_synthetic_run` creates its time directory using the same
literal the reader searches for — fixture and checker share the bug, so the arrangement is
self-consistent and false.

## Carry-forward to the NEXT F5b registration — three items

1. **A real rc on disk**: `setsid bash -c 'CMD; echo $? > RC.txt; sync'`. Already applied on
   F11 and F3; both graded on a measured integer and needed no proxy.
2. **A clause-1 breaker that actually breaks the `record.json` branch** (L-320).
3. **`END_TIME_STR` must not be a hand-written literal** — derive it from what OpenFOAM
   writes, or match the time directories numerically rather than by string equality. This is
   the item that cost this run its verdict.

## Standing practice this run established

- **Sample loadavg throughout the run, not only at launch** — this run's `WATCH_LOG.txt`
  (127 samples at 15 s, each carrying `ExecutionTime` and loadavg) is what made a
  load-conditioned basis reconstructable after concurrency contaminated the average.
- **External sampler, `setsid`, PPID 1**, writing its terminal state to disk once. An
  in-agent watcher dies with the agent; one did, on this run.
