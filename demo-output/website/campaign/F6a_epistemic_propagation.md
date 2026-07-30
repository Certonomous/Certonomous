# F6a — epistemic uncertainty PROPAGATION on the NASA hump: what the theory prescribes, and what this case allows

Companion to `F6a_epistemic_band.md` (the bounding study, rewritten across
2026-07-29/30) and `LITERATURE_REPRODUCTION_REVIEW.md` §2 (the convergence
literature already gathered). This document answers a narrower, harder
question: not "does a band contain the experiment" but "does the published
eigenvalue-perturbation theory let us go from that band to a defensible
*propagated* uncertainty on a quantity of interest" — and if not, what is
the honest, computable substitute using only data this project can actually
converge.

**Every number used as an input below was checked with
`scripts/check_convergence.py` before use, per this task's own rule.** The
command and its verdict are quoted at the point each number is introduced,
not asserted separately. No input comes from a run the checker classifies
NOT_CONVERGED or CANNOT_TELL.

---

## 1. What the published theory actually prescribes for propagation

Two primary sources were read in full for this document (not abstracts —
both fetched as PDF, decompressed and read directly with `pdftotext`, with
the exact page/line locations of every quote below verifiable against the
saved source).

**Source A — Mishra, A.A., Mukhopadhaya, J., Iaccarino, G. & Alonso, J.,
"An uncertainty estimation module for turbulence model predictions in
SU2," arXiv:1803.00725 (2018), submitted to *AIAA Journal*.** Open access
(arXiv preprint). This is the EQUiPS module paper — the reference
software implementation of the Emory/Larsson/Iaccarino eigenspace
perturbation framework our own `r4`/`channel3_eigenvalue_perturbation`
code implements. Read in full via local `pdftotext` extraction of the
arXiv PDF (the paywalled 2013 *Physics of Fluids* paper that originates
the method, Emory, Larsson & Iaccarino, is **not** independently read here
either — same caveat as `LITERATURE_REPRODUCTION_REVIEW.md` §2 already
carries; everything attributed to it below is relayed through sources A
and B, which describe and cite it directly).

**Source B — Mishra, A.A. & Iaccarino, G., "Uncertainty estimation for
turbulence models in aerospace applications," Center for Turbulence
Research Annual Research Briefs 2017, pp. 327–334, Stanford University.**
Open access (Stanford CTR public archive). A condensed statement of the
same methodology, by the same group, applied to aircraft nozzle jets.

### 1.1 The output is a deterministic bound, not a distribution — stated explicitly, not inferred

Source A, verbatim: *"Due to the nature of this formulation, these bounds
are explicitly deterministic."* And: *"The uncertainty bounds on the
profiles are engendered by the union of all the states lying in the set
of perturbed RANS simulations."*

This is a direct answer to the question this task opened with. **The
theory does not prescribe propagation to a probability distribution at
all.** Its own stated output is an envelope — the union, at each point in
the flow, of whatever a small fixed set of extremal simulations predict
there — with no probability measure attached. It is weaker than a
"confidence region" (which presupposes a probability space) and closer to
a plain **support-like range under the model's own structural
assumptions**: a claim that the truth is expected to fall inside the
envelope, not a claim about how likely any particular value inside it is.
Reporting anything from this method as a "distribution" or a
"confidence level" would misrepresent what the method itself claims to
produce, and this document does not do that anywhere below.

### 1.2 The canonical propagation set is five simulations, all at full corner magnitude — not interior points

Source A, verbatim: *"This eigenspace perturbation framework gives us 5
distinct extremal states of the Reynolds stress tensor... These correspond
to 3 extremal states of the componentiality (1C, 2C, 3C) and 2 extremal
alignments of the Reynolds stress eigenvectors, (v_min, v_max)... so the
bounds correspond to the set {(1C, v_max), (1C, v_min), (2C, v_max),
(2C, v_min), (3C, v_max/v_min)}."* And, on the perturbation magnitude:
*"Instead of relying on a user-defined magnitude for Δ_B, we set Δ_B =
1.0 so that the three limiting states are considered. These are the
default settings."*

So the prescribed method is not a sweep over moderation magnitude at all
— **it is defined at the full corner, by default, with no interior
points in the canonical 5-simulation set.** Moderation (`f` or `Δ_B < 1`,
the mechanism our `r4` sweep exercises) is a documented departure from
this default, motivated purely by convergence or plausibility concerns
(Heyse et al. 2021's data-driven variant; Matha & Morsbach 2023's
moderation factor — both already cited in `LITERATURE_REPRODUCTION_REVIEW.md`
§2), not part of the propagation prescription itself.

### 1.3 3C is structurally cheaper, not just empirically easier here

Source A, verbatim: *"For the 3C limiting state, the Reynolds stress
ellipsoid is spherical. Due to rotational symmetry, all alignments of
this spherical Reynolds stress ellipsoid are identical and eigenvector
perturbations are superfluous."* This is why the canonical set has 5
simulations, not 6 (2+2+2): 3C needs exactly one run, 1C and 2C each need
two (the two eigenvector extremes). Independent of anything found on the
hump, the theory itself singles out 3C as the one corner that does not
carry an eigenvector degree of freedom — a structural fact, not a
coincidence of what happened to converge for us.

### 1.4 The theory assumes convergence as a precondition and has no fallback for its absence

Source A, verbatim, on the module's operating procedure: *"For smooth
operation, it is best to have performed a baseline simulation with SU2
and have achieved sufficient convergence... and, if run through the
python script, can provide converged perturbed solutions."* And: *"As the
solution converges, the Reynolds Stress also converges to its perturbed
state. Once a perturbed solution is converged, the python script moves on
to the next eigenspace perturbation to be performed."*

**Convergence of every one of the 5 simulations is a working precondition
of the method as described, not a contingency it plans for.** Nowhere in
either source read for this document is there a discussion of what to
report, or how to modify the bound, if one of the 5 required states
cannot be reached. This is not an oversight this document can fill in
with confidence — it is a genuine gap in the published guidance,
consistent with (and now doubly confirmed alongside) the finding already
recorded in `LITERATURE_REPRODUCTION_REVIEW.md` §2 that convergence
difficulty is a known, named, corner-dependent hazard with no
documented fallback anywhere read this session.

### 1.5 A genuinely distributional alternative exists in the literature, but it is a different framework, not an extension of this one

A random-matrix-theoretic line of work (Xiao, Wu, Wang, Sun & Roy,
"A Random Matrix Approach for Quantifying Model-Form Uncertainties in
Turbulence Modeling," arXiv:1603.09656, also *Computer Methods in Applied
Mechanics and Engineering*) constructs a genuine maximum-entropy
**probability distribution** over the space of realizable Reynolds-stress
tensors and samples from it (with Bayesian updating against data where
available), rather than running a fixed set of deterministic corner
cases. This is the literature's actual answer to "how do you get a
distribution rather than a bound out of RANS structural uncertainty" —
but it is a separate machinery (a random-field sampler satisfying
positive-semi-definiteness constraints, typically evaluated with dozens
of Monte Carlo draws, not five deterministic runs), not something the
eigenspace-corner data this project already holds can be repurposed into.
**Not implemented, not attempted, and not verified to fare any better on
a short/aggressive bubble than the corner method does** — flagged as a
genuine open question for future work in §6, not claimed as a fallback
here. Read at abstract/secondary-source depth only (not full text), so it
is cited here as a named alternative and nothing more — no claim in this
document rests on its content.

---

## 2. What is reachable on this case — every input gate-checked

| point | direction / corner | Δ | status (`check_convergence.py`) | separation x/c | reattachment x/c |
| --- | --- | --- | --- | --- | --- |
| baseline | unperturbed | 0.00 | `CONVERGED: solver printed 'SIMPLE solution converged in 1795 iterations'` | 0.6544 | 1.2534 |
| interior, oneC direction | 1C | 0.05 | `CONVERGED: solver printed 'SIMPLE solution converged in 2124 iterations'` | 0.6534 | 1.3077 |
| full corner | 3C (isotropic) | 1.00 | `CONVERGED: solver printed 'SIMPLE solution converged in 2948 iterations'` | 0.6589 | 1.1069 |
| full corner | 1C | 1.00 | `NOT_CONVERGED: no 'SIMPLE solution converged' string...` | — | excluded |
| full corner | 2C | 1.00 | `NOT_CONVERGED: no 'SIMPLE solution converged' string...` | — | excluded |

Commands run (reproducible): `python3 scripts/check_convergence.py
demo-output/website/solve_registry/r4_oneC_d0.00_20260729T204314Z.log
--oneline`; the analogous call on `r4_oneC_d0.05_...log`,
`uq_threeC_...log`, `uq_oneC_...log`, `uq_twoC_...log`.

**No interior (moderated) sweep exists in either the 2C or 3C direction
at all.** Checked directly against `system/fvOptions` across every case
in `r4_band_tightening_hump/`: every one hardcodes `perturbCorner oneC;`
(confirmed by `grep perturbCorner .../oneC_delta0.10/system/fvOptions` →
`perturbCorner oneC;`, and identically across all other Delta points).
The entire Delta-moderation campaign this project ran tonight — the one
that found and characterized the fragmentation/non-convergence pattern —
swept only the 1C direction. 2C has exactly one data point in the whole
project (its own full, unconverged corner) and 3C has exactly one
(its own full, converged corner) — neither has ever been swept at
intermediate magnitude.

---

## 3. What cannot be claimed

Stated plainly, because this is the more useful half of the answer:

1. **The canonical 5-simulation deterministic bound cannot be constructed
   on this case.** It requires both eigenvector extremes at both 1C and
   2C plus the single 3C state — 5 runs. We have 1 of the 5 (3C).
   1C contributes zero canonical (full-corner, either-eigenvector-extreme)
   points; 2C contributes zero of any kind, canonical or otherwise. A
   claim of "the eigenspace-perturbation bound on this case" cannot
   honestly be made — there is no version of it that does not silently
   assume convergence this case does not have.
2. **The genuinely distributional alternative (§1.5) is not available
   either**, on the evidence gathered tonight: it requires new sampling
   machinery not built this session, and there is no basis in anything
   read here to assume it converges better on a short, violent
   separation bubble than the corner method does — that is untested, not
   ruled in.
3. **The one interior data point we have (Δ=0.05, 1C direction) cannot be
   extrapolated toward its own corner.** The band-tightening study
   already established (`F6a_epistemic_band.md`) that the response is
   non-monotonic and that the flow fragments into a multi-valued
   structure starting at Δ=0.10 — a single converged point near the
   origin says something about *local* sensitivity (§5) and nothing
   defensible about the corner's value, which the fragmented, unconverged
   interior of the sweep does not let us interpolate toward.
4. **The 2C direction is not merely under-sampled, it is entirely
   unconstrained by any converged data.** Nothing computed this session
   bounds, weights, or even locally characterizes the 2C contribution to
   the true envelope. Any propagation scheme that reports a number for
   "the eigenspace-perturbation uncertainty" without flagging this as a
   totally open direction would be reporting confidence the data does not
   support.

---

## 4. What is defensible: a reduced, explicitly non-canonical envelope

Given §3, the only honest construction from data this project can
actually converge is **not** the theory's prescribed bound. It is a
*reduced envelope* — the union of whichever of the theory's designated
extremal directions happen to have at least one converged point, plus the
baseline — reported as exactly that, not relabeled as the canonical
method.

| quantity | value |
| --- | --- |
| Reduced envelope (reattachment x/c) | **[1.1069, 1.3077]** |
| Driven by | 3C corner (lower) and Δ=0.05, 1C-direction interior (upper) |
| Contains NASA experiment (1.100)? | **NO** — 3C sits 0.63% above it |
| Compare: canonical/full published band (channel 1 + channel 3, all channels, converged points only) | [1.0717, 1.2534], contains 1.100 (`F6a_epistemic_band.md`) |

**This is the single most important number in this document.** Restricted
to only the data this specific theory's own machinery can actually
converge on this case, channel 3 alone does not bound the experiment —
the lower edge of the reduced envelope (1.1069) sits *above* 1.100, not
below it. The published band's containment of the experiment is carried
entirely by channel 1 (kOmega's converged 1.0717), a different and
non-theoretical mechanism (four independent closure models happening to
disagree about which side of 1.100 they land on) — already characterized
in `F6a_epistemic_band.md` as "closer to a coincidence that happened to be
informative... not worth promoting to a method." That characterization is
reinforced, not contradicted, by this document: the one channel that *is*
a designed, theory-grounded bound cannot currently be evaluated on this
case at all in its prescribed form, and the reduced version of it that
*can* be evaluated does not itself contain the truth.

---

## 5. Local sensitivity: a real, converged data point, not a bound

The Δ=0.05 point is informative on its own terms, independent of whether
it can be extended toward its corner. Moving from baseline (1.2534) to
Δ=0.05 along the 1C direction moved reattachment to 1.3077 — **away from
the experiment**, not toward it (+4.33% relative to baseline, +18.88% vs.
experiment against baseline's own +13.95%). This is a genuine, gate-checked
statement about the *local derivative* of reattachment with respect to
1C-directed anisotropy perturbation near Δ=0: **positive**, i.e. pushing
in the 1C direction initially makes the over-prediction worse, not
better, on this case. It corroborates from an independent angle the
non-monotonicity `F6a_epistemic_band.md` already found further out in the
sweep (the response rises through Δ≈0.15 before catastrophically falling
in the untested/unconverged Δ≈0.15–0.25 window) — the local slope at
the very start of the sweep already points the "wrong" way, which is
consistent with, not contradicted by, that later finding.

One point does not define a distribution and this document does not
treat it as one. What it rules out is the comfortable assumption that
"the corner would obviously pull the number down smoothly if only we
could reach it" — the nearest reachable evidence says the opposite, at
least initially.

---

## 6. Ambition: two concrete, literature-grounded, untested levers

Not a repeat of the diagnostics already run (`boundedU`, `finemesh` —
both in `F6a_epistemic_band.md`, both eliminated as the cause of the
corner non-convergence). Two different things, found while reading
Source A for this document, that have not been tried on this case:

1. **Gradual eigenvalue-perturbation ramp, as the reference implementation
   describes.** Source A: *"An under-relaxation factor is used to
   gradually march the stress tensor to the perturbed state. This makes
   the simulation numerically stabler."* Our own `uqEigPerturb`
   `fvOptions` applies the full target `blendDelta` from the first
   iteration of every run, with no ramp — a genuine, citable,
   mechanically distinct difference from the reference implementation's
   own described practice, and untested here.
2. **Initialize the perturbed run from the converged baseline field,
   not a fresh uniform-freestream IC.** Every point in this project's
   Delta sweep starts cold (confirmed: `0/` in each `r4_...` case is a
   uniform-freestream initial condition, not a restart from `oneC_delta0.00`'s
   converged state or from any other Delta's result). Source A's
   description of the module's operation implies perturbed runs proceed
   from an already-converged baseline case. Combined with lever 1, this
   is the standard multi-stage RANS restart strategy already used
   successfully elsewhere in this study (realizableKE's fix, documented
   in `F6a_epistemic_band.md`) — carries no information about the
   experimental target, only about the flow physics, and has not been
   tried on the 1C/2C corners specifically.

Neither is attempted in this document — both are proposed as the next,
specific, falsifiable tests, not run against today's 3-core/4-GB budget
without being asked for.

---

## 7. Summary

- The published theory prescribes a **deterministic envelope from 5
  full-corner simulations**, not a probability distribution — quoted
  directly from the reference implementation's own paper, not inferred.
- On this case, **1 of those 5 simulations is reachable** (3C); 1C
  contributes only an off-canonical interior point; 2C contributes
  nothing converged at any magnitude.
- The canonical bound **cannot be constructed** here. A reduced,
  explicitly-labeled substitute can, and is computed above: **[1.1069,
  1.3077]**, which **does not contain the experimental value on its own**
  — that containment currently rests entirely on channel 1, a different
  and non-theoretical mechanism.
- The one usable interior data point is informative about local
  sensitivity (positive, i.e. away from the experiment) and is reported
  as exactly that — not stretched into a bound or a distribution it
  cannot support.
- Two specific, cited, untested numerical levers are named for anyone
  who wants to push on the corners again; a genuinely distributional
  alternative exists in the wider literature but is out of scope today.

---

## 8. 2026-07-30, later: both levers tried, and both failed — a negative result, precisely stated

**This section is about whether the corners are reachable. It is not a
finding that the band is wrong.** The published band (`F6a_epistemic_band.md`)
rests entirely on runs that met their own convergence gate; nothing below
touches those runs or that number. What follows establishes a limit on how
far the eigenspace-perturbation *machinery* can be pushed on this specific
case, not a defect in what has already been reported.

### What was tried

Three single-variable diagnostics, each isolating one candidate fix, none
replacing or resubmitting an existing sweep point:

| case | lever tested | IC | ramp | target |
| --- | --- | --- | --- | --- |
| `oneC_delta1.00_initFromBaseline` | §6 lever 2 alone | converged baseline field (t=1795) | none — full Δ=1 from iteration 1 | 1C corner |
| `twoC_delta1.00_initFromBaseline` | §6 lever 2 alone | converged baseline field (t=1795) | none — full Δ=1 from iteration 1 | 2C corner |
| `oneC_delta1.00_ramp` | §6 lever 1 alone | fresh uniform freestream (unchanged from every other sweep point) | linear 0→1 over first 1500 iterations, held at 1 for the remaining ~2300 | 1C corner |

All three ran to their 3800-iteration cap. **All three came back
`NOT_CONVERGED` from `scripts/check_convergence.py`** — zero occurrences
of `SIMPLE solution converged` in any of the three logs, checked the same
way as every other run tonight.

### The residual behaviour, because stagnation and wandering are different animals

**1C (`initFromBaseline` and `ramp`) both settle into an identical, stable,
non-zero floor — not a wander, not a blow-up.** `initFromBaseline`'s Ux
Initial residual: 0.125 (t=1000) → 0.143 → 0.159 → 0.169 → 0.172 → 0.172
→ 0.172 (t=3800) — monotonically approaches a fixed plateau and holds
it, with the velocity limiter settling at 64% of cells from roughly
t=2500 onward and staying there. `ramp`, despite reaching Δ=1 gradually
over 1500 iterations rather than instantly, lands at essentially the
*same* plateau by t=3800 (Ux Initial 0.170, 64% of cells limited) — the
two different paths to the same target converge to the same non-converged
state. **This is the strongest evidence yet that 1C's non-convergence at
full strength is a property of the target perturbed state itself on this
mesh, not an artifact of how the run gets there** — two genuinely
different numerical approaches, one starting from a converged field with
no transient at all, both land in the same place.

**2C (`initFromBaseline`) is a materially different animal: a slow drift
away from a clean start, not a floor and not an instant blow-up.** Ux
Initial residual: 4.69e-5 (t=1000) → 2.54e-4 → 7.62e-4 → 2.89e-3 → 4.81e-3
(t=3000) — **grows monotonically by a factor of ~103× over 2000
iterations**, with the velocity limiter staying at exactly 0% until
t≈2000 and then activating on a tiny fraction of cells (0.1–0.22%,
essentially noise-level compared to 1C's 64%). From t=3000 to t=3800 the
growth flattens and very slightly recedes (4.81e-3 → 4.34e-3). This is
orders of magnitude closer to the gate than 1C ever gets (still ~8,700×
over the 5e-7 target on Ux, versus 1C's ~344,000×), and it is *growing
away from* a genuinely clean initial state rather than diverging
outright — a residual floor being approached from below with a slow
climb, not chaos. Whether it would eventually turn over and decay given
much more budget is not established either way by this run; what is
established is that it did not in the 3800 iterations tried, and that its
character is qualitatively different from 1C's.

### What this settles, and what it does not

**Settled**: both documented literature remedies for hard-converging
eigenspace-perturbation corners — initializing from a converged field,
and ramping the perturbation gradually rather than applying it instantly
— were tried on this case and neither rescues either corner within a
3800-iteration budget. Combined with the eight moderation-magnitude points
already tested (`F6a_epistemic_band.md`), that is now five independent
treatments of the 1C direction alone (eight magnitudes at Δ<1 from a
fresh IC with no ramp, plus full-strength from a converged IC, plus
full-strength with a ramp), all non-convergent.

**Not settled, and this is the honest correction the evidence demands**:
`F6a_epistemic_band.md`'s "moderation does not rescue them here" and
"appears to have no accessible steady RANS solution... on every mesh and
scheme variant tried so far" language was written **before** either of
these two levers had been tried. At the time it was written, that
conclusion rested on eight points that all shared the same untested
assumption — instant full-strength application from a cold, fresh
initial condition — and calling the resulting limit "intrinsic" was
reaching past what the evidence at that time actually supported, in
exactly the same shape as this project's other overreach corrections
tonight (a claim stated more strongly than the runs behind it justified).
**The corrected statement**: the intrinsic-limit reading is now
independently supported by five treatments instead of eight variations on
one treatment, and for 1C specifically the two different paths (clean IC,
gradual ramp) landing on the identical plateau is stronger evidence than
the original moderation sweep alone provided. For 2C, the picture is
still open — its behavior under this treatment is different enough
(orders of magnitude closer, growing rather than floored, no violent
limiting) that "intrinsic limit" is not yet the right word for 2C the way
it is for 1C. This is a genuinely corner-dependent result, which is
exactly what Heyse et al. (2021) report on their own, milder geometry
(`LITERATURE_REPRODUCTION_REVIEW.md` §2: *"the convergence difficulties
were dependent on the particular limiting state"*) — now corroborated,
not merely cited, on a harder case.

**What remains untried**: nothing the eigenspace-perturbation literature
read this session documents as a remedy. Both named levers (§6) are now
exhausted on both corners. What is left is either a fundamentally
different numerical approach not described in any source read here (a
different pressure-velocity coupling, a coupled or pseudo-transient
solver instead of SIMPLE, or a genuinely unsteady/URANS treatment — the
last of which the literature explicitly does *not* recommend for this
purpose, per §2's earlier finding), or the different framework named in
§1.5 (random matrix / Bayesian sampling), which does not depend on
reaching these specific corner states at all. Per this task's explicit
instruction, no fourth corner-convergence variant was attempted after
these three — three independent, literature-grounded treatments failing
the same way is a result, not a reason to keep guessing.

### The question that decides where this goes next: do the corners have to be reachable for propagation to matter?

**Yes, for the eigenspace-perturbation method specifically — not as an
incidental difficulty but because the corners ARE the method's
computational content.** Re-read §1.2: the theory does not describe
"propagation" as a step performed *on* the corner results after they are
obtained — the corners *are* the prescribed output. Source A's own words,
quoted in §1.1: *"the uncertainty bounds on the profiles are engendered
by the union of all the states lying in the set of perturbed RANS
simulations."* There is no propagation step in the cited theory that
operates on anything short of that union. A construction built from
"whatever states happen to converge" is not a weaker version of the
same method — it is a *different, uncited* construction, which is exactly
why §4 of this document labeled the reduced envelope explicitly as
non-canonical rather than presenting it as the theory's output. That
labeling is not caution for its own sake; it is the accurate description
of what was actually computed.

So: **the three failures cost the theoretical propagation objective
everything it had left to lose, and nothing that has not already been
priced in.** §4's reduced envelope was already the honest ceiling on what
this specific method could support without the corners, computed and
reported before these three tests ran. The three tests were the last
opportunity, prescribed by the literature itself, to raise that ceiling
by making the real corners reachable — for 1C, that opportunity is now
closed by direct, repeated, path-independent evidence; for 2C, it is not
fully closed but nothing tried tonight opened it either. **The practical
consequence for this thread: eigenspace-perturbation propagation, in the
sense the cited papers define it, is not currently achievable on this
case beyond the reduced, non-containing envelope already reported in §4.**
Any further "propagation" work that wants a defensible band from
convergent states alone is not an extension of this method — it would be
a new, differently-justified construction (most plausibly the random-
matrix/Bayesian route named in §1.5, which was built by a different group
precisely because it does not require sampling the extremal corners the
way the Emory/Iaccarino method does), and should be scoped, budgeted, and
reported as that, not folded into this document's method as though it
were the same thing with a smaller number attached.
