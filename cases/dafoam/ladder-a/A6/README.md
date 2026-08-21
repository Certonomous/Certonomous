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

---

**2026-08-21, Lane A — the N=16 rung ran, and the N=29 rung is NOT RUN.**
`rung_n16_np1/RESULTS.md` grades the coarsened N=16 rung (41,760 cells, np=1) on both images.
**The first A6 adjoint that has ever existed converged** — 517 GMRES iterations,
`PetscConvergedReason: 2` — but **FD-vs-adjoint GATE FAILS on BOTH the shipped and the patched
image**: 8 of 9 graded components exceed 15% (57.06% … 340.70% on the patched image) and **3 of 9
reverse sign**; only `patchV` idx1 (AoA) lands inside the ≤5% band, at 3.29%. Measured cause is the
**finite-difference reference, not the adjoint**: the primal stops 556× short of `primalMinResTol`,
its CD wobbles by 9.0e-6, and at `step=1e-3, form=central` that leaves a derivative noise floor of
4.5e-3 which 8 of the 9 FD magnitudes do not clear. Peak RSS **9.787 GiB** (predicted 6.8, ceiling
12). Cost 76.653 core-min ($0.0655), 47.9% of the registered 160 core-min ceiling.
**GATE DECISION: Sanaa's approval of N=29 was conditional on N=16 passing on the patched image. It
does not pass. N=29 IS NOT RUN** — nothing launched, staged or queued for it. Enlarging the mesh
would not address the diagnosed cause; N=29 is 79,560 cells, where the same solver is already known
to stagnate. Fixing the FD reference is the next step and is not yet registered anywhere.
Full numbers, per-component table, verdicts and amendments: `rung_n16_np1/RESULTS.md` §6–§10.
