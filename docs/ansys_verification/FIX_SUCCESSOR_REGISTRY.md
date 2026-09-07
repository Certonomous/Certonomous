# FIX / SUCCESSOR REGISTRY — Ansys VM landed fails under §2ay

**STATUS: DRAFT — for the ansys-verification supervisor's §2ay.7 diff-read and commit.**
Drafted by `ansys-lane-opus` (running as **claude-opus-4-8**), **2026-09-06**. **Zero
compute** — no solver was started; this is a reading of the register, the adopted
`RECOVERABILITY_SWEEP.md`, the supervisor's dated rulings of 2026-09-06, and the frozen
per-case pre-registrations. Nothing here is filed, sent or contacted upstream (rule 7).

**Law this registry answers to.** `VERIFICATION_CHARTER §2ay` (commit `75463642`) makes
Sanaa's "fix until it runs" executable. Its instrument `scripts/check_completion_enforcement.py`
flags every landed `GATE FAIL` / `NOT A RESULT` that is not in one of two acceptable
states: **(a)** a MEASURED, on-Sanaa's-desk capability-gap filing with all six of
bug / solver-selection / preconditioner / numerics-scheme / config / model-form ruled out
at source; or **(b)** an ACTIVE, DATED fix-successor — a registered next attempt that
**changes what failed and re-runs**, or its discharge by a landed passing successor.

**THE HEADLINE — read this before the table.** **NONE of the 18 cases below is a proven
OpenFOAM capability gap (state a).** Every one carries a live fix path and is therefore
**state (b)**. This is the answer the adopted `RECOVERABILITY_SWEEP.md` reached at source
("zero proven capability gaps; every fail carries a live fix path") and it is not changed
here. **⚠ §2ay.3 honesty bar:** each entry below is a *genuine registered next attempt that
changes the failing lever and re-runs* — NOT a bare mechanism diagnosis. A diagnosis alone
does not clear a flag; a dated successor with a concrete lever does. **No gate, threshold,
band, cap, tier or verdict is touched by this file.** It only records the next attempt each
landed fail is being carried forward by.

**Status vocabulary.** **LIVE** = a successor is frozen and queued/running now. **REGISTERED**
= a successor pre-registration directory already exists on disk (a later attempt already
run, or its prereg frozen and ready). **OWED-DATED-PLAN** = the next attempt is registered
*here*, dated, with its concrete lever named; its case directory is to be created and frozen
before that compute, per rule 2. All three are state (b) under §2ay.1.

**Verdicts were read from the register**
(`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`), the same artifact the
instrument enumerates from; the same fail rows also appear in `docs/capability/ansys_ROWS.md`
and `docs/CAPABILITY_GRID.md`. Case-id tokens below are written exactly as the instrument
extracts them, so each clears its every duplicate row.

---

## SUMMARY

- **Landed fails carried here:** 19. **Capability gaps (state a):** **0**. **State (b):** **19**.
- **LIVE:** 0 — VMFL046-R5 GRADED 2026-09-07 `NOT A RESULT` (register row #62): the shock
  **washed out** because `waveTransmissive lInf 2.0` un-anchored the back-pressure (outlet p
  collapsed to ~10% of the 176 325 Pa target). NOT a hunt. The R4 outlet-reflection question is
  therefore left OPEN, and the successor for the whole VMFL046 lineage is now **VMFL046-R6 with a
  back-pressure-anchoring outlet** (the pre-committed `rhoCentralFoam` R6 recipe carries the same
  defective `lInf 2.0` outlet and MUST fix it before freeze). State (b), a config/BC lever, not a
  capability gap.
- **REGISTERED (successor dir exists):** 3 — VMFL007-R2 → `VMFL007-R3`; VMFL011-R2 → `VMFL011-R3`;
  **VMFL054-R2 → `VMFL054-R3` (prereg + comparator FROZEN 2026-09-07, freeze `addd8240`; --selftest 16/16; LAUNCH HELD on Sanaa's desk)**.
- **OWED-DATED-PLAN (next attempt registered here):** 16 — the four VMFL046 lineage rows
  (VMFL046-INVISCID, VMFL046-R2, VMFL046-R3, **VMFL046-R5**, all → the outlet-anchored
  **VMFL046-R6**, dated 2026-09-07) plus the twelve dated 2026-09-06: VMFL003-M2, VMFL010,
  VMFL011-R3, VMFL017-R2, VMFL022, VMFL034-R2, VMFL051, VMFL063, VMFL072-R2,
  VMFLGPU002, VMFLGPU003, VMFLGPU005.

**GPU note (Task 1 finding).** VMFLGPU002, VMFLGPU003 and VMFLGPU005 are **LANDED, GRADED
verdicts, not drafts** — the GPU solver ran, the frozen comparator graded it (rc/exit 0 in
each, NOT an instrument refusal), and the verdict is recorded in the register with preserved
run artifacts under `verification/runs/ansys_verification/VMFLGPU00{2,3,5}/`. They are NOT
instrument false-positives; they genuinely need a dated successor like the CPU cases. GPU
quota is granted (us-east-2); `BLOCKED-GPU` is retired (CLAUDE.md rule 12), so a re-run is a
legitimate lever.

---

## REGISTRY TABLE

| Case (exact token) | Verdict | §2an.5 process class | Dated active successor — WHAT IT CHANGES, and it RE-RUNS | Status |
|---|---|---|---|---|
| **VMFL003-M2** | `NOT A RESULT` | #2 convergence (ε residual floor / wall-treatment) | **VMFL003-M3** — the M2 arms varied only `endTime`/grid; M3 changes the **near-wall treatment**: kOmegaSST or low-Re kEpsilon wall-resolved y+≈1 (or standard kEpsilon with the y+ 30–300 band held across all three levels) and a relaxed ε linear solver / residualControl, then re-runs the frozen triple. | OWED-DATED-PLAN |
| **VMFL007-R2** | `NOT A RESULT` | #4 instrument (planted-zero control refused, exit 2; no physics graded) | **VMFL007-R3** — repairs the planted-zero control so the reader is shown able to see a non-zero (sibling repair pattern in `VMFL011-R3/`), then re-registers and re-runs the pipe profile. Directory `cases/ansys_verification/VMFL007-R3/` exists. | REGISTERED |
| **VMFL010** | `NOT A RESULT` | #2 grid (triple OSCILLATORY) | **VMFL010-R2** — replaces the mesh family with a **structured hex triple, r=2 cleanly-refined at the junction** so the flow-split functional converges monotonically, then re-runs. | OWED-DATED-PLAN |
| **VMFL011-R2** | `NOT A RESULT` | #4 instrument (earlier planted-control refusal) | **VMFL011-R3** — the instrument refusal that failed R2 is fixed (rc measured, clean End, planted control fires); R3 re-ran the case and landed a graded value. Directory `cases/ansys_verification/VMFL011-R3/` exists. | REGISTERED |
| **VMFL011-R3** | `GATE FAIL` | #2 grid `[inferred]` (rms still falling with refinement) | **VMFL011-R4** — adds an **L4 finer level** and a higher-order convection scheme (linearUpwind→linear), and **bounds the Jyotsna & Vanka digitisation error** (§2al/§2am) before reading the band; re-runs the extended ladder against the frozen band ≤0.030. | OWED-DATED-PLAN |
| **VMFL017-R2** | `NOT A RESULT` | #1 completion (per-level cap rc=124 + comparator refused; no gradeable value) | **VMFL017-R3** — a **converging transonic rhoSimpleFoam setup** (the base VMFL017 divergence is process class #3, a finding until triaged): relaxation/under-relaxation and a stable transonic initialisation so the solve completes to `endTime`, then re-runs. | OWED-DATED-PLAN |
| **VMFL022** | `NOT A RESULT` | #2 grid (triple OSCILLATORY; cavitating solve ran) | **VMFL022-R2** — a **monotone grid triple with refined near-orifice resolution**, mirroring the `VMFL021-R2` recovery recipe (`interPhaseChangeFoam` is present; no cavitation capability gap), then re-runs against the frozen 5% band. | OWED-DATED-PLAN |
| **VMFL034-R2** | `NOT A RESULT` | config / numerics (per supervisor ruling 2026-09-06 — NOT a capability gap) | **VMFL034-R3** — supervisor-ruled today: a `limitVelocity` fvOption, a CFL-limited transient, **or** a frozen-flow re-scope (dilute alpha2), with a manual regime-check that **must not widen the gate** (L-487 anti-circularity preserved); re-runs. | OWED-DATED-PLAN |
| **VMFL046-INVISCID** | `NOT A RESULT` | config / numerics (outlet reflection at the boundary) | **VMFL046-R6 (outlet-anchored)** — R5 (register #62) tried the single-variable `fixedValue`→`waveTransmissive lInf 2.0` outlet and graded `NOT A RESULT`: it did NOT hunt, the shock **washed out** because `lInf 2.0` un-anchored the back-pressure. R6 = the pre-committed `rhoCentralFoam`/Kurganov recipe (`VMFL046-R5/PREREGISTRATION.md §6`) **with its outlet BC fixed to anchor `p≈176 325 Pa` while damping reflections** (gate-blind choice; the `lInf 2.0` carry-forward is now known-defective). Re-runs. | OWED-DATED-PLAN |
| **VMFL046-R2** | `NOT A RESULT` | config / numerics (outlet reflection at the boundary) | **VMFL046-R6 (outlet-anchored)** — same lineage successor; R5's non-reflecting outlet washed the shock out (#62), so R6 carries `rhoCentralFoam`/Kurganov with a back-pressure-anchoring outlet, not `lInf 2.0`. Re-runs. | OWED-DATED-PLAN |
| **VMFL046-R3** | `NOT A RESULT` | config / numerics (outlet reflection at the boundary) | **VMFL046-R6 (outlet-anchored)** — same lineage successor; R6 = `rhoCentralFoam`/Kurganov with a back-pressure-anchoring outlet (R5's `lInf 2.0` washed out, #62). Re-runs. | OWED-DATED-PLAN |
| **VMFL046-R5** | `NOT A RESULT` | config / numerics (outlet un-anchored the back-pressure — the shock washed out; register #62, diagnosed 2026-09-07) | **VMFL046-R6 (outlet-anchored)** — the `waveTransmissive lInf 2.0` outlet relaxed the exit pressure to ~10% of target and the shock washed out of the domain (not a hunt, uniform at L1/L2/L3). R6 keeps the density-based `rhoCentralFoam`/Kurganov shock-capturing path but **must replace the outlet with a partially-reflecting subsonic outlet that anchors `p≈176 325 Pa`** (candidates to research/pin gate-blind: a smaller geometric `lInf`, an alternative anchoring BC, or the Fluent pressure-outlet equivalent) — a density-based solver does not restore a lost back-pressure. Re-runs. | OWED-DATED-PLAN |
| **VMFL051** | `NOT A RESULT` | #2 grid (triple OSCILLATORY) | **VMFL051-R2** — a **monotone grid triple** plus a **Mach functional sampled on a downstream line** (less shock/expansion-position sensitive than a volume zone), sibling to the VMFL045 oblique-shock recovery; re-runs against the frozen ±0.5% band. | OWED-DATED-PLAN |
| **VMFL054-R2** | `GATE FAIL` | #2 grid (order not asymptotic — observed p=3.438 ∉ [1,3]) | **VMFL054-R3** — adds a **4th finer level L4 = 320×320 (r=2)** so the order is graded on the FIXED finest triple L2/L3/L4 (nearest the asymptotic range), with a 4-point settling diagnostic; band [1,3] AND GCI ≤ 5 % frozen **BYTE-IDENTICAL** to R2 and **NOT widened** (L-487 anti-circularity). Directory `cases/ansys_verification/VMFL054-R3/` exists; prereg + comparator FROZEN at **`addd8240`** (comparator blob `fd959928`, driver blob `f451c24c`; `--selftest` 16/16; L4 mesh checkMesh OK, L4 solve de-risked converging within cap). Re-runs the extended ladder. **LAUNCH HELD** (Sanaa's desk, rule 9). | REGISTERED |
| **VMFL063** | `GATE FAIL` | #2 grid (GCI_fine 120.6% ≫ the 40% deviation) | **VMFL063-R2** — **refines the triple** (finer, separation-region graded mesh) to bring GCI below the deviation, plus higher-order convection (linearUpwind→linear), so the reattachment length is read on a converged grid; re-runs. | OWED-DATED-PLAN |
| **VMFL072-R2** | `NOT A RESULT` | numerics / model (film dewetting), per supervisor routing 2026-09-06 | **VMFL072-R3** — dewetting remedy: an alternate film model `kinematicSingleLayer`, **or** precursor-film regularization, **or** a VOF re-formulation; the anti-circularity property (L-487) is kept; re-runs. | OWED-DATED-PLAN |
| **VMFLGPU002** | `NOT A RESULT` | #2 grid (GPU triple OSCILLATORY, R=−0.197; limb B GPU=CPU at 4.07e-10) | **VMFLGPU002-R2** — a **monotone grid triple** for the flow-split functional (structured, r=2 cleanly refined near the split), re-run **on the GPU path** (petsc4Foam) so the split converges monotonically; the verified GPU=CPU agreement is unaffected. Re-runs. | OWED-DATED-PLAN |
| **VMFLGPU003** | `GATE FAIL` | #2 grid / referent (limb C rms 0.0341 vs 0.030 band, CONVERGING triple; digitised benchmark) | **VMFLGPU003-R2** — GPU sibling of VMFL011-R3: adds an **L4 finer level** + higher-order convection and **bounds the Jyotsna & Vanka digitisation error** (§2al/§2am), re-run on the GPU path; limbs A/B already hold, so the physics limb is the lever. Re-runs. | OWED-DATED-PLAN |
| **VMFLGPU005** | `NOT A RESULT` | #2 grid (rule 5 disqualified channels C1/C2 non-CONVERGING; limb B PASS at 2.957e-10) | **VMFLGPU005-R2** — rebuilds **monotone/CONVERGING grid triples for the C1/C2 physics channels** (finer, cleanly refined), re-run on the GPU path; the verified GPU path (limb B) is unaffected. Re-runs. | OWED-DATED-PLAN |

---

## FILING NOTE

This is a durable, checkable state-(b) registry (the recognized `*SUCCESSOR*`-named shape the
§2ay instrument reads), so a repository document under the team's owned
`docs/ansys_verification/` is the correct form (FILING_CHARTER). It carries no gate,
threshold, band or verdict change. To be reviewed under the supervisor's §2ay.7 diff-read
and committed under the CLAUDE.md rule-10 private-index protocol. Each OWED-DATED-PLAN
successor's case directory and frozen pre-registration is created **before** its compute
(rule 2); this file registers the dated intent and the concrete lever, not a completed run.
