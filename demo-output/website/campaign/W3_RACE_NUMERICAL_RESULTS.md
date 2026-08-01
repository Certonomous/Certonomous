# W3 — the race's numerical channel: results

Item: `w3-race-shrink-the-dominant-term`. Gates fixed in
`W3_RACE_NUMERICAL_PREREGISTRATION.md`, committed 05abf189 before any solve
below alpha = 0 was launched. Run 2026-08-01, 14:22 to 14:25 UTC.

Primary evidence: `demo-output/website/race/w3_refine/g2_scan.json` and
`demo-output/website/race/w3_refine/g3_peak.json`, each carrying every solved
point with its own wall clock. Prior record:
`demo-output/website/race/pass2/race.json`.

---

## The gates, as they fell

**G1 — reproduction. PASS, bit-identical.** 2026-08-01 14:22:03 UTC, alpha = 0,
Re_c = 1.0e6: L/D 18.140687390989, cl 0.248302524055, cd 0.013687602829, 3.93 s.
Every digit matches `race.json`'s `mc_points[0]`, so the machine, the toolchain
and the wing are the ones that produced the stored act.

**G2 — is the reported peak a boundary optimum? FAIL, and the failure is the
finding.** 23 solves on a 0.5-deg grid over alpha in [-8, +3]:

| alpha | -1.0 | -0.5 | **0.0** | +0.5 | +1.0 |
| --- | --- | --- | --- | --- | --- |
| L/D | 17.3542 | 17.9237 | **18.1407** | 18.0683 | 17.8546 |

The maximum falls at alpha = 0, with lower values on **both** sides. The peak is
a **genuine interior maximum** that happens to sit within an eighth of a degree
of the boundary of the interval the act searched. My pre-registered hypothesis —
that the cambered section's optimum lay at negative incidence and the act had
reported a boundary optimum — is **wrong, and is refuted by its own gate.**
L/D falls away below zero incidence faster than above it (17.9237 at -0.5
against 18.0683 at +0.5); the wing's profile drag does not drop fast enough to
pay for the lost lift.

**G3 — does refinement shrink the term, or only rename it? PASS.** 15 solves on
a 0.125-deg grid over [-0.75, +1.0]. Solved maximum L/D 18.149284 at
alpha = +0.125. A quadratic through the three solved points nearest it
(0.0, 0.125, 0.25) gives `L/D = 18.140687 + 0.138672 a - 0.559168 a^2`, vertex
at **alpha = +0.12400 deg, L/D 18.149285**.

| half-step (deg) | 0.5 | 0.25 | 0.125 |
| --- | --- | --- | --- |
| bracket, stored global fit | 0.41913 | 0.20943 | 0.10468 |
| bracket, resolved local fit | **0.13979** | **0.03495** | **0.00874** |

The stored bracket ratio between half-step 0.5 and 0.25 is 2.0011. The resolved
one is **4.0000**. The pre-registered threshold was "nearer 4 than 2". The term
is curvature-limited once it is measured on a surrogate that represents the
function where the peak actually is, so refining the angle grid genuinely
resolves it instead of rescaling it.

**G4 — the number.** At the act's own `TOLERANCE_DEG = 0.5`, the numerical
channel is **0.140**, against the published **0.419**. Recomposed through the
act's own `uq.combine_expanded` with its other two channels unchanged
(input 2-sigma 0.072, model 0.056):

| | numerical | composed 95% band |
| --- | --- | --- |
| published | 0.419 | **±0.4288** |
| resolved | 0.140 | **±0.1671** |

The headline tightens by a factor of **2.57**. The numerical channel still
dominates — it is 70% of the composed variance — but it now falls as the square
of the step, so the next halving buys a real factor of 4 rather than a factor
of 2 of relabelling.

---

## What was wrong, and it is not what the record says

Both the proposal and the act's own published narration give the same cause.
`race_study.py` emits, when `peak_at_edge` holds:

> the peak sits on the α = 0° edge of the range, where a half step reads slope
> and not curvature

**That explanation is false, and G2 measured it false.** The peak is interior.
The bracket read a slope for a different reason: `peak_grid_bracket` evaluates
it on a quadratic fitted through the reduced-order lane's four anchors, at
alpha = 0, 3.3, 6.7 and 10 degrees. That fit spans the whole interval, so near
the peak it is not a local model at all:

| | curvature coefficient at the peak |
| --- | --- |
| global fit through the four anchors | **+0.0021771** |
| resolved local fit, three solved points 0.125 deg apart | **-0.5591681** |

The global fit has the **wrong sign** and is **257 times too small** in
magnitude. Its stationary point is at alpha = 192.3 deg, so `alpha_star = 0.0`
was produced by the clamp `min(max(vertex, ALPHAS[0]), ALPHAS[-1])` and not by
locating anything. `peak_at_edge` then tested whether `alpha_star` landed on an
end of the swept range — which it did — and attributed the large bracket to
that. Two independent facts happened to point the same way and the wrong one
was published as the cause.

The distinction matters because it changes the remedy. If the peak were on a
boundary, no amount of grid refinement inside the interval would help and the
interval itself would have to be extended. Because the peak is interior and the
surrogate is merely too wide, the fix is to **bracket on a local fit** — which
costs 15 solves and 1.0 core-minutes, measured below.

The proposal's own remedy, "halving the grid step near the peak", would have
reported 0.209 in place of 0.419 and measured nothing: on the stored global fit
the bracket halves exactly with the step, to five figures. That is recorded here
as a corrected premise rather than an executed one.

---

## Cost, estimated against measured

| | solves | core-minutes | wall |
| --- | --- | --- | --- |
| pre-registered estimate | 40 | 2.6 | ~20 s |
| **measured** | **39** | **2.644** | **24.9 s** |

Run as **8 concurrent single-process VSPAERO solves — separate processes, not
MPI ranks**; VSPAERO is invoked here without a thread flag. The 39th is the G1
reproduction solve, which ran alone. Per-solve cost was flat across all 39 at
3.91 to 4.50 s, so concurrency cost nothing in throughput: the 38 concurrent
solves totalled 154.7 core-seconds in 21.0 s of wall, **7.4x on 8 processes**.

The estimate was derived from one measured solve (3.93 s at 14:22:03 UTC) and
came in **1.7% high on core-minutes**. The docket's `est_core_min` for this item
is **30.0**, carrying no rank count and no per-solve time. The measurement is
**11.3 times cheaper**. The item was ranked at 0.100 gain per core-minute on
that price; on the measured price it ranks at 1.13, which would have placed it
above every other compute item on the approved list.

---

## What is not done

The act still publishes ±0.43. Nothing here has been changed in
`race_study.py`, because moving `peak_grid_bracket` onto a local fit changes a
filmed act's headline number and its narration, and that needs the act re-run
and re-verified rather than the number edited. The measurement, the local fit
and the recomposed band are on the record so that change can be made against
evidence; a follow-on proposal is filed for it.
