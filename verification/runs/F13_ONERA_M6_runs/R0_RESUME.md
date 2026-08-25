# F1 (ONERA M6) -- R0 RESUME RECORD

**This run does not depend on the lane that started it being alive.**

- Registration: `verification/campaign/F13_ONERA_M6_PREREGISTRATION.md`, frozen
  `2eabe5971b1c45624c189c669b69b5f17788a56e`, AMENDMENT 1 `3b88ab09`, AMENDMENT 2 `73c264c3`.
- Rung: **R0** -- build L1/L2/L3, `checkMesh` x3, grade the §5 admission checks.
- Driver: `verification/runs/F13_ONERA_M6_runs/run_r0.sh`, launched **detached under `setsid`**.
- **SERIAL, 1 RANK.** Domain decomposition is **NOT APPLICABLE** to this rung -- mesh generation
  and `checkMesh` both run single-rank. §6's partition pair enters at R1/R2/R3/R4, not here.
  Stated explicitly so an absent decomposition is not later read as an omission.
- **HARD CAP 90 core-min** (§8). Serial, so core-min == wall-min. **A breach STOPS the run** and
  writes `R0_CAP_BREACH.txt`; it does not get a new budget.
- `rc` is **measured, never proxied**: each step writes `RC_*.txt` and `sync`s; the terminal
  reader reads the file back and REFUSES a missing or non-integer value.
- Outputs: `mesh/m{1,2,4}/{log.makeMesh,log.checkMesh,RC_make.txt,RC_check.txt}`,
  `R0_ADMISSION.json`, `log.analyse_f13`, `R0_TERMINAL.md` (written ONCE, at the end).

## To resume after this lane dies

1. `pgrep -af run_r0.sh` -- if it is alive, **do not restart it**; sample `R0_ADMISSION.json`.
2. If it is dead and `R0_ADMISSION.json` is absent, re-run
   `setsid bash -c '/home/ubuntu/Certonomous/verification/runs/F13_ONERA_M6_runs/run_r0.sh > .../log.r0 2>&1; echo $? > .../RC_r0.txt; sync' &`
   after `rm -rf mesh/m1 mesh/m2 mesh/m4` -- the generator refuses to write into a populated case.
3. **Admission at all three levels or it is a NAMED BLOCKER, not a launch.** No solver starts on a
   level that fails §5 admission, and an ABSENT `checkMesh` log reads `ABSENT`, never clean.
