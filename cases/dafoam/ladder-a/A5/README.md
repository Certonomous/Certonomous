# Ladder A5 — U-bend internal flow, pressure-loss objective

The **frozen record of this case** is `../A5_ubend_internal.md` (2026-07-28, carrying twelve dated
addenda through 2026-07-31) with `../A5_ubend_internal.json`; frozen logs are in `../logs/`
(`A5_*.log`) and the working case tree with its probe scripts is `../A5_work/UBend_Channel_pressureloss/`.
The case is **4,800 cells** (not 21,000 — that figure belongs to the CBFS case in the decomposition
reach matrix), `DASimpleFoam`, objective adapted from the stock weighted sum to pure `TP1 - TP2`.
The recorded verdict against the shipped toolchain is **FAIL** — 46.64% aggregate, 5 of 27
components in band, idx8 and idx17 sign-flipped. Its 2026-07-29/30 `mesh.warpDeriv` clearance is
**RETRACTED** by the 2026-07-31 addendum: the clearance used a random seed, and under the real
`d(OBJ)/dXv` seed the same components read 207% and 122%. Regrade: `../W5_GRADIENT_REGRADE.md`
§4/§7.2/§7.3; the idx16 reference question is `../W4_IDX16_IS_THE_REFERENCE.md`; status settlement
`../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §2. **Nothing in this subdirectory edits any frozen file.**
