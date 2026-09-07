# DAFoam §2ay SUCCESSOR-LINEAGE MAP — flagged fails to their dated fix-successors

**Written 2026-09-07 by the dafoam-supervisor personally, on the chief's routing of verification's
§2ay instrument strengthening (`c47c2e13`). ZERO COMPUTE.** This record bridges the Aug-25
`MATRIX_CONTRIBUTION.md` row ids (`G-##`/`O-##`) and the newer curriculum ids (`D#`, `SO#`) to their
**registered or landed fix-successors**, so the completion enforcer
(`scripts/check_completion_enforcement.py`, §2ay) recognises the lineage that the id-suffix pattern
alone cannot see (`§2ay.2(b)`: "a landed passing successor whose lineage is recorded" / "a registered
next attempt").

**NOT FILED ANYWHERE. SUBMISSIONS PARKED** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Scope discipline, stated so this file cannot be read as gaming the check:** a matrix id appears below
**only if it has a genuine successor that already exists** — a landed passing row, or a registered
`PREREGISTRATION`/`SUCCESSOR` on disk. The fails that only OWE a successor (not yet registered) are
**deliberately absent** from this file and remain FLAGGED; they are tracked in the dafoam board
(`docs/LAB_STATE.md`) and named in §3 below with no clearing line, so the enforcer keeps flagging them
until their successor is actually registered. **A diagnosis clears nothing** (`§2ay.3`).

---

## 1. CLEARED — matrix `G-##`/`O-##` fails with a landed/registered successor (state b)

Each entry carries a line-leading `Supersedes:` field keyed to the flagged id (the enforcer's
recorded-lineage reader), the successor, its verdict, and the on-disk evidence.

Supersedes: G-01 — A1 NACA0012 shipped `dCD/dshape` GATE FAIL (11.43 %, idx6 flip) is the SHIPPED face of the IDWarp rotation defect (D-A). Successor: the PATCHED-row reverify LANDED PASS. Evidence: `cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` (patched arm, 0 sign flips). The shipped defect is a MEASURED toolchain limitation whose upstream draft (D-A) is prepared and NOT FILED — Sanaa's alone.

Supersedes: G-22 — A5 U-bend shipped `OBJ.val`/`shapexUpper` GATE FAIL (46.840 %, 2 flips idx8/idx17) is the SHIPPED face of the same rotation defect. Successor: the PATCHED-row reverify LANDED **PASS on the aggregate band, 2.768 %, 0 sign flips, idx16 0.90 %**. Evidence: `cases/dafoam/ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` §5. D-A upstream prepared, NOT FILED (Sanaa's).

Supersedes: G-28 — A6 N=16 gradient vs the ORIGINAL FD reference, GATE FAIL (88.93 %). The row itself records it is superseded as an FD-REFERENCE artefact, not an adjoint defect. Successor: G-30. LANDED.

Supersedes: G-29 — A6 N=16 gradient vs the original FD reference, rotation-patched, GATE FAIL (88.96 %) — a wrong-reference artefact (the patch moves A6 twist only 0.664 %, so the defect is the reference, not the gradient). Successor: G-30 — A6 N=16 vs a FIXED, noise-sized FD reference, **PASS on 8 of 9 (aggregate 1.0432 %, 0 sign flips)**, twist idx6 excluded NOT A RESULT by name. Evidence: `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md`.

Supersedes: G-21 — A4 decomposition survey, NOT A RESULT (no pre-registered gate; np=4 scotch 8.95 % vs simple 0.00054 %, the ~16,600× split). Successor: G-19 — the GRADED A4 configuration, np=1, **1.10 % PASS, HOLDS**. Evidence: `cases/dafoam/ladder-a/A4_ahmed_body.md:256-264`. The decomposition split is the MEASURED D-B toolchain defect (upstream draft prepared, NOT FILED — Sanaa's).

Supersedes: O-01 — A2 MACH-wing IPOPT drag-min, NOT A RESULT (time-boxed at 47/100 majors, no IPOPT convergence statement). The optimiser could not converge because the A2-wing PRIMAL fails DAFoam's post-End acceptance (maxNonOrth 71.48 > 70). Successor: D6RF5 — the A2 non-orthogonal-correction primal repair (REGISTERED, sizing frozen `9ed7aa78`), then the A2 multipoint optimisation D6R2 (D6RF5 → SO3DR Stage-2 → D6R2). Evidence: `cases/dafoam/ladder-a/A2/curriculum_D6RF5/PREREGISTRATION.md`.

**Registered 2026-09-07 (this annotation) — the five that until now were held out of §3 because their successor was not yet registered. Both successors are now REGISTERED (DRAFT, awaiting supervisor freeze). Neither is a proven capability gap; both are state (b) with an active, dated, named attempt that changes what failed and re-runs.**

Supersedes: G-11 — A3 rung-3 shipped-mode adjoint, GATE FAIL (4,000 iterations, `reason −3`, 1.31× residual reduction; peak 11.65 of 22 GiB, a MEASURED conditioning wall, not a memory one; `dafoam-subpclu:v1` banner absent = stock preconditioner path). Successor: **A3R3PC** — the rung-3 adjoint re-run with a WORKING preconditioner (the sub-LU `dafoam-subpclu:v2`, never tried on rung-3, or the ksp-options patch). A3R3PC changes the preconditioner of the linear solve — the one §2an process class not yet ruled out. REGISTERED (DRAFT): `cases/dafoam/ladder-a/A3/curriculum_A3R3PC/PREREGISTRATION.md`. Original fail evidence: `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2d, `35171866`.

Supersedes: G-12 — A3 rung-3 patched adjoint attempt 1, NOT A RESULT — stopped by memory (host-floor guard MemAvailable 7.3944 < 8.0 GiB while RSS 9.202 of 15.0; killed at 85 s of 2,600 s; 0 of 11 checkpoints). A registration-design memory defect, not numerics (L-239 in a new size). Successor: **A3R3PC** — the adequate-memory plan (gate limb `MemAvailable ≥ 19.65 GiB` from the shipped arm's complete measured peak + the 8 GiB floor, with the 25.2 GiB stage-0 risk disclosed beside the threshold). REGISTERED (DRAFT): `cases/dafoam/ladder-a/A3/curriculum_A3R3PC/PREREGISTRATION.md`. Original fail: `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/RESULTS.md`, `67edcc19`.

Supersedes: G-13 — A3 rung-3 patched adjoint attempt 2, GATE FAIL (adjoint, INHERITED) — all 11 KSP residual checkpoints bit-identical to the frozen shipped-equivalent path, NO `PetscConvergedReason` printed, terminal −3 inherited; rc=137 the registered deliberate stop. The IDWarp rotation patch is orthogonal to the adjoint conditioning, so it could not touch what failed. Successor: **A3R3PC** — changes the conditioning inside the linear solve (executable `KSP_PATH_DIFFERS` guard asserts the checkpoints are no longer bit-identical to the shipped fingerprint). REGISTERED (DRAFT): `cases/dafoam/ladder-a/A3/curriculum_A3R3PC/PREREGISTRATION.md`. Original fail: `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md`, graded `8871acf3`, row `bec36c9d`.

Supersedes: G-14 — A3 rung-3 gradient, rotation-patched, NOT A RESULT — no gradient was produced on rung 3 by any patched arm (silent both ways on rung 2's degradation finding), because no patched adjoint converged. Successor: **A3R3PC** — a gradient exists the moment the adjoint converges under a working preconditioner; the FD-vs-adjoint check and the Roache triple on the existing 21,840 / 42,120 / 79,560-cell family become reachable (named downstream, not folded into A3R3PC's cost). REGISTERED (DRAFT): `cases/dafoam/ladder-a/A3/curriculum_A3R3PC/PREREGISTRATION.md`. Original fail: same file, grading `8871acf3`, row `bec36c9d`.

Supersedes: O-10 — D2 AB2 design-point non-uniqueness, GATE FAIL (the item's REGISTERED FINDING, not a defect of the item): `‖Δshape‖₂/‖shape_A‖₂ = 33.259 %` vs the frozen 10.0 % band; `‖Δshape‖_∞ = 1.9379e-02` vs 8.0e-03; `|ΔAoA| = 0.2428` deg inside 0.25. AB1 passes, AB2 fails, and that combination is the result — the objective is near-flat along the direction separating the two designs (a flat-valley non-uniqueness, NOT an aerodynamic finding). Successor: **D2ABR** — a REGULARIZED Adams-Bashforth re-run (a registered shape-regularizer convexifies the flat valley; the acceptance band is carried byte-identical and never widened). REGISTERED (DRAFT): `cases/dafoam/ladder-a/A1/curriculum_D2ABR/PREREGISTRATION.md`. **Alternative disposition (PARKED, Sanaa's alone): a valid-terminal-result ruling that the registered non-uniqueness is itself terminal.** Original fail evidence: `cases/dafoam/ladder-a/A1/curriculum_D2` grading, row `b840fcd5`.

---

## 2. CLEARED — newer curriculum `D#`/`SO#` fails bridged to their registered successors (state b)

These verdicts postdate the Aug-25 matrix and so are absent from it; recorded here so the enforcer sees
their coverage. Each has a registered `PREREGISTRATION`/`SUCCESSOR` on disk.

Supersedes: D6RF4 — A2-wing convergence probe, NOT A RESULT (p first-solve at 1.66× the 1e-05 floor). Successor: D6RF5 (REGISTERED, `cases/dafoam/ladder-a/A2/curriculum_D6RF5/PREREGISTRATION.md`, sizing `9ed7aa78`).

Supersedes: D6RF5 — A2-wing convergence probe `P_conv`, **BLOCKED** (a HARNESS defect, NOT physics). The baseline primal converged to `End` (CD 0.01849, CL 0.399) then hit DAFoam's physically-EXPECTED post-`End` `Primal solution failed!` (p first-solve initRes 1.625570732e-05 > the 1.0e-05 accept floor, ~unchanged from D6RF4's 1.658e-05 — Fix#1 limited-corrected + Fix#2 nNonOrthogonalCorrectors 3 did NOT bring the binding field under floor), but the `P_conv` baseline primal was UNGUARDED (unlike the F5_scheme path), so the raise aborted the run before `d6rf5_fd_endpoint.json` was written and the grader refused at G1 (product absent). Successor: D6RF6 — the SAME arm with the baseline primal guarded the SAME way the F5_scheme path is guarded (records `primal_raised` + the per-field residuals and STILL writes the product), so the expected **G-CONV GATE FAIL** (binding p_first 1.626e-05 > 1.0e-05 floor) is GRADED instead of crashing to BLOCKED. The accept floor is NOT moved (N-D43); the LIMITED fvSchemes + 3-corrector scheme is carried BYTE-IDENTICAL — the successor changes the harness's survival of the expected refusal, not the numerics or the gate. REGISTERED DRAFT (`cases/dafoam/ladder-a/A2/curriculum_D6RF6/PREREGISTRATION.md`, PERMISSION=NOT_FROZEN, awaiting dafoam-supervisor freeze).

Supersedes: D6RF6 — A2-wing convergence probe `P_conv`, **BLOCKED** (a HARNESS defect, NOT physics). D6RF6's guard caught the expected post-`End` `Primal solution failed!` and STILL wrote the product, but with `points={}` + `primal_raised=True`; the section-3e planted-CD control returned NOT_EXERCISED only for a FILE-ABSENT artefact, so it hard-**REFUSED** on the PRESENT-BUT-EMPTY product (`REFUSE:PLANT_CD → CD_READER point_absent cl05 points_present=[]`) inside `run_planted_controls`, which runs BEFORE `gate_conv` — grading aborted (rc 2) and never reached G-CONV. Successor: D6RF7 — ONE class of DELTA, grading FAILURE-PATH handling, so the WHOLE path SURVIVES the present-but-empty (primal-raised) product and produces the graded verdict: one detector `cdc.points_empty_by_primal_raise` routes the planted-CD/FD controls to NOT_EXERCISED (never refuse) and G-OFF/G-PRICE/G-FD to NOT A RESULT (`ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY`); the fixture (D6RF6 run root, NO re-solve) then grades **G-CONV GATE FAIL** on L1 (binding p_first 1.6256e-05 = 1.626× the 1.0e-05 floor; nuTilda 1.408e-05 also over floor — Fix#1+Fix#2 insufficient), F5 AS PREDICTED, overall NOT A RESULT per the unaltered ladder rung 6 (want-of-input on the unbought FD/CD/off/price gates). Two latent read-path defects the fixture exposed were folded in (grading-side, no gate/scheme change): rank-duplicate LEG markers (`read_legs` now folds MPI-rank duplicates) and the stale `F5_loose`→`F5_scheme` mode name. Accept floor NOT moved (N-D43); scheme/mesh carried BYTE-IDENTICAL; no gate/threshold/band/cap widened (T25). Pin fixpoint ALL_PINS_MATCH, stager dry-run rc 0. REGISTERED DRAFT (`cases/dafoam/ladder-a/A2/curriculum_D6RF7/PREREGISTRATION.md`, PERMISSION=NOT_FROZEN, awaiting dafoam-supervisor check-1 + freeze).

Supersedes: D6R — A2 compressible multipoint optimisation, NOT A RESULT (no IPOPT EXIT; primal-acceptance failure). Successor chain: D6RF5 → SO3DR Stage-2 → D6R2 (D6RF5 and SO3DR Stage-2 both REGISTERED; `curriculum_D6RF5/`, `curriculum_SO3DR_stage2/`).

Supersedes: SO3DR — A2 dose-response GATE FAIL (H2 refuted — a valid result). Successor: SO3DR Stage-2, the cl04-standalone discrimination (REGISTERED, `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2/PREREGISTRATION.md`, `c83bfd41`; directed by RULING 3 §9.2).

Supersedes: D9 — A5 U-bend optimisation, NOT A RESULT (SLSQP driver failure + endpoint outside the mesh-quality envelope, maxNonOrth 80.93 > 70). Successor: D9successor, the meshQualityKS-constrained optimisation (REGISTERED, `cases/dafoam/ladder-a/A5/curriculum_D9successor/PREREGISTRATION.md`, ruled constraint-ALONE `cdca4d1e`).

Supersedes: D6RF3 — A2-wing lineage NOT A RESULT. Successor: D6RF4 → D6RF5 (above).

Supersedes: SO3a — A1 multipoint gradient-verification NOT A RESULT (comparator refusal). Successor: SO3aR → SO3aR2 (terminal PATCHED PASS; the FD basis MP-A1 rides).

Supersedes: A1WRT2 — A1 wall-refinement NOT A RESULT. Successor: A1WRT3 (successor draft on record).

Supersedes: S1_FD_PLATEAU — S1 CBFS field-inversion FD NOT A RESULT. Successor: W4-reanchor (REGISTERED, ran; BLOCKED on the anchor-snapshot infrastructure defect — a re-run of one leg, not a capability gap).

Supersedes: D2 — A1 shipped BLOCKED. Successor: the patched A1 optimisation, PATCHED PASS landed (two-row §6 semantics).

---

## 3. FORMERLY STILL-FLAGGED — the five now carry active dated fix-successors (state b)

**Update 2026-09-07.** The five fails that this section previously held out of the file — because their
successor was not yet registered and a `*SUCCESSOR*`-named file's tokens would have cleared them
prematurely (a diagnosis clears none, `§2ay.3`) — **now have registered successors** and so their
tokens are written into §1 above, deliberately and correctly:

- **`G-11`, `G-12`, `G-13`, `G-14`** (A3 rung-3 adjoint group: shipped-mode conditioning-wall
  non-convergence, the memory-stop attempt, the bit-identical INHERITED attempt, and the no-gradient
  row) → **A3R3PC** — the rung-3 adjoint with a WORKING preconditioner (`dafoam-subpclu:v2`, never
  tried there, or the ksp-options patch) + an adequate-memory plan. REGISTERED (DRAFT),
  `cases/dafoam/ladder-a/A3/curriculum_A3R3PC/PREREGISTRATION.md`.
- **`O-10`** (D2 AB2 flat-valley design-point non-uniqueness) → **D2ABR** — a regularized
  Adams-Bashforth re-run. REGISTERED (DRAFT),
  `cases/dafoam/ladder-a/A1/curriculum_D2ABR/PREREGISTRATION.md`. Alternative disposition (a Sanaa
  valid-terminal-result ruling) is **PARKED — hers alone**.

**None is a proven capability gap (state a).** Each is state (b): an active, dated, named attempt that
changes what failed and re-runs. The A3 conditioning wall remains the one *hypothesis* of a genuine
capability gap in the whole set — and it stays state (b) until the sub-LU / ksp-options preconditioner
has actually been run on rung-3 (`4ae4b33`: keep fixing until it runs, or MEASURE the gap and file it).

---

## 4. SUMMARY FOR THE ENFORCER AND THE CHIEF

- **11 flagged matrix fails:** **all 11 now cleared to state (b)** with landed or registered
  successors (§1); **0 still flagged**; **0 proven capability gaps (a).** (Was, until 2026-09-07:
  6 cleared, 5 flagged.)
- **Newer curriculum fails (§2):** all bridged to registered successors. **Enumeration note:** these
  newer ids are not in `cases/dafoam/MATRIX_CONTRIBUTION.md` and so are not enumerated by the enforcer
  unless a source carrying their verdict rows is added; that companion is
  `cases/dafoam/DAFOAM_NEWER_ID_VERDICT_RECORD.md` (see it for the SOURCES-addition request). Their
  coverage lives here in §2.
- **The one hypothesis of a genuine capability gap** in the whole set is the A3 rung-3 conditioning
  wall — state (b) pending the sub-LU / ksp-options attempt that has never been run there.
- **Upstream defect filings referenced (D-A, D-B) are prepared and NOT FILED — Sanaa's alone.**
