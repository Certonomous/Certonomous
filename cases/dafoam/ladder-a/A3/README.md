# Ladder A3 — ONERA M6 transonic wing

**Two distinct campaigns live under this name and must not be merged.** The **frozen record of the
original ladder rung** is `../A3_onera_m6.md` (2026-07-28) with `../A3_onera_m6.json` and logs in
`../logs_A3/`: 399,360 cells, `DARhoSimpleCFoam`, converged primal and an AGARD AR-138 / NASA-TMR
Case 2308 Cp validation, with the adjoint recorded as **BLOCKED** after eight disclosed mitigations.
The **reopened sweep ladder** (2026-08-08 → 08-11) is a separate campaign on a separate mesh family
and is where A3's only FD-verified gradients live: pre-registrations `../A3_TPC1_ARM_PREREGISTRATION.md`,
`../A3_TPC1_CONTROL_PREREGISTRATION.md`, `../A3_FD3_PREREGISTRATION.md`,
`../A3_RUNG2_N28_PREREGISTRATION.md`, `../A3_RUNG3_N52_PREREGISTRATION.md`, and the lever campaign
`../A3_TRIAGE_LEVERS_PREREGISTRATION.md`, `../A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md`,
`../A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md`, `../A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md`,
`../A3_RUNG3_FILL1_ENGINEERING_PREREGISTRATION.md`, `../A3_RUNG3_RESTART_CHALLENGE_PREREGISTRATION.md`,
`../A3_SUBLU_PREREGISTRATION.md`, `../A3_SUBLU_SWEEP_PREREGISTRATION.md`, `../A3_KSPOPTS_PATCH_PREREGISTRATION.md`;
results `../A3_SUBLU_RESULT.md`, `../A3_RUNG2_N28_RESULT.md`, `../A3_RUNG3_N52_RESULT.md`. Its logs
are in `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/`, `A3-rung2-n28-tpc1/` and
`A3-rung3-n52/`. **Nothing in this subdirectory edits any frozen file.**
