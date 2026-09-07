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

---

## 2. CLEARED — newer curriculum `D#`/`SO#` fails bridged to their registered successors (state b)

These verdicts postdate the Aug-25 matrix and so are absent from it; recorded here so the enforcer sees
their coverage. Each has a registered `PREREGISTRATION`/`SUCCESSOR` on disk.

Supersedes: D6RF4 — A2-wing convergence probe, NOT A RESULT (p first-solve at 1.66× the 1e-05 floor). Successor: D6RF5 (REGISTERED, `cases/dafoam/ladder-a/A2/curriculum_D6RF5/PREREGISTRATION.md`, sizing `9ed7aa78`).

Supersedes: D6R — A2 compressible multipoint optimisation, NOT A RESULT (no IPOPT EXIT; primal-acceptance failure). Successor chain: D6RF5 → SO3DR Stage-2 → D6R2 (D6RF5 and SO3DR Stage-2 both REGISTERED; `curriculum_D6RF5/`, `curriculum_SO3DR_stage2/`).

Supersedes: SO3DR — A2 dose-response GATE FAIL (H2 refuted — a valid result). Successor: SO3DR Stage-2, the cl04-standalone discrimination (REGISTERED, `cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2/PREREGISTRATION.md`, `c83bfd41`; directed by RULING 3 §9.2).

Supersedes: D9 — A5 U-bend optimisation, NOT A RESULT (SLSQP driver failure + endpoint outside the mesh-quality envelope, maxNonOrth 80.93 > 70). Successor: D9successor, the meshQualityKS-constrained optimisation (REGISTERED, `cases/dafoam/ladder-a/A5/curriculum_D9successor/PREREGISTRATION.md`, ruled constraint-ALONE `cdca4d1e`).

Supersedes: D6RF3 — A2-wing lineage NOT A RESULT. Successor: D6RF4 → D6RF5 (above).

Supersedes: SO3a — A1 multipoint gradient-verification NOT A RESULT (comparator refusal). Successor: SO3aR → SO3aR2 (terminal PATCHED PASS; the FD basis MP-A1 rides).

Supersedes: A1WRT2 — A1 wall-refinement NOT A RESULT. Successor: A1WRT3 (successor draft on record).

Supersedes: S1_FD_PLATEAU — S1 CBFS field-inversion FD NOT A RESULT. Successor: W4-reanchor (REGISTERED, ran; BLOCKED on the anchor-snapshot infrastructure defect — a re-run of one leg, not a capability gap).

Supersedes: D2 — A1 shipped BLOCKED. Successor: the patched A1 optimisation, PATCHED PASS landed (two-row §6 semantics).

---

## 3. STILL FLAGGED — five fails that OWE a not-yet-registered successor

**Their matrix ids are DELIBERATELY NOT written in this `*SUCCESSOR*`-named file**, because the
enforcer clears any case-id token that appears in such a file's text, and these must stay FLAGGED
until their successor is actually registered (a diagnosis clears none, `§2ay.3`). They are tracked in
full — with their ids, verdicts and named-but-unregistered successors — in the dafoam board
(`docs/LAB_STATE.md`, block S-116) and in the supervisor's report to the chief. In summary, and
without their tokens: the A3 rung-3 adjoint group (four flagged rows — shipped-mode non-convergence,
two patched attempts, and the gradient row) owes an adjoint with a WORKING preconditioner (the sub-LU
`dafoam-subpclu:v2` never tried there, or the ksp-options patch) plus an adequate-memory plan; and the
AB design-point row owes either a regularized re-run to confirm its flat-valley non-uniqueness or a
Sanaa ruling that a registered non-uniqueness finding is a valid terminal result. **None is a proven
capability gap; both are state (b) pending a named attempt.**

---

## 4. SUMMARY FOR THE ENFORCER AND THE CHIEF

- **11 flagged matrix fails:** **6 cleared to state (b)** with landed/registered successors (§1); **5
  still flagged** owing a not-yet-registered successor (§3, tokens held out deliberately); **0 proven
  capability gaps (a).**
- **Newer curriculum fails (§2):** all bridged to registered successors.
- **The one hypothesis of a genuine capability gap** in the whole set is the A3 rung-3 conditioning
  wall — and it is state (b) pending the sub-LU / ksp-options attempt that has never been run there,
  exactly as `4ae4b33` requires (keep fixing until it runs, or MEASURE the gap and file it).
- **Upstream defect filings referenced (D-A, D-B) are prepared and NOT FILED — Sanaa's alone.**
