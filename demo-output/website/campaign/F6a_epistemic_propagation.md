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

---

## 9. 2026-07-30: scoping the random-matrix/Bayesian alternative (§1.5) — not started, per explicit instruction

**Source, read in full this time (not abstract-depth):** Xiao, H., Wang,
J.-X. & Ghanem, R.G., "A Random Matrix Approach for Quantifying
Model-Form Uncertainties in Turbulence Modeling," arXiv:1603.09656
(2016), also *Computer Methods in Applied Mechanics and Engineering*.
Open access (arXiv). Read via local `pdftotext` extraction of the full
PDF (same method used for §1's sources), not the abstract or a secondary
summary. All four questions below are answered from the paper's own
methodology and results sections, quoted or cited by line.

**No solve was launched to answer this. This section is research and
arithmetic against already-measured numbers from tonight's own runs, per
the explicit instruction to scope, not start.**

### 9.1 What it requires as input

A single converged baseline RANS field (the paper's own §4.1/Table 1
lists "Baseline RANS" as one of its two meshes/inputs, alongside a
separate, coarser "KL mesh" used only for the random-field expansion) —
**we already have this** (the hump's converged kOmegaSST baseline,
1.2534, `check_convergence.py`-confirmed CONVERGED). Beyond that, the
method requires machinery this project does not currently have in any
form:

1. **A Cholesky factorization of the normalized (barycentric) Reynolds
   stress tensor**, used specifically because it "guarantee[s] realizability
   ...by construction" (paper's own abstract) — a different realizability
   mechanism from the eigenvalue-perturbation method's barycentric
   projection, not interchangeable with it.
2. **A Karhunen–Loève (KL) expansion of a spatially correlated Gaussian
   random field** over the mesh, truncated to `N_KL` modes (the paper's
   own demonstration: `N_KL = 30` modes on a `50×30` auxiliary mesh, with
   user-chosen correlation length scales `l_x/H = 2, l_y/H = 1`) — this
   requires either building a KL-mode solver (a mesh-based eigenvalue
   problem for a chosen covariance kernel) or finding and adapting an
   existing one; neither exists in this project's stack.
3. **A polynomial chaos expansion** (the paper's demonstration: order
   `N_p = 3`) mapping independent Gaussian variables to the random
   Reynolds-stress field.
4. **A chosen dispersion parameter** `δ` (or spatially-varying `δ(x)`) —
   a genuinely subjective input the paper itself calls "guided by the
   subjective belief of the user on the uncertainty in the Reynolds
   stresses" (§4.1) — this project has no principled way to set it yet,
   and the paper's own two demonstrated values (`δ=0.2`, `δ=0.6`) produce
   visibly different distributions on the same case, so the choice is not
   a detail.

**None of items 1–4 exist in this project today.** This is new
mathematical/software infrastructure, not a configuration change to the
existing `uqEigPerturb` `fvOptions` — a materially larger lift than
either lever tried in §8, both of which reused code that already existed.

### 9.2 Does it need converged corner states — and does it inherit the same wall?

**By construction, no — explicitly.** The paper's own discussion section
states the maximum-entropy distribution has *"zero measure on the
two-component (and one-component) limiting states"* (§5) — the 1C/2C
corners are a probability-zero edge case of the sampling distribution,
not a target. Individual Monte Carlo draws essentially never land exactly
on a corner, so the method does not require converging AT the corner
states the way the Emory/Iaccarino method structurally does. **This is a
real, citable difference, not a technicality dodged.**

**But this is not the same as escaping the wall — it relocates it, and
arguably makes it more damaging.** The method still requires converging a
large number of RANS solves at a *spread* of anisotropy-perturbation
magnitudes governed by `δ`. The paper's own "large" demonstration case
(`δ=0.6`) is explicitly described as producing "appreciable deviations"
that can approach the realizability boundary in high-shear regions —
qualitatively the same territory (moderate-to-large anisotropy departure
from baseline) as this project's own `r4` moderation sweep, which showed
**fragmentation starting at Δ=0.10** and total non-convergence from
Δ=0.10 through Δ=0.75 (`F6a_epistemic_band.md`). A Monte Carlo sampler
drawing ~100 realizations from a distribution with real probability mass
in that same magnitude range would, on the evidence this project already
has, plausibly see a meaningful fraction of its required samples fail to
converge on this specific short, violent bubble — **not all of them, the
way the deterministic 5-simulation method does, but enough to matter, and
in a way that is worse for a Monte Carlo estimate specifically**: silently
dropping the hardest-to-converge samples (the ones furthest from baseline)
biases the resulting distribution toward the calm center and away from
exactly the tail behavior a model-form uncertainty estimate exists to
capture. Restricting `δ` small enough to avoid this reliably (closer to
our own converged Δ=0.05, which moved *away* from the experiment) would
likely buy convergence at the cost of a distribution too narrow to be
informative — the same trade this project already met once tonight.

**Verdict on this question, stated plainly per the instruction: this
route does not inherit the *identical* wall (it does not require the
exact, unreachable corner states), but it plausibly inherits a
*statistical* version of the same wall through its intermediate samples,
on this specific case, based on evidence already in hand — not proven,
since no sample has actually been run, but a real, evidence-grounded risk
that must be disclosed before committing resources, not discovered after.**

### 9.3 The smallest honest first result

Not a single gated number in the same sense as the corner method's — this
method's minimal unit of *output* is a distribution (or at least a mean
and credible interval), built from an ensemble, not a single converged
run. There is no literature-prescribed minimum ensemble size read in this
source; the paper's own working choice is 100 velocity-propagation
samples (drawn from 1000 cheaper Reynolds-stress-only samples). A smaller
first test — perhaps 20–30 propagated samples — could produce a rough,
explicitly-labeled-as-under-sampled kernel density estimate, but shrinking
the ensemble undermines the specific thing this method is for (a
Monte-Carlo-converged distribution), so "smallest honest" here means
*"smallest ensemble whose distribution is disclosed as provisional,"* not
*"one run,"* the way §4's reduced envelope could honestly be built from
three. The honest floor is: **build the software (§9.1) once, on the
project's own baseline field, and run enough samples that the *convergence
failure rate itself* becomes a reportable number** — even a failed
majority would be informative, provided it is reported as such rather
than quietly filtered out.

### 9.4 What it would cost — measured against tonight's own numbers, not guessed

**No new solve was run to produce this estimate.** It is arithmetic
against this project's own already-measured per-run wall times on the
identical 51,626-cell hump mesh, same solver, same host, from tonight's
`r4` sweep (`solve_registry`):

| Δ (r4 sweep) | outcome | wall time (1 core) |
| --- | --- | --- |
| 0.00 | converged, 1795 iter | 334 s |
| 0.05 | converged, 2124 iter | 429 s |
| 0.10 | capped at 3800, not converged | 536 s |
| 0.15 | capped at 3800, not converged | 1096 s (heavy GAMG struggle) |
| 0.25 | capped at 3800, not converged | 636 s |
| 0.50 | capped at 3800, diverged | 482 s |
| 0.75 | capped at 3800, diverged | 467 s |

Median across the non-trivial points: **~500–650 s/run**, with one
outlier at 1096 s reflecting real pressure-solve difficulty under
moderate perturbation — itself evidence that "harder" samples cost more
wall time as well as more risk, not just more risk. Applying the paper's
own 100-velocity-propagation-sample requirement (§9.1) at this measured
per-run cost: **100 × ~500–1100 s ≈ 14–31 core-hours of serial compute**,
or roughly **5–10 hours wall-clock at this task's own 3-core budget** —
before accounting for any sample that runs to a larger cap than 3800 or
needs re-launching after a crash, and **before any of the software in
§9.1 has been written at all.** That software item has no honest
core-minute estimate — it is a mathematics-and-implementation task, not a
compute one, and should be costed and reviewed separately rather than
folded into a core-hour number that would understate it.

### 9.5 Recommendation

**Do not start this on the hump.** The evidence-grounded risk in §9.2 —
that a meaningful fraction of the required intermediate-magnitude samples
would likely fail to converge on this specific short, violent bubble, for
reasons this project has already established independently — combined
with the substantial unbuilt-software cost in §9.1, means the hump is not
the case to spend that investment proving out this method on. **The
paper's own demonstration geometry is flow over periodic hills at
Re=2800** (Breuer et al.) — mild, well-behaved, converges even at its
"large" dispersion setting per the paper's own account — and **this
project already has an incomplete, queued campaign on exactly that
geometry** (`F6b — periodic hills`, `demo-output/website/dafoam/f6b_periodic_hills/`,
currently DRAFT, gate rung not yet run). If this framework is pursued at
all, F6b is the properly-scoped first target: a geometry class the
method's own authors validated it on, not a second attempt on the one
case this project has now shown breaks two different UQ machineries in
two different ways. Brought here for a decision, not started.

---

## 10. 2026-07-30, later still: the corner runs behind §§2-8 were applying the perturbation with the wrong sign — correction, with the numbers that survive and the numbers that do not

Found while building the random-matrix framework §9 scoped, not while looking
for it. Full record, evidence and reproduction: **`F6d_random_matrix_uq.md` §4**.
This section states only what it changes here.

### 10.1 The finding

Every `system/fvOptions` under `demo-output/website/dafoam/f6a_epistemic_band/`
(18 dictionaries; `grep -rl "eqn += fvc::div(deltaR)" --include=fvOptions` →
18, and zero use `-=`) ends its `codeAddSup` with

```
eqn += fvc::div(deltaR);        deltaR = blendDelta * 2k (bPert - bB)
```

In OpenFOAM an fvOption's `eqn += X` places **+X on the right-hand side** of the
momentum equation, and simpleFoam's `divDevReff(U) = -div(2 nuEff symm(grad U))`
already carries the modelled stress on the left. The effective deviatoric
Reynolds stress is therefore `R_eff = R_model - deltaR`, so

```
b_eff = 2 b_B - b_pert       i.e.    b_eff - b_B = -(b_pert - b_B)
```

**the perturbation is applied backwards.** Established four independent ways —
the OpenFOAM v2606 sources (`fvMatrix.C:1682`, `meanVelocityForce.C:209`,
`simpleFoam/UEqn.H:9,11`, `linearViscousStress.C:107-117`); a controlled
four-run solver experiment that discriminates the two hypotheses by the driving
pressure gradient (`f6d_random_matrix_uq/signcheck/`, agreement 0.055% and
0.016%); a one-character A/B replication; and a realizability audit.

### 10.2 What it did to these runs, measured on this case's own mesh

Fraction of the hump's 51,626 cells handed a Reynolds stress with a negative
eigenvalue — i.e. one no velocity field can have — computed on this case's own
converged baseline field (`r4_band_tightening_hump/oneC_delta0.00/1795/`):

| corner | intended `b_pert` | actual, with `eqn +=` |
| --- | --- | --- |
| 1C | 0.90% (inherited from the baseline itself) | **95.93%** |
| 2C | 0.13% | 0.23% |
| 3C | 0.00% | 4.33% |

And the corresponding solver behaviour, from the runs' own logs:
`uq_oneC_20260729T023701Z.log` reports
`limitVelocity limitVelocity1 Limited 24864 (48.16%) of cells`, while the same
case with the sign corrected reports `Limited 0 (0%) of cells`.

That is the mechanism behind everything §8 characterised as an intrinsic
property of the target state: half the mesh was being velocity-clipped because
it was being fed a non-realizable stress. Note also that this explains the
otherwise odd corner-dependence §8 puzzled over — with the flipped sign, 3C
becomes merely "double the baseline anisotropy" (mild, 4.33% non-realizable,
and it converged), while 1C becomes a reflection far outside the barycentric
triangle (96% non-realizable, and it never converged).

### 10.3 What survives

**§8's headline negative result stands.** Re-running all three corners on this
case, this mesh, these schemes, from this converged baseline, changing nothing
but the sign (`f6d_random_matrix_uq/f6a_recheck/`), still returns
`NOT_CONVERGED` from `scripts/check_convergence.py` at the 3,800-iteration cap,
with Ux initial residuals plateauing at 7.08e-3 (1C), 1.05e-3 (2C), 2.85e-3
(3C). **The corners are still not reachable on this case within this budget.**

**§1's reading of the literature stands** — it is about what the papers say, and
nothing here touches that.

**Channel 1 stands.** The four-model spread that actually carries
`F6a_epistemic_band.md`'s published band contains no eigenvalue perturbation at
all.

### 10.4 What does not survive

1. **The channel-3 numbers.** 1C 0.5278, 2C 0.6701, 3C 1.1069 are not the
   1C/2C/3C corner states. They are the states `2 b_B - b_pert`.
2. **§4's reduced envelope [1.1069, 1.3077]**, labelled in this document as
   "the single most important number in this document." Its lower edge is the
   3C run above; its upper edge is the Δ=0.05 point of a sweep that swept the
   flipped direction. The interval is withdrawn. The observation it supported —
   that channel 3 alone does not bound the experiment — is **not** re-established
   by anything here and must be treated as open.
3. **§5's local-sensitivity claim** that "pushing in the 1C direction initially
   makes the over-prediction worse." The Δ=0.05 point was pushing in the
   *opposite* direction, so the measured slope has the wrong sign attached to it.
4. **§8's diagnosis** that 1C's plateau is "a property of the target perturbed
   state itself on this mesh." The target state actually imposed was
   non-realizable in 96% of cells. §8's two levers (restart-from-converged,
   gradual ramp) were also tested against that same wrong target, so their
   failure says nothing about the intended corners.
5. **§9.2's verdict** that the random-matrix route "plausibly inherits a
   statistical version of the same wall" on the hump. It was reasoned from the
   flipped-sign Δ sweep. It has since been tested directly on F6b instead:
   38 of 40 samples produced a usable solution (`F6d_random_matrix_uq.md` §6.1),
   so the feared wholesale sample loss did not occur there. **§9.2's other
   prediction — that gating out the hard samples biases the distribution toward
   the calm centre — was confirmed and is now a measured number**
   (`F6d_random_matrix_uq.md` §6.4).

### 10.4b What this does NOT touch: the published band and the ACT

Traced case by case rather than reasoned from prose, because the shoot script
depends on it. `F6a_epistemic_band.md`'s published band `[1.0717, 1.2534]` has
its lower edge in `channel1_rans_sweep/kOmega` and its upper edge in the
kOmegaSST baseline. Neither is perturbed: the four `channel1_rans_sweep/*/system/fvOptions`
are the only four `fvOptions` under `f6a_epistemic_band/` that do **not** contain
`deltaR`, and each holds a single `limitVelocity1` entry and nothing else. The
one gate-met channel-3 point, `threeC` at 1.1069, lies strictly inside the band
and sets neither endpoint. **The band is a pure turbulence-model-comparison
result and is unaffected by the sign error.**

The `nasa-hump` ACT is likewise unaffected. Its "Reattachment model-form band
±20%" is a constant in the workflow — `sdk/workflows/nasa_hump.py:50`,
`REATTACHMENT_MODEL_BAND = 0.20` — justified in the transcript itself by the
documented fact that a linear eddy-viscosity closure over-predicts this bubble,
and independently corroborated by NASA's own SST CFD landing at 1.25–1.27
(`F6_closure_aligned_flows.md`). It does not trace to this family's
eigenvalue-perturbation work in any way.

The one channel-3 number with public exposure is `threeC`'s **1.1069**, quoted
on `D9_TALKING_POINTS.md` and `benchmarks.html` as "closest single check to the
experiment". The value and its +0.63% offset are real and gate-met; what is
withdrawn is the description of that run as the isotropic-limit corner. It
imposed `b_eff = 2 b_Bouss`. See `F6a_epistemic_band.md` for the full
public-surface audit table.

### 10.5 The new, non-gate-passing observation this correction produces

With the sign corrected, the hump's 1C and 2C corners give reattachment
x/c **1.0409** and **1.1085**, bracketing the NASA experimental **1.100** from
below and above (−5.4%, +0.8%), with the velocity limiter completely inactive
and a clean single-bubble wall trace where the recorded runs had 230+ noise
crossings. **These are not gate-passing numbers and must not be quoted as a
band.** They are recorded as the reason a fourth corner-convergence attempt —
which §8 explicitly closed the door on — is now worth reopening, because the
three attempts §8 counted were never running the method.
