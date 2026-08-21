# Ladder A4 — Ahmed body, 25 degree rear slant

The **frozen record of this case** is `../A4_ahmed_body.md` (2026-07-28, amended in place five times
since) with `../A4_ahmed_body.json`; frozen logs are in `../logs_A4/`. Two meshes: 45,760 cells for
the primal comparison and **2,777 cells for the adjoint and FD verification**. The verdict of record
is **PASS**, graded at np=1 against the shipped toolchain (1.10%); the published 10.04% is a
`scotch`-decomposition artifact at np=4. A4 is the case on which the decomposition defect was found
and characterised: `../DISCRIMINATORS_A4_decomposition_mechanism.md`,
`../UPSTREAM_BUG_REPORT_decomposition_adjoint.md` (**NOT FILED ANYWHERE**),
`../DEFECT_REACH_decomposition_cases.md`, `../DEFECT_ROBUSTNESS_mesh_and_setup.md`, verified in
`../VERIFICATION_A4_decomposition_supervisor_sweep.md` and `../VERIFICATION_A4_mechanism_supervisor_sweep.md`.
The SIMPLEC retraction and its three-legged replacement are in
`../A4_SIMPLEC_ACTIVITY_PROOF_PREREGISTRATION.md`. **Nothing in this subdirectory edits any frozen file.**
