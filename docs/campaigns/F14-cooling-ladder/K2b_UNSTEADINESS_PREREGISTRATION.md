# K2b-U — is the rack-row module steady? Pre-registration

**Campaign F14, rung K2b, unsteadiness diagnosis. Written 2026-08-18 BEFORE any
diagnostic solver ran.** Every threshold and every outcome-to-meaning mapping
below is fixed here. Authorisation: 45 core-minutes on the 2D module.

---

## 1. Why this exists, and what it blocks

The 3D graded pair (374–697 core-minutes, `K2b_PILOT_RESULTS.md` §9) is held on
one sentence from this rung's own record:

> *On this configuration the unsteadiness is the binding limit on every
> differential measurement, in both cases — not the instrument.*

**Two independent differential measurements hit the same wall.** C3's planted
source could not reach its 0.500 W tolerance because the no-plant twin's ledger
wanders **48.313 W** peak-to-peak. The wall-treatment comparison could not
resolve a 0.5466 K spread against a 1.0832 K single-case swing. Neither failure
was the instrument's.

**If this flow is physically unsteady, a steady SIMPLE solver is the wrong tool**
and 374–697 core-minutes buys a converged-looking answer to the wrong question,
which every rung above would inherit. K2a §5 risk 1 already records the K2c
primary's authors failing to converge a steady 10-rack module and moving to
transient averaging over 600 s.

**A residual that will not settle and a monitored quantity that oscillates look
identical from inside a steady solver whether the cause is physical or
numerical, and the remedies are opposite.** Hence a discriminator, fixed in
advance.

## 2. The observation to be explained

`K2bP_under` (70 % tile provisioning), T_in peak-to-peak over 1000-iteration
blocks:

| iterations | mean T_in | peak-to-peak |
|---|---:|---:|
| 1000–2000 | 291.8931 K | **3.1996 K** |
| 2000–3000 | 293.8059 K | **2.0271 K** |
| 3000–4000 | 293.7655 K | **1.1444 K** |
| 4000–5000 | 294.1595 K | **1.0678 K** |

**The amplitude decays by 3× and then plateaus at ≈1.07 K.** A plateau is what a
limit cycle looks like. It is also what a slowly-decaying numerical transient
looks like at 5,000 iterations. That ambiguity is the whole question.

## 3. The two tests, and the predictions, fixed now

### Test A — under-relaxation strengthening (steady solver)

Re-run `K2bP_under` from `0.orig` with every under-relaxation factor cut:
p_rgh 0.3 → 0.15, U 0.5 → 0.25, T 0.5 → 0.25, (k|omega) 0.5 → 0.25. Same mesh,
same BCs, same iteration count (5,000). **Under-relaxation is the direct remedy
for a numerically unstable outer iteration and has no counterpart in physics: it
cannot damp a real vortex, only the solver's pursuit of one.**

Graded on **A = T_in peak-to-peak over the final 400-iteration window**, against
the baseline's **1.0162 K**:

| A | reading |
|---|---|
| **A ≤ 0.20 K** (≤0.2× baseline) | **numerical** — halving the relaxation halved-and-more the oscillation |
| **A ≥ 0.51 K** (≥0.5× baseline) | **physical** — the oscillation does not care about the iteration scheme |
| 0.20 K < A < 0.51 K | ambiguous on this test alone; Test B decides |

### Test B — transient run (the decisive one)

`buoyantBoussinesqPimpleFoam`, same mesh, same BCs, started from
`K2bP_under/5000` (the oscillating state), adjustable time step at maxCo 2,
**40 s of physical time**, T_in written every 0.1 s. In physical time the
question is direct: does the flow settle, or does it oscillate?

Graded on **B = T_in peak-to-peak over the FINAL 10 s**, and on whether the
amplitude over the final 10 s is smaller than over the preceding 10 s:

| B | reading |
|---|---|
| **B ≥ 0.30 K and not decaying** (final 10 s ≥ 0.8× the previous 10 s) | **physical** — a sustained limit cycle in physical time |
| **B ≤ 0.10 K, or decaying** (final 10 s ≤ 0.5× the previous 10 s) | **numerical** — the real flow settles; only the steady iteration oscillated |
| otherwise | undecidable at this run length |

### Test C — physical plausibility of the period (arithmetic, no compute)

Only if B says physical. Extract the dominant period T_osc from the transient
T_in series and compare against three timescales computed from the case's own
parameters:

- **rack-face shedding**: St = D/(U·T_osc) with D = rack height 2.00 m and U the
  rack-face velocity 0.2917 m/s; physically plausible bluff-body St ≈ 0.05–0.5
- **aisle transit**: L/U with L the 1.2 m aisle width
- **buoyant**: √(H/(g·β·ΔT)) with H = 2.7 m

A period matching any of these within a factor of ~3 supports "physical". A
period matching none of them, but matching the steady solver's oscillation
period *in iterations*, supports "numerical".

## 4. The three outcomes, and what each MEANS — fixed before the runs

**O1 — PHYSICALLY UNSTEADY.** Test A says physical (A ≥ 0.51 K) **and** Test B
says physical (B ≥ 0.30 K, non-decaying).
→ **The steady formulation is wrong for this configuration.** The §9 estimate of
374–697 core-minutes is **VOID**: it prices steady runs. K2a §5's unsteady
escalation (5–10×) becomes the baseline, and K2a §9 must be re-specified to make
the module transient-with-averaging at this provisioning. Every K2b number
produced by a steady solve on an oscillating case — θ, r, T_in, and the closure
figures on `K2bP_under` and its twins — is a window mean over a limit cycle and
must be relabelled as such. **This is a finding, not a setback:** it invalidates
a plan before it is paid for, and it explains C3's noise floor, the
wall-treatment noise floor and the convergence refusals with one mechanism.

**O2 — NUMERICALLY STALLED.** Test A says numerical (A ≤ 0.20 K) **or** Test B
says numerical (B ≤ 0.10 K or decaying).
→ **A solver-settings problem, not a physics problem.** The §9 estimate
**STANDS**, with the corrected relaxation factors written into K2a §9. C3 and
the wall-treatment comparison should be re-run at the corrected settings before
either is quoted, because both were noise-floor-limited by an artefact.

**O3 — UNDECIDABLE AT THIS COST.** A is ambiguous and B is ambiguous, or the two
disagree in a way C cannot break.
→ **Stated as the answer, not resolved by preference.** The 3D pair stays held.
The next step and its cost are named, and nothing is quoted from the affected
cases in the meantime.

## 5. Two things this diagnosis will NOT do

- **It will not raise the iteration cap to make the oscillation go away.** A cap
  increase that "fixes" a physical oscillation has hidden it.
- **It will not report a window mean as a converged value.** Where a window mean
  is quoted it is labelled as a mean over an oscillation, with the window and the
  amplitude beside it.

## 6. What this cannot reach

The 2D slice. If the 2D module is unsteady the 3D one is at least as likely to
be, but a 2D slice suppresses spanwise instabilities and can also manufacture
oscillations a 3D flow would damp by three-dimensionalising. **A 2D verdict of
"physical" is a warning about the 3D module, not a measurement of it**; a 2D
verdict of "numerical" does not license the 3D pair to skip its own monitor.

---

## 7. AMENDMENT 1 — run length, forced by compute, made before the windows were readable

**Written 2026-08-18T05:27 UTC, while Test B stood at t ≈ 3.0 s of a 40 s
target and no amended window contained data.** Recorded here rather than applied
silently, because an amendment made after seeing the outcome is not an amendment.

**Why.** Test B is measured at **≈1.7 core-minutes per second of physical time**
(2.96 s for ~5 core-minutes). The 40 s specified in §3 would cost **≈68
core-minutes** against a 45 core-minute authorisation, of which Test A has
already taken ~7.7. **The run length must come down; the thresholds must not.**

**What changes.**

- **`endTime` 40 s → 20 s.** That is ~5 aisle transit times (4.11 s) and ~7
  buoyant timescales (2.62 s), so a limit cycle on either would still show
  several periods. It is *not* enough to resolve the 23 s room-turnover
  timescale, and §8 below records that as a stated limit rather than a caveat
  discovered afterwards.
- **The first 5 s are discarded as start-up.** The transient begins from a
  *steady-solver* field, which is not a solution of the time-dependent equations,
  so the opening seconds contain an adjustment that belongs to neither the flow
  nor the iteration scheme. **This is the amendment's one real risk and it cuts
  toward NUMERICAL:** leaving the start-up in would inflate the earlier window,
  drive the final/previous ratio down, and trip the "decaying" branch by
  artefact. Discarding it removes a bias *against* the physical reading.
- **The windows become the final 7.5 s (12.5–20 s) against the preceding 7.5 s
  (5–12.5 s).**

**What does NOT change.** Every threshold and every outcome-to-meaning mapping in
§3 and §4 stands exactly as written: B ≥ 0.30 K non-decaying = PHYSICAL,
B ≤ 0.10 K or decaying (final ≤ 0.5× previous) = NUMERICAL, otherwise
undecidable. Test A is untouched.

## 8. What Amendment 1 costs the conclusion

A 20 s window can see an oscillation with a period up to ~4 s with several
cycles, and cannot see one slower than ~7 s at all. **If the diagnosis returns
NUMERICAL or UNDECIDABLE, a slow mode above that period remains unexcluded and
must be said so.** If it returns PHYSICAL on a period well inside the window, the
shortened run does not weaken that finding — a limit cycle observed is a limit
cycle.

---

## 9. AMENDMENT 2 — the cost estimate that forced Amendment 1 was wrong; the ORIGINAL windows are restored

**Written 2026-08-18T05:28 UTC with Test B at t = 5.18 s. The §3 windows
(30–40 s and 20–30 s) contain no data and cannot, for another 15 s of physical
time.**

**Why.** Amendment 1 shortened the run on an estimate of ≈1.7 core-minutes per
second of physical time, taken from *wall-clock elapsed during heavy machine
contention*. Measured against the solver process's own CPU time it is
**0.72 core-minutes per second** — 260 steps, 225 s, mean dt 19.9 ms. The full
40 s therefore costs **≈29 core-minutes**, not 68, and with Test A's 7.7 the
diagnosis fits inside the 45 authorised.

**This is the same error this rung has now made twice**: pricing a long run from
a short, contended sample. The first instance is recorded at §8 of
`K2b_PILOT_RESULTS.md` — a 100-iteration probe that mis-priced the pilot by
1.9×. **A cost estimate is a measurement and needs the same care as any other.**

**What changes: Amendment 1 is withdrawn except for its start-up discard.**

- **`endTime` back to 40 s**, as originally pre-registered in §3. The running
  process already carries `endTime 40` from its own `controlDict`; only the
  builder had been lowered, and it is restored.
- **The §3 windows are restored exactly**: final 10 s (30–40 s) against the
  preceding 10 s (20–30 s).
- **The 5 s start-up discard is KEPT.** It was the one part of Amendment 1
  justified by physics rather than by budget — the run begins from a
  steady-solver field, which is not a solution of the time-dependent equations —
  and it removes a bias *toward* the NUMERICAL reading. With 40 s available it is
  now free: the graded windows start at 20 s regardless.
- **§8's limitation is withdrawn with it.** A 40 s record spans the 23 s
  room-turnover timescale, so a slow aisle-scale mode is no longer outside what
  the run can see.

**Restoring the original criterion is the conservative move**, not a further
departure: after two amendments the test is graded on exactly the thresholds and
windows fixed before anything ran.

---

## 10. LIMITATION OF TEST A, found during execution and recorded before it was graded

**Written 2026-08-18T05:29 UTC with Test A at 4,221 of 5,000 iterations and the
final window not yet complete.**

Test A's design compares the final-window amplitude of the halved-relaxation run
against the baseline's **at equal iteration count**. Halving the under-relaxation
also **slows the approach to steady state**, so at 5,000 iterations Test A is at
an earlier point in its own development than the baseline was. Measured at 4,221
iterations: Test A's T_in has spanned 3.8230 K and stands at 290.8632 K, against
the baseline's 5.7510 K span and 294.1854 K.

**The confound runs in both directions, which is why it must be named rather than
argued away.** The baseline's own amplitude decayed 3.1996 → 1.0678 K between
iterations 1,000 and 5,000, so an under-developed case can show a *larger*
amplitude, not only a smaller one. A small Test A amplitude could be damping *or*
under-development; a large one could be a persistent oscillation *or* an early
transient.

**What is done about it, fixed now:**

- **The pre-registered §3 reading stands as the primary and is reported as
  specified**, thresholds unchanged.
- **A secondary MATCHED-STATE reading is added and labelled as secondary**: the
  baseline window whose mean T_in is closest to Test A's final-window mean is
  located, and the two amplitudes are compared there. This compares like with
  like in development rather than in iteration index. It changes no threshold; it
  is a second view of the same data.
- **Test B remains the decisive test**, exactly as §3 already says. Test A was
  always the cheap corroborator, and this limitation is the reason the
  pre-registration did not rest the outcome on it alone.

**If the two Test A readings disagree, Test A is reported as AMBIGUOUS** and the
outcome is decided by Test B under the §4 mapping.

---

## 11. AMENDMENT 3 — wall-clock, not core-minutes, is the binding constraint; BOTH window definitions will be graded

**Written 2026-08-18T05:33 UTC with Test B at t = 12.17 s. The Amendment-1
window 12.5–20 s contains NO data at this moment, and the §3 windows 20–30 s and
30–40 s are 8 s and 18 s away.**

**Why.** Amendment 2 restored the 40 s run because the CPU cost was affordable —
and it is: 0.728 core-minutes per second of physical time, 29 core-minutes total,
inside the 45 authorised. What Amendment 2 did not account for is that this
machine is running up to eight other agents' jobs, so **wall-clock is ≈9× CPU
time**: t advanced 10.73 → 12.17 s in ten wall-minutes. Reaching 40 s would take
**over three hours of wall-clock** for 22 core-minutes of work.

**What changes: nothing about thresholds, and no single window definition is
chosen after the fact.**

- **Test B is graded on BOTH window definitions and both are reported**: the §3
  pair (30–40 s vs 20–30 s) and the Amendment-1 pair (12.5–20 s vs 5–12.5 s).
  **Both were fixed before the data they cover existed** — §3 before anything
  ran, Amendment 1 at t = 4.0 s. Grading both removes the choice rather than
  making it.
- **The verdict is declared once at least one pair is complete.** If both
  complete and disagree, Test B is AMBIGUOUS and the §4 mapping decides on Test A
  plus Test C.
- **The run is left going.** If it reaches 40 s the §3 pair is graded and
  reported alongside; if it does not, the §3 pair is reported as UNGRADED with
  the time reached, and never as a result.

**The thresholds are untouched**: B ≥ 0.30 K non-decaying = PHYSICAL, B ≤ 0.10 K
or decaying = NUMERICAL. The 5 s start-up discard stands.

**Stated plainly because it is the third amendment**: two of the three have been
forced by mis-estimating cost — once too high, once on the wrong resource. The
thresholds and the outcome mapping have never moved, and that is the property
that makes this still a pre-registration rather than a narrative. **The estimate
that keeps failing is the cost estimate, which is itself a measurement and has
now been wrong three times on this rung** — a 100-iteration probe by 1.9×,
Amendment 1 by 2.3× on CPU, Amendment 2 by 9× on wall-clock.

---

## 12. Hash ledger — how to verify this was not written after the answer

This file was hashed when it was written and then **amended three times**, so its
hash today is not the hash it was pre-registered under. Both are recoverable and
the check is two lines:

```bash
python3 - <<'EOF'
import hashlib
s = open("K2b_UNSTEADINESS_PREREGISTRATION.md").read()
orig = s[:s.index("\n\n---\n\n## 7. AMENDMENT 1")].rstrip("\n") + "\n"
print(hashlib.sha256(orig.encode()).hexdigest())
EOF
# -> 932451adb8f4e57b6243777c239f9a93b56315a701455a8af7060460f5709e1d
```

| what | sha256 | when |
|---|---|---|
| **as pre-registered** (§1–§6, i.e. this file truncated at §7) | `932451adb8f4e57b6243777c239f9a93b56315a701455a8af7060460f5709e1d` | 2026-08-18T05:20:05Z, **before any diagnostic solver ran** |
| with Amendment 1 (§7) | — | 05:27, Test B at t ≈ 3.0 s |
| with Amendment 2 (§9) | — | 05:28, Test B at t ≈ 5.2 s |
| with Amendment 3 (§11) | — | 05:3x, Test B at t ≈ 12.2 s |

**Every threshold and every outcome-to-meaning mapping lives in §3 and §4, inside
the truncation**, so the hash above covers all of them. No amendment touched
either; each records the state of the run at the moment it was written, and each
was written before the data it could have been fitted to existed.

---
