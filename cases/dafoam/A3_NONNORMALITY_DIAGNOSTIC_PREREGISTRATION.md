# Rung 3 — departure-from-normality diagnostic: PRE-REGISTRATION

Filed 2026-08-10, chief-approved, **~25 core-min HARD CAP**. Committed BEFORE any computation.
This is the capstone question the fill-1 arm generated: ILU(1) improved the mid-cycle
preconditioned condition estimate by ~10^7 (4.69e+10 → 1.66e+03) and the solve still stalled at
1.9x, so the condition estimate is not predicting convergence. Reading (ii) — non-normality —
would explain the entire nine-row elimination table in one stroke, because a non-normal operator's
GMRES behaviour is not governed by its spectrum at all, and every remedy tried so far targets
scale, structure or decomposition.

**Retro-justification guard stays armed:** whatever this returns, it does not revive the Saad
arm's NOT-MET proof clause and does not retract any row of the elimination table.

## 1. Price, before running — and it is the unusual part

**Zero solver core-min.** Both assembled operators are already on disk from the diagnosis arms:
`A3-diag-rung3/pmat_rung3.dat` (983 MB, 724,609 unknowns, 81,718,327 nonzeros) and
`A3-diag-rung2/pmat_rung2.dat` (517 MB, 384,518 unknowns, 42,988,956 nonzeros). No container, no
solver, no new dump. The cost is my own offline wall time, estimated 10–20 minutes of numpy/scipy.

**Memory arithmetic** (fourth application; the previous three landed at 3.3%, within-range, and
within-range): rung-3 CSR = 81.7M float64 values (654 MB) + 81.7M int32 indices (327 MB) + row
pointers (~6 MB) ≈ **0.99 GB**; rung 2 ≈ 0.52 GB; probe vectors 5.8 MB each, negligible; scipy's
`.T` returns a CSC **view sharing the same buffers**, so transposed products add nothing. Peak
**≈1.6 GB against ~29 GB free.** Safe by three orders of headroom.

**This comes in at ~0 of the 25 core-min cap because the expensive part was already paid for by
the diagnosis arms.** No half-measure is being substituted for a decisive measurement — the
decisive measurement happens to be affordable.

## 2. Step 1 — test reading (i) FIRST, as ordered, at zero cost

Reading (i): `KSPComputeExtremeSingularValues` returns extremes of the **current cycle's**
Hessenberg matrix — a lower bound over the visited Krylov subspace, not the operator's spectrum.
If (i) alone explains the seven-order jump, (ii) is unmotivated and this stops there.

**The discriminator, computable from logs already on disk:** the estimate's *within-run*
variability bounds how much of any difference is subspace artifact. Every `sMax/sMin` reading
from the control (fill 0) and the fill-1 arm is tabulated, restart-boundary readings
(`1./1.=1.`, where the Hessenberg estimate is empty) excluded as degenerate, and the ratio
between within-run spread and the between-configuration jump computed.

- **If the within-run spread is comparable to the 10^7 jump** → (i) explains it, (ii) is
  unmotivated, **stop**, and record that the seven-order number was an artifact of my own
  instrument.
- **If the within-run spread is orders of magnitude smaller than the jump** → (i) is
  insufficient, (ii) is motivated, and step 2 runs.

## 3. Step 2 — the measurable, and why this one

**Normalized Frobenius departure from normality:**

    nu_F(P) = || P^T P − P P^T ||_F / || P ||_F^2

The commutator `P^T P − P P^T` is exactly zero iff P is normal, so this is the standard scalar
departure-from-normality (Henrici's measure in its Frobenius form), normalized to be
dimensionless and scale-invariant — necessary here, because the operator spans 14.5 decades and
any unnormalized norm would just re-measure the scale spread I already refuted.

**Why it is computable at this size:** forming `P^T P` explicitly is out of the question (fill),
but its Frobenius norm is not needed — only the commutator's, and for any C,
`E[|| C z ||^2] = tr(C^T C) = || C ||_F^2` for random z with `E[z z^T] = I` (Hutchinson). With
`C z = P^T(P z) − P(P^T z)`, each sample costs **four sparse mat-vecs** and no fill at all.
`|| P ||_F^2` is exact and free (sum of squares of the stored values). Rademacher probes,
**k = 200 samples**, with the reported figure carrying a standard error from the sample variance
so the number arrives with an error bar rather than as a point claim.

**Why it discriminates, and the control that gives the number meaning:** a bare non-normality
figure is uninterpretable — this is the lesson the diagonal-spread refutation taught, where 14.47
decades looked damning until 14.40 decades turned out to converge. So the measurement is run
**identically on rung 2's operator, the rung that CONVERGES**, and the finding is the
**comparison**, not the rung-3 value alone.

**Stated limitation, prominently, because it bounds every conclusion below:** the dumped matrix is
DAFoam's assembled preconditioner matrix `dRdWTPC`, **not** the matrix-free transpose Jacobian
GMRES applies, and **not** the preconditioned operator `A M^-1` whose normality actually governs
convergence. This measures the non-normality of the operator DAFoam builds its preconditioner
from. That is indicative — `dRdWTPC` is DAFoam's own approximation to the transpose Jacobian —
and it is not conclusive. Any positive result is therefore a **motivated hypothesis with a
measurement behind it**, not a proven mechanism, and it will be worded that way.

## 4. Pre-stated outcomes — no third reading invented afterwards

Decision bar fixed now: rung 3 counts as **markedly more non-normal** if `nu_F(rung3)` exceeds
`nu_F(rung2)` by **at least 3x**, well outside the Hutchinson standard error at k = 200.

- **Rung 3 markedly more non-normal than rung 2** → the elimination table gains its unifying
  explanation: nine refuted candidates stop looking like nine coincidences, because every one of
  them targets scale, structure or decomposition and none targets non-normality. **The ceiling
  gains a candidate MECHANISM rather than only a bracket**, stated as motivated-and-measured
  rather than proven, with the §3 limitation attached. The report's chapter changes shape.
- **Comparable (within 3x)** → **non-normality does not discriminate the converging rung from the
  stalling one.** The mechanism remains unknown, the elimination table stands exactly as
  published, and I say so plainly — the same way the diagonal-spread refutation was recorded. The
  hypothesis my own fill-1 arm generated would then be refuted by my own follow-up, which is the
  outcome I should be most willing to report.
- **Rung 3 markedly LESS non-normal** → reported as the surprise it would be; no mechanism
  claimed, and the reading recorded as refuted in the strong direction.

Auxiliary numbers reported alongside for context but carrying **no verdict**: the skew fraction
`|| (P − P^T)/2 ||_F / || P ||_F` (asymmetry, which is not non-normality — a rotation is normal
and maximally asymmetric) and each matrix's symmetry pattern. They are context, and the §4 bar
is the only thing that decides.

---

# §5. RESULTS — **reading (i) refuted, then reading (ii) refuted. The mechanism remains unknown.**

## Step 1 — reading (i) is insufficient (zero cost, from logs already on disk)

Every non-degenerate `sMax/sMin` reading (restart-boundary `1./1.=1.` entries excluded as empty
Hessenberg estimates):

| run | readings | values | within-run spread |
|---|---|---|---|
| fill 0 control | 3 | 4.309e+10, 4.687e+10, 9.572e+10 | **2.22x** |
| fill 1 arm | 5 | 1.845e+03, 1.660e+03, 1.860e+03, 1.760e+03, 1.080e+04 | **6.51x** |
| overlap 2 arm | 3 | 4.389e+10, 4.589e+10, 1.017e+11 | **2.32x** |

Subspace-to-subspace variability is at most **6.5x**; the fill0→fill1 jump is **~2.5e+07**.
**The jump exceeds the artifact scale by six to seven orders of magnitude**, so reading (i) cannot
account for it. Step 2 is motivated, exactly as pre-registered.

*Bonus control, unplanned:* the fill-0 and overlap-2 runs — different arms, hours apart — return
near-identical estimates at matched iterations (4.31e10 vs 4.39e10; 4.69e10 vs 4.59e10; 9.57e10 vs
1.02e11). The estimate is reproducible, which both validates it as an instrument and independently
re-confirms that doubling the ASM overlap did nothing.

## Step 2 — the measurement, and it goes the OTHER way

Hutchinson estimator, k = 200 Rademacher probes, four sparse mat-vecs per probe, seed fixed:

| | rung 2 — **CONVERGES** (42,120 cells) | rung 3 — **STALLS** (79,560 cells) |
|---|---|---|
| unknowns / nonzeros | 384,518 / 42,988,956 | 724,609 / 81,718,327 |
| ‖P‖_F | 4.261146e+12 | 7.587909e+12 |
| **nu_F = ‖PᵀP − PPᵀ‖_F / ‖P‖_F²** | **4.298842e−03** [95% CI 4.2813e−03, 4.3163e−03] | **2.651122e−03** [95% CI 2.6377e−03, 2.6645e−03] |
| skew fraction (context, no verdict) | 0.3502 | 0.3058 |

**Ratio rung3/rung2 = 0.617, against a pre-registered bar of ≥ 3.0.**

**Reading (ii) is REFUTED.** The stalling rung is not more non-normal than the converging one — it
is measurably **less** so, by 1.62x, with non-overlapping confidence intervals, so the difference
is real and precisely resolved rather than a null from noise. Both operators are only mildly
non-normal in absolute terms (nu_F ~ 10⁻³ on a measure whose range runs to order 1).

The pre-registered branch fires as written: *"non-normality does not discriminate the converging
rung from the stalling one. The mechanism remains unknown, the elimination table stands exactly as
published, and I say so plainly."* **The hypothesis my own fill-1 arm generated is refuted by my
own follow-up.** That is the outcome I said I should be most willing to report, and it is the one
that arrived.

**Limitation, restated because it bounds the claim in both directions:** this measures DAFoam's
assembled preconditioner matrix `dRdWTPC`, not the matrix-free transpose Jacobian nor the
preconditioned operator `A M⁻¹` whose normality actually governs GMRES. A conclusive test would
need the preconditioned operator, which this build never assembles. So the honest scope is: **the
non-normality of the operator DAFoam builds its preconditioner from does not distinguish the rung
that converges from the rung that does not**, and it therefore fails to explain the elimination
table. It does not prove the preconditioned operator is well-behaved.

## §5.1 Elimination table — tenth entry

**Non-normality (of the assembled PC operator)** — nu_F 2.65e−03 at the stalling rung against
4.30e−03 at the converging one, ratio 0.617 against a 3.0 bar. Refuted as a discriminator.

Ten candidate causes have now been tested and refuted by measurement: method breakdown, Krylov
subspace size, field separation, geometric localization, mesh volume scaling, diagonal-spread
magnitude, one-level Schwarz overlap, stronger PC application, ILU fill level, and non-normality.
**The surviving statement is unchanged and now better defended: the rung-3 wall is real, it is not
memory, and nothing this build exposes — and nothing measurable on the operator it assembles —
distinguishes it from the rung that converges.** What remains unexplained is now precisely bounded
rather than vaguely open, and the capability-boundary defect (`f29378d9`) names why the next class
of remedy cannot even be attempted here.

## §5.2 Cost

**0 of the 25 core-min cap** — no solver ran; both operators were already on disk, and the offline
computation took 6 s + 48 s (rung 3) and 3 s + 24 s (rung 2). Peak memory ~1.6 GB against ~29 GB
free, inside the pre-registered arithmetic for the fourth consecutive arm.
