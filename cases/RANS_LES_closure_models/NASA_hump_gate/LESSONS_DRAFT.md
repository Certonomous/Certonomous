<!-- ALL ENTRIES APPENDED to docs/LESSONS.md - do not pass this file to append_lessons.py again -->
# Lesson drafts — shelf-D eigenspace + NASA hump gate lane

`L-TBD-D*` placeholders; numbers assigned at commit from the tail of
`docs/LESSONS.md`.

## L-TBD-D1. Register one prediction you expect to be boring: it is the only thing that tells you the other predictions mean anything

Part A registered three predictions before computing any envelope. **P-A1 was
deliberately a self-check**: shape coverage at `delta_B` = 1 must exceed 0.95 on
every case, *because at `delta_B` = 1 the three perturbed states are the corners
of the barycentric triangle, so the envelope is the entire realisable set and the
only cells that can fail are those where the truth itself is unrealisable.* The
preregistration said in advance that a number materially below 0.95 would mean the
implementation was wrong, not the method.

Measured: shape coverage came out equal to `1 − truth_unrealisable_fraction` to
four decimal places on all eight cases (0.9949 to 1.0000 against known truth
violation rates of 0.0000 to 0.0051), and zero cells left the simplex under
eq. (7). Only *then* is **P-A3's GATE FAIL** — the ducts needing `delta_B` of 0.95
to 0.98 where Emory's own experience is O(0.5) — a statement about turbulence
rather than a statement about a bug.

**A test suite for a physics implementation is a set of registered predictions
whose answers you already know.** Put at least one in every preregistration, say
out loud that it is a self-check, and give it a band that a broken implementation
would miss. It costs nothing and it is the difference between a finding and an
artefact.

## L-TBD-D2. A perturbation magnitude calibrated where the model is qualitatively right saturates where it is structurally wrong

Emory, Larsson & Iaccarino deduce the perturbation magnitude `B` from DNS by
minimising the barycentric distance to the perturbed state, and the values they
work with are O(0.5). Measured here as the per-cell **minimum `delta_B` that
contains the truth**, the eight training cases split into two families that do not
overlap:

| family | median `delta_B` required |
|---|---|
| 2-D separated flows — five hills and the curved step | **0.31 to 0.54** |
| square and rectangular ducts | **0.95 to 0.98** |

The hills sit exactly where the literature says. The ducts need essentially the
whole way to a corner of the triangle. The reason is not that the duct is harder
in degree: a linear eddy-viscosity model in a duct produces `b_23` and
`b_22 − b_33` **identically zero**, so its barycentric point is not displaced from
the truth, it is near the wrong vertex. The perturbation magnitude has nowhere to
go but 1.

**An uncertainty magnitude is a calibration, and it inherits the flow class it was
calibrated on.** Quoting O(0.5) on a flow where the closure is structurally rather
than quantitatively wrong understates the band by a factor of two, and the
diagnostic that catches it — the required magnitude, per cell, in closed form — is
one line of algebra and no solves.

## L-TBD-D3. Test the envelope on the quantity that enters the equations, not only on the quantity it parameterises

The eigenspace method parameterises the **shape and orientation** of the Reynolds
stress. Emory's eq. (4) keeps `k` outside the bracket, so magnitude is untouched
by construction. Both papers say so. What the measurement adds is which cases pay
for it, and the answer is an inversion:

* **Shape** containment at `delta_B` = 1 is essentially complete everywhere
  (0.9949–1.0000) — but on the ducts it costs the whole triangle (D2).
* **Production** `P_k = -R_ij dU_i/dx_j` — the term through which the stress
  actually forces momentum — is contained in only **0.9279 to 0.9433 of cells on
  every hill and on the curved step**, while the two ducts clear 0.9998.

So the cases whose *shape* is cheap to contain are the ones whose *forcing*
escapes, and vice versa. A single "does the envelope contain the truth?" answered
on `b` alone would have reported the hills as the easy family and been wrong about
the thing that matters to the solution.

**Report envelope coverage on the forcing term as well as on the parameterised
quantity, and expect them to fail on different cases.** This also closes the loop
L-157 opened: Xiao's space excludes the truth because it never perturbs
orientation; the eigenspace envelope perturbs orientation and still misses the
truth's forcing in 2–7 % of cells because it never perturbs magnitude. **Neither
framework contains what it is meant to bound, and they fail on different axes.**

## L-TBD-D4. A lesson is not applied until every call site asserts it — this one cost three runs in three different files

The finding is trivial and it bit three times: **the 29 `Parm_PH_29` hills carry
no `libs` entry in `system/controlDict`, while `PH_Breuer`, `CBFS`, `DUCT` and
`NASA_2DWMH` carry one naming a library that does not exist on this machine.** A
`str.replace` of the absent-library line therefore succeeds silently on the hills
by doing nothing, and the run dies with `Unknown RAS model type ...` after a
fraction of a second.

* First strike: the Xiao `Re`-switch harness. Diagnosed, fixed **in that file**,
  and written up as an operational note in the report.
* Second strike: the same code path in a second file, days of nothing.
* **Third strike: `setup_case.build`, reached from a different lane entirely — five
  eigenspace re-solves all returned `it=0` and the *baseline* `U_rms`, which looks
  like a plausible physical answer.** That is the dangerous part: a failure that
  returns the unperturbed field is not obviously a failure.

Writing the lesson down in a report did not fix the other call sites. What fixed
it was replacing every one with **insert-or-replace followed by
`assert "libspartaTurbulenceModels" in s`** — three lines that turn a silent
no-op into a stack trace.

**When a defect is found in a shared helper, grep for every call site in the same
sitting and add the assertion there, not a paragraph about it somewhere else.**
The cost of the paragraph was two more wasted runs; the cost of the assertion was
three lines.
