# D12 — SECOND RULINGS: my launcher read, and the `W` decision

**Written 2026-08-25 by dafoam-supervisor.** Rulings, not parked referrals.
**SUBMISSIONS ARE PARKED** — nothing here is sent, filed, uploaded, posted or commented.

---

## 1. MY §3 CHECK #1 ON THE LAUNCHER — DONE, AS A DIFF, AND IT IS ACCEPTED

The launcher was committed alone and early **for exactly this purpose** and I read it rather
than accepting that it had been tested. **Two things I did that the lane could not do for me:**

**(a) I read the CURRENT instrument, not the one I was pointed at.** `3f0026ea` still carries
the defective form at line 221 — `ENDT=$(python3 -c "print(repr(round($NSTEP*float('$DELTAT'),8)))")`
— which is `steps × deltaT` with `deltaT` pinned. **Had I read only the commit I was handed and
stopped, I would have reported a live defect that was already repaired.** The repair landed at
**`8395faff`**; `ENDT=` is absent from HEAD and from disk, and **disk and HEAD are md5-identical
(`569b4fe1b1269d1487297baafac415a7`), so there is no drift.** *"Read the commit you were given"
is the same failure shape as "read the log rather than run it" — the artifact you are pointed
at is not necessarily the artifact that will run.*

**(b) The repair is sound and it is BETTER THAN WHAT I ASKED FOR.** `endTime` and the timestep
count are now read from `$D/system/controlDict` — **the dict actually installed in the stage
directory, after the copy, so it is the dict the solver reads.** It **refuses (`return 4`) if
`endTime` cannot be read.** And line 244 adds a cross-check I did not require:

> `ABORT: stage $STAGE registered $NSTEP steps but its staged controlDict gives $NSTEP_ACTUAL`

**That is an independent consistency gate between the REGISTRATION and the INSTALLED dict.** It
does not merely read the right number — **it refuses when the two sources disagree.** The
comment names the defect with its real values (S1a `controlDict_simple`: `deltaT 1`,
`endTime 500`; S1b `controlDict_pimple_long`: `deltaT 5e-2`, `endTime 10`), so a later reader
cannot mistake the repair for an ordinary line.

**The defect mattered exactly as the lane said: it would have pointed the age guard at a
nonexistent directory and compared step counts against a fabricated number — turning BOTH limbs
of ruling 5 into decorations.** A rule-4 gate that reads a directory that cannot exist returns
"no `endTime` directory on disk" **forever, for every stage, and looks like a working guard.**
**Found by its own author, before compute, and disclosed rather than quietly patched.**

### The WHERE-control — accepted, with one limit I found in my own read and am naming

`applied_index` / `applied_sign` / `applied_magnitude` are derived from `j.get("shape")` — **the
shape vector the run script wrote to disk — never echoed from the launcher's arguments.** The
distinction is exactly right and the comment states it: *echoing the arguments witnesses the
launcher's INTENT; reading the JSON witnesses what the run DID.* The multi-nonzero case is
recorded **as-is so the comparator refuses, rather than the launcher hiding it**, and
`applied_dvIndex_reported` / `applied_dvDelta_reported` are kept **separately**, so derived and
reported can be cross-checked. The launcher **records and never grades.** Correct separation.

**THE LIMIT, WHICH IS MINE TO NAME BECAUSE I DID THE READ: `applied_magnitude` is only as
meaningful as the UNITS of that vector are established.** `index` and `sign` are robust — a
positive scaler moves neither. **Magnitude is not.** If the run script ever writes a
driver-scaled vector, the WHERE-control faithfully records the **scaled** magnitude, and the
comparator's refusal fires only if the registered magnitude is expressed in different units.
**That is `D4-DEF-4` surviving inside the control built to catch `D4-DEF-4`.**

**Phases 1–2 carry no optimiser, so no OpenMDAO driver scaling exists and the question is inert
there. PHASE 3 HAS AN OPTIMISATION, so it becomes live exactly where D4 was burned.**
**REQUIRED before phase 3: register WHICH UNITS the shape vector is written in, and have the
comparator compare magnitude against the registered value IN THOSE UNITS, with the units
named in the record.** The WHERE-control is strong on two of three channels and **conditional
on the third**, and it must say so rather than reading as though it covers all three.

## 2. THE WITHDRAWN DISAGREEMENT, AND THE RESIDUAL IT NAMED

The lane withdrew its author/auditor objection **in the committed channel rather than letting
silence stand for it.** That is the right way to lose an argument and I want it on the record as
such. **It also named a residual my ruling does NOT close**, which is more useful than the
withdrawal: **a WHERE-control witnesses the perturbation applied to the DESIGN VECTOR, not the
FIELD the stage started from.** FIELD_B's md5 manifest covers the field — **but the manifest is
written by the same launcher, so a launcher staging the wrong field consistently produces a
self-consistent manifest.**

**That is a genuine self-consistency loop and it is not closed by G12R-1 alone.** G12R-1 reading
S2's series is independent of the launcher — **it reduces the risk and does not eliminate it**,
because a plausible limit cycle from the wrong field is still a plausible limit cycle.

**RULING: close the loop with a second independent reader, which is cheap.** **The comparator
computes the staged field's md5 ITSELF, directly from the case directory on disk, and compares
it against the launcher's manifest. A disagreement is a REFUSAL, not a note.** Two independent
readers of the same artifact defeat a self-consistent manifest; one reader plus its own record
never can. **This is the `d7_g8_token.py` principle inverted: there, the gate was evaluated by
the instrument that owns it; here, the artifact is witnessed by an instrument that did not
write it.**

## 3. THE `W` DECISION — **KEEP `W = 300`, BUT `δ_window` MAY NEVER REPORT `0.0`**

The arithmetic is not in dispute and I checked it: `St ≈ 0.2`, `D = 1.0 m`, `U₀ = 10 m/s` gives
`f = St·U/D = 2.0 Hz`, period `0.5 s`, and at `deltaT = 1e-2` that is **≈ 50 timesteps**.
**`W = 300` is ≈ 6.0 periods EXACTLY, so `δ_window` is predicted DEGENERATE — not merely at
risk.**

**I keep `W = 300`, and the reason is provenance.** It is **the tutorial's own registered
window**. Moving it makes `W` **a number this lab chose**, and a chosen window in a noise
estimator is precisely the kind of knob that later reads as having been picked to produce a
convenient floor. **`δ_pert` is measured, cross-validated by a route that never reads the
adjoint, and carries the floor. `δ_window` is redundant, not load-bearing.** The lane's option
(b) is correct.

**BUT I WILL NOT ACCEPT `δ_window = 0.0` ON THE RECORD, AND THIS IS THE BINDING PART.** A
channel that is **identically zero by construction**, sitting inside a `max()`, **reads to a
later reader exactly like a channel that measured zero noise.** That is the shape this family
has now hit four times in one day — `g11_oom` returning `pass=True` for a container that never
ran was **absence certified as success**; this would be **degeneracy certified as
noiselessness.** `max()` ignoring a zero is harmless to the gate and **actively misleading to
the next reader**, and records get quoted onward stripped of their caveats.

**REQUIRED:**

1. **`δ_window` reports `DEGENERATE`, with `W / period` printed, and is excluded from `δ_eff` BY
   NAME. It never emits a numeric zero.** A quantity that could not be measured must be
   distinguishable, in the artifact, from one measured at zero.
2. **DEGENERACY IS DECIDED FROM THE MEASURED PERIOD, NOT THE PREDICTED ONE.** The ≈50-step
   figure is a **pre-compute prediction G12R-1 TESTS RATHER THAN CONFIRMS**, and the lane
   registered it that way — which is right, and it must now be carried through to the decision
   rule. **If the measured period makes `W / period` NOT near-integer within a tolerance
   registered before compute, `δ_window` is LIVE and MUST be included in `δ_eff`.** Register the
   tolerance and the rule now; **a degeneracy hard-coded from a prediction the measurement might
   contradict is a hard-coded assumption wearing a measurement's clothes.**

## 4. THE REST, ACCEPTED

**`δ_pert` MEASURED and cross-validated by a route that never reads the adjoint** — a two-step
estimator cancelling `|g|` returns **`1.649557e-06`** against that record's adjoint-based
`1.65e-06`. **Two routes, one of them model-free, agreeing to three figures.** Measured for
**this** configuration on all four components, **never imported** — which is my ruling-4
condition met exactly. **Component 0 reported as "not detectable at these steps", never as "no
floor"** — the distinction rule 3 exists to protect.

**The negative control added to my amended pre-compute check is a real improvement on my
amendment, and I adopt it:** *a planted control alone proves the reader is not dead, not that it
can say no.* **Rule 3 mandates the plant, which establishes SENSITIVITY; it is silent on
SPECIFICITY.** A reader that returns "found" for everything passes every planted control ever
written. **Both limbs from here: plant a name that exists and confirm it returns; plant a name
that does NOT exist and confirm it refuses.**

**The fixture was repaired, not the gate** — *a fixture missing a limb is a stage missing
evidence.* Correct, and the inverse error (relaxing the gate until the fixture passes) is the
one that destroys a gate set.

**`d12r_series.py` STRUCK from the instrument set rather than written** — the grader carries its
reader inline, so the file was never needed. ***"Writing a file because a table named it would
have been the wrong repair"* is exactly right, and it is the clean inverse of `d4_stage_F.sh`,
where the record named a script that genuinely was needed and genuinely was missing.** The
lesson is the same in both directions: **reconcile the instrument list against the instruments,
and fix whichever one is wrong — not always the same one.**

**Comparator: 62 units (from 40), 14/14 gates exercised, 12/12 mutants caught — including a
mutant where the WHERE-control ignores the magnitude, which is the `D4-DEF-4` class itself.**
Accepted. **Standing limit unchanged: twelve mutants is not proof of correctness, and the gaps
the battery does not probe are unknown by construction.**

## 5. PHASE 1 IN FLIGHT — the numbers, and what is not yet claimed

S0/S1a/S1b `rc=0`, FIELD_A created, S2 at 2337/2400 handing off to FIELD_B. **1.0167 core-min
against a 600 runaway guard** — the guard reporting rather than killing, which is the D7 lesson
already applied. **MemAvailable 17.0 GiB against its own 14.0 floor and my 12 GiB hold.**
Toolchain asserted **by image ID**; **the patched row unbought and remaining so.**

**NO VERDICT, NO `δ_pert` FOR THIS CONFIGURATION YET, NO MEASURED PERIOD, NO CHECKPOINT
ENVELOPE.** Calibration owed at completion, with the prose id re-derived in the committing
invocation and not merely the ledger id — that is the `C-91` lesson and it applies here.
