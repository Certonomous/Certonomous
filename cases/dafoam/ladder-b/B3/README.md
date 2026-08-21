# Ladder B3 — CBFS field inversion: start here

**B3 is the rung where Ladder B's adjoint blocked.** Its verdict is **two rows, always**:
against the **shipped** toolchain it is **BLOCKED** — the discrete-adjoint GMRES solve
returns PETSc `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0, because the
ASM sub-block *incomplete* factorization hits an exact zero pivot; against a **locally
rebuilt** library with the sub-block preconditioner switched to complete LU
(`DAFOAM_SUBPC_TYPE=lu`), the same configuration converges at `PetscConvergedReason: 2`.
Under grading policy **R11** the patched result is recorded *beside* the shipped verdict
and never in place of it, so **BLOCKED stands until the fix ships upstream or Katie adopts
a forked toolchain**. The original rung's records are frozen at
`cases/dafoam/ladder-b/B3_duct_field_inversion.md`, `B3_supervisor_debug.md`,
`B3_duct_field_inversion.json` and `B3_work/`; the unblock is frozen at
`W4_ADJOINT_PC_UNBLOCK.md` and was adversarially verified in
`../../VERIFICATION_cbfs_unblock_supervisor_sweep.md`. **New work goes in a `<run-slug>/`
subdirectory here as `PREREGISTRATION.md` then `RESULTS.md`** — see
`adjoint_unblock_reproduce/` for the first one, and `DEFECT_NOTE_ilu_zero_pivot.md` for
the filing-ready-but-**NOT FILED** upstream note (filing is Sanaa's call alone). Nothing
in this directory edits a frozen record, and nothing here has been filed, sent or pushed.
