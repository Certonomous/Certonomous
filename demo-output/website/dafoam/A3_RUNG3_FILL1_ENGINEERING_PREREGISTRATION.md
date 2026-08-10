# Rung 3 `pcFillLevel: 1` — ENGINEERING arm, explicitly OUTSIDE the proof: PRE-REGISTRATION

Filed 2026-08-10, chief ruling 2. Committed BEFORE compute.

## 1. What this arm is, and what it is not

**It is an attempt to make rung 3 converge. It carries NO diagnostic claim.** The Saad diagnosis
(`A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md`, outcome `368996c3`) never indicted
dropped ILU fill — the dropping was never measured — so nothing in the diagnosis predicts this
will work or explains it if it does.

**Binding, and stated before the result exists:** if this converges, the record says **"a knob
converged it and we do not know why."** It **must not** retro-justify the diagnosis, and it does
not convert the NOT-MET proof clause into a met one. A convergence here would add a *boundary
condition* to the ceiling statement, not a *mechanism* for it. I am writing that now precisely
because a convergence is the outcome most likely to tempt a different reading later.

## 2. Configuration

Staged copy of the rung-3 case; identical to the diagnostic control in every respect except
**`pcFillLevel: 0 → 1`**, plus two deliberate differences from that control, both stated:
`gmresMaxIters` 400 → **800**, and the `-ksp_monitor_true_residual` monitor **dropped** (it costs
an extra matvec per iteration and A1 already established the recursive residual is faithful, so
the monitor would only buy cost). `KSPCalcSingularVal: 1` retained, so κ is reported.

Everything else unchanged: `transonicPCOption 1`, `natural`, `gmresRestart 200`, ASM overlap 1
(default), `DAFOAM_SUBPC_TYPE` unset, np=4, cold start, staged copy per guidelines §8.

**Memory arithmetic** (the standard set by the restart-challenge arm): rung 3 peaked at 11.65 GiB
at fill 0. ILU(1) adds fill-in on a 6-field Jacobian; the archived precedent at 99,840 cells went
18,422 MiB (fill 0) → ≥20,480 MiB (fill 1, censored at its cap), i.e. ≥+11%. Taking a 25–35%
increase as the working range gives a predicted peak of **~14.6–15.7 GiB against the 22 GiB cap**,
with the host at ~29 GB free. Affordable. Standing guard applies: stop and report if the container
approaches the cap or host MemAvailable falls below 6 GB, and **a memory death is NOT EVALUABLE**.

## 3. Grading — three outcomes, all reported the same way

Control for comparison, from the diagnostic run at identical settings (fill 0):
**residual `1.615428631404e-02` at iteration 400**, κ `9.57e+10`, `-3`.

- **CONVERGES** (`PetscConvergedReason: 2` on CD): the ceiling statement gains the boundary
  condition *"…under ILU(0); ILU(1) converges it"*, recorded as an unexplained engineering result.
  The proof clause stays NOT MET. The rung-3 ceiling record is amended to carry the boundary, and
  the elimination table is untouched — nothing in it is retracted by a knob that works.
- **DESCENDS MATERIALLY BUT DOES NOT CONVERGE** (residual at iteration 400 at least 10x below the
  control's `1.615e-02`, i.e. ≤ `1.615e-03`): reported as partial; no extension is run without a
  new approval, and the 10x bar is fixed here so it cannot be chosen afterwards.
- **STALLS** (within 10x of the control, or flat): fill level is not the lever either; it joins
  the elimination table as the ninth refuted candidate, and the ceiling stands unqualified.

## 4. Price, flagged before spending

Per-iteration cost at fill 0 without the monitor is 0.316 s (stage-1 basis, 4,000 iterations in
1,265 s); ILU(1) raises it ~30%, so ~0.41 s/iteration → 800 iterations ≈ 330 s plus ~150 s
primal/PC assembly ≈ **480 s ≈ 32 core-min**.

**That is ~2x the ~15 core-min approved, and I am saying so before running rather than after.**
The 15 core-min figure buys roughly 250 iterations, which cannot distinguish a stall from slow
descent — the control was still nominally moving in its sixth digit at 400. If the chief prefers
the 15 exactly, the cap drops to 400 and the arm answers only "does it beat the control at 400",
losing the chance to see convergence at all. I have chosen the 800 cap and flagged the overrun.
