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

---

# §5. RESULT: **STALLS — fill level is not the lever either. It becomes the ninth refuted candidate.**

Ledger rc=1, wall 508 s = **33.9 core-min** (estimated 32; the ~15 approved was flagged as
insufficient before launch). Proofs in-log: `ILU PC Fill Level: 1`, `transonicPCOption 1;`, no
sub-LU banner, cold start. Peak memory **14.33 GiB** against the predicted 14.6–15.7 GiB range
and the 22 GiB cap — the arithmetic held again.

| | control (fill 0) | fill 1 | |
|---|---|---|---|
| residual @ iteration 400 | 1.615428631404e−02 | 8.687780770929e−03 | **1.859x better** |
| residual @ iteration 800 | — | 8.512086557474e−03 | only **2.0% further** than its own 400 |
| total reduction from 2.1213e−02 | 1.31x | 2.49x | |
| reason | −3 | **−3** | |

**Against the pre-registered 10x materiality bar, 1.859x is a STALL, not a partial.** §3's third
branch fires as written: fill level joins the elimination table as the ninth refuted candidate,
and the rung-3 ceiling stands **unqualified** — no boundary condition is added, because none was
earned. The knob did not converge it, so the question of whether a convergence would have been
allowed to retro-justify the diagnosis never arises; the guard is recorded as having been in
place beforehand regardless.

## §5.1 The one genuinely surprising number, and what it does NOT license

Mid-cycle preconditioned condition estimates, measured at the identical point of the identical
cycle (iteration 300, restart 200, i.e. 100 iterations into cycle two):

| | control (fill 0) | fill 1 |
|---|---|---|
| `sMax/sMin` @300 | 1.379e+10 / 0.294228 = **4.69e+10** | 254.03 / 0.153029 = **1.66e+03** |

**ILU(1) improves the preconditioned condition estimate by roughly seven orders of magnitude —
and the solve still stalls, at 1.9x.** (Readings at iterations 200/400/600 print `1./1.=1.`:
those are exact restart boundaries where the Hessenberg estimate is empty, so only mid-cycle
values are comparable; at iteration 700 fill 1 reads 1.76e+03 and at 800, 1.08e+04.)

Stated plainly because it cuts against the tidy story: **κ estimated from the Krylov cycle is not
predicting convergence here.** A seven-decade improvement in that estimate buys 1.9x in residual.
Two readings are consistent with it and this arm cannot separate them:
(i) `KSPComputeExtremeSingularValues` reports extremes of the *current cycle's* Hessenberg matrix,
a lower bound over the visited subspace rather than the operator's true spectrum — so the control's
4.69e+10 may be measuring how badly the cycle is spanning the space, not the conditioning itself;
(ii) the true obstruction is not spectral condition at all but something the Krylov estimate does
not see (e.g. a near-defective/non-normal operator, where eigenvalue or singular-value clustering
does not govern GMRES convergence at all — Saad's own caution that for non-normal matrices the
spectrum alone tells you nothing about GMRES behaviour).

**Reading (ii) would explain the entire elimination table**, including why every scale-, structure-
and decomposition-based remedy has failed: non-normality is invisible to all of them. **I am not
claiming it.** It is a hypothesis this arm generated and did not test, it would need a departure-
from-normality measurement on the assembled operator to become a finding, and — per §1 — nothing
here revises the Saad arm's NOT-MET verdict or its published elimination table.

## §5.2 Elimination table, updated

Ninth entry: **ILU fill level** — `pcFillLevel 1` at rung 3 improves the mid-cycle condition
estimate by ~10^7 and the residual by 1.9x, and does not converge (`-3` at 800, flat after 400).
Recorded as an engineering result with no mechanism attached, exactly as pre-registered.
