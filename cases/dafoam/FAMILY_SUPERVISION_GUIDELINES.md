# DAFoam/adjoint family supervision guidelines

**Standing rules for every agent working in this family. Issued 2026-08-07 by
the family supervisor (first pass), under the SUPERVISION_CHARTER structure
(`docs/charters/`). These guidelines encode what this family has already paid
to learn — LESSONS L-29..L-38, four adversarial verification sweeps, and three
campaigns of pre-registered arms. They bind future sessions unless the chief
supervisor or Katie supersedes them. Where a rule cites a lesson, the lesson
is the reasoning; the rule here is the operative form.**

Scope: everything in `demo-output/website/dafoam/` (ladders A and B, the
defect campaigns, the two unfiled upstream reports, the LaTeX companion), the
run trees under `/home/ubuntu/certonomous-runs/W4-*`/`W5-*`, and any future
work touching DAFoam, IDWarp, pyGeo/DVGeo, or the MACH-Aero adjoint stack.

---

## 1. Regression tests before any toolchain version bump

No DAFoam / IDWarp / OpenFOAM-image version bump (including "latest" re-pulls
of `dafoam/opt-packages`) is adopted for family work until the one-word
reproducers below are re-run on the new stack and their signatures compared
against the recorded ones. They are cheap by construction — that is why they
were kept. A bump that changes any signature is a finding, not an
inconvenience: record it before proceeding.

| # | reproducer | lever (one word / one env var) | recorded stock signature | recorded clean signature | cost |
|---|---|---|---|---|---|
| R-1 | IDWarp rotation guard, `upstream_repro/run_repro.sh` (U-bend, `--seed real --objective pressure-loss`) | `useRotations` True/False; or patched clone via `PYTHONPATH` | idx8 207.0% SIGN-FLIPPED, idx17 121.6% SIGN-FLIPPED | patched: 3.0e-06 / 7.0e-06, signs agree; rotations-off: 0.0000 all 27 | ~2 min, no CFD solve needed for the airfoil variant |
| R-2 | A4 decomposition defect, A4 coarse `check_totals` | `decomposeParDict` daOption: `scotch` vs `simple 4x1x1` at np=4 | scotch 8.95% (patched IDWarp; 10.04% stock), KSP 719; simple 4x1x1 0.00054% | np=1 stock 1.10% (the graded configuration) | ~5 core-min/arm |
| R-3 | limiter branch (parallel excitation), A4 coarse np=4 scotch | `div(phi,U)` `linearUpwind limited` -> `linearUpwind default` (one word) | 8.95%, KSP 719 | 0.849%, KSP 41 | ~6 core-min |
| R-4 | limiter branch (SERIAL excitation), A1 + freestreamVelocity + limiter staging (`run_a1lim_arm.sh`) | same one word, at np=1 | CD/shape 92.8%, one component sign-flipped, CL 7.9% | `default`: 0.121% | ~6.5 core-min |
| R-5 | ILU conditioning wall, B3/CBFS adjoint | `DAFOAM_SUBPC_TYPE=lu` on the `dafoam-subpclu:v1` image (env off = stock) | `-9` DIVERGED_NANORINF at iter 0, initial residual 7.091590452305e-04 (13 digits) | reason 2, 667 iterations | ~6 core-min off / ~16 on |
| R-6 | `mdolab/idwarp#57` self-test, `inflate_cube` `verifyWarpDeriv` | patched vs stock clone | DOFs 0/3: 210.16% / 212.62% | 8.6e-06% / 3.4e-05%; DOFs 1,2,4,5 bit-identical | seconds, no CFD |

Bump protocol: run R-1, R-2 (np=1 + scotch arms), R-3, R-5-off, R-6 minimum.
The STOCK signatures must reproduce (they are the evidence base of two unfiled
upstream reports); if a bump silently fixes one, that is a headline event —
escalate to the chief before regrading anything (§6). Verify the toolchain
identity in-log every time: `IDWARP_IMPORTED_FROM:` stamp, `Decomposition
method` line, and (for R-5) the `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to
complete LU` line. A run without its stamp does not count (sweep finding W-2).

## 2. Cross-residual instrument discipline

The cross-residual (L-35) is this family's operator-level truth instrument.
Rules, all of them already paid for:

1. **Sign convention.** The system is `A^T psi = -b` (OpenMDAO seeds `-dF/dW`).
   An instrument computing `Atpsi - b` prints the degenerate
   `ratio=2.000000e+00` on its own-operator control — that printed 2.0 is the
   tell that the sign is wrong, and the published values are offline
   corrections `res + 2b`. As of this writing `w4_dump`/`w4_crossres` still
   carry the wrong sign and only `w4_crossres2` is correct
   (`SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` A-1). **Fix the instrument
   before its next use; until then, never quote a ratio directly from a
   W4X/W4D log line — recompute from the dumped vectors and say so.**
   `w4x_res_*.npy` files hold `Atpsi - b`; `w4x2_res_*.npy` hold the true
   residual. Do not mix them.
2. **Map validation is a gate, not a printout.** Before any psi comparison:
   duplicated processor-face phi copies must agree at machine precision
   (recorded floors 2.7e-15 .. 3.6e-15) and, where AdjointIndexing centres are
   available, mapped coordinates must match at max |dxyz| = 0.0. A validation
   that fails stops the arm. Integer addressing maps only
   (`cellProcAddressing`/`faceProcAddressing`, sign on flipped faces) — never
   coordinate matching (L-35).
3. **Bands in floor units.** Register cross-residual verdict bands in units of
   the configuration's OWN np=1 floor, never absolute x||b||. The R5 band was
   mis-calibrated by ~5 orders and survived on luck; the R7x band repeated the
   mistake (robustness erratum, banding lesson). Measure the np=1 floor first
   or in the same session.
4. **State-override control.** A lever's cross-residual verdict should carry a
   `crossres2`-style control (operator linearized at the other arm's mapped
   state, ~0.4 core-min) whenever the container is warm; the R5 levers ran
   without one and the gap is a named protocol debt.
5. **A clean gradient is not a clean operator (L-36), and
   decomposition-invariance is not correctness (L-38).** Any lever that turns
   a gradient error off must be re-verified at operator level before any
   configuration is called safe; any invariance pass must be anchored to an
   external reference (own-run FD with a step-check, or the cross-residual)
   before it is promoted to a correctness statement. The two measured
   counterexamples: `inletOutlet` hides a 1.047x||b|| wrong operator under a
   0.019% gradient; `a1lim` is decomposition-invariant to 4e-04 while 92.8%
   wrong.
6. **Branches first (L-37).** In any differentiated-code wrongness hunt,
   enumerate the recorded BRANCHES (limiters, switching/mixed BCs, guards,
   min/max/abs) and one-knob them before theorizing. The one-word dictionary
   edit is the cheapest discriminator this family has ever run, serial or
   parallel.

## 3. Shipped-vs-patched grading (R11, restated as practice)

R11 (`docs/charters/SUPERVISOR_RULINGS.md`, adopted 2026-08-04) is the grade
law; the family practice it requires:

1. Verdicts are graded against the SHIPPED toolchain (DAFoam 5.0.0 + IDWarp
   2.6.2 as installed). A1 CD/shape FAIL (11.43%, sign-flipped idx6) and A5
   FAIL (46.64%, two flips) stand while the shipped package carries the bug —
   however completely the local patches repair them.
2. Patched numbers are recorded BESIDE the stock verdict as
   diagnosis-confirmed-by-repair. They never move a grade. This applies to
   ALL THREE local patches: the IDWarp rotation patch, the sub-LU
   `DAFOAM_SUBPC_TYPE` rebuild, and any future instrumented build.
3. A patched grade requires its paired-run controls on the record: FD column
   bit-identical between stock and patched halves, primal invariant
   (md5/objective digits), and provenance stamped in both logs
   (`IDWARP_IMPORTED_FROM:` / the sub-LU Info line).
4. A patched grade replaces a shipped grade only if the fix ships upstream or
   Katie formally adopts a forked toolchain. Not a session's call, not the
   chief's; Katie's.
5. When a verdict moves, the case's own `ladder-*` record (.md AND .json)
   moves FIRST, quote-and-strike in place (L-32). A satellite citing a verdict
   its case file contradicts is a defect.
6. Nothing is filed upstream by anyone in this family, ever. Both reports and
   the tex carry NOT FILED status; filing is Katie's call alone.

## 4. Pre-registration before compute (as it applies to FD arms)

1. Every arm with a solver in it gets a registered prediction COMMITTED before
   the arm runs; the commit timestamp is the witness. Score HELD / NOT HELD /
   NOT SCORED against the registered wording, never reworded after
   measurement. Named alternatives and gray zones are written at registration
   so no outcome can be re-read favourably.
2. FD protocol of record: `check_totals`, step 1e-3, central, `step_calc="abs"`,
   error convention ||Jan-Jfd||/||Jfd|| as printed. One convention throughout;
   any other quoted convention must be labeled at the number.
3. FD trust requires a step-check when symptoms warrant: if the FD magnitude
   differs from the analytic np=1-class value by >20%, or the verdict lands in
   a gray band, buy the one h=3e-3 (or one-decade) re-run BEFORE scoring
   (the R2 guard / R7f1 pattern). An FD wobble of ~2% cannot explain a ~90%
   gap — state the arithmetic when scoring.
4. An arm whose primal fails, or whose adjoint returns no analytic, is
   NOT SCORED — reported as the finding it is, never coerced into a band
   (R2, R3b, R3c precedents). `primalMinResTol` is a pass/fail gate in
   DAFoam, not a depth control; do not design arms that assume otherwise.
5. Never grade an FD arm from a re-used FD column: the FD is computed per run,
   inside that run's own `check_totals`. And never re-use a "the FD cannot
   have changed" argument in place of re-measuring it (L-31 — the idx16
   lesson: re-measure the reference by an independent path, with a
   neighbouring component as control).
6. Random-seed dot-product tests do not clear a derivative; only the real
   objective seed does (A1/A5 retraction history). Any warpDeriv-class test
   uses `--seed real`.
7. Ledger every run wall x cpus-cap, confess overruns and aborted launches,
   keep contingent-arm ledgers separate when a sweep says so. Budget escapes
   are decided by registered decision rules, not in the moment.

## 5. Crash triage table

The family's failure signatures are now well-mapped. "Known-benign" means: has
a recorded mechanism, needs no fresh triage IF the signature matches exactly —
verify the signature, cite the mechanism, move on. Anything not matching a row
is guilty until triaged (and a crash on a NEW case/configuration is a new row
candidate, not an automatic benign).

| signature | where seen | mechanism | disposition |
|---|---|---|---|
| `PetscConvergedReason: -9` (DIVERGED_NANORINF) at iteration 0, initial residual identical to 13 digits across reorderings | B3/CBFS, NASA hump | ASM sub-block ILU factorization failure (factor growth; `spilu` "exactly singular" offline; shift machinery cannot catch it) — `PROOF.md` §25.2-25.3, `W4_ADJOINT_PC_UNBLOCK.md` | KNOWN. On these cases: sub-LU env switch on the patched image. On a NEW case: dump the PC matrix + RHS (stock PETSc flags), reproduce offline before believing anything else. |
| `-9` immediately after `adjUseColoring: False` | discriminators M2 | crash BY CONSTRUCTION in v5 (`DAColoring.C:1021`: `calcdRdWT` reads a coloring that `solve_linear` never wrote) | KNOWN-BENIGN as a signal about the option, never about the case. Do not attempt the forced identity-coloring workaround: measured memory-unbounded (>20 GiB on a 2,777-cell case). |
| `-3` (DIVERGED_ITS), residual flat or nearly flat to many digits | CBFS `natural` reordering; hump; R3c restart-60; R2 refined-mesh limited arm | two mechanisms, distinguish by configuration: (a) conditioning wall family (flat to 13 digits, all reorderings fail) — same ILU mechanism as above; (b) limited-scheme + scotch configurations: conditioning TRACKS the operator defect (719 vs 41 iters; stagnation on refined mesh) | (a) KNOWN on the conditioning cases. (b) EVIDENCE, not noise — a `-3` on a limiter+scotch arm is part of the defect record; log it as a datum (R2 precedent). |
| `-5` (DIVERGED_BREAKDOWN) immediately before an OOM | A3 coarsened, once | not independently diagnosed; occurred inside the memory-wall envelope | MUST-TRIAGE if it appears outside an OOM context; otherwise subsumed by the OOM row. |
| OOM during dRdW coloring or GMRES, compressible 6-field cases order 1e5 cells | A3 fine/coarse, A6 (not attempted), sail_medium, wing_coarse (consistent) | structural: mesh-sized d[R]/d[Xv] block built unconditionally by the reverse sweep | KNOWN. Do not burn budget re-fighting it; the envelope statement is family-scoped (incompressible cases have passed coloring at 51.6k cells). |
| `AnalysisError: Primal solution failed!` when a tightened `primalMinResTol` is not reached at endTime | R3b | DAFoam treats unreached tolerance as failure — a gate, not a crash | KNOWN-BENIGN as a crash; the arm is NOT SCORED. |
| `AnalysisError: Adjoint solution failed!` after GMRES stagnation | R3c, R2 | see `-3` row | as `-3`. |
| rc=1 from `docker stop` / session kill | hump sub-LU run; R2b through the 2026-08-05 kills | the kill, not a KSP verdict | KNOWN-BENIGN; state it. Detached (`setsid`/detached-driver) solvers survive session kills — foreground-Bash solvers do not (memory: openfoam-restart-watcher-traps). |
| `check_totals` first-attempt garbage after a previous run's processor dirs left behind | A1 run1 ("stale-processor trap") | stale decomposition state | KNOWN-BENIGN; cold-reset processor dirs (the FD protocol already requires it). |
| mid-run cleanup deleting tracked `0/`, `0.orig/` | A1 session 2026-07-30 | over-broad `rm -rf [0-9]*` glob | prevention rule: never glob-delete numbered dirs in a tracked case without `git status` before and after. |

Two standing meta-rules: a converged solve (`reason 2`) is NOT evidence of a
correct operator (L-35 — A4's 8.95% converged cleanly); and an OOM/stall
without a captured error message is "consistent with", never "confirmed" —
say which one you have.

## 6. Escalation to the chief supervisor

Escalate BEFORE acting on any of these; a session does not decide them alone:

1. **Any scoring-grade claim**: a verdict moving in either direction on any
   rung (PASS/CONDITIONAL/FAIL/BLOCKED), a grading-standard change, or a
   patched grade proposed for adoption (that one continues to Katie per R11).
2. **Anything upstream-filing-relevant**: edits to either
   `UPSTREAM_BUG_REPORT_*` draft or the tex companion that change a claim
   (corrections mandated by sweeps are fine — flag them); any new evidence
   that would strengthen, scope, or contradict a filed-version claim; any
   contact with upstream (which is banned anyway — filing is Katie's).
3. **Anything touching the case file's headline numbers**: 8.95% / 0.00054% /
   329x / 1.047x / 92.8% / 0.121% / 634% / 207.0%/121.6% / 46.64% / 11.43% /
   1.10% / 667-iteration unblock / the FD-gate percentages. If a re-run or a
   new instrument moves one of these, stop and escalate with the logs.
4. **A new defect class** (anything that is not the rotation guard, the
   decomposition branch defect, the serial limiter tape, or the ILU wall), or
   an existing reproducer changing signature under a version bump (§1).
5. **Budget**: projected overrun beyond a registered decision rule's
   allowance, or any arm whose failure mode is consuming budget without
   producing a number (the coloring-off lesson: the second forced attempt
   should not have been launched).
6. **Session-limit exposure**: long solver arms must run under detached
   drivers with self-writing ledgers (the R2b pattern) so a fleet kill loses
   no core-minutes; pre-registration-first makes recovery cheap.

## 7. Record hygiene (the L-32 family, condensed)

- Verdict moves update the case's own ladder record first, satellites second,
  always quote-and-strike, never silent rewrite.
- Corrections mandated by a sweep are applied at EVERY site, including
  successor documents and LESSONS entries — grep for the number, do not trust
  memory of where it lives (the 590 lesson).
- Every log cites provenance stamps; every claim cites a log that still
  exists (drivers must stop truncating evidence logs — review item A-4).
- Reports/tex quote each number in its stated units and carry the
  counter-instances (CD/twist degrading; the R6b 0.849% vs 0.041% floors)
  wherever the headline improvement is quoted.

## 8. Cold-start restoration before any archived-case rerun (the warm-start hazard, 2026-08-08)

pyDAFoam writes the primal end state back into the time-0 directory at run end
(`0/U` becomes bit-identical to the final writeout), so the SECOND run of any
case dir silently warm-starts — "the cold start you assumed is not the start
that ran" — and `renameSolution` (pyDAFoam.py:1543) hard-raises on a leftover
`0.0001`. Provenance: the entry-8 campaign (A3_SUBLU_SWEEP_PREREGISTRATION.md
addendum f77b2607; audit WARMSTART_AUDIT.md). Standing rule, per the approved
`pydafoam-silent-warmstart-state-hazard` instrument-check:

1. Before rerunning ANY archived case dir: move `processor*/0.000*` and the
   overwritten `processor*/0` aside (preserve, never delete), then
   `decomposePar -fields` from the pristine serial `0/` (verify serial `0/`
   against `0.orig` first). Partition and coloring caches stay untouched.
2. Prove the cold start IN THE LOG: the first `Time step continuity errors`
   value must match the case's known cold-from-uniform signature (bit-stable
   across runs; 55x above the warm value on the M6 rung it was validated on).
3. For A/B lever arms, prefer the staged-copy pattern (one fresh case subdir
   per arm, the W4 reordering/unblock layout) — structurally immune, and it
   leaves the bit-identical first-continuity-error line as the state-control
   proof.

## 9. Family state, 2026-08-10: AT REST — available by decision, not idle by default

The DAFoam/adjoint family's queue is empty and the family rests. Recorded here so a later reader
finds a decision rather than an absence.

**What closed it.** The A3 line went from *blocked at every mesh size, cause unknown* to: one
token was the wall (negative control reproducing the archived failure bit-for-bit); two rungs
converged and FD-verified; a ceiling bracketed and defended against the one challenge whose
mechanism matched it; **twelve candidate causes eliminated by measurement**; a capability-boundary
defect written up filing-ready with its fix implemented and regression-controlled; and an
unexplained residue that is *precisely bounded* rather than vaguely open.

**What was declined, and why that is the point.** The one remaining item — testing whether
`pcFillLevel 1` also collapses at rung 2, the restart-destabilisation prediction left labelled
unproven in `R5_ADJOINT_CONDITIONING.md` — was priced at ~29 core-min and **declined by the chief
on the agent's own reasoning: it would tidy a hypothesis, not move a verdict.** The standard
applied all day is that **compute which cannot change a decision is not spent.** An empty queue
reported honestly beats manufactured work, and the same call was made twice in one day across two
families.

**Held elsewhere, not lost:** the KSP-options defect candidate and the branch-taping class are
filing-ready and parked by policy; the condition-estimate methodological finding (three arms
saying the standard diagnostic does not predict convergence on this operator class) and the
launcher memory-cap L-40 are routed to their owners.

**Standing lessons this family contributed today:** L-40 (the switch you set is not the switch
that ran), L-44, L-49 (a search built from what you have been reading returns what you have been
reading), and **L-50 — a correction must not travel on the evidence class of the thing it
corrects**, which is why the FD-2 refutation was held until a 435-vs-490 iteration measurement
joined its source read and its config read.

**Restart condition:** this family reopens on a new case, a toolchain bump (run the R-1/R-2/R-3/
R-5-off/R-6 regression set of §1 first), or a decision that actually turns on one of the parked
items — not on the availability of an agent.
