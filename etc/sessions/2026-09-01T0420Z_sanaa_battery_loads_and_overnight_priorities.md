# SANAA-DIRECT — battery volumetric loads + overnight priorities (2026-09-01, ~04:20Z)

She is going to bed after this. This is the overnight work order.

## Sanaa's words, verbatim

> [SANAA-DIRECT] Battery loads: set the heat source as a volumetric rate from
> a real cell, not a per-cell wattage on a unit-depth model. Takeoff:
> q‴ ≈ 1×10⁵ W/m³ (≈40–50 W in a 100×30×150 mm cell, 5–8C class); cruise
> ≈ 2.5×10⁴ W/m³. State the basis in the assumptions box. The temperature
> rise is then whatever the physics gives; I am not prescribing "tens of
> kelvin", I am prescribing realistic heat density. If the result is 8 K,
> 8 K is the answer.. I am going to bed. Priorities are the demos: JF1, the
> heat transfer ones, wiht their correct solvers state, the correct phsics
> stated, and their correct bands/ uncertainties and their correct geometries
> and meshes and conclusions, the onera M6 and mach 10 whenever they are
> ready, the multi point adjoing whenever they are ready. for all demos, they
> should look like a live demo, everything syncrhonized, no internal
> information,no past tense, no long sentences, all results in table,
> NOTHIGN that makes it look recorded, the pt is for it to look exactly like
> what a user would experience if they were running the case. Only real
> geometries everywhere and their real meshes. Only profetional prompts. All
> plots latexfied. Plus all my other requests applied.

## Chief's reading

1. BATTERY LOADS SUPERSEDE the "tens of kelvin" wording of 6ad8f5b7: the
   source is volumetric — q''' ≈ 1e5 W/m³ takeoff, ≈ 2.5e4 W/m³ cruise, basis
   (real-cell 100×30×150 mm, 5–8C class) in the assumptions box. The rise is
   whatever the physics gives; nobody tunes toward a target. This also
   resolves heat-transfer's boarded reachability objection — she is
   prescribing heat density, not ΔT.
2. Overnight priority order: JF1 demo; thermal demos (correct solver stated,
   correct physics, correct bands/uncertainties, correct geometry+mesh,
   correct conclusions); ONERA M6 + Mach-10 DMR when ready; multipoint
   adjoint demo when ready.
3. All demos: live-looking, synchronized, no internal info, no past tense
   (progressive while running, per DEMO MODE), short sentences, all results
   in tables, nothing that looks recorded, real geometries + their real
   meshes only, professional prompts, ALL PLOTS LATEXFIED, plus every prior
   directive applied.
