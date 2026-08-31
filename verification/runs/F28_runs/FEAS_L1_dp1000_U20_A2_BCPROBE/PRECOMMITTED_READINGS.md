# F28 FARFIELD BC-VARIATION PROBE — PRE-COMMITTED READINGS

**FEASIBILITY. NOT GRADEABLE. NO VERDICT VOCABULARY ATTACHES.**
Written and frozen **before the probe case was decomposed or launched**. Nothing
below was chosen after seeing a probe number. The probe run directory
`processor0..3` **does not exist** at the moment this file is written — that is
the condition, and it is checked by the launcher transcript that follows.

Authorised by `cfd-supervisor` (one arm, one variation). Registration
`verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md` is **not
edited by this probe**; §2.2 leaves the farfield form open and directs that the
form used be *recorded*, which is what this file does.

---

## 1. THE HYPOTHESIS UNDER TEST — ONE SENTENCE

The `farfield` patch carries `p: totalPressure p0=0` with `U: inletOutlet
inletValue (20 0 0)`. On a boundary whose normal is **radial**, a forced
**axial** inflow has a near-zero normal component, and the pressure form lets the
outer boundary pass mass freely. **The mass flux through the outer boundary is
therefore a free parameter that the SIMPLE loop never settles**, which is why the
continuity error concentrates there (measured, dp=0: 41.38 % of `sum local` on the
256 farfield-adjacent cells; 59.63 % in the outer radial band r ∈ [3.0, 3.577)).

## 2. THE SINGLE VARIATION — AND WHY IT IS THE CLEANEST DISCRIMINATOR

**`farfield` becomes `slip` on `U`, `p`, `k`, `omega`, `nut`. Nothing else changes.**

This is one conceptual change — *make the outer boundary impermeable* — and it
removes **exactly** the degree of freedom the hypothesis names, and nothing else.
`slip` sets the boundary-normal flux identically to zero, so the outer mass flux
stops being a free parameter and becomes a fixed one. Mesh, schemes, relaxation,
`fvOptions` disk source, iteration cap, rank count and every other patch are
**byte-identical** to `FEAS_L1_dp1000_U20_A2`.

A sweep over four farfield forms was considered and **rejected**: it would report
which form converges without isolating why, and a mechanism that is not isolated
is how a wrong method gets adopted.

**Stated in advance as a limitation:** `slip` confines the flow and is therefore
**not** proposed as the production farfield. This probe identifies a *mechanism*;
it does not select a boundary condition. If it confirms, the production form is a
separate question and its choice is the supervisor's.

## 3. THE ARBITER — REGISTERED, ABSOLUTE, AND NOT THE RESIDUAL

Registration §8 table: **`|dT_total| < 0.1 %` over the last 2000 iterations.**

Operationally, and matching the precedent already set in the registration's own
Addendum (item 2 of the 2026-08-31 appendix), the metric is

```
ptp% = ( max(Fx) - min(Fx) ) / |mean(Fx)| * 100
```

over the **final 2000 iterations**, on `postProcessing/forcesDuct/0/force.dat`
column `total_x`. This reader was validated by **reproducing the registration's
own published figure exactly**: dp=1000 baseline min −0.356179, max −0.295725,
mean −0.333725 → **18.1149 %**, against the registration's **18.1149 %**.

The metric is invariant to the sign convention and to `WEDGE_SCALE = 72`, both of
which are pure scalar multipliers.

**Why the dp=1000 arm and not dp=0:** dp=0 is drag-only with mean `Fx` = 0.003308 N,
so the percentage normalisation is ill-conditioned and returns **617.30 %** — a
number dominated by a near-zero denominator, not by unsteadiness. dp=1000 has a
well-conditioned mean (−0.333725 N), is the arm the registration itself measured,
and is the loaded case the campaign exists to map.

## 4. THE READINGS — COMMITTED NOW, IN NUMBERS

Baseline to beat: **18.1149 %**. Registered threshold: **0.1 %**.
Probe runs the same 15,000-iteration cap so the window is directly comparable.

| Reading | Condition on probe `ptp%` | What it means |
|---|---|---|
| **A — HYPOTHESIS CONFIRMED** | `ptp% < 0.1` | The registered absolute criterion is **met**. The free outer mass flux was the cause of the stall. |
| **B — HYPOTHESIS SUPPORTED, NOT SUFFICIENT** | `0.1 <= ptp% < 1.81` | A **≥10×** reduction. The farfield is a major contributor but does not account for the whole stall; something else remains. |
| **C — HYPOTHESIS FALSIFIED** | `ptp% >= 1.81` | Less than a 10× reduction. **The farfield is exonerated as the leading cause**, exactly as the axis columns were. Report as falsification and do **not** start tuning. |

`1.81 %` is `18.1149 / 10`, fixed here and not adjustable afterwards.

**Corroborating channels — evidence, NOT the arbiter.** These may not overturn the
reading above; they are recorded so the mechanism can be read even if the arbiter
is ambiguous.

- `p` first-solve initial residual at the final iteration. Baseline **0.3668997977**
  (dp=1000 at 15000). Gating is on the **first** of the two `p` solves per outer
  iteration, per the registration's own note.
- `time step continuity errors : sum local` at the final iteration. Baseline
  **2.775360385e-04**.
- Share of `sum local` carried by the 256 farfield-adjacent cells, from
  `localise_residual_f28.py`. Baseline (dp=1000, t=14000) **17.69 %**.
- Whether any `SIMPLE solution converged` line appears. Baseline: **none**.

## 5. WHAT IS BOUGHT, BEFORE IT IS BOUGHT

Measured rate **23.93–24.83 iterations/wall-s at 4 ranks** on this mesh.
15,000 iterations → **~605–627 wall s** → **~40.3–41.8 core-min**, plus
`decomposePar` ≈ **1 core-min**.

**Registered probe estimate: 42 core-min.** Wall `timeout` set to **1500 s**,
matching the parent arms and leaving ~2.4× margin over the expected 627 s.
Derived cost 42 core-min = 0.70 core-h × $0.0513/core-h = **$0.036 — DERIVED at
the recorded rate, never measured**; this box cannot read its own billing.

An overrun **stops the probe**; it does not get a second budget.

## 6. STOP CONDITION

If the reading is **A**, the probe **stops there and reports**. It does not
proceed toward a gated solve. The gated registration is frozen, does not name a
farfield form, and amending it is the supervisor's drafting, not this lane's.
If the reading is **B** or **C**, the probe stops and reports likewise. **No
tuning follows either outcome.**
