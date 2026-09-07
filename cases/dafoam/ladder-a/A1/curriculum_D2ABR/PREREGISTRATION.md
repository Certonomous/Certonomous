# DRAFT — NOT FROZEN — awaiting dafoam-supervisor check-1 read and freeze

**`D2ABR` — D2 Adams-Bashforth REGULARIZED re-run. The active dated fix-successor to `O-10`.**

Drafted 2026-09-07 by a `lab-lane` on the dafoam-supervisor's brief. **The freeze and the enqueue
belong to the dafoam-supervisor and are not taken here.** No gate, threshold, cap or label in this
file is registered until that supervisor freezes it by sha (`VERIFICATION_CHARTER.md` §2b; `CLAUDE.md`
rule 2). Until then it is a lane's prediction-first proposal, written so the supervisor can read it as
a diff, size every predicted number against its own bar, and freeze it — or send it back.

**SUBMISSIONS PARKED.** Nothing here is sent, filed or uploaded (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

<!-- RECORDED-LINEAGE FIELD (§2ay.2(b)); first case-id token on the line = the superseded/flagged case. -->

Supersedes: O-10 — D2 AB2 design-point non-uniqueness, `GATE FAIL` (the item's REGISTERED FINDING, not a defect of the item). `‖Δshape‖₂/‖shape_A‖₂ = 33.259 %` against the frozen 10.0 % band; `‖Δshape‖_∞ = 1.9379e-02` against 8.0e-03 (more than twice `shape[6]`'s entire value); `|ΔAoA| = 0.2428` deg, inside 0.25. Evidence: `cases/dafoam/ladder-a/A1/curriculum_D2` grading, row commit `b840fcd5`. D2ABR regularizes the NLP and re-runs.

---

## 0. WHAT O-10 ACTUALLY MEASURED, STATED PLAINLY

Two optimizers (AB1, AB2) reach **different design points** on the D2 NLP. **AB1 passes the frozen
shape-agreement band and AB2 fails it, and that combination IS the result:** on this NLP the objective
is close to **flat along the direction that separates the two designs**. O-10 is therefore a statement
about the two algorithms and the problem's conditioning (a **flat-valley non-uniqueness**), **not an
aerodynamic finding.** It is a registered finding, not a defect of the item — which is exactly why it
owes either (i) a regularized re-run that resolves whether the non-uniqueness is a removable artifact
of the flat objective, or (ii) a Sanaa terminal ruling that a registered non-uniqueness finding is a
valid terminal result. **This item is disposition (i).**

## 1. WHAT D2ABR CHANGES — AND WHAT IT DOES NOT

**1a. The change (numerics/conditioning, NOT the bar).** D2ABR adds a **regularization term** to the
D2 NLP — a small, registered shape-regularizer (candidate forms to fix at freeze: an `‖Δshape‖₂`
Tikhonov penalty, a shape-smoothness / curvature penalty, or a trust-region radius on the shape step)
— chosen to **convexify the flat valley** that separates the two AB design points, and re-runs the
Adams-Bashforth optimisation. Both the AB1 and AB2 arms are re-run under the identical regularizer so
the design-point comparison is like-for-like.

**1b. The bar is NOT widened.** The **acceptance band is frozen and carried byte-identical from O-10**:
`L2`-relative **10.0 %**, `L∞` **8.0e-03**, `|ΔAoA|` **0.25 deg**. D2ABR judges the *regularized* AB1↔AB2
design-point agreement against that **same** band. The regularizer is applied to the optimizer's
objective/step, never to the acceptance threshold (Sanaa 2026-09-04; the gate is never widened to fit).

**1c. The two outcomes, both honest and pre-committed:**

- **Design points AGREE within the frozen band under regularization** → the non-uniqueness was a
  **removable artifact of the flat objective**; the regularized design point is the resolved answer,
  reported with the regularizer strength that achieved it and a sensitivity of the design to that
  strength (so the regularizer is not silently choosing the answer).
- **Design points STILL DISAGREE under regularization** → the non-uniqueness is **genuine** (not a
  conditioning artifact), which strengthens — but does not itself decide — disposition (ii). That
  decision is Sanaa's.

## 2. THE ALTERNATIVE DISPOSITION — PARKED

The alternative to this re-run is a **Sanaa valid-terminal-result ruling**: that O-10's registered
flat-valley non-uniqueness is itself a valid terminal result requiring no further compute. **That path
is Sanaa's alone and is PARKED — nothing is sent, filed, escalated or posted from here** (`CLAUDE.md`
rule 7). This item does not pre-empt it; if she so rules, D2ABR is stood down, not run. Recording the
alternative here is scope disclosure, not a request.

## 3. PRE-REGISTERED COST (lane estimate — the supervisor sizes at freeze)

| quantity | value | basis |
|---|---|---|
| predicted core-minutes (estimate) | **180 core-min** | two regularized AB optimisations (AB1 + AB2) on the small A1 NACA0012 mesh to optimizer convergence; ~90 core-min each. np and mesh size to be confirmed against the D2 case at freeze; A1 opts have historically run np=1 on a few-thousand-cell mesh. |
| **cap (overrun STOPS the run — no second budget)** | **270 core-min** | 1.5× the estimate; past the cap the verdict is `NOT A RESULT` — stopped by budget (`CLAUDE.md` rule 12). |
| cost_basis (derived $, **reported-by-owner, NOT measured**) | estimate ≈ **$0.154** (3.0 core-h × $0.0513/core-h); cap ≈ **$0.231** (4.5 core-h) | c7a.4xlarge at $0.0513/core-h, owner-stated (`COMPUTE_BUDGET_CHARTER.md` §5: derived, reported-by-owner, never measured — the box cannot read its own billing). Under the $25 pre-authorised ceiling. |

Estimate-vs-actual calibration owed at completion (`CLAUDE.md` rule 12) into `docs/COST_CALIBRATION.md`.

## 4. EXECUTABLE REFUSALS TO REGISTER AT FREEZE (§6, sketched)

1. `BAND_UNMOVED` — reads the acceptance band (10.0 % / 8.0e-03 / 0.25 deg) back and refuses (exit 2)
   if any value differs from O-10's frozen band, in either direction.
2. `REGULARIZER_PRESENT` — asserts the registered regularizer actually loaded and its strength is the
   registered value (a planted-control on the fix; `CLAUDE.md` rule 3).
3. Strict completion + age guard (`CLAUDE.md` rule 4) and planted-zero control (rule 3) as standard.

**This document authorises no launch. When approved it becomes a new item with its own frozen
pre-registration, its own commit and its own budget.**
