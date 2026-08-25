# F12 — ADMISSION GATE B: RULING

**Ruled by the cfd supervisor personally, 2026-08-25. `[lab-attributed]` under Sanaa's
desk-item disposal rule of this date: referred with recommendation and reasoning,
ADOPTED unless she rules otherwise within one day. Overrulable.**

Evidence: `verification/runs/F12_runs/gateB_probe_2026-08-25/RESULTS_GATE_B_PROBE.md`
(committed at HEAD, blob `414470b6`, hash-verified against disk before this ruling).

---

## 0. THE GATE IS NOT TOUCHED

Gate B reads, and continues to read, exactly as frozen:

> **Admission gate B, convergence.** The solver must print its own convergence
> statement. A small-looking residual is not a substitute (LESSONS L-14, L-15).
> A run that does not converge is not a result and is not graded.

`F12_PREREGISTRATION.md:54-56`. **No threshold, band, cap or label moves here.**
F12 rung 1 has fired, so §2d is live and gates are closed. The probe was correct to
record that loosening `residualControl` in the registered case is a threshold change
and is not available post-freeze. **Nothing in this ruling loosens it.**

Verified by me in the fired case's own `system/fvSolution`:
`p 1e-06; U 1e-06; "(k|omega|e)" 1e-06;`. The 1e-6 figure is measured, not recalled.

## 1. THE MECHANISM OBJECTION IS DISMISSED

The hypothesis that gate B is **unsatisfiable by `rhoSimpleFoam` on this box** is
refuted by direct counterfactual. Probe arm 1 — F12's own `thermophysicalProperties`,
`turbulenceProperties`, `fvSchemes` and `fvSolution`, with **only the three
`residualControl` numbers** changed, on a 400-cell box — converged in 14 iterations,
printed `SIMPLE solution converged in 14 iterations`, printed `End`, exited `rc = 0`.

That eliminates four sub-hypotheses at once: the key names, the `"(k|omega|e)"` regex,
the `SIMPLE` sub-dictionary structure, and `hConstThermo`/`sensibleInternalEnergy` with
energy field `e`. **The mechanism fires. No relief is available on mechanism grounds.**

**The generalisation from seven `rhoSimpleFoam` logs that none had ever printed the
statement did not support "it cannot."** Zero-of-seven was a property of those seven
runs. This probe is the eighth and it prints. Recorded because the inference, not the
observation, was the defect.

## 2. A CORRECTION TO THE PROBE, MADE BY ME AND AGAINST IT

The probe attributes the first-solve/last-solve divergence to **F2's
`nNonOrthogonalCorrectors 2`**, giving three `p` solves per iteration. That is right
for F2. **It does not transfer to F12 unexamined, and I checked rather than assumed:
F12's fired rung-1 case runs `nNonOrthogonalCorrectors 1`** — two `p` solves per
iteration, not three.

**The mechanism survives; the multiplicity does not.** `simpleControl` reads the
**first** `p` solve of the iteration; a tail-read of the log returns the **last
corrector's** value. With one corrector the two readings still differ, and still only
for `p` — every other channel is solved once, so first and last coincide. The size of
the gap is F2's, not F12's, and **no F12 number may be quoted from F2's 130x spread.**

## 3. THE BINDING INSTRUMENT CONDITION — this is the load-bearing part

> **Every residual reading on F12, by any monitor, sampler, grader or human, is the
> FIRST solve of the iteration. A tail-read of `p` is reading a number the solver's
> own criterion never sees, and is an instrument defect wherever it appears.**

The earlier report that *"every single channel sat one to two orders of magnitude
below its own threshold"* is **struck for `p`** and stands for the others. F2 never
satisfied its own `residualControl`: **iterations out of 2,000 where every channel's
first solve sat below 1e-4 = ZERO.** It ran to `endTime`. There is no anomaly and no
mechanism defect — there was a reading defect, in this lab's own reader.

This condition is general, not F12's. It goes to `docs/standards/MONITOR_STANDARD.md`
as a lab-wide reading rule: **a residual criterion is read where the solver reads it.**

## 4. THE REAL RISK, RESTATED SHARPLY AND NOT SOFTENED

`p` is the hard channel and on the closest analogue it is **not converging**. F2's
first-solve `p` by window: 2.157e-02 (0-100), 1.319e-03 (400-500), 6.386e-04
(900-1000), **1.812e-04 (1400-1500, the floor)**, **3.839e-04 (1900-2000, risen)**.
Median over 1500-2000 is **1.177x** the median over 1000-1500.

**It descended, bottomed near 1.8e-4, and drifted back up. More iterations do not
reach it.** F12 asks **1e-6**. That is ~180x below where the analogue floored on the
looser 1e-4 comparison and ~180,000x below the floor in absolute terms, on a channel
that has stopped descending. **On this evidence gate B at 1e-6 is unlikely to be met
by any F12 run within 6,000 iterations, and that is independent of any relaxation
change.** It is a convergence question. The mechanism question is closed.

## 5. THE SCHEDULING RULING

Under standing rule 5 clause (1), **a level not iteratively converged is `NOT A RESULT`
whatever its value** — clause 1 fires *before* the triple is read. So a gate-B failure
at every level delivers `NOT A RESULT` rows and **no triple, no observed order, no
GCI**. Firing rungs 2-5 blind would therefore spend the ladder's full cap to buy six
labels this evidence already predicts.

**But a predicted `GATE FAIL` is never a reason to withhold a frozen, armed gate.**
Declining to run because the answer is expected to be no is precisely the
outcome-fitting that pre-registration exists to prevent. The question is not *may we
fire* but *what does firing buy*.

**RULING:**

1. **Rung 2 (medium) FIRES.** It is the cheapest level whose gate-B outcome is
   genuinely unknown — F2 is an *analogue*, not F12's mesh, and F12's attempt-2 ladder
   is a different mesh family that passed admission gate A at 51.12 / 51.53 / 51.93
   degrees with zero faces over 70. Rung 2 also supplies **the measurement this team
   has owed itself all session: where first-solve `p` floors on a STABLE run.** No arm
   so far has been stable, so the quantity is unmeasured. Rung 2 measures it.

2. **Rungs 3-5 DO NOT FIRE on rung 2's authority.** They fire if rung 2's first-solve
   `p` descends through 1e-6, or through a floor low enough that the ladder is live.

3. **If rung 2's `p` floors above 1e-6**, the ladder's remaining rungs are predicted
   `NOT A RESULT`, the measurement is in hand, and **the spend decision goes to Sanaa
   as a cost question — not as a gate question.** The gate would be settled; only the
   value of confirming it would be open.

4. **The grading path is pinned by hash before rung 2 starts**, per standing rule 2:
   the frozen file must be shown to BE the file that ran. Any byte difference stops
   the rung.

## 6. WHAT THIS RULING DOES NOT DO

It does not alter gate A, gate B, gates 1-4, any threshold (0.08, 0.04, 0.020 chord,
5 %, 20 %), any cap or any label. It does not regrade rung 1, which stands
`NOT A RESULT`. It does not reopen the topology or the mesh instrument. It is a
**scheduling and reading** ruling and nothing wider — standing rule 9.
