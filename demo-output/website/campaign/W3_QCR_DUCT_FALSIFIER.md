# W3 — QCR2000 on the training ducts: the falsifier verdict and the rank-2 parity term

Record for two docket items executed together, 2026-08-05:

- `w3-qcr-constitutive-term-for-rank2-parity` — build the untrained QCR2000
  constitutive term the rank-2 closure-challenge entry carries.
- `w2-the-duct-zero-stated-as-a-structural-limit-with-a-falsifier` — the
  falsifier arm, whose pre-registered instrument is *"the toolchain's shipped
  quadratic eddy-viscosity closure, run once on the smallest training duct's
  existing mesh."*

**TEST-BLIND.** Every case run here is in the benchmark's own **training**
column (`AR_1_Ret_180`, `AR_3_Ret_180`, `AR_5_Ret_180`, `AR_10_Ret_180`,
README lines 71–77). The three scored test ducts — `AR_1_Ret_360`,
`AR_3_Ret_360`, `AR_14_Ret_180` — were not opened. Nothing was fitted, nothing
was tuned, no scoring call was made. `Ccr1 = 0.3` is Spalart's 2000 published
constant, adopted untrained exactly as the rank-2 entry adopts it.

Pre-registration written before any solve: `PREDICTION.md` in
`/home/ubuntu/certonomous-runs/w3-qcr-duct/`.

---

## 1. Shipped or patched: **patched**, and the patch is small

The proposal asked to check first whether QCR ships. It does not, in either
tree the lab holds:

| tree | search | result |
|---|---|---|
| OpenFOAM v2606, host install `/usr/lib/openfoam/openfoam2606/src` | `grep -rli qcr src/` | **zero hits** |
| OpenFOAM v2506 inside `dafoam/opt-packages:latest` | `grep -rli qcr .../OpenFOAM-v2506/src/` | **zero hits** |

Neither ships `kOmegaSSTQCR`, `SpalartAllmarasQCR`, nor any QCR switch on a
turbulence-model dictionary. The RAS directory listing is the stock set
(`EBRSM LRR LaunderSharmaKE RASModel RNGkEpsilon SSG SpalartAllmaras
kEpsilon kEpsilonPhitF kOmega kOmegaSST kOmegaSSTLM kOmegaSSTSAS
realizableKE`) plus the incompressible nonlinear group (`LienCubicKE`,
`ShihQuadraticKE`, `LienLeschziner`) — quadratic *eddy-viscosity* models, not
the QCR constitutive rotation. **So this was code, not configuration.**

### 1.1 Where the stress divergence lives — the proposal's open scoping question, answered

The cost basis named one unpriced question: *"where DAFoam's momentum equation
takes its stress divergence from, and hence whether QCR is a
turbulence-model-class change or a solver-class change."* Answered by reading:

`src/TurbulenceModels/turbulenceModels/linearViscousStress/linearViscousStress.C:107`

```
divDevRhoReff(volVectorField& U) const
{
    return
    (
      - fvc::div((this->alpha_*this->rho_*this->nuEff())*dev2(T(fvc::grad(U))))
      - fvm::laplacian(this->alpha_*this->rho_*this->nuEff(), U)
    );
}
```

`divDevRhoReff` is **virtual on the turbulence model** and the solver
(`simpleFoam`'s `UEqn.H`) only calls it. So QCR is a **turbulence-model-class
change, not a solver-class change**: no solver is patched, no solver is
rebuilt, and the term rides a user library the case loads by name. This is the
cheapest structural outcome available and it is now measured rather than
assumed.

### 1.2 The patch

`sdk/openfoam/qcr/kOmegaSSTQCR/` — 3 files, ~180 lines, deriving from stock
`kOmegaSST` and overriding `divDevRhoReff` (both overloads) and
`devRhoReff`. Implements the rank-2 entry's Eq. (1) verbatim:

```
tau_ij = tau^l_ij - c_r ( O_ik tau^l_kj - tau^l_ik O_kj )
O_ij   = (d_j U_i - d_i U_j) / sqrt(d_n U_m d_n U_m)
c_r    = 0.3   (Spalart 2000, untrained)
```

with `tau^l = nut * devTwoSymm(grad U)` (turbulent part only — the molecular
stress is not rotated) and the normalisation floored at `SMALL` for the
zero-shear cells. `k` and `omega` transport are inherited **unchanged**: QCR2000
is constitutive-only, per Spalart and per the entry.

Built first-pass clean with stock `wmake libso` against the host v2606
(`libkOmegaSSTQCRTurbulenceModels.so`). A case activates it with two lines:
`libs ( "libkOmegaSSTQCRTurbulenceModels.so" );` in `controlDict` and
`RASModel kOmegaSSTQCR;` in `turbulenceProperties`.

**The proposal's gate is met on its first clause** — the term is active in the
primal — and its alternative clause (a documented statement of where the stress
divergence lives) is delivered anyway, in §1.1, because it turned out to be the
fact that made the term cheap. The adjoint/FD half of the gate is *not* claimed
here: this run is primal-only, the DAFoam rebuild was not attempted, and that
remains the item's open half. Said plainly rather than folded into a pass.

---

## 2. The falsifier verdict: **the structural claim is CONFIRMED**

Two forward primals, **same mesh, same BCs, same `fvOptions` bulk-velocity
forcing, same schemes, same `fvSolution`**, differing only in the RAS model
name. Graded by the unmodified gate instrument
`dafoam/ladder-b/duct_baseline/duct_secondary_flow.py`.

| arm | in-plane RMS, % of Ubar (37.5 m/s) | converged |
|---|---|---|
| stock `kOmegaSST` | **3.16e-16** | 401 iters, `residualControl` |
| `kOmegaSSTQCR`, Ccr1 = 0.3 | **0.6239** | 401 iters, `residualControl` |
| reference LES/DNS field (`0/U_LES`) | 0.7570 | — |

The pre-registered thresholds were: above 0.1 percent confirms, below 1e-10
refutes, between the two is indeterminate. **0.6239 percent is above the
confirming threshold by a factor of six**, and it lands at **82 percent of the
reference field's own in-plane magnitude**.

So the structural reading holds on its own instrument: a change that adds
*nothing but a quadratic constitutive relation*, on the identical mesh, with
identical boundary conditions and an unchanged `k`–`omega` system, recovers
secondary flow that the linear model expresses at machine zero. The duct zero
is a property of the closure class, not of the setup. **The tensor-basis
carrier is not being built on a wrong premise.**

### 2.1 The falsifier was run with a control, and the control is exact

The confirming direction was flagged in the pre-registration as the weaker
inference, so it was strengthened rather than accepted. Two independent checks:

**(a) `Ccr1 = 0` control.** The same new library, same binary, same case, with
the QCR coefficient set to zero:

```
max |U(kOmegaSSTQCR, Ccr1=0) - U(stock kOmegaSST)| = 0.0
```

Bit-for-bit identity, and its own in-plane RMS returns to 3.16e-16. The library
adds **nothing whatsoever** except the QCR term, and the QCR term is therefore
the entire cause of the secondary flow. A latent asymmetry in the new code path
is excluded, not argued away.

**(b) Sign and structure.** A sign error in the commutator would produce
secondary flow of the right magnitude and the wrong orientation. Correlating
the in-plane vector components against the reference field gives Pearson
**r = +0.953**. The recovered flow is not merely nonzero, it is the reference
field's own eight-vortex structure, with the correct sign.

---

## 3. The measured field for the eval battery

Extended to all four training ducts (the same four the rank-1 entrant trains
on — see §4). Metric is the challenge's own form,
`mean(||U_pred − U_true||₂) / mean(||U_true||₂)`, evaluated over all cells.

| case | cells | SST in-plane % | QCR in-plane % | ref in-plane % | SST scaled MAE | QCR scaled MAE | change | in-plane r |
|---|---|---|---|---|---|---|---|---|
| `AR_1_Ret_180` | 2,209 | 3.2e-16 | 0.624 | 0.757 | 0.1076 | **0.0632** | **−41.2%** | 0.953 |
| `AR_3_Ret_180` | 6,627 | 5.5e-16 | 0.705 | 0.813 | 0.1122 | **0.0477** | **−57.5%** | 0.935 |
| `AR_5_Ret_180` | 11,045 | 8.3e-16 | 0.676 | 0.749 | 0.0958 | **0.0437** | **−54.4%** | 0.930 |
| `AR_10_Ret_180` | 22,090 | 1.1e-15 | 0.590 | 0.661 | 0.0604 | **0.0401** | **−33.5%** | 0.877 |

Every arm, every case: the linear model reads machine zero, QCR reads 79–93
percent of the reference magnitude, and the scaled MAE falls by a third to
well over a half — **from an untrained constant**.

**Three caveats, stated rather than buried:**

1. **This is not a challenge score and must never be quoted as one.** The
   challenge metric interpolates to 1,000 fixed evaluation points; this is an
   all-cell computation on training cases with no published floor. The
   *ratio* QCR/SST is the transferable quantity; the absolute numbers are not
   comparable to a leaderboard column.
2. **`AR_5_Ret_180` and `AR_10_Ret_180` are cap-stopped, not converged.** Both
   arms hit the pre-registered 3,000-iteration cap with `k` initial residual at
   8e-6 to 1.3e-5 against a `residualControl` threshold of 5e-6 — just outside.
   Under the lab's own `w7-cap-stopped-is-a-monitor-signature` rule these are
   reported as cap-stopped. Both arms of each pair stopped at the same cap on
   the same criterion, so the *comparison* is fair; the *absolute* values on
   those two rows carry an unquantified settling residue. `AR_1_Ret_180` (401)
   and `AR_3_Ret_180` (1,387 SST / 1,725 QCR) converged on their own control.
3. **QCR overshoots nothing and undershoots consistently** — the in-plane
   magnitude ratio is 0.82–0.90 across all four, never above 1. The untrained
   constant is systematically slightly weak, which is precisely the residue a
   trained coefficient or a trained beta would take up, and is consistent with
   the rank-2 entry carrying a trained beta alongside its untrained QCR.

---

## 4. Why this is the campaign's headline, in one number

Reissmann, Fang & Sandberg — **rank 1** — train on *exactly these four ducts*
(`CLOSURE_METHODS_COMPARISON.md` §2.1, from their own `score_eval.ipynb`) and
put their correction **inside the PDE**. Wu & Zhang — **rank 2** — are
SST-QCRC, also inside the PDE, and their duct scores are 0.0455 / 0.0399. Our
round-4 entry is a **post-hoc ML correction added to a converged field** and
scores 0.0811 / 0.0775 on the same two ducts.

Our deficit to rank 1 is +0.0059 overall, and 0.0107 of it — **1.8 times the
whole deficit** — sits in those two ducts alone. This run is the first
demonstration on this box that the in-PDE route is buildable here, costs one
small library, and moves the duct field by 33–57 percent with zero training and
zero leakage surface. The costed campaign that follows from it is
`CLOSURE_RANK1_CAMPAIGN.md`.

---

## 5. Cost

| arm | wall s | cores | core-min |
|---|---|---|---|
| `AR_1_Ret_180` SST | 29 | 1 | 0.48 |
| `AR_1_Ret_180` QCR | 5 | 1 | 0.08 |
| `AR_1_Ret_180` QCR, Ccr1=0 control | 4 | 1 | 0.07 |
| `AR_3_Ret_180` SST / QCR | 115 / 182 | 1 | 1.92 / 3.03 |
| `AR_5_Ret_180` SST / QCR | 147 / 147 | 1 | 2.45 / 2.45 |
| `AR_10_Ret_180` SST / QCR | 379 / 489 | 1 | 6.32 / 8.15 |
| **total solver** | **1,497** | | **24.95** |

Against a 60 core-min budget and a 30 core-min estimate for the item. The
library build was ~30 s of single-core compile, not solver time. The overrun
past the item's 30-estimate did not happen; the *extension* from one duct to
four cost 22 of the 25 and bought the four-case battery §3 rests on.

**Artifacts:** `/home/ubuntu/certonomous-runs/w3-qcr-duct/` — `PREDICTION.md`,
`ledger.txt`, `eval_battery.json`, `falsifier_result.json`, `battery.py`,
per-arm case directories with `log.simpleFoam` and final-time fields.
**Source:** `sdk/openfoam/qcr/kOmegaSSTQCR/`.
