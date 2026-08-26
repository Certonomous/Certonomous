# `D7F-DEF-1` — MY OWN REPAIR IS WRONG ABOUT ITS PRODUCER, AND ARM `P1` FOUND IT IN ELEVEN SECONDS

**2026-08-26. dafoam `lab-lane`. This is a finding against work I did tonight, recorded before any
regrade and before any repair, because `PREREGISTRATION.md` §R4's inheritance registered exactly
this: the grader's first invocation on real arm artifacts is an event to watch, not a formality.**

**STATUS: REPORTED, NOT REPAIRED. The grading path is CLOSED — compute has occurred.** See §4.

---

## 1. What fired

`D7R-GRADER-DEF-7` was that `g1_completion`'s docstring named a terminal-statement clause and the
code carried none. I repaired it in `d7f_grade.py`, drove it in both directions in the selftest
(marker removed → fails; `End` removed → fails; log absent → fails; restored → passes), and
`scripts/check_docstring_clauses.py` reported **0 alibis**.

**Then arm `P1` ran, and the clause is wrong about the producer it was pointed at.**

| limb of the clause I added | what I assumed | what is MEASURED |
|---|---|---|
| an `End` line in the arm's own log | every arm's producer prints one | **`P1`'s log carries ZERO `End` lines** — `grep -c '^End'` is `0` on `P1_20260826T035944Z_3171735.log`, and `0` on **both** of D7R's `P1` logs too. `P1` runs `decomposePar`, whose output is redirected into `d7_decomp_A.log` / `d7_decomp_B.log` **inside the work directory**, so the arm log never sees it. **Arm `X` will be the same: it runs Python and no OpenFOAM solve at all** |
| a `.log.ok.<stamp>` marker as the completion witness | the launcher writes it on `rc = 0` | **it does not.** `d7f_run_arm.sh:585` is `test -s "$LOG" && touch "$LOG.ok.${STAMP}"` — **the marker means THE LOG IS NON-EMPTY, not that the arm succeeded.** A crashed arm that printed one line gets a marker |

## 2. What it would have cost, stated as a number

`g1_completion` runs the terminal loop over **every** arm in `arms_expected`, and `G1` is a **hard
gate** in `map_verdict`. A full D7F grade over `P1,X,ACC,F-S,F-P` would therefore have returned
**`NOT A RESULT` for the whole item** on the strength of a healthy `P1` — after `F-S` and `F-P` had
spent their registered **970.0 core-min**.

**And the other limb fails the other way.** Because the `.ok` marker is a non-emptiness test, the
clause would have **PASSED** an arm that crashed after printing a banner. **One limb is a false
alarm and the other is a false clean. They are not the same error and neither cancels the other.**

## 3. The class, and it is a third one — not the one L-335 names

**L-335** says a comment that names a clause is the implementation's alibi, and its executable check
closes **ABSENT**. Its recorded blind spot is **VACUOUS** — a clause that is present and cannot fire.

> **THIS IS NEITHER. The clause is PRESENT, it is NOT VACUOUS — it fires, and I drove it firing —
> AND IT IS POINTED AT THE WRONG EVIDENCE.** `check_docstring_clauses.py` reports it `OK` and is
> right to: an implementation is there. **A check can be present, live, demonstrated, and still be
> asking the wrong file the wrong question.**

**The selftest could not have caught it, and the reason is the instructive part: I WROTE THE
FIXTURE.** My fixture log contained `Time = 1 / ExecutionTime = 1 s / End` because I put `End` in
it. **A fixture written by the same hand that wrote the clause encodes the same assumption twice and
tests it zero times.** The real producer was eleven seconds away and I did not ask it.

**This is the night's pattern in a third instrument, and this time the instrument is mine:** the
`G-COLD` guard was correctly written and wrongly placed; `g_completion`'s docstring was correctly
worded and never coded; **this clause is correctly coded and wrongly aimed.**

## 4. WHY IT IS NOT REPAIRED IN THIS COMMIT

**Compute has occurred.** Arm `P1` completed at `20260826T035944Z_3171735`, `rc = 0`, `wall_s = 11`,
**`core_min = 0.733`** against a registered prediction of `0.75` — **ratio 0.977**. Its row is in
`/home/ubuntu/certonomous-runs/CURRICULUM-D7F-a3-m6-fd/ledger.txt`.

**`CLAUDE.md` rule 2: after first compute the gates are closed.** `G1` is a gate, the terminal clause
is part of it, and changing it now is a change to the grading path after compute. **The route that
exists is `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception, and invoking it is the
SUPERVISOR'S call, not a lane's** — D4's own `D4-DEF-4` repair went through a written supervisor
ruling for precisely this reason, and this lane will not repair an instrument on the authority of
the verdict that instrument produces.

**A lane that quietly fixed this would have destroyed the only evidence that the freeze discipline
works.**

## 5. What a repair would have to establish, for whoever writes it

Registered here so the repair is not designed by whoever happens to be tired:

1. **The clause must be PER-ARM, because the producers differ**, and the arm→producer map must be
   read out of the launcher rather than assumed: `P1` = `decomposePar` (no `End` in the arm log);
   `X` = Python, no OpenFOAM solve at all; `ACC`, `F-S`, `F-P` = `mpirun` DAFoam primals, which do
   print `End`.
2. **The `.log.ok` marker must be made a REAL success witness or must stop being cited as one.**
   `test -s "$LOG"` is a non-emptiness test. Either the launcher writes the marker on `rc = 0`, or
   the clause stops treating it as terminal evidence. **Both are changes; neither is free.**
3. **Every limb must be driven against a REAL arm log, never a fixture the repairer wrote** — that
   is the whole content of this finding.
4. **A negative control is required**: an arm whose producer crashed after printing output must
   FAIL. Without it the repaired clause is the false-clean limb again under a new name.

**Nothing here is sent, filed or reported outside this box** (`CLAUDE.md` rule 7).
