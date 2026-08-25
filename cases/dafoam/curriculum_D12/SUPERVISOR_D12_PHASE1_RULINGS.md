# D12 PHASE 1 — RULINGS: re-register, and a correction to MY OWN control

**Written 2026-08-25 by dafoam-supervisor.** Rulings, not parked referrals. **SUBMISSIONS PARKED.**
All four defects are in **this lab's own instruments** — no upstream report arises.

---

## 1. THE ARREST WAS RIGHT, AND ITS GROUND IS THE CORRECT READING OF SANAA'S DIRECTIVE

The lane stopped after 23 stages rather than let ~25 more fail identically. Its ground:
***cost being lifted is not a licence to let a known-broken run continue — that is not rigor,
it is negligence.***

**I endorse that without qualification and I want it standing for this family.** Sanaa lifted
cost so that **rigor would not be traded for money**. She did not license waste. A lane that
had run the remaining stages "because compute is free" would have burned real core-minutes
producing 25 more copies of a known failure and called it thoroughness. **Waste 2.7165
core-min = 22.6 %, named separately and not absorbed.**

**And no actual/predicted ratio was quoted** — *"a ratio against an arrested phase would be a
fabrication wearing a decimal point."* Correct, and consistent with the `C-84` precedent where
arm F's 1.0/53.0 was withheld. **A ratio compares work done against work predicted; an
arrested phase delivered none.**

## 2. THE HEADLINE IS NOT A DEFECT — MY SECOND RULING PAID FOR ITSELF ON ITS FIRST RUN

Registered **before compute**: shedding period ≈ 50 timesteps, `St ≈ 0.2`, `W/period ≈ 6.0` →
**degenerate**. **Measured: period 18.9955 timesteps, `St = 0.5264`, `W/period = 15.79` — NOT
degenerate, and `δ_window` is LIVE at `1.274958e-03`.** The prediction came in at **0.38× the
measurement** and **the frozen code caught it**. G12R-1 `PASS`: 221 sign changes, peak-to-peak
19.4 % of `|mean|`, mean `CD` 0.65635 — **a limit cycle is established.**

**The branch was decided from the MEASURED period, which is exactly what my second ruling
required.** Had degeneracy been hard-coded from the prediction, **a real noise term of
`1.27e-03` would have been silently excluded from `δ_eff`** — *an assumption wearing a
measurement's clothes*, in the precise sense I registered.

**Credit is shared and I will not take more of it than is mine.** The lane registered the
≈50-step figure as a **prediction G12R-1 tests rather than confirms** — that was its choice,
before I ruled. My ruling required the *decision* to come from the measurement. **Either half
alone would have failed: a prediction registered but not binding on the branch, or a branch
rule with no prediction to refute.**

**AND THE CAVEAT IS CARRIED, WHICH MATTERS AS MUCH AS THE NUMBER.** The estimator is
mean-crossing, so **18.9955 is a LOWER bound on the period and 0.5264 an UPPER bound on `St`.**
**I sharpen it further: `St = 0.5264` is roughly 2.6× the accepted `≈0.2` for a circular
cylinder at moderate Re. On a 2,450-cell 2D URANS mesh that is far more likely a RESOLUTION
ARTIFACT than a discovery, and it must never be quoted as a Strouhal measurement.** The
re-registration says so in its own words.

**A consequence that is strategy, not bookkeeping:** with `δ_window` live, direction-only
arithmetic gives `h_min ≈ 1.10` against `h_max = 0.05` — **~22× over, so the no-admissible-step
branch would fire.** The `|g|` there is the probe's and S5 never ran, so **this is direction,
not a result.** But it points the same way D12-F′ did — *on this window an FD verification
could not have beaten ~5 % even in principle.* **D12 may be a case where the FD bright line
cannot be crossed AT ALL, and that would be a genuine finding about the method-case pair, not
a failure of either.** Register it as a possible outcome rather than discovering it later.

## 3. DEFECT 1 — AND IT REFUTES A CONTROL I MYSELF ORDERED

`FIELD_B` cannot start a solve: `cannot find file .../0/nut`. **Verified by me directly:
`FIELD_A` holds ELEVEN fields — `U U_0 betaFINuTilda fvSource meshPhi nuTilda nuTilda_0 nut p
p_0 phi` — and `FIELD_B` holds FOUR: `U nuTilda p phi`. No `nut`.** The launcher hashed
whatever was there and re-asserted that manifest **faithfully before all 23 stages, passing
every time. Internally perfect, externally false.**

**THE LANE OWNS IT PRECISELY AND SO DO I:** it named this residual in `3f0026ea` — *"a launcher
staging the wrong field consistently produces a self-consistent manifest"* — and then shipped
an instrument that fell into it. **And MY ORDERED REPAIR — the comparator computing the field
md5 itself — WOULD NOT HAVE CAUGHT IT EITHER. Both readers agree on the same four files.**

**THE LESSON IS MINE AND IT IS THE MOST GENERAL THING IN THIS REPORT: INDEPENDENCE OF READERS
IS NOT INDEPENDENCE OF QUESTIONS.** Two independent readers defeat a self-consistent manifest
**about the same question**; they are powerless against a **shared wrong question**. My md5
control asks *"is this the file we staged?"* — **it never asks "is this enough to start a
solve?"** Adding a second reader to a wrong question buys nothing but confidence.

**RULING — and it is NOT a §2d.1 repair, which the lane correctly identified: THE PIPELINE IS
WRONG, NOT THE LAUNCHER.** A per-step write emits what `writeControl` selects — a **diagnostic
subset**. **A restart field must carry the full state a solve needs, and `FIELD_B` must
therefore NOT come from a per-step write.** S2 must produce a **complete** write at its end, or
`FIELD_B` must be taken from a dedicated complete write. **That is a design change and it goes
into the re-registration, not an addendum.**

**The control that actually catches this class is a COMPLETENESS CHECK AGAINST WHAT A SOLVE
NEEDS** — enumerate the required fields from the case's own complete write (`FIELD_A`'s
manifest is the natural reference) and **refuse** on any missing. **Neither of us specified it.
It is required now.**

## 4. DEFECT 2 — THE AGE GUARD CANNOT ARM. §2d.1 REPAIR **AUTHORISED**.

`writeCompression on` → fields are `U.gz`, so the datum `0/U` **never exists** and the guard
returns `None` on every stage after S1a. **Conditions: (1) demonstrable — `None` on every
stage, not a preference; (2) established BY RUNNING, which grades nothing and has no
direction; (3) and (4) hygiene, required.** Derive the datum from the file that exists
(`0/U` or `0/U.gz`), or read `writeCompression` from the controlDict — **never from a typed
assumption.**

**IT FAILED SAFE, AND THAT DISTINCTION IS WORTH MORE THAN THE REPAIR.** `None` was a
**refusal**. Compare `D7-GRADER-DEF-3`, where `g11_oom` returned `pass=True` for a container
that never ran. **A guard that cannot see its datum and says `None` is a guard in name only.
A guard that cannot see its datum and says `pass` is a hazard.** Same blindness, opposite
failure direction, and only one of them can certify a wrong result.

## 5. DEFECT 3 — THE FROZEN DOCUMENT SPECIFIES A QUANTITY THAT COULD NEVER HAVE PASSED

`obj_from_log` reads **`CL`, not `CD`** — and **§5 of the frozen pre-registration specifies it**,
freezing *"the LAST `average:` value"* while the solver prints `average:` on **both** lines.
**I verified the frozen text myself at line 156.** The correct `CD:` reading matches the JSON
`obj` **to the last digit**; the frozen reading is off by **93.9 %** against a **1e-12**
tolerance. **A mis-specified gate quantity that could never have passed — the VMFL059 class,
and the second instance in this lab in one day.**

**RULING: THIS IS NOT A §2d.1 REPAIR. The defect is in the FROZEN DOCUMENT, not in an
instrument, and a pre-registration that specifies a quantity which cannot produce the
registered comparison is not repairable into a correct one by addendum** — the same conclusion
I reached for D7's cap. §2d.1's exception was cut for a **comparator script**; stretching it to
rewrite a pre-registration's own specification of *what to measure* would hollow out rule 2.
**D12-proper is RE-REGISTERED.** Phase 1 is already `NOT A RESULT` with **zero graded output**
and the run root is preserved byte-for-byte, so **nothing is lost but a document.**

**The comparator is unaffected and its control is a model of the kind I want:** its anchored
`^CD:` reader returned **2,400 samples with zero negatives**, while `CL` swings negative half
the time. **`CD` is positive-definite for this flow and `CL` oscillates about zero, so "zero
negatives in 2,400" is a STRUCTURAL WITNESS that the reader is reading `CD` — a positive
demonstration of zero contamination, not an absence of evidence.** That is what a control
should look like.

## 6. DEFECT 4 — `Time =` IS NOT A STEP PROXY FOR THE STEADY STAGE. §2d.1 REPAIR **AUTHORISED**.

Six `Time =` lines against 500 registered steps, with **the registered and staged controlDicts
agreeing with each other and both disagreeing with the log.** **That agreement is what makes
this an instrument defect rather than a registration defect** — the two sources that specify
the run concur; only the proxy that reads it is wrong. Repair: make the step proxy
**stage-type aware**, and **refuse rather than silently compare incomparable counts.** A
completion limb that compares a steady solver's outer iterations against an unsteady step count
is not a weak check — **it is a check of the wrong quantity**, which is defect 3's shape in a
different limb.

## 7. THE COMBINED RULING — ONE RE-REGISTRATION, NOT FOUR PATCHES

Defects 1 and 3 require re-cutting the document regardless. **Repairing instruments under
§2d.1 that belong to a document being replaced is bookkeeping for its own sake.**

**RULE: re-register D12-proper as a NEW ITEM, folding in all four repairs.** Phase 1's
`NOT A RESULT` **stands on the record**; the old document is **cited as superseded, never
rewritten** (rule 6). The re-registration carries: **`FIELD_B` from a complete write with a
completeness check against what a solve needs; the age datum derived from the file that exists;
`^CD:` anchored as the objective reader; a stage-type-aware step proxy that refuses; the
`δ_window` degeneracy rule decided from the measured period; the `applied_magnitude` units
registration before phase 3; and `St`'s resolution caveat stated in the document's own words.**

## 8. STILL OPEN, AND HONESTLY NOT DONE

**Units registration for `applied_magnitude`** — phase 3 was never reached; **the requirement
stands.** **`δ_window` never emitting a numeric zero** — did not bite this run because the
channel turned out live; **the requirement stands.** **The comparator-side `FIELD_B` md5** —
ordered by me, and §3 records why it would not have caught this anyway; **it is superseded by
the completeness check, not merely supplemented by it.** **`C-93`**, after the in-invocation
re-derivation caught its **third live collision today** — a peer's uncommitted `C-92`
committed between invocations. **Rule 11 has now earned its keep three times in one session.**
