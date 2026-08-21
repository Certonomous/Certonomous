# Ladder A6 — CRM wing-alone (not a full wing-body)

The **frozen record of this case** is `../A6_crm_wingbody.md` (2026-07-28) with
`../A6_crm_wingbody.json`; frozen logs are in `../logs_A6/` (6 files; the only substantive one is
`run_model_accepted_t0_to_t1000.log`, 914 lines). The case is 579,072 cells, `DARhoSimpleCFoam`,
**primal only — no adjoint of any kind was ever attempted**, by explicit instruction, on the
strength of A3's memory evidence. The primal is force-stationary at CD = 0.02090143421526141.
Four published statements about this case were executed and found wrong in
`../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §3 (the "converged below 1e-8" claim, the "0.0067%"
claim, the "8.5e8 temperature-residual signature", and the "memory wall" label); the earlier
diagnosis is `../A1_A5_A6_DIAGNOSIS.md` §2. The adjoint memory envelope this case must be costed
against is `../ADJOINT_MEMORY_ENVELOPE.md` / `.json`. **Nothing in this subdirectory edits any
frozen file.**
