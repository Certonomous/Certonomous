# Ladder A1 — NACA0012 incompressible (official DAFoam tutorial)

The **frozen record of this case** is `../A1_naca0012_incompressible.md` (2026-07-28) with its
machine-readable sibling `../A1_naca0012_incompressible.json`, and the finite-difference step-size
probe that calibrated this lab's grading bands, `../A_stepsize_study.md` / `.json`. Frozen logs are
in `../logs/` (`compute_totals_run1.log`, `check_totals_run1.log` = the failed attempt kept as
evidence, `check_totals_run2.log` = the accepted FD verification) and `../logs_A1_stepsize/`
(12 step-sweep logs plus `fdStepSweep.py`). The case is 4,032 cells, `DASimpleFoam`, and its
recorded verdict against the shipped toolchain is **FAIL** — `CD wrt shape` 11.43% with component
idx6 sign-flipped. Two *independent* mechanisms are now known to flip that same component: the
IDWarp `getRotationMatrix3d` degenerate-branch defect (root-caused in `../ROOTCAUSE_getRotationMatrix3d.md`,
repaired in `../PATCH_getRotationMatrix3d.md`, regraded in `../W5_GRADIENT_REGRADE.md` §1) and the
`cellLimited` slope limiter's reverse tape (`../DEFECT_ROBUSTNESS_mesh_and_setup.md` R7,
verified in `../VERIFICATION_A1_serial_limiter_supervisor_sweep.md`). The status settlement at HEAD
is `../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §1. **Nothing in this subdirectory edits any of
those files**; new work lives in dated run-slug subdirectories, each a `PREREGISTRATION.md` written
before the runs and a `RESULTS.md` written after.
