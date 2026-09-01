# DRAFT amendment 1 to `DMR_PREREGISTRATION.md` — NOT APPLIED

**Status: DRAFT. NOT APPLIED to the frozen document. NOT COMMITTED by the lane
that wrote it.** Prepared by a cfd lane, 2026-09-01, on the cfd supervisor's
instruction. Applying it means appending the block between the rules below to
the foot of `verification/campaign/DMR_PREREGISTRATION.md` and nothing else:
no line above that foot is edited, reordered, inserted or deleted.

**Why it is a draft and not an edit.** The pre-registration is a frozen file
(CLAUDE.md rule 6). A departure is disclosed in a dated amendment appended at
the foot with a version bump and the zero-lines-changed assertion; it is never
a rewrite, and the decision to append is the supervisor's, not the lane's.

**What was checked before it was written, and by whom.** Every claim in the
block below was verified on disk by the lane on 2026-09-01, box clock, with
the check named beside it in the block. The absence of the cited directory was
confirmed by `ls` returning "No such file or directory", not inferred from a
missing entry in a listing.

---

## Amendment 1 — 2026-09-01: §6 names a retained-artifact directory that no longer exists

**Version: v1.0 to v1.1.** The frozen text carries no version marker of its
own, so v1.0 designates it as committed at `74797a57`, 2026-08-07T22:40:28Z.

**Lines whose number changed above this section: 0.** Nothing above this
heading has been edited, reordered, inserted or deleted. This section is
appended below the closing rule of the frozen text.

**What is wrong.** §6, first bullet, registers the runs and retained artifacts
as living "under `demo-output/website/campaign/DMR_runs/` (logs, controlDict,
locator script, final fields) per the launch prompt". **That directory is
absent from the working tree.** Checked 2026-09-01: `ls
demo-output/website/campaign` returns "No such file or directory"; the parent
`demo-output/website/` holds `latex/`, `motorbike-video/`, `solve_registry/`
and `surfaces/` and no `campaign/`. A reader following §6 to the artifacts
finds nothing.

**Where the artifacts actually are.** `verification/runs/DMR_runs/`. Verified
present 2026-09-01: `res120/` and `res60/`, each holding all eleven written
times 0 through 0.2, `constant/`, `system/`, the four processor directories,
`log.blockMesh`, `log.checkMesh`, `log.setExprFields`, `log.decomposePar`,
`log.rhoCentralFoam`, `log.reconstructPar`, `log.writeCellCentres` and
`locator_result.json`; and beside them the case generator `make_case.py`, the
locator `dmr_locator.py` and the contour deliverable
`dmr_density_contours_t0p2.png`.

**Cause, and what this amendment does not change.** The runs were relocated by
the repository-wide move recorded at `a1fbe127`, 2026-08-18 ("MOVE_MAP batch
7") — eleven days after this document was frozen and after all compute for
this item was complete. **No gate, threshold, cap, label or prediction is
altered by this amendment, and none may be:** this is a location correction
only. The gates and their verdicts stand exactly as `DMR_RESULTS.md` records
them.

**Two things a reader of this file must carry away.**

1. **`git log` on this file alone misidentifies the freeze.** It reports
   `a1fbe127`, 2026-08-18, which is the rename, not the freeze. The freeze is
   **`74797a57`, 2026-08-07T22:40:28Z**, recoverable only with `git log
   --follow`. The primary rung's own `0/T` was written at
   **2026-08-07T22:43:42Z**, three minutes and fourteen seconds after that
   commit, and the trend rung's at 22:45:04Z. That ordering — freeze strictly
   before first field — is this document's entire evidentiary content, and a
   reader who takes the rename date for the freeze date destroys it.

2. **The same stale path appears in three other places, and one lookalike is
   not stale.** Stale, and correctable the same way: `DMR_RESULTS.md` line 8
   ("Everything retained under `campaign/DMR_runs/`"), and the `case:` line of
   both registry records
   `demo-output/website/solve_registry/dmr_res120_20260807T224408Z.done` and
   `dmr_res60_20260807T224510Z.done`. **Not stale, and not to be touched:** the
   `Case :` header line inside each solver log, which records where the solver
   actually ran on 2026-08-07 and is historically true. Editing it would
   falsify a run record in order to tidy a path.

   **This distinction is adopted by the cfd supervisor as a standing caution,
   2026-09-01, beyond this document:** a solver log's own `Case :` header is a
   record of where the run happened, not a pointer to where its artifacts live
   now. A repository-wide sweep-and-replace over stale run paths that does not
   exclude solver logs falsifies every run record it touches. Correct the
   prose and the registry records; leave the logs alone.

**Nothing else in this document is amended.**

---

## Notes for the supervisor, outside the block above

- The block above is what gets appended. This section does not.
- A fourth file, `F2_transonic_naca0012.md`, is reported to carry the same
  stale-path problem. It was **not** examined by this lane and is not covered
  by this draft.
- The display mission built for this benchmark is wired from
  `verification/runs/DMR_runs/`, read off the filesystem. It never reads the
  path this document cites, so it does not depend on this amendment landing.
