# DRAFT — NOT FROZEN — awaiting dafoam-supervisor check-1 read and freeze

**`A3R3PC` — A3 rung-3 adjoint with a WORKING preconditioner + an adequate-memory plan.
The active dated fix-successor to `G-11`, `G-12`, `G-13`, `G-14`.**

Drafted 2026-09-07 by a `lab-lane` on the dafoam-supervisor's brief. **The freeze and the enqueue
belong to the dafoam-supervisor and are not taken here.** No gate, threshold, cap or label in this
file is registered until that supervisor freezes it by sha (`VERIFICATION_CHARTER.md` §2b; `CLAUDE.md`
rule 2). Until then nothing here is a registration: it is a lane's prediction-first proposal, written
so the supervisor can read it as a diff, size every predicted number against its own bar, and freeze
it — or send it back.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed or uploaded anywhere (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). Upstream toolchain-defect drafts (D-A/D-B) remain **NOT FILED** — Sanaa's alone.

<!-- RECORDED-LINEAGE FIELDS (§2ay.2(b); read by scripts/check_completion_enforcement.py's
     recorded-lineage reader from a *PREREGISTRATION*-named file's line-leading Supersedes:/Predecessor:
     field, first case-id token on the line = the superseded/flagged case). One line per predecessor,
     because the reader keys on the FIRST case-id match per line. -->

Supersedes: G-11 — A3 rung-3 shipped-mode adjoint, `GATE FAIL` (4,000 iterations, `reason −3`, 1.31× residual reduction; peak 11.65 of 22 GiB, a conditioning wall not a memory one). `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2d, commit `35171866`. A3R3PC changes the PRECONDITIONER of the adjoint linear solve.
Supersedes: G-12 — A3 rung-3 patched adjoint attempt 1, `NOT A RESULT` — stopped by memory (host-floor guard: MemAvailable 7.3944 GiB < 8.0, RSS 9.202 of 15.0 GiB; killed at 85 s of 2,600 s; 0 of 11 checkpoints). `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/RESULTS.md`, commit `67edcc19`. A3R3PC changes the MEMORY PLAN.
Supersedes: G-13 — A3 rung-3 patched adjoint attempt 2, `GATE FAIL` (adjoint, INHERITED) — all 11 KSP residual checkpoints bit-identical to the frozen shipped-equivalent path, NO `PetscConvergedReason` printed, terminal −3 inherited; rc=137 the registered deliberate stop. `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md`, graded `8871acf3`, row commit `bec36c9d`. A3R3PC changes the actual conditioning, so the KSP path is no longer inherited.
Supersedes: G-14 — A3 rung-3 gradient, rotation-patched, `NOT A RESULT` — no gradient was produced on rung 3 by any patched arm; silent both ways on rung 2's degradation finding. Same file, grading `8871acf3`, row commit `bec36c9d`. A3R3PC makes a gradient exist by converging the adjoint.

---

## 0. THE BRIGHT LINE, STATED FIRST

**The adjoint-convergence gate and the FD-vs-adjoint band ARE NOT WIDENED in this item.** A3R3PC
changes *how* the rung-3 adjoint is solved (its preconditioner) and *how much memory the launch is
given* (its gate limb) — it does **not** relax the bar the rung-3 registration set for a converged
adjoint or for a graded gradient. The gate is worked until it passes; the gate is never widened to fit
(Sanaa 2026-09-04; `N-D43`). If the working preconditioner still cannot drive the adjoint below floor,
the honest verdict stays `GATE FAIL`/`NOT A RESULT`, and only THEN is a capability-gap filing on
Sanaa's desk reachable (state (a)) — never before the preconditioner has been tried (`4ae4b33`:
keep fixing until it runs, or MEASURE the gap and file it).

## 1. WHY A SUCCESSOR — THE MECHANISM EACH PREDECESSOR MEASURED

The A3 rung-3 group (79,560 cells, np=4) has **four flagged rows that all resolve to two distinct,
measured mechanisms**, neither of which has ever been met by the fix it calls for:

| flagged | verdict | what it MEASURED | why it is not a capability gap yet |
|---|---|---|---|
| **G-11** | `GATE FAIL` | The shipped-mode adjoint KSP does not converge: 4,000 iterations, `reason −3`, only **1.31× residual reduction**. Peak 11.65 GiB of 22 — a **conditioning wall**, explicitly measured as *not* a memory one. The `dafoam-subpclu:v1` banner was **absent** (stock preconditioner path). | The sub-LU preconditioner `dafoam-subpclu:v2` has **never been tried on this rung**. A non-converging KSP under the *stock* preconditioner is a preconditioner-class question (§2an), the one process class not yet ruled out. |
| **G-12** | `NOT A RESULT` | A registration-design memory defect, not numerics: the launch-gate memory limb (16 GiB) admitted a launch its own 8 GiB neighbourliness floor then killed 60 s later. RSS 9.202 GiB, 0 of 11 identity checkpoints reached. | A gate that admits a launch its floor will kill is not a gate (L-239 in a new size). The numerics question was never reached. |
| **G-13** | `GATE FAIL` (INHERITED) | The IDWarp rotation patch is **orthogonal to the adjoint conditioning**: all 11 KSP checkpoints came back **bit-identical** to the shipped path (`1.615247229756e-02` at 1000; 1.3133× flat), and the arm printed **no** `PetscConvergedReason` — the −3 is the shipped value carried across by bit-identity. | The patch changed the mesh-warp toolchain, not the linear solve — so it could not touch what failed. The conditioning was never changed. |
| **G-14** | `NOT A RESULT` | No gradient exists on rung 3 because no patched arm's adjoint converged. | A gradient is downstream of a converged adjoint; it becomes reachable the moment G-11's mechanism is fixed. |

**The single hypothesis of a genuine capability gap in the whole A3 set is G-11's conditioning wall —
and it is state (b) until the preconditioner it names has actually been run here.**

## 2. WHAT A3R3PC CHANGES

**2a. The preconditioner (the fix for G-11 and G-13).** The adjoint linear solve is re-run with a
WORKING preconditioner:

- **Primary:** the sub-LU preconditioner **`dafoam-subpclu:v2`** — never applied on A3 rung-3. The
  banner presence is asserted at grade time (the `v1` banner was *absent* in G-11; an executable
  `SUBPCLU_BANNER_PRESENT` refusal, §6, reads it back from the container log and stops grading if the
  working preconditioner did not actually load — a planted-control on the fix itself, `CLAUDE.md`
  rule 3).
- **Fallback (registered as the alternative arm, not a widening):** the **ksp-options patch** (an
  explicit PETSc KSP/PC option set: e.g. a stronger sub-block factorisation / restart / GMRES basis
  tuning) if `v2` is unavailable at freeze. Whichever loads, the acceptance floor is unchanged.

This directly addresses G-13's INHERITED verdict: because the change is *inside* the linear solve, the
11 KSP checkpoints can no longer be bit-identical to the shipped path — the executable guard asserts
the checkpoints DIFFER from the frozen shipped fingerprint (else the preconditioner did nothing and
the verdict stays INHERITED, honestly).

**2b. The memory plan (the fix for G-12).** The launch-gate memory limb is registered at
**`MemAvailable ≥ 19.65 GiB`** — the shipped arm's **complete, measured** peak
(`A3_RUNG3_REREGISTRATION_PROPOSAL.md` §3; 11.65 GiB was the *conditioning-wall* peak of the shipped
arm reported in G-11's row, and 19.65 = that complete peak basis + the 8.0 GiB neighbourliness floor
under the proposal's own rule `gate_limb ≥ floor + predicted_peak`). **Disclosed risk, registered
beside the threshold, not in a footnote:** if the 17.19 GiB stage-0 lever record governs, even 19.65
GiB is too low and the correct limb is 25.2 GiB (82% of the box's 30.64 GiB `MemTotal`); this item
does not resolve which governs and registers that if the guard fires the verdict is `NOT A RESULT` —
stopped by memory, with **no second budget** (`CLAUDE.md` rule 12).

**2c. The gradient (the fix for G-14).** Once the adjoint converges, the gradient exists; the FD-vs-
adjoint check on rung 3 and the Roache triple on the already-existing 3-level mesh family
(21,840 / 42,120 / 79,560 cells) become reachable. **Scope note:** A3R3PC's own gate is the converged
adjoint + a produced gradient; the FD reference and the GCI triple are the immediate downstream item
and are named here, not folded into this cost.

## 3. PRE-REGISTERED COST (lane estimate — the supervisor sizes at freeze)

| quantity | value | basis |
|---|---|---|
| predicted core-minutes (estimate) | **300 core-min** | primal warm-restart (~15 min wall) + one adjoint solve to floor under a working preconditioner (~40 min wall, generous for a first working attempt) + gradient assembly, np=4: ~75 min wall × 4 ranks ≈ 300 core-min. Anchored on G-12's 2,600 s (43 min) intended budget and the shipped 4,000-iteration adjoint. |
| **cap (overrun STOPS the run — no second budget)** | **450 core-min** | 1.5× the estimate; a run past the cap is `NOT A RESULT` — stopped by budget, per `CLAUDE.md` rule 12. |
| cost_basis (derived $, **reported-by-owner, NOT measured**) | estimate ≈ **$0.257** (5.0 core-h × $0.0513/core-h); cap ≈ **$0.385** (7.5 core-h) | c7a.4xlarge at $0.0513/core-h, owner-stated (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing, so any $ is derived and reported-by-owner, never measured). Under the $25 pre-authorised ceiling. |

Estimate-vs-actual calibration is owed at completion (`CLAUDE.md` rule 12) into `docs/COST_CALIBRATION.md`.

## 4. EXECUTABLE REFUSALS TO REGISTER AT FREEZE (§6, sketched)

1. `SUBPCLU_BANNER_PRESENT` — reads the working-preconditioner banner back from the container log;
   refuses (exit 2) if the stock path loaded instead (the fix did not actually apply).
2. `KSP_PATH_DIFFERS` — asserts the rung-3 KSP checkpoints are **not** bit-identical to the frozen
   shipped fingerprint (else the preconditioner did nothing; guards against a repeat INHERITED verdict).
3. `MEM_GATE_PROTECTS_FLOOR` — asserts `gate_limb ≥ neighbourliness_floor + predicted_peak` before launch.
4. Strict completion + age guard (`CLAUDE.md` rule 4) and planted-zero control (rule 3) as standard.

**This document authorises no launch. When approved it becomes a new item with its own frozen
pre-registration, its own commit and its own budget.**
