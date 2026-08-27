# Uncertainty doctrine (internal; never referenced on camera)

Distilled 2026-07-24 from docs/papers by the chief agent. Sources: ASME V&V
20-2009 (Dowding overview, Paper2.pdf), Eca & Hoekstra 2014 JCP (Paper1.pdf),
Oberkampf & Roy 2010 (Paper3.pdf, frontmatter), Mouzahir & Lermusiaux OSM26
sparse-GP closure poster, Xia et al. 2025 JMSE 13:431 (GP error
quantification).

Every act quantifies all three channels. "Not quantified" is retired as a
displayed state; if a channel genuinely cannot be quantified the act must say
what it assumed instead (input: "No input uncertainty was assumed for this
problem.").

## Channel recipes

1. INPUT (u_input): propagate stated input spreads through the model by Mean
   Value (variance propagation) or Latin Hypercube sampling (V&V-20 sect.
   uinput). When the owner specifies exact conditions, the channel displays
   the assumption sentence, not a dash.

2. NUMERICAL (u_num): grid-refinement study per Eca & Hoekstra 2014:
   3+ genuinely different meshes (verify cell counts differ), least-squares
   fit of the observed order p, uncertainty from the fit with safety factor
   (GCI-style, Fs = 1.25); clamp p to [0.5, 2.5] for band computation; on
   non-monotone rungs fall back to max-spread * 1.25 and say so. For discrete
   design grids (optimization acts) u_num additionally includes the
   grid-spacing bracket: local quadratic fit of the objective around the
   winner, half-step variation = the between-grid-points uncertainty.

3. MODEL (u_model, epistemic): per V&V-20 the model error E = S - D is
   characterized within [E - u_val, E + u_val], u_val^2 = u_num^2 +
   u_input^2 + u_D^2, from VALIDATION comparisons. Two mechanisms, in order
   of preference:
   a. Direct: the case has its own reference (NACA 4412, motorbike drag
      area) -> E and u_val computed on the spot.
   b. Transferred: no direct reference -> estimate from the lab's measured
      discrepancy history (validated-case E values, mega-batch ledger,
      screen-vs-solve deltas). Preferred estimator: GP regression over case
      features (body class, Re, mesh quality, solver) predicting |E|;
      posterior mean = the channel value, posterior variance widens the band
      when the case is far from validated support (OOD honesty, per the
      OSM26 poster's confidence gating). Fallback while the GP is thin:
      conservative pool statistic (max of mean+1sigma of |E| over the
      relevant body class). ON CAMERA the method is described only as
      "estimated from the lab's validation history"; never name the GP.
   Special case optimization acts: when the same designs carry both a
   conceptual screen value and a solved value, the measured screen-vs-solve
   discrepancy IS direct model-channel evidence for the screen (airliner:
   |screen L/D - VSPAERO L/D| across the 9 finalists).
   Coefficient-interval propagation (landed 2026-07-27, motorbike case): a
   measured parametric basis for this channel - perturbed-coefficient solve
   sets on a held mesh using the published epistemic intervals for the
   k-omega SST closure coefficients, band = the min/max envelope across the
   set, carried as an interval alongside u_val and never converted to a
   sigma inside the quadrature. Per "Uncertainty Quantification of
   Turbulence Model Closure Coefficients for Transonic Wall-Bounded Flows"
   and "Uncertainty Quantification and Sensitivity Analysis of SA
   Turbulence Model Coefficients in Two and Three Dimensions" (Schaefer et
   al.). Two measured bands now stand side by side, deliberately not
   merged: a two-corner (12/32 full-factorial corners sampled)
   linear-superposition worst-case envelope, 0.4074-0.4390 Cd (0.0316,
   7.6% of baseline); and a 20-sample maximin LHS (seed 20260726) over the
   top three coefficients by measured swing, 0.4100-0.4273 Cd (0.0173,
   4.15%), which characterizes the box interior and is narrower than the
   corner envelope for structural reasons (fewer factors moved, maximin
   avoids vertices, the vertex response is measured super-additive), not
   because interactions stopped mattering. See
   demo-output/website/r2-closure-coefficient-uncertainty/report.json
   (stage_two_lhs) and proposal r2-closure-coefficient-uncertainty for the
   full evidence.

## Combination: the one rule, stated once

A viewer who is shown three channels and no total cannot say how uncertain
the answer is. So an act that quantifies more than one channel reports a
total, and every act computes it the same way.

**The rule.** The combined expanded uncertainty at 95 percent is the root sum
of squares over the channels that carry a figure. It lives in exactly one
function, `combine_expanded` in `sdk/chief_engineer/uq.py`, and no act
implements its own arithmetic. V&V 20 treats independent channels that way,
which is also where the rule's two limits come from.

**Limit 1: unquantified is not zero.** A channel with no figure contributes
nothing to the sum and is displayed as unquantified, never as `0`. The total
therefore covers less than the whole, and the act says which channels it
covers. The NASA hump is the worked example: separation 0.6544 x/c with
numerical 0.0002, model form 0.220, input unquantified, total 0.2200 over the
two quantified channels.

**Limit 2: RSS assumes independence, so a shared evaluation is withheld.**
Two channels that share a point are not independent and squaring both
double-counts that point, reporting a total wider than either channel earned.
The valve study is the worked case: the correlation family's cd = 0.62 member
and the cycle study's coarsest level are the same arithmetic on the same
waveform and both read 1252.8 Pa, so the numerical channel is withheld from
the combination rather than quietly squared into it. Stored studies record
`independent_of_numerical` for this reason.

**A term may not be in the total that the breakdown does not show.** This is
`combine_expanded`'s own contract: the combined band is never presented
without the channel table one level down. A total wider than the channels
displayed is a difference the viewer cannot account for.

`scripts/self_audit.py` enforces both halves: that an act quantifying two or
more channels routes its total through the one call, and that no term enters
the total which the act's own channel table reports unquantified.

## Standing product rules that bind these
- Never a fake number; every displayed value traces to a computation.
- Channel text carries no tool names, no internal study IDs, no method
  jargon (GP, LHS, GCI stay internal; the citation Eca & Hoekstra 2014 is
  allowed for the numerical procedure).
- Every new computed-uncertainty pattern gets a lesson entry so the team
  converges on automatic computation for all future cases.

---

## Dated note — 2026-08-27 — EVERY V&V-20 CITATION IN THIS FILE IS SECONDARY, AND SAYS SO FROM NOW ON

**Appended at the foot. Nothing above is edited, struck or renumbered — other records cite this
file by line. `lines whose number changed above this section: 0`.**

**Sanaa's standing directive, 2026-08-27T16:54Z §0**, captured verbatim at
`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` (boarded `55b95ba9`), her words:

> *"the standard's own text gets acquired this week (MIT library route first) — until it lands,
> every V&V-20 practice cites Dowding 2016 as secondary, stated as such."*

**The measured fact this rests on: ASME V&V 20-2009's own text is NOT ON THIS BOX.** `git ls-tree`
and a raw `find` over `docs/papers/` return exactly two matching artefacts —
`docs/papers/verification_validation/dowding_2016_asme_vv.pdf` and its `.txt` sidecar. **That is a
paper *about* the standard, not the standard.**

**Therefore, governing every V&V-20 reference above and every use made of them:**

- **`:3-4`** — the Sources line reads *"ASME V&V 20-2009 (Dowding overview, Paper2.pdf)"*. **Read
  it as: Dowding 2016, a SECONDARY source describing ASME V&V 20-2009. The primary standard was
  not consulted, because the lab does not hold it.**
- **`:30-31`** — *"per V&V-20 the model error E = S - D is characterized within `[E - u_val,
  E + u_val]`, `u_val^2 = u_num^2 + u_input^2 + u_D^2`"*. **This formulation is taken from Dowding
  2016 and is SECONDARY. It has not been checked against the standard's own text.** The lab may
  use it — Sanaa's directive authorises exactly that — but **no claim of conformance to ASME
  V&V 20 may be made on it**, and any external-facing statement must say "following Dowding
  (2016)'s account of ASME V&V 20-2009", never "per ASME V&V 20".
- **`:17`** and **`:81`** — the LHS/variance-propagation reference and *"V&V 20 treats independent
  channels that way"* are secondary on the same ground.

**What clears this note:** the standard's own text landing under
`docs/papers/verification_validation/` with a title-page verification (`L-144` — never by filename
or hash), after which each line above is re-checked against it and the note is superseded by a
dated successor. **Until then a `u_val` computed by this doctrine is a lab quantity computed by a
published recipe, not a certified ASME V&V 20 validation uncertainty**, and this file will not be
cited as though it were.

**Not touched by this note: `docs/NUMERICS_KNOWLEDGE.md:118`**, whose *"Previously paywalled — now
supplied"* heading is false for this entry. **Sanaa stated she will correct it herself today and
no agent touches it.**
