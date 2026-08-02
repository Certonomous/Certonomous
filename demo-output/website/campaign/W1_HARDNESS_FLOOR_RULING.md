# W1 — ruling nine approved follow-ons against the hardness floor

Approved item `w1-approved-backlog-below-the-floor`, estimated 0 core-minutes,
**measured 0 core-minutes**: no solver was launched. Every number below cites a
file on this box. Ruled 2026-08-02.

The gate: *each of the nine is either shown to clear the floor, relabelled a
regression test, or dismissed.*

**Result: three clear the floor, six are dismissed, none is relabelled a
regression test — and the reason none can be is itself the finding.**

---

## 1. Three premises in the item, corrected before the ruling

The item was filed 2026-07-31. Two of its three numbers have moved and one of
its sentences was imprecise. Correcting them does not weaken the item; two of
the three corrections make its case stronger.

**"Nine of the twelve approved items."** There are now **19** approved W1
items, not twelve, totalling **1,843 core-minutes**, not the ~1,400 the item
quotes. The nine are nine of nineteen. The queue grew by seven items and 443
core-minutes in the two days the ruling sat unmade, which is the argument for
making it.

**"Follow-ons on the vortex-lattice airliner and the analytic valve."** There
are **three** parent studies, not two, and the third is not a panel method:

| Parent study | Follow-ons | What actually solves it |
| --- | --- | --- |
| Aircraft L/D optimization: 300 pax, 6000 km | 3 | VSPAERO vortex-lattice, OpenVSP 3.51.1 (`mfmc_error_budget.json`) |
| Valve opening-angle screen | 3 | **Nothing.** "Each phase is a reduced-order orifice model, not a solved flow" (`mission-output/valve-study/transcript.txt`, Numericist line) |
| Geometry study: NACA 4412 finite wing | 3 | simpleFoam, steady RANS, 137,569 cells, 13 s of solver time (`mission-output/geometry-study/study-naca4412_wing/report.md`) |

So the item's "more studies on a panel method" argument lands squarely on
three of the nine and not on the other six. The other six are disqualified too,
on two different defects the item did not name — which is section 3 below.

**"The model-form error of that panel method is now the largest term in its own
error budget."** Nearly right, and the exact wording matters because the record
already carries the correction. `demo-output/website/mfmc_error_budget.json`
has `high_fidelity_model_form: null` and `combined.missing: ["model"]`. The
model-form term is not the largest term; it is **the term with no number in
it**. The largest *quantified* term is the input spread at 0.21938, which is
**99.997%** of the quantified total, and the record flags itself with
`ranks_only_what_was_measured: true`. The item's conclusion survives intact and
is arguably sharper: the airliner's error budget is dominated by a term that
was measured and led by a term that was not, and neither of them is anything a
further design sweep would move.

---

## 2. What the floor actually says, and the gap the nine fall into

`docs/charters/CASE_SELECTION_CHARTER.md` section 2 lists six HARD criteria and
says the list "is the owner's and it is closed". Section 2 also fixes how to
apply it: **"Hardness is a property of the regime, not of the shape"**, and the
converse binds — "A wing at low incidence in attached steady flow is a
regression test with a nice picture attached."

Section 3 permits below-floor work for exactly three purposes: regression
tests, instrument checks, and ladder rungs below a HARD rung. A **regression
test** is defined there as a run "to prove the machinery still gives the number
it gave before … The expected value is written down before the run."

**That definition is why none of the six dismissed items can be relabelled.**
Every one of them sweeps a *new* design point — a span beyond today's cap, a
cruise Mach not yet flown, a yaw angle not yet run, a body not yet chosen.
There is no number it gave before, so there is nothing to regress against. They
are not HARD and they are not regression tests. They are new easy results,
which is precisely the category section 1 was written to prevent: *"An easy
case converges, produces a clean number, fills a report row and teaches the lab
nothing."*

The gate offered three dispositions and the honest answer for these six is the
third.

---

## 3. The nine, one at a time

### Clears the floor — 3 of 9, all on criterion 3

**`agp-527efc1cbb44` — Harmonic-balance cycle solve (valve).**
**Criterion 3, unsteady statistics.** The reported quantity would be a
phase-resolved cycle loss, which is a phase-aligned waveform by construction.
The parent study's own Chief Researcher named the gap and the fix in the same
breath: Womersley α ≈ 16.7, "above the strict limit 1, inertially unsteady",
"dropped phase-interaction rides as model-form in the channel table", and "to
solve this for real. Required: a transient pulsatile solve (moving-boundary
incompressible solver with the time-varying inlet waveform) **on a meshed valve
geometry**."
**Verdict: clears the floor, and is blocked.** There is no meshed valve. The
curriculum record's own method line reads "quadrature convergence of a
reduced-order orifice model, k = 3/5/9 segments of the ejection window; **not a
mesh refinement**" (`models/curriculum/uq-studies/aortic-valve.json`). The 60
core-minute estimate prices a solve of a case that has no mesh and no solver
path. **Stays approved; re-priced as unknown, and marked blocked on the two
capabilities the parent study already named.**

**`agp-a3cc843ce473` — Resolve the shedding (NACA 4412 finite wing).**
**Criterion 3 on its wording; below the floor at the regime it would inherit.**
The parent solve's freestream is `internalField uniform (15 -0 -0)` — purely
streamwise, no cross-flow component — and it reports Cl 0.2516 and Cd 0.02167
in steady attached flow. There is no shedding at that condition for an unsteady
solve to resolve; "the wake the steady picture averages away" is, at this
incidence, a thin attached wake. Run as inherited, this is the charter's own
worked failure: a wing at low incidence in attached flow.
**Verdict: clears the floor only if re-scoped**, to a post-stall incidence
where the wake is genuinely three-dimensional and separated — at which point it
carries criteria 1 **and** 3 and becomes a good item. **Stays approved with the
re-scope written into it as a condition, not an aspiration.** Its 60
core-minute estimate does not survive either way: the lab's own unsteady
spectral work is the cost reference and it is not a 60 core-minute shape.

**`agp-37da30f972b3` — Unsteady fluid-structure interaction, moving leaflets
(valve).** **Criterion 3.** Coupling leaflet dynamics to the flow makes opening
solved rather than prescribed, and every reportable quantity is a
cycle-to-cycle statistic.
**Verdict: clears the floor, and is a capability request rather than an
experiment.** The lab has no fluid-structure coupling and no meshed valve. 60
core-minutes for an FSI campaign is not an estimate, it is the drafter's
default. **Stays approved; re-priced as unknown and marked blocked**, alongside
`agp-527efc1cbb44`, which it shares both blockers with.

### Dismissed — 6 of 9

**`agp-12fdfe05e05f` — Composite-span structural limits (airliner).**
No criterion. Steady, attached, subsonic, and a vortex-lattice method cannot
represent separation or a shock at all, so criteria 1 and 2 are unavailable to
it by construction; 3, 4 and 5 do not arise; the airliner produces no scored
column of the challenge, so 6 does not either. It is also not primarily a flow
study — a composite wing-box weight model driving MTOW is a structures
question wearing an aerodynamics estimate. **Dismissed.**

**`agp-f6354ae61613` — Cruise Mach trade (airliner).**
**The sharpest of the six, because the criterion it would meet is the one its
instrument cannot express.** A cruise Mach sweep on a transport wing runs into
the transonic range, which is criterion 2 — but the sweep would be flown on
VSPAERO, a vortex-lattice method with no discontinuity in its solution space.
Charter section 4 step 4 is explicit that the detector is checked before the
physics and that this is a zero-compute check that "kills a family before it
starts". A shock-free method sweeping for the shock-limited peak of a
range–speed–L/D surface will return a smooth peak in the wrong place and no
gate will fire. **Dismissed as proposed.** The transonic question is real and
the lab already owns HARD instruments for it — the ONERA M6 and DPW5 lines —
so nothing is lost by refusing the panel-method version.

**`agp-8991d74e789f` — Drag build-up under yaw (NACA 4412 finite wing).**
A yaw sweep that reached large enough angles would carry criterion 1, and the
proposal names no angles, so it does not claim it. It also inherits a mesh with
a documented, still-open defect: every rung of that ladder is layerless at
chord Reynolds 1.0e6 (`addLayers false` in all three run directories), and two
of the three rungs "never converged; they ran to the 180-iteration cap with no
convergence statement" — both recorded in this body's own
`fifth_rung_preflight` block. A yaw sweep on that mesh measures the absence of
a wall treatment, not yaw. **Dismissed**, and the credential-repair item on
that body is upstream of any re-filing.

**`agp-a13672d0713c` — Next body in the class (NACA 4412 finite wing).**
"Take the same gated chain to the nearest unsolved body in the library." It
names no body and no regime. Since hardness is a property of the regime, this
proposal **cannot be ruled either way**, and charter section 4 step 1 makes
naming the HARD criterion a required field of any proposal that spends compute
on a family. A proposal that cannot name its criterion cannot clear a floor
that requires it to. **Dismissed as unrulable**, not as uninteresting; a
successor naming a body and a regime is welcome.

**`agp-d64295666c56` — Full-configuration solve (airliner).**
Fuselage and tail added to the solved model, trimmed for static margin. Steady,
attached, subsonic vortex-lattice; same unavailability of criteria 1 and 2 as
its two siblings. Trim for static margin is a stability-and-control task whose
answer is a moment balance, not a flow-physics result. **Dismissed.**

**`agp-f68b5c37221c` — Non-Newtonian blood rheology (valve).**
Names no criterion, and proposes to replace the Newtonian viscosity "in the
orifice jet and wake" of a model that has neither. The valve screen is an
algebraic orifice correlation; there is no jet and no wake in it to make
shear-thinning.
**Dismissed, and the family's live defect is somewhere else entirely.** The
parent study's own conclusion records that the winning candidate sits at
orifice ratio 1.00 against a correlation "calibrated to" a 0.75 ceiling, and
that "above that ceiling the magnitude is not bounded by the reported band".
That is L-23 exactly — a correlation used outside its stated limit — and it is
the term that has stopped the family from meaning anything. Refining the
rheology inside an extrapolated correlation refines a term that is already
dominated by the extrapolation, which is the same shape of error the parent
item identified on the airliner.

---

## 4. What the ruling costs and what it returns

| | before | after |
| --- | --- | --- |
| approved W1 items | 19 | 12 |
| approved W1 declared core-minutes | 1,843 | 1,463 |

The item count drops by seven: the six dismissals, plus this ruling item
itself, which closes. The core-minutes drop by 380 in two separate ways, and
the second is the larger one:

- **200 core-minutes withdrawn by dismissal** (20 + 20 + 20 + 20 + 60 + 60).
- **180 core-minutes withdrawn by re-pricing** — the three items that *clear*
  the floor, each carrying the same default 60, all now `est_core_min: 0` with
  `cost_basis: unknown`. Not because they are cheaper. Because nobody had
  estimated them at all.

That second line is the return. The three items which do clear the floor were
priced identically to the six that do not, and two of the three are blocked on
capabilities that do not exist on this box — which no reader of the queue could
have seen, because "approved, 60 core-min" reads the same either way.

**One pattern worth carrying.** All nine were generated from "next
investigations" lines in mission reports, and a next-investigation line is
written to be interesting, not to be runnable. Six of nine could not name a
HARD criterion; three of nine named a real one and none of those three carried
a cost that survived contact with what the lab can actually do. The drafter
that converts those lines into proposals does not check the floor and does not
check the capability, and every one of these nine reached "approved" without
either check firing.

---

## Related

- `docs/charters/CASE_SELECTION_CHARTER.md` sections 1 to 5, the floor itself.
- `demo-output/website/mfmc_error_budget.json`, the airliner's error budget.
- `mission-output/valve-study/transcript.txt`, which names the valve's three
  missing capabilities before any of these follow-ons were filed.
- `models/curriculum/uq-studies/naca4412_wing.json`, `fifth_rung_preflight`.
- `LESSONS.md` L-23, a correlation used past its stated limit.
