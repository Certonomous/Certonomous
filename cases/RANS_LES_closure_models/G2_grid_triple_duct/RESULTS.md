# G2 — grid-convergence triple, square duct AR_1_Ret_360: RESULT

**RUNG VERDICT: `PASS`.**

**Closure's first converged grid-convergence triple, and the first `PASS` this
line has produced.** Graded 2026-08-28T17:40Z, comparator exit status **0**.

Comparator sha256
`6839aad1d91db7c2a413e61c53b8e3c904a1651d948a9e3795f34391f472bbd9` — **identical
on disk, at HEAD, and in the blob at the amendment commit `04366870`**, which is
rule 2's check that the frozen file is the file that ran. Raw stdout at
`artefacts/g2_grading_stdout_2026-08-28T1740Z.txt`.

---

## 1. The result

| functional | L1 (1,024) | L2 (4,096) | L3 (16,384) | R | triple | p (band) | GCI_fine (ceiling) | verdict |
|---|---|---|---|---|---|---|---|---|
| **gradP** — PRIMARY, mean streamwise momentum source, m/s² | 52172.3179852 | 53160.8696885 | 53590.2894333 | 0.434393 | **CONVERGING** | **1.2029** ([1.0, 3.0]) | **0.7693 %** (5.0 %) | **PASS** |
| Kint — volume-integrated k, m⁵/s² | 5.63182571058e-08 | 5.71135402457e-08 | 5.75367931852e-08 | 0.532204 | CONVERGING | 0.9099 ([0.5, 3.0]) | 1.0461 % (10.0 %) | PASS |
| tauwint — integrated streamwise wall shear, m⁴/s² | 5.21723179852e-05 | 5.31608696885e-05 | 5.35902894383e-05 | 0.434393 | CONVERGING | 1.2029 ([0.5, 3.0]) | 0.7693 % (10.0 %) | PASS |

Richardson extrapolate for the primary: **53920.0887131**. All three triples are
monotone with `R < 1`, so the order and GCI are quoted from inside the branch that
established monotonicity — never outside it.

**The headline is the primary's. The secondaries carry their own verdicts and
never change it.**

## 2. The honest caveat on the observed order, stated because a PASS invites less scrutiny

**`p = 1.2029` is inside the registered band and it is at the LOW end of it.** The
band `[1.0, 3.0]` was frozen before any value existed, and 1.2029 passes it on the
band's own terms. But a reader should not take this as a demonstration of
second-order behaviour: a nominally second-order scheme would give `p ≈ 2`, and
**1.20 is closer to first order than to second.** That is a statement about the
discretisation actually achieved on this mesh family — limiters, the wall
treatment, and the single streamwise cell all plausibly contribute — and **none of
those causes is established here.** The rung's claim is that the triple converges
monotonically at a measured order inside a pre-registered band, with a small GCI.
It is not a claim about scheme order, and it is not evidence of one.

The GCI is the part that is unambiguously good: **0.77 % on the primary against a
5 % ceiling** means the fine-grid discretisation uncertainty is small.

## 3. Contrast with G1, because the two rungs disagree and the disagreement is informative

G1/G1b ran the same *kind* of rung on the **periodic hill** and its triple was
**`DIVERGENT`** (`R = 8.5436`; differences growing under refinement). G2 on the
**square duct** is **`CONVERGING`** on all three functionals. Same lab, same
comparator design, same Roache gating, opposite outcomes.

**This is not a contradiction and neither result impeaches the other.** The duct
at `Re_tau = 360` is a simple, attached, statistically one-dimensional flow whose
solution is smooth on a Cartesian mesh; the periodic hill has a separating shear
layer and a reattachment region whose resolution changes qualitatively between
3,840 and 61,440 cells. **A grid triple measures the mesh family it was run on,
not the solver.** What the pair establishes is that closure's comparator and its
gating produce `PASS` and `NOT A RESULT` on the same instrument — which is the
minimum evidence that the gate discriminates at all.

## 4. The controls, and the one that decided the rung

All four planted controls round-tripped real files through the same readers the
real data goes through:

- **gradP** — plant `1.234567e-03` written to disk and read back exactly; the
  unplanted file reads `53590.2894`, so the reader is not a constant.
- **Kint** — uniform-k closed form and a single-cell plant at a known index both
  recovered; `sum(V) = 1.000000000e-09` against the closed form.
- **tauwint** — uniform-shear closed form and a single-face plant both recovered
  exactly; a short face list **REFUSED**.
- **fatal** — *"a genuine `--> FOAM FATAL ERROR` block reads True and a fired
  sigFpe handler with its stack reads True, while a CLEAN log carrying OpenFOAM's
  `trapFpe:` banner verbatim reads False — the reader is a detector, not a
  constant."*

**That fourth control is why this rung has a verdict at all.** Its clause was
repaired **pre-compute** this morning (amendment 1, `04366870`) after the same
defect was found to have voided G1. **Had it not been, all three levels would have
refused on `P3 fatal` and this `PASS` would have been a `NOT A RESULT`** — the
entire 67.28 core-min spent to buy a refusal produced by a reader that fires on
OpenFOAM's own healthy-start banner. The repair's value is therefore measured, not
argued: **G1, unrepaired → `NOT A RESULT`; G2, repaired → `PASS`, on the same
instrument defect.**

The comparator additionally satisfies Sanaa's **birth requirement** (canonized
2026-08-28), demonstrated on **real** artifacts rather than synthetic strings and
recorded before this grading in `BIRTH_REQUIREMENT_CONFIRMATION.md`: over 1,200
real solver logs the frozen reader returns `fatal=True` on 35 and `fatal=False` on
1,165, including **1,036 real logs carrying the banner** that the superseded clause
would have called fatal. G2's own L1/L2/L3 logs read `fatal=False`.

**The reconstruction and family controls also passed:** the constructed dictionary
regenerates the shipped mesh to **4.800e-14 m** over 6,272 points; the `vertices`
block is byte-identical across L1/L2/L3; all bytes outside the single `hex` line
are byte-identical; and the cell counts 1,024 / 4,096 / 16,384 are distinct and in
the exact registered 1:4:16 ratio.

## 5. The momentum-balance identity — an alarm, not a gate, and it did not fire

At every level `gradP · V` agrees with the integrated wall shear to
**0.0000 %** against a registered alarm level of 5.0 %. It is **reported and never
gated**, by design: a near-identity that grades nothing cannot have been selected
to move a verdict. The measured disagreements are the reading this rung owes a
successor, which may register a real threshold **from them** rather than from an
argument.

## 6. Infrastructure defects, carried into the record and voiding nothing (L-342)

Two, on every level, both **INFRASTRUCTURE**:
- **I1** — `checkMesh` log absent or not `Mesh OK`;
- **I5** — the solver could not load a library named in the shipped
  `controlDict`. **The entry is kept, never deleted to tidy a case** (rule 14);
  the loader warns and continues.

**Bookkeeping never voids physics.** Neither defect touches a graded number, and
both are named beside the verdict rather than absorbed into it. I1 in particular
means this rung does **not** carry a mesh-quality certificate — the family control
proves the three meshes are one geometry at three resolutions, which is a
different claim from `Mesh OK`.

## 7. Cost, and the estimate-versus-actual calibration (rule 12)

| | core-min |
|---|---|
| registered estimate | 61.0 |
| registered cap | 120.0 |
| **measured actual** | **67.28** |

Per level, from `CHAIN.log`'s own readings at ranks 1: **L1 125 wall s = 2.083**,
**L2 642 s = 10.700**, **L3 3,270 s = 54.500**.

**Ratio actual/estimate = 1.1030** — a 10.3 % overshoot of the estimate, **56.1 %
of the cap**. Rule 12's overrun clause binds on the **cap**, which was never
approached; nothing was stopped and no gate moved. Dollars: 1.1213 core-h ×
$0.0513/core-h = **$0.05753, derived not measured**.

**The timing reservation this rung inherited is now settled by measurement.** My
predecessor declined to file G2 because L3's registered 2,949 s of work left only
**1.83× headroom** against its 5,400 s timeout and contention eats exactly that.
**L3 ran 3,270 wall s — 60.6 % of the guard.** The reservation was sound and the
margin held. It held because filing is not launching: the entry sat until the
runner's own ceiling released it, which is the protection the reservation was
asking for.

Grading pass: **3.11 s wall, 0.0518 core-min**, MaxRSS 122,884 kB.

A calibration row lands in `docs/COST_CALIBRATION.md`.

## 8. What this rung does NOT establish

**Numerical convergence only.** No reference field is read and none is compared:
this says nothing about agreement with DNS or LES truth for the square duct, and
in particular **nothing about the secondary-flow structure a linear
eddy-viscosity model cannot produce at all** — the comparator's own diagnostic
notes that the `Uy`/`Uz` residuals never fall because there is no secondary flow
to converge. A converged `gradP` on this mesh family is a statement about
discretisation error, not about physics.
