# CERTONOMOUS DEMO STANDARD v2 — GUI-NATIVE, CUSTOMER-FACING
[SANAA-DIRECT, captured verbatim by the chief at receipt, 2026-08-31 ~23:0xZ.
She steps away; on return, demos shoot on the GUI.]

[VERBATIM BODY — §1 OUTPUT RULES R1-R10; §2 THE FOUR ACTS (A motor-in-duct
thermal map, B jet-flap/blown wing, C battery module under takeoff pulse,
D shape optimization multipoint — whichever variant is ready, the other
never mentioned); §3 MECHANICS. Full text as received:]

## §1 OUTPUT RULES (platform-wide, permanent)
R1. Numbers live in TABLES (header, units, uncertainty column). Never in prose. Prose may reference a table row.
R2. Scientific/engineering notation; significant figures tied to the uncertainty; units everywhere.
R3. Plots latexified: vector, LaTeX labels, units, uncertainty bands, reference curves labeled with their source ("Spence 1956", "Ansys verification manual VMFL___", "exact conduction solution").
R4. Role voices: Lead Researcher (scientific direction), Lead Engineer (application guidance), Lead Numericist (verification, convergence, uncertainty). Signed sections; concise, plain English.
R5. NO INTERNAL JARGON in anything user-visible. Translation table (binding): PASS -> "verified against [reference] within [X]%"; GATE REACHED -> "verified; no experimental comparison available for this configuration"; NOT A RESULT -> "run rejected: [plain reason]"; pre-registration -> "success criteria fixed before running"; heat balance -> "energy conservation checked: closed to [X]%". Tier words, case ids, rule numbers, docket/lesson ids, patch/defect talk: NEVER user-visible.
R6. Verification statements are explicit and sourced, in plain words.
R7. Caveats in a visible plain-English box.
R8. Cost transparency: every result states compute used and the upfront estimate.
R9. No mention, ever, of internal repairs, toolchain patches, instrument defects, or lab process. The lab's intelligence is shown ONLY through: (a) correcting/refining a USER assumption, (b) saving the USER compute, (c) stating its understanding and confidence before spending.
R10. Concise sentences. Plain English. An engineer reads every line without a glossary.

## §2 THE FOUR ACTS — universal GUI arc (user STL+prompt; lab restates task+confidence+cost; ONE assumption beat; live geometry+mesh; cheap check first; live monitors; results = tables+latexified plots+verification lines+caveat box+cost line). ACT A motor-in-duct thermal map (hand-model vs solved side by side, overprediction 1.9-3.5x, safe region shaded). ACT B jet-flap (Spence 1956 sqrt-growth beat; Cp blown/unblown; CL-vs-Cmu with theory curve; aero lift and jet-reaction as separate columns; unconverged high-blowing fallback line scripted). ACT C battery module (exact-solution confidence beat first; live 8-cell histories; spread vs time; time-step independence). ACT D shape optimization (multipoint, whichever variant is ready, the other never mentioned; Mach mis-assumption correction beat for incompressible; live shape morphing; thrift beat; FD-verified gradients; fresh-mesh re-solve; improvement decomposed).

## §3 MECHANICS — four 90-180 s GUI captures, Sanaa narrates; one-page LaTeX result sheet per act; nothing mentions rotor, acoustics, internal ids, patches, defects, tiers, or unshown cases. (Some things will change depending on what completes by tonight.)
