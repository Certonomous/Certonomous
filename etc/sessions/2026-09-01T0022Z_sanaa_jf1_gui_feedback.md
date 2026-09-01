# Sanaa GUI feedback — JF1 visuals + conversation edits, captured verbatim 2026-09-01 ~00:2xZ

## JF1 visuals, before any capture
> (1) Confirm the slot geometry in the run tree matches the registration (single TE jet, 30°); explain the two mid-chord openings in the surface render. (2) Replace the surface Cp render with the standard Cp vs x/c plot, unclipped, upper/lower separated, blown vs unblown overlaid, LE stagnation visible. (3) Show the actual 2D mesh slice: boundary-layer layers at the wall, >=12 cells across the slot height, wake refinement box, plus the checkMesh summary and the run's y+ histogram. (4) Confirm spanwise uniformity of all fields (2D case: zero variation in the empty direction). (5) Any render for the GUI must show the real computational mesh, not an STL tessellation.

## Conversation transcript edits (GUI role-voice templates)
- CHIEF RESEARCHER "One gated solve; the only freedom is mesh and convergence." -> REMOVE
- CHIEF RESEARCHER "Rejected: pricing by analogy (wrong wake); an ungated coarser mesh." -> REMOVE
- CHIEF RESEARCHER "Admissible against the standard mesh-quality acceptance band, a published threshold." -> REMOVE, change to: "Mesh quality per registered standards"
- CHIEF ENGINEER "Question: does the chain produce a converged force on a believable mesh?" -> REMOVE
- NUMERICIST "The gates are the standard acceptance band, per OpenFOAM mesh-quality guidance." / "The mesh is judged against a published threshold, not itself." -> REMOVE (second line)
- CHIEF ENGINEER solver line -> ADD PHYSICS TYPE ("Standard closure for attached external flow" + physics type)
- MONITOR "New on an unfamiliar body:" -> DO NOT SAY "unfamiliar body" (three occurrences)
- NUMERICIST "That near-wall modelling error is not separated here; it rides the model channel, which the certificate marks as a floor." -> USE LESS OBSCURE WORDING
- MONITOR "3 repeats counted, not repeated at you." -> REMOVE
- CHIEF ENGINEER conclusion -> "elapsed time: 2 min. C_d flat across avg window"
- NUMERICIST "The mesh spread rides the numerical channel." -> REMOVE
- CHIEF ENGINEER "Total spend 2 core-minutes, refinement rungs included." -> REMOVE (mentioned above)
- NUMERICIST "Lessons entered to memory." -> "No new lessons entered to memory" (when none were)
- LAB stats table -> "total hours ran this week: ..." (most hours ran this week; no need to be precise on the dot)

She reviews Acts A and C next while these are incorporated.
