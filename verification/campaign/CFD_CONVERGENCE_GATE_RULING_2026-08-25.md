# cfd — RULING: **CLASS C IS THE REGISTERED SHAPE FOR EVERY CONVERGENCE GATE FROM THIS DATE**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]` under
Sanaa's desk-item disposal rule; **overrulable.** **ZERO COMPUTE.**

**Origin:** heat-transfer's T8 audit, relayed cross-team. **This ruling is the
forward-looking policy only. The row-by-row classification of cfd's existing gates,
and the free Δ/2Δ/3Δ checkpoint test, are being measured by a lane and are NOT
asserted here.** I am ruling the shape now because the shape does not depend on
which rows turn out exposed, and because a ruling held until the evidence arrives
is a ruling taken under pressure to match it.

---

## 1. THE HAZARD, STATED SO IT CANNOT BE MISREAD AS A TOLERANCE PROBLEM

T8's finest level sat **at or below its 1e-6 criterion for 228 consecutive
iterations, then never again** — it oscillated over two decades. Its gate reads the
**field change between the last two written checkpoints**.

> **On an oscillating field, a two-point sample is a PHASE LOTTERY. Two checkpoints
> that happen to land at similar phases show a small change, and the gate reports
> converged.**

**This is not fixed by tightening the tolerance.** A tighter tolerance on a
two-point sample is a **narrower lottery**, not a test. **The defect is the sample
size and the absence of a stationarity test, not the threshold** — and that is why
the repair is a change of shape rather than a change of number.

## 2. THE RULING

> **From this date, every convergence, plateau or steady-state gate in a cfd
> pre-registration is CLASS C. A Class A gate — a relative tolerance on the last
> two checkpoints, or on the last residual reading — may not be registered by this
> team again.**

**Class C has four elements and all four are required. Three of four is Class A
with extra steps:**

1. **A SUSTAINED WINDOW FLOOR.** The criterion must hold across a registered
   minimum number of consecutive samples, not at the last one. **T8 would have
   passed a 200-sample window and failed a 300-sample one; the window length is a
   registered quantity and must be justified in the document, not inherited.**
2. **A TREND FIT THAT REJECTS A GROWING SERIES.** A fitted slope over the window
   that is not decreasing (or not flat within a registered band) **refuses**. This
   is what catches a residual that bottoms and drifts back up.
3. **AN EXPLICIT STATIONARITY TEST.** Not a proxy. The field must be shown
   stationary over the window, and **the test must be able to report NOT
   stationary** — with a planted control demonstrating it does.
4. **REFUSAL BELOW A MINIMUM SAMPLE COUNT.** Fewer samples than the registered
   minimum is **`NOT A RESULT`, exit non-zero — never a verdict computed from what
   happened to be on disk.** **This is the limb that would have caught T8, and it is
   the limb most likely to be quietly dropped, because dropping it always makes a
   run gradeable.**

**ONE SHAPE FOR THE LAB, NOT TWO.** `analyse_e4a2.py:300` and `analyse_k0cx.py:644`
already implement this. **cfd adopts THEIR shape rather than inventing a rival**;
heat-transfer is ruling the same for its territory. **Two teams converging on one
tested implementation is worth more than two teams each with a good one.**

## 3. WHAT THIS RULING DOES **NOT** DO

- **It does not retrofit anything into a frozen pre-registration.** Rule 2 closes
  gates after first compute. **A Class A gate inside a fired freeze stays exactly as
  frozen** — replacing an instrument after seeing what it graded is the fit rule 2
  exists to prevent, and it would be that whether the replacement is better or not.
- **It does not regrade a settled verdict, and it does not authorise a re-audit
  beyond the free checkpoint test.** That is capped meta-work.
- **It does not amend a standing rule.** See §5 — that is referred, not pressed.

**What it DOES require, and this is the operative part for existing work:** **where
a graded row rests on a Class A gate, a dated note is filed BESIDE it** naming the
class and the exposure. **The verdict is not moved — a verdict is moved by a gate,
not by an audit — but no reader may take that row at face value without meeting the
caveat.** Same two-part shape I ruled for F4's 2026-07-28 `PASS` verdicts in
`54ae328e`, and for the same reason.

## 4. cfd ALREADY HAS TWO INSTANCES OF THIS HAZARD IN A DIFFERENT COSTUME

Both found today, before the cross-team relay arrived, and **both are Class A
failing to fire:**

- **F6a**: `residualControl` **met by 0.6 % on one partition and missed by 4.6× on
  another.** A single-reading criterion that gives two different answers about the
  same run.
- **F12**: the first-solve `p` residual **bottomed at 9.5548e-03 at iteration 5 and
  then ROSE** for the remaining 143 iterations. **A last-reading gate at any
  iteration below 5 would have reported descent on a run that never converged in its
  life.** Element 2 — a trend fit rejecting a growing series — catches this exactly.

**And today's F12 discriminator supplies the sharpest instance of all:** **arm 1
satisfied EVERY limb of standing rule 4** — `rc = 0`, `End`, last time == `endTime`,
`Time` count == `ExecutionTime` count, all fields, age guard — **while its minimum
first-solve `p` residual was 6.98e-04, three orders above its own
`residualControl`, and its solution sat 99.2 K outside the flow's adiabatic
ceiling.** **A complete run, by every point test the lab has, that never converged
and could not be right.**

## 5. THE STRUCTURAL OBSERVATION — REFERRED TO VERIFICATION, NOT PRESSED

**Standing rule 5 limb (1) requires that a level be *"iteratively converged or
plateaued"* and specifies NO TEST FOR IT.** `scripts/roache_triple.py:133` says so
in its own words — it knows *"nothing about iterative convergence or plateau …
those states are the caller's."*

> **The lab's standing rules NAME the plateau requirement and delegate its
> determination entirely to whoever calls the instrument. Every caller has been
> free to answer it with a two-point sample, and eleven comparators in one team
> did.**

**That is the structural gap this hazard sits in, and it is not a cfd defect — it
is where the standard stops.** **Amending or extending a standing rule is reserved
and is emphatically not a supervisor's call**, so this is **referred to
verification with the evidence, and cfd presses nothing.** cfd's own answer — Class
C, above — binds cfd and proposes nothing for anyone else.

## 6. THE METHOD NOTE, ADOPTED AS BINDING ON THE CLASSIFICATION ITSELF

The audit that found this had **two greps fail silently**, caught only by
cross-checking a narrow scan against a wider one.

> **A classifier that misses files the broad scan flagged is the instrument, not
> the territory.**

**Binding on cfd's sweep:** run **both** a narrow targeted scan and a deliberately
over-broad one and **reconcile them**, and use `git ls-tree -r HEAD` — **never
`git ls-files`**, which consults the shared index and was measured here **hiding
101 of 565 tracked `.md`, 18 % of the population.** **An audit for a sampling defect
that is itself under-sampled would be the joke this lab cannot afford.**

## 7. PENDING, AND DELIBERATELY NOT PRE-EMPTED

The A/B/C classification of cfd's existing gates, the graded rows resting on each,
and the free **Δ / 2Δ / 3Δ** checkpoint test on F4 — **eight checkpoints are on disk
for all nine cases and the grade used only the last three.** All being measured now.
**No result from it is assumed in this document**, including the hypothesis I put to
the lane: that F4's three `OSCILLATORY` standoff triples might be **temporal phase
aliasing** rather than the detector bias both the 2026-07-28 record and the
conversion concluded. **I expect the detector diagnosis to survive. I have asked to
be told plainly either way.**
