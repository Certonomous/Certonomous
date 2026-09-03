# CHECK-1 TOKEN — F28G. THE SUPERVISOR'S OWN RECORD, QUOTED VERBATIM.

**`SUPERVISION_CHARTER.md` §3 check 1 may not be delegated.** This file is the
`cfd-supervisor`'s record of their **personal** read, reproduced word for word by the lane
that consumed it. **The lane did not compose it and did not summarise it.** Where this file
and any lane's paraphrase of it differ, this file is the token and the paraphrase is wrong.

`run_f28.sh` requires `--check1-token` as a non-empty string. The string passed at launch is
an identifier that **cites this file**; the file is the token's content. A token whose basis
is not recorded is a rubber stamp.

---

## THE TOKEN — the supervisor's words, verbatim

> CHECK-1 TOKEN, F28G. Issued by cfd-supervisor, 2026-09-03, from personal reads at source.
> Two graders, two different strengths, and they are NOT interchangeable:
>
> analyse_f28g.py -- STRONG. Read personally and EXECUTED. Verified: zero bare assert
> statements; --selftest returns limbs_failed 0, pass true, rc 0 under python3 -O, which is
> the only run that proves guards survive optimisation; Roache gating implemented in rule 5's
> order and one permitted direction, with assert_one_way proving the one-wayness on synthetic
> rows rather than in prose; GCI at Fs=1.25 with a separate guard refusing a GCI on a
> non-monotone triple; aspect ratio provably never gates, an absurd 1e9 planted and the row
> still not rejected on it alone; rule 1's verdict vocabulary exact; one plant per reader that
> produces a number, each read back from disk, each refusing if unseen.
>
> analyse_f28.py -- QUALIFIED, SOURCE-READ ONLY. Read personally, NOT EXECUTED, because THE
> FILE HAS NO --selftest ENTRY POINT: rc 2 identically with and without python3 -O, its usage
> exposing only --grade and --guard-virgin. Verified by reading: zero bare assert statements;
> refuses at exit 2 with NOT A RESULT rather than degrading; one plant per reader producing a
> graded number (PLANT_PA, PLANT_FO, PLANT_SU, PLANT_DX), with the superseded file's weaker
> plant recorded in source as a lesson; tolerance written as a function of the operand over a
> PLANT_TOL floor. NOT VERIFIED, AND MATERIAL: its plants are DECLARED, NOT EXECUTED. I have
> read that this instrument CAN be made to fail; I have not seen it fail and cannot make it,
> because there is no entry point. T_total flows through this file, so this qualification
> attaches to the graded quantity.
>
> f28_apex_mechanism_check.py -- NO TOKEN REQUIRED. Standalone diagnostic, not in the grading
> path.
>
> NO-UPGRADE CLAUSE: the QUALIFIED scope does not become STRONG by the passage of time, by
> byte-identity to a freeze blob, by a successful run, or by any agent's summary of this
> token. It becomes STRONG only when a --selftest entry point exists and a supervisor executes
> it under python3 -O and says so. Byte-identity to a freeze blob and somebody-looked are
> different facts.

---

## What the lane records beside it, as fact rather than as gloss

- **Both files are in F28G's grading path.** `analyse_f28g.py:206` does `import analyse_f28 as
  F28`, and calls it at `:600, :1580, :1582, :1595, :1596, :1631, :1648` — including
  `total_thrust`, `t_disk_from_source`, `t_disk_analytic`, `completion` and
  `thrust_stationarity`. **`T_total`, the graded quantity, flows through the QUALIFIED file.**
- **`f28_apex_mechanism_check.py` is imported by nothing but itself.** Population searched:
  every `*.py` in `cases/F28_DUCTED_ACTUATOR_DISK/`.
- **The owed item.** `analyse_f28.py` has no `--selftest`. Adding one changes a **frozen
  grading path**, so it is **FORWARD-ONLY and rides a successor** (Sanaa 2026-09-03 ~21:00Z).
  It is carried onto the F28G certificate as a **recorded prediction**, in these words: *"the
  parent comparator's controls are declared and unexecuted; no selftest entry point exists."*
  **It does not block.**
- **The no-upgrade clause binds this lane and every later reader**, including any future
  invocation of this record. `verification/campaign/F28G_GRID_CONVERGENCE_PREREGISTRATION.md`
  §A5.4 carries the same qualification in the registration itself.
