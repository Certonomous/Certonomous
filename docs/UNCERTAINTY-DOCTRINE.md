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

## Standing product rules that bind these
- Never a fake number; every displayed value traces to a computation.
- Channel text carries no tool names, no internal study IDs, no method
  jargon (GP, LHS, GCI stay internal; the citation Eca & Hoekstra 2014 is
  allowed for the numerical procedure).
- Every new computed-uncertainty pattern gets a lesson entry so the team
  converges on automatic computation for all future cases.
