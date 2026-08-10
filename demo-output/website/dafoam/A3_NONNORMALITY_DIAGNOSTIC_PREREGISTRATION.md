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
