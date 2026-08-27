# F12 — ARM E: THE FIRST PRESSURE SOLVE. PRE-REGISTRATION (predictions frozen; **NOT YET LAUNCHABLE**)

Team cfd. Written 2026-08-27 by cfd lane R2 at the cfd supervisor's direction.
An **L0 DIAGNOSTIC EXTENSION** under `docs/standards/NONCONVERGENCE_STANDARD.md`
§1 (*"L0 DIAGNOSE FIRST … which channel; balance state; where in the domain"*).
**It is not an L1–L3 repair and no dial is tuned toward a better answer.**

**THIS ARM GRADES NOTHING.** It moves no gate, threshold, band, cap or label.
**F12 rung 1 stands `NOT A RESULT`; rungs 2–5 stand `BLOCKED`.** Rung 2's
`rate_calibration_gate()` interlock is **not invoked, not imported, not read
around and not edited** by any part of this arm. No verdict from the fixed
vocabulary is due to this probe and none will be issued from it. Its output is
a field, a count and a location.

---

## 1. THE QUESTION, AND WHY IT IS NOW THE FIRST ONE

Arm D established that F12 rung 1's initial state is **admissible**: `0/T`
uniform 300 K, `0/p` uniform 101,325 Pa, `0/U` uniform, and — because the case
is `hePsiThermo` + `perfectGas` — ρ is *derived* as ψp, so there is no `0/rho`
that could disagree with the equation of state. T₀ = 332.330992 K recomputed
from that field reproduces the discriminator's frozen constant to the last
digit, and the initial T_max of 300 K sits **32.33 K below** it.

**One SIMPLE iteration from that field produces a pressure range of
[−411,376.774, +2,974,458.981] Pa** (the iteration-1 `pressureControl`
pre-clip print) against registered bounds **[10,132.5, 202,650] Pa** —
**40.6× below zero and 14.68× above the upper bound.**

That is a single, isolated, fully reproducible event, and **nothing measured
explains it.** Every other F12 probe has examined iterations 1–148 in
aggregate. This arm examines **one**.

---

## 2. THE TWO ARMS — ONE CHANGE BETWEEN THEM

Both run the rung-1 case definition on the rung-1 mesh, **1 rank**, `endTime 1`.

- **E1 — INSTRUMENTATION ONLY.** Every physics dictionary byte-identical to
  rung 1. The only delta is `system/controlDict`: `endTime 1`,
  `writeInterval 1`, `purgeWrite 0`, `writeCompression off`, and writing `p`,
  `U`, `T`, `rho`, `phi` at times 0 and 1. **This is the same class of delta the
  energy-bound discriminator's arm 0 used and which was measured faithful
  (885 residuals, 0 mismatches).**
- **E2 — ONE CHANGE: `pMinFactor` and `pMaxFactor` are REMOVED from the
  `SIMPLE` block**, so `pressureControl` does not limit and the written `p` at
  time 1 **is the pre-clip field**. Nothing else differs from E1.

**E2's configuration is a MEASUREMENT INSTRUMENT AND MAY NEVER BE CARRIED INTO
ANY GRADED RUN.** It is registered here solely to put the pre-clip field on
disk where it can be read. Removing a limiter to *see* a field is a
measurement; removing it to *survive* would be the anti-gaming clause's
"parameter hunt" and is forbidden.

---

## 3. WHAT IS MEASURED

1. The written `p` field at time 1 — **post-clip in E1, pre-clip in E2** —
   cell by cell, with its extrema and their **cell indices and coordinates**.
2. The **spatial distribution** of the extreme cells: radius from the quarter
   chord, and whether they lie on the aerofoil surface, in the near field, in
   the wake, or at the far field.
3. The count of cells at or outside each registered bound.
4. The two `p` solves' initial and final residuals and iteration counts at
   iteration 1, from each arm's own log.
5. Whether the extremes are present **after the first inner `p` solve** or only
   after the second (the non-orthogonal corrector). **This is the open
   question; see PE7.**

---

## 4. REGISTERED PREDICTIONS — frozen before compute, scorable, and one is deliberately absent

| id | prediction | fails if |
|---|---|---|
| **PE1** | E1's iteration-1 log reproduces rung 1's **exactly**: Ux `0.9999999533`, Uy `0.9999999583`, e `0.9999999059`, p#1 initial `1` → final `0.009729218448` in **47**, p#2 initial `0.00077669948` → final `6.945700699e-06` in **28**; continuity sum local `8.216163968e-05`, global `1.981380643e-05`. **0 mismatches.** | any digit differs — the arm is then not rung 1 and nothing it says transfers |
| **PE2** | E1's time-1 `p`, post-clip, has **exactly 6,914 of 23,040** cells at a bound | any other count |
| **PE3** | E1's time-1 `p` has **no cell outside** [10,132.5, 202,650] | any cell outside |
| **PE4** | E2's time-1 `p` reproduces the pre-clip print to its printed digits: min **−411376.774**, max **2974458.981** | either differs beyond print precision |
| **PE5** | E1 and E2 have **identical** iteration-1 solve residuals, because `pressureControl::limit()` acts **after** both `p` solves | they differ — which would mean the limiter acts earlier than this registration believes, and that is itself the finding |
| **PE6** | the pre-clip extreme cells lie within **r ≤ 0.836 chords** of the quarter chord — the radius the frozen field-localisation probe measured for the iteration-1 bound violations | they lie outside it |

**PE7 — NO PREDICTION IS REGISTERED** on whether the extremes appear after the
first inner `p` solve or only after the second. **No evidence on disk bears on
it, and registering a guess would be outcome-fitting.** The arm reports the
answer either way and the record states it as a measurement.

---

## 5. CONTROLS — rule 3, each shown able to REFUSE (exit 2), never degrade

- **C1 — PLANTED ZERO on the `p` reader.** A known value is planted into a
  **copy** of the written time-1 `p` **on disk**, read back **through the real
  reader**, and required to return at the **exact planted cell index**. The
  reader **refuses** if it cannot see the plant. A zero from a reader not shown
  able to see a non-zero is not evidence.
- **C2 — KNOWN NON-ZERO.** The reader must independently reproduce E1's bound
  values (10,132.5 / 202,650) and the 6,914 count.
- **C3 — LEVER-EFFECT on E2.** E2's written `p` must **differ** from E1's. An
  arm whose output is identical to the control did not exercise its lever, and
  E2 is then not the arm it claims to be.
- **C4 — MESH IDENTITY.** Both arms' `constant/polyMesh/{points,faces,owner,neighbour}`
  must hash identical to rung 1's.
- **C5 — DICTIONARY IDENTITY.** E1's physics dictionaries byte-identical to
  rung 1's; **E2's differ in exactly the two lines `pMinFactor` and
  `pMaxFactor` and in nothing else**, asserted by diff before launch.
- **C6 — RUNG 1 IS NOT TOUCHED.** Rung 1's directory fingerprint is taken
  before and after every arm and must be **unchanged**; rung directories 2–5
  asserted **ABSENT** before and after.

---

## 6. COST — rule 12, on a basis measured from this case

**The rate is measured on this exact case by differencing two arms of the
energy-bound discriminator**, so no rate is imported and no growth exponent is
registered:

- arm0: **27.861 wall s** for 148 iterations · arm2: **11.223 wall s** for 52
- ⇒ 96 iterations = 16.638 s ⇒ **0.17331 s per iteration**
- ⇒ build + startup = 27.861 − 148 × 0.17331 = **2.211 s**
- one-iteration arm = 2.211 + 0.173 = **2.384 wall s**; **two arms = 4.769 s**

**REGISTERED ESTIMATE: 0.0795 core-min** (1 rank, both arms).
**REGISTERED CAP: 0.50 core-min**, enforced as a **30 wall-second `timeout`
per arm**; a kill leaves an incomplete arm, which is refused, and **the cap is
never raised**.

**The cap/estimate ratio is 6.3× and that is deliberate — stated rather than
hidden.** This lab's usual ceiling is 1.5×, which is right for a budget and
wrong for a five-second arm: `ClockTime` has **integer-second** resolution, so
quantisation alone is ±0.0167 core-min per arm = **42 % of the whole estimate**.
A 1.5× cap here would abort on rounding. **This cap is a hang detector, not a
budget tracker**, and it is set from the wall-clock envelope, not from the
estimate.

**Dollars: $0.000068 at the estimate, $0.000428 at the cap — DERIVED, NOT
MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read
its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).

---

## 7. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

`/home/ubuntu/Certonomous/verification/runs/F12_runs/first_pressure_solve_2026-08-27`
**DOES NOT EXIST at 2026-08-27T19:52:47Z** (stamp in the freezing commit message;
`os.path.exists` and `os.path.lexists` both `False`, and a glob returns `[]`).
**0.000 core-min have been spent on this arm.** Amendments before first compute
remain legal under rule 2 and must state this condition and how it was checked.

---

## 8. WHY THIS DOCUMENT IS **NOT LAUNCHABLE**, said plainly

**The launcher and the reader are NOT WRITTEN.** This document freezes the
*predictions, controls, cost and cap* — which is rule 2's evidentiary content,
and freezing them now is what proves they were not fitted to the answer. But
rule 2 also fixes **the grading path** at the pre-registration commit, and a
grading path that does not exist cannot be fixed.

**So: no launcher, no reader, no queue entry, and none may be written from this
state into a launch.** A second commit must add the instrument and fix its
blobs before anything runs, and the cfd supervisor's `SUPERVISION_CHARTER.md`
§3 check 1 (measurement-script diffs read **as diffs**) and check 4 are owed on
that commit, not on this one. **Writing a launcher and a grader for a
registration that is not ready would manufacture the appearance of readiness —
the defect F26_RINGLEB refused to commit and this document refuses too.**

## 9. NOT REGISTERED, NOT SENT

No mechanism is claimed. No fix is proposed. No F12 gate is read, and the
interlock is not touched. **Nothing is sent, filed, uploaded or submitted**
(rule 7).
